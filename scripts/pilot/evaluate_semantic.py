"""Run source-first coverage and claim-level factuality pilot evaluations.

The default is a local dry run. --execute makes paid Responses API calls.
Every evaluator response is saved before its structure and evidence are scored.
"""

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from generate_summaries import api_json, get_api_key


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data/cleaned/bills.jsonl"
SAMPLE = ROOT / "data/pilot/education-sample.json"
GENERATION_DIR = ROOT / "data/pilot/responses"
OUTPUT_DIR = ROOT / "data/pilot/evaluation/llm"
PROMPT_DIR = ROOT / "prompts"

EXPECTED_CORPUS_SHA256 = "df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a"
EXPECTED_SAMPLE_SHA256 = "0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1"
REASONING_EFFORT = "medium"
MAX_OUTPUT_TOKENS = 16384

STAGES = {
    "source": {
        "prompt": "pilot-eval-source-v1.txt",
        "prompt_sha256": "c86243259ccaf0fc9ce0a39153d3bf4bf3058299f4d3687b8894566a71c07e82",
        "format": "pilot-eval-source-v1.format.json",
        "format_sha256": "af19c35f54002e90a7b348d74f6d99d47551f085a8f308ac4b0ec427ef9aae73",
    },
    "coverage": {
        "prompt": "pilot-eval-coverage-v1.txt",
        "prompt_sha256": "bd2e322314353bfcf064a1a04b394109f55b35713695d32b60aac13ad1229b86",
        "format": "pilot-eval-coverage-v1.format.json",
        "format_sha256": "687b6ab37c18cffd8935191e505d1033bee9a831036569ff30bda4e844bb6595",
    },
    "factuality": {
        "prompt": "pilot-eval-factuality-v1.txt",
        "prompt_sha256": "0e42e30058942ba548c931e861e70ec312662fbfa954d792d1dead8acb3ef64b",
        "format": "pilot-eval-factuality-v1.format.json",
        "format_sha256": "c3e0f73e51f69d35f85d0f176e1ac932e85eee3714ffc0adc6cdc9d22e9f2869",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frozen(path: Path, expected_hash: str) -> bytes:
    data = path.read_bytes()
    if sha256(data) != expected_hash:
        raise SystemExit(f"Frozen input changed: {path.relative_to(ROOT)}")
    return data


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def exact_quote(quote: str, text: str) -> bool:
    return bool(quote.strip()) and norm(quote) in norm(text)


def load_stage_files() -> dict:
    stages = {}
    for name, paths in STAGES.items():
        prompt = frozen(PROMPT_DIR / paths["prompt"], paths["prompt_sha256"]).decode("utf-8")
        format_config = json.loads(frozen(PROMPT_DIR / paths["format"], paths["format_sha256"]))
        stages[name] = {"prompt": prompt, "format": format_config}
    return stages


def load_pairs() -> list[dict]:
    corpus_bytes = frozen(CORPUS, EXPECTED_CORPUS_SHA256)
    sample = json.loads(frozen(SAMPLE, EXPECTED_SAMPLE_SHA256))
    by_number = {
        r["bill_number"]: r
        for r in (json.loads(line) for line in corpus_bytes.splitlines() if line.strip())
    }
    pairs = []
    for item in sample["selected"]:
        number = item["bill_number"]
        source = by_number[number]["bill_text"]
        generation = json.loads((GENERATION_DIR / f"{number}.json").read_text(encoding="utf-8"))
        if (sha256(source.encode("utf-8")) != item["bill_text_sha256"]
                or generation["generation_status"] != "completed"
                or generation["bill_text_sha256"] != item["bill_text_sha256"]):
            raise SystemExit(f"Source or summary changed for {number}")
        pairs.append({"number": number, "sample": item, "source": source, "summary": generation["summary"]})
    return pairs


def parse_response(response: dict) -> dict:
    if response.get("status") != "completed" or response.get("error"):
        raise ValueError(f"Evaluator response status is {response.get('status')!r}")
    parts = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content["text"])
            elif content.get("type") == "refusal":
                raise ValueError("Evaluator refused")
    if not parts:
        raise ValueError("No evaluator output_text")
    value = json.loads("".join(parts))
    if not isinstance(value, dict):
        raise ValueError("Evaluator output is not an object")
    return value


def validate_source(value: dict, source: str) -> None:
    propositions = value.get("propositions")
    if not isinstance(propositions, list) or not propositions:
        raise ValueError("No source propositions")
    for index, item in enumerate(propositions, 1):
        if item.get("id") != f"P{index}" or item.get("importance") not in ("core", "supporting"):
            raise ValueError(f"Invalid source proposition ID or importance at {index}")
        if not item.get("proposition") or not item.get("section") or not exact_quote(item.get("source_quote", ""), source):
            raise ValueError(f"Missing content or nonmatching source quote for P{index}")


def validate_coverage(value: dict, propositions: list[dict], summary: str) -> None:
    assessments = value.get("assessments")
    if not isinstance(assessments, list) or len(assessments) != len(propositions):
        raise ValueError("Coverage does not assess every source proposition")
    expected = {item["id"] for item in propositions}
    seen = set()
    for item in assessments:
        ident = item.get("proposition_id")
        status = item.get("status")
        if ident not in expected or ident in seen or status not in ("full", "partial", "omitted"):
            raise ValueError("Invalid or duplicate coverage proposition ID/status")
        seen.add(ident)
        quote = item.get("summary_quote", "")
        if status == "omitted":
            if quote.strip():
                raise ValueError(f"Omitted proposition {ident} has a summary quote")
        elif not exact_quote(quote, summary):
            raise ValueError(f"Coverage quote does not match summary for {ident}")
        if not item.get("rationale", "").strip():
            raise ValueError(f"Coverage rationale missing for {ident}")
    if seen != expected:
        raise ValueError("Coverage proposition IDs do not match source inventory")


def validate_factuality(value: dict, source: str, summary: str) -> None:
    claims = value.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("No summary claims")
    for index, item in enumerate(claims, 1):
        verdict = item.get("verdict")
        error_type = item.get("error_type")
        if verdict not in ("supported", "contradicted", "not_established"):
            raise ValueError(f"Invalid verdict for claim {index}")
        if (verdict == "supported") != (error_type == "none"):
            raise ValueError(f"Inconsistent verdict and error type for claim {index}")
        if not item.get("claim") or not item.get("rationale") or not exact_quote(item.get("summary_quote", ""), summary):
            raise ValueError(f"Missing content or nonmatching summary quote for claim {index}")
        source_quote = item.get("source_quote", "")
        if source_quote and not exact_quote(source_quote, source):
            raise ValueError(f"Source quote does not match bill for claim {index}")


def build_input(stage: str, pair: dict, propositions: list[dict] | None = None) -> str:
    source_part = f"Bill number: {pair['number']}\n<bill_text>\n{pair['source']}\n</bill_text>"
    if stage == "source":
        return source_part
    summary_part = f"<summary>\n{pair['summary']}\n</summary>"
    if stage == "factuality":
        return source_part + "\n\n" + summary_part
    if propositions is None:
        raise ValueError("Coverage requires source propositions")
    inventory = json.dumps(propositions, ensure_ascii=False)
    return source_part + f"\n\n<source_propositions_json>\n{inventory}\n</source_propositions_json>\n\n" + summary_part


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def run_stage(stage: str, pair: dict, files: dict, api_key: str, model: str, propositions: list[dict] | None = None) -> dict:
    number = pair["number"]
    path = OUTPUT_DIR / stage / f"{number}.json"
    settings = STAGES[stage]
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if (saved.get("evaluation_status") != "completed"
                or saved.get("requested_model") != model
                or saved.get("prompt_sha256") != settings["prompt_sha256"]
                or saved.get("format_sha256") != settings["format_sha256"]
                or saved.get("source_sha256") != pair["sample"]["bill_text_sha256"]
                or saved.get("summary_sha256") != sha256(pair["summary"].encode("utf-8"))):
            raise SystemExit(f"Existing evaluator record needs review: {path}")
        parsed = saved["parsed"]
        if stage == "source":
            validate_source(parsed, pair["source"])
        elif stage == "coverage":
            validate_coverage(parsed, propositions, pair["summary"])
        else:
            validate_factuality(parsed, pair["source"], pair["summary"])
        print(f"Reused {stage} for {number}")
        return parsed

    body = {
        "model": model,
        "instructions": files[stage]["prompt"],
        "input": build_input(stage, pair, propositions),
        "reasoning": {"effort": REASONING_EFFORT},
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "text": {"format": files[stage]["format"]},
        "store": False,
    }
    response = api_json("POST", "/responses", api_key, body)
    saved = {
        "stage": stage,
        "bill_number": number,
        "source_sha256": pair["sample"]["bill_text_sha256"],
        "summary_sha256": sha256(pair["summary"].encode("utf-8")),
        "prompt_sha256": settings["prompt_sha256"],
        "format_sha256": settings["format_sha256"],
        "requested_model": model,
        "returned_model": response.get("model"),
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "request": body,
        "response": response,
    }
    try:
        parsed = parse_response(response)
        if stage == "source":
            validate_source(parsed, pair["source"])
        elif stage == "coverage":
            validate_coverage(parsed, propositions, pair["summary"])
        else:
            validate_factuality(parsed, pair["source"], pair["summary"])
        saved["parsed"] = parsed
        saved["evaluation_status"] = "completed"
    except (ValueError, KeyError, TypeError) as exc:
        saved["parsed"] = None
        saved["evaluation_status"] = "needs_review"
        saved["problem"] = str(exc)
    save(path, saved)
    print(f"Saved {stage} for {number}: {saved['evaluation_status']}")
    if saved["evaluation_status"] != "completed":
        raise SystemExit(f"Stopped after evaluator issue; review {path}")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-6-sol")
    parser.add_argument("--execute", action="store_true", help="make paid evaluator API requests")
    args = parser.parse_args()
    pairs = load_pairs()
    files = load_stage_files()
    print(f"Frozen corpus, summaries, evaluator prompts, and schemas: PASS ({len(pairs)} pairs)")
    if not args.execute:
        print("Dry run complete. No API calls made.")
        return
    api_key = get_api_key()
    for pair in pairs:
        source = run_stage("source", pair, files, api_key, args.model)
        propositions = source["propositions"]
        run_stage("coverage", pair, files, api_key, args.model, propositions)
        run_stage("factuality", pair, files, api_key, args.model)


if __name__ == "__main__":
    main()
