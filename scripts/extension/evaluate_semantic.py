"""Reuse frozen Astra source inventories to audit the 72 extension summaries.

Default mode validates every saved generation and original source inventory,
without API calls. --execute makes only the 144 new coverage/factuality calls.
"""

import argparse
import importlib.util
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/full"))
from common import (EVALUATOR, GEN_FORMAT_SHA, GEN_PROMPT_SHA, SAMPLE_SHA,
                    api_json, frozen, get_api_key, load_selected, save_record, sha)  # noqa: E402
from check_generation_feasibility import (CLAUDE_MODEL, parse_summary)  # noqa: E402
from generate_full import (FORMAT, GEMMA_MODEL, MAX_OUTPUT_TOKENS as GEN_MAX,
                           OUTPUT as GENERATION, PROMPT, validate_existing)  # noqa: E402

# The frozen full-study module imports the pilot's parse_response helper by
# module name; put that original helper ahead of this extension script.
sys.path.insert(0, str(ROOT / "scripts/pilot"))
spec = importlib.util.spec_from_file_location("frozen_full_eval", ROOT / "scripts/full/evaluate_semantic.py")
full_eval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(full_eval)

OUTPUT = ROOT / "data/extension/evaluation/llm"
PROVIDERS = {"claude": CLAUDE_MODEL, "gemma": GEMMA_MODEL}
EFFORT = "medium"
MAX_OUTPUT_TOKENS = 16384


def generation(provider: str, item: dict, prompt: str, fmt: dict) -> dict:
    model = PROVIDERS[provider]
    from check_generation_feasibility import build_request
    body = build_request(provider, model, item, prompt, fmt, GEN_MAX)
    path = GENERATION / provider / f"{item['sample']['bill_number']}.json"
    validate_existing(path, item, provider, model, body)
    return json.loads(path.read_text(encoding="utf-8"))


def source_inventory(item: dict, files: dict) -> list[dict]:
    path = full_eval.output_path("source", None, item["sample"]["bill_number"])
    if not path.exists():
        raise SystemExit(f"Frozen source inventory absent: {path}")
    parsed = full_eval.run_stage("source", item, files, api_key="")
    return parsed["propositions"]


def output_path(stage: str, provider: str, number: str) -> Path:
    return OUTPUT / stage / provider / f"{number}.json"


def run_stage(stage: str, provider: str, item: dict, summary: str,
              propositions: list[dict] | None, files: dict, key: str) -> None:
    number = item["sample"]["bill_number"]
    model = PROVIDERS[provider]
    path = output_path(stage, provider, number)
    _, prompt_sha, _, format_sha = full_eval.STAGES[stage]
    summary_sha = sha(summary.encode("utf-8"))
    inventory_sha = sha(json.dumps(propositions, ensure_ascii=False).encode("utf-8")) if propositions is not None else None
    if path.exists():
        record = json.loads(path.read_text(encoding="utf-8"))
        if (record.get("evaluation_status") != "completed"
                or record.get("generator_provider") != provider
                or record.get("generator_model") != model
                or record.get("sample_sha256") != SAMPLE_SHA
                or record.get("source_sha256") != item["sample"]["bill_text_sha256"]
                or record.get("summary_sha256") != summary_sha
                or record.get("inventory_sha256") != inventory_sha
                or record.get("prompt_sha256") != prompt_sha
                or record.get("format_sha256") != format_sha
                or record.get("requested_model") != EVALUATOR
                or record.get("returned_model") != EVALUATOR
                or record.get("quote_validator_version") != full_eval.QUOTE_VALIDATOR_VERSION):
            raise RuntimeError(f"Existing evaluator record mismatch: {path}")
        parsed = full_eval.parse_response(record["response"])
        if parsed != record["parsed"]:
            raise RuntimeError(f"Evaluator raw/parsed mismatch: {path}")
        full_eval.validate(stage, parsed, item, summary, propositions)
        return
    body = {
        "model": EVALUATOR, "instructions": files[stage]["prompt"],
        "input": full_eval.build_input(stage, item, summary, propositions),
        "reasoning": {"effort": EFFORT}, "max_output_tokens": MAX_OUTPUT_TOKENS,
        "text": {"format": files[stage]["format"]}, "store": False,
    }
    response = api_json("POST", "/responses", key, body)
    record = {
        "stage": stage, "generator_provider": provider, "generator_model": model,
        "bill_number": number, "sample_sha256": SAMPLE_SHA,
        "source_sha256": item["sample"]["bill_text_sha256"],
        "summary_sha256": summary_sha, "inventory_sha256": inventory_sha,
        "prompt_sha256": prompt_sha, "format_sha256": format_sha,
        "requested_model": EVALUATOR, "returned_model": response.get("model"),
        "quote_validator_version": full_eval.QUOTE_VALIDATOR_VERSION,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "request": body, "response": response,
    }
    try:
        if response.get("model") != EVALUATOR:
            raise ValueError("Returned evaluator model differs from requested model")
        parsed = full_eval.parse_response(response)
        full_eval.validate(stage, parsed, item, summary, propositions)
        record["parsed"] = parsed
        record["evaluation_status"] = "completed"
    except (ValueError, KeyError, TypeError) as exc:
        record["parsed"] = None
        record["evaluation_status"] = "needs_review"
        record["problem"] = str(exc)
    save_record(path, record)
    if record["evaluation_status"] != "completed":
        raise RuntimeError(f"Evaluator issue for {provider} {stage} {number}: {record['problem']}")


def evaluate_bill(item: dict, summaries: dict, propositions: list[dict], files: dict, key: str) -> str:
    for provider in PROVIDERS:
        summary = summaries[provider]
        run_stage("coverage", provider, item, summary, propositions, files, key)
        run_stage("factuality", provider, item, summary, None, files, key)
    return f"Completed four Astra audits for {item['sample']['bill_number']}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise SystemExit("workers must be 1-4")
    _, selected = load_selected()
    prompt = frozen(PROMPT, GEN_PROMPT_SHA).decode("utf-8")
    fmt = json.loads(frozen(FORMAT, GEN_FORMAT_SHA))
    files = full_eval.stage_files()
    summaries = {}
    inventories = {}
    for item in selected:
        number = item["sample"]["bill_number"]
        inventories[number] = source_inventory(item, files)
        summaries[number] = {provider: generation(provider, item, prompt, fmt)["summary"]
                             for provider in PROVIDERS}
    print("Validated 36 original source inventories and 72 exact extension summaries", flush=True)
    print("Frozen Astra v2 prompts/schemas and evidence validator: PASS; 144 new audits", flush=True)
    if not args.execute:
        print("Dry run; no evaluator API calls made", flush=True)
        return
    key = get_api_key()
    available = {r["id"] for r in api_json("GET", "/models", key).get("data", [])}
    if EVALUATOR not in available:
        raise SystemExit("Frozen Astra evaluator unavailable")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(evaluate_bill, item, summaries[item["sample"]["bill_number"]],
                               inventories[item["sample"]["bill_number"]], files, key)
                   for item in selected]
        for future in as_completed(futures):
            print(future.result(), flush=True)
    print("All 144 extension Astra audits complete", flush=True)


if __name__ == "__main__":
    main()
