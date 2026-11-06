"""Run the frozen source-first Astra audits for the 36 paired summaries."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from common import (ROOT, SAMPLE_SHA, EVALUATOR, MODELS, api_json, frozen,
                    get_api_key, load_generation, load_selected, save_record, sha)
from evaluate_semantic import parse_response
from evidence_quotes_v2 import (VERSION as QUOTE_VALIDATOR_VERSION, validate_source,
                                validate_coverage, validate_factuality)

PROMPT_DIR = ROOT / "prompts"
OUTPUT = ROOT / "data/full/evaluation/llm"
EFFORT = "medium"
MAX_OUTPUT_TOKENS = 16384
STAGES = {
    "source": ("full-eval-source-v2.txt", "e60639a7b1cc45f710854a2953c71879cab08de1ffc6263661fcdea88e8badaf",
               "full-eval-source-v2.format.json", "744aacd831094d7b3ec5b57303bae790617526ba8025f82be7e65765e492186e"),
    "coverage": ("full-eval-coverage-v2.txt", "843a969af3d218c859abfa5c323a5c53b39f49df547a8b10a7f3eb59a7fccf65",
                 "full-eval-coverage-v2.format.json", "d48bc7aa5bba9079c7b4936a57d07033b3f2fd96b9495ec9b67ea5f4053cd915"),
    "factuality": ("full-eval-factuality-v2.txt", "cf94d6026e90bc3c1c2a9ced75353faddbe5497bab4b3b7c86dfe07f0de7775b",
                   "full-eval-factuality-v2.format.json", "7e29c626820e84e8c549e146c6fdfd80c30fd12daae2930302452153da40ea17"),
}


def stage_files() -> dict:
    files = {}
    for stage, (prompt_file, prompt_sha, format_file, format_sha) in STAGES.items():
        prompt = frozen(PROMPT_DIR / prompt_file, prompt_sha).decode("utf-8")
        format_config = json.loads(frozen(PROMPT_DIR / format_file, format_sha))
        if format_config.get("type") != "json_schema" or format_config.get("strict") is not True:
            raise SystemExit(f"{stage} does not use a strict JSON schema")
        files[stage] = {"prompt": prompt, "format": format_config}
    return files


def output_path(stage: str, model: str | None, number: str):
    return OUTPUT / stage / (model or "source_only") / f"{number}.json"


def build_input(stage: str, item: dict, summary: str | None, propositions: list[dict] | None) -> str:
    source = f"Bill number: {item['sample']['bill_number']}\n<bill_text>\n{item['bill_text']}\n</bill_text>"
    if stage == "source":
        return source
    if summary is None:
        raise ValueError("Summary is required")
    summary_part = f"<summary>\n{summary}\n</summary>"
    if stage == "factuality":
        return source + "\n\n" + summary_part
    if propositions is None:
        raise ValueError("Source propositions are required")
    inventory = json.dumps(propositions, ensure_ascii=False)
    return source + f"\n\n<source_propositions_json>\n{inventory}\n</source_propositions_json>\n\n" + summary_part


def validate(stage: str, parsed: dict, item: dict, summary: str | None, propositions: list[dict] | None) -> None:
    if stage == "source":
        validate_source(parsed, item["bill_text"])
    elif stage == "coverage":
        validate_coverage(parsed, propositions, summary)
    else:
        validate_factuality(parsed, item["bill_text"], summary)


def run_stage(stage: str, item: dict, files: dict, api_key: str,
              model: str | None = None, summary: str | None = None,
              propositions: list[dict] | None = None) -> dict:
    number = item["sample"]["bill_number"]
    path = output_path(stage, model, number)
    _, prompt_sha, _, format_sha = STAGES[stage]
    summary_sha = sha(summary.encode("utf-8")) if summary is not None else None
    inventory_sha = sha(json.dumps(propositions, ensure_ascii=False).encode("utf-8")) if propositions is not None else None
    if path.exists():
        record = json.loads(path.read_text(encoding="utf-8"))
        if (record.get("evaluation_status") != "completed" or record.get("requested_model") != EVALUATOR
                or record.get("returned_model") != EVALUATOR or record.get("sample_sha256") != SAMPLE_SHA
                or record.get("source_sha256") != item["sample"]["bill_text_sha256"]
                or record.get("summary_sha256") != summary_sha or record.get("inventory_sha256") != inventory_sha
                or record.get("prompt_sha256") != prompt_sha or record.get("format_sha256") != format_sha):
            raise RuntimeError(f"Existing evaluator record needs review: {path}")
        parsed = parse_response(record["response"])
        if parsed != record["parsed"]:
            raise RuntimeError(f"Parsed evaluator record differs from raw response: {path}")
        validate(stage, parsed, item, summary, propositions)
        return parsed
    body = {
        "model": EVALUATOR, "instructions": files[stage]["prompt"],
        "input": build_input(stage, item, summary, propositions),
        "reasoning": {"effort": EFFORT}, "max_output_tokens": MAX_OUTPUT_TOKENS,
        "text": {"format": files[stage]["format"]}, "store": False,
    }
    response = api_json("POST", "/responses", api_key, body)
    record = {
        "stage": stage, "generator_model": model, "bill_number": number,
        "sample_sha256": SAMPLE_SHA, "source_sha256": item["sample"]["bill_text_sha256"],
        "summary_sha256": summary_sha, "inventory_sha256": inventory_sha,
        "prompt_sha256": prompt_sha, "format_sha256": format_sha,
        "requested_model": EVALUATOR, "returned_model": response.get("model"),
        "quote_validator_version": QUOTE_VALIDATOR_VERSION,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "request": body, "response": response,
    }
    try:
        if response.get("model") != EVALUATOR:
            raise ValueError("Returned evaluator model differs from requested model")
        parsed = parse_response(response)
        validate(stage, parsed, item, summary, propositions)
        record["parsed"] = parsed
        record["evaluation_status"] = "completed"
    except (ValueError, KeyError, TypeError) as exc:
        record["parsed"] = None
        record["evaluation_status"] = "needs_review"
        record["problem"] = str(exc)
    save_record(path, record)
    if record["evaluation_status"] != "completed":
        raise RuntimeError(f"Evaluator issue for {stage} {model or 'source'} {number}: {record['problem']}")
    return record["parsed"]


def evaluate_bill(item: dict, summaries: dict, files: dict, api_key: str) -> str:
    number = item["sample"]["bill_number"]
    source = run_stage("source", item, files, api_key)
    propositions = source["propositions"]
    for model in MODELS:
        summary = summaries[model]
        run_stage("coverage", item, files, api_key, model, summary, propositions)
        run_stage("factuality", item, files, api_key, model, summary)
    return f"Completed Astra source + paired audits: {number} ({len(propositions)} propositions)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 4:
        raise SystemExit("workers must be 1-4")
    _, selected = load_selected()
    files = stage_files()
    summaries = {item["sample"]["bill_number"]:
                 {model: load_generation(model, item)["summary"] for model in MODELS}
                 for item in selected}
    print(f"Validated 36 sources, 72 raw summaries, frozen prompts and strict schemas; 180 Astra calls", flush=True)
    print(f"Evaluator {EVALUATOR}, effort {EFFORT}, max output tokens {MAX_OUTPUT_TOKENS}", flush=True)
    if not args.execute:
        print("Dry run; no API calls made", flush=True)
        return
    key = get_api_key()
    available = {r["id"] for r in api_json("GET", "/models", key).get("data", [])}
    if EVALUATOR not in available:
        raise SystemExit("Frozen evaluator model is unavailable")
    print("Account evaluator availability rechecked: PASS", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(evaluate_bill, item, summaries[item["sample"]["bill_number"]], files, key)
                   for item in selected]
        for future in as_completed(futures):
            print(future.result(), flush=True)
    print("All 180 Astra audits completed", flush=True)


if __name__ == "__main__":
    main()
