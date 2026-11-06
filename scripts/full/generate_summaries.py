"""Generate both frozen paired summaries for every full-study bill."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from common import (ROOT, SAMPLE_SHA, CORPUS_SHA, GEN_PROMPT_SHA, GEN_FORMAT_SHA,
                    MODELS, api_json, frozen, generation_path, get_api_key,
                    load_generation, load_selected, parse_summary, save_record)

PROMPT = ROOT / "prompts/pilot-summary-v1.txt"
FORMAT = ROOT / "prompts/pilot-summary-v1.format.json"
EFFORT = "medium"
MAX_OUTPUT_TOKENS = 8192


def build_request(model: str, prompt: str, format_config: dict, item: dict) -> dict:
    return {
        "model": model,
        "instructions": prompt,
        "input": f"Bill number: {item['sample']['bill_number']}\n\n<bill_text>\n{item['bill_text']}\n</bill_text>",
        "reasoning": {"effort": EFFORT},
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "text": {"format": format_config},
        "store": False,
    }


def generate(model: str, item: dict, prompt: str, format_config: dict, api_key: str) -> str:
    number = item["sample"]["bill_number"]
    path = generation_path(model, number)
    if path.exists():
        load_generation(model, item)
        return f"Reused {model} {number}"
    body = build_request(model, prompt, format_config, item)
    response = api_json("POST", "/responses", api_key, body)
    record = {
        "bill_number": number, "id": item["sample"]["id"], "cell": item["sample"]["cell"],
        "bill_text_sha256": item["sample"]["bill_text_sha256"],
        "corpus_sha256": CORPUS_SHA, "sample_sha256": SAMPLE_SHA,
        "prompt_sha256": GEN_PROMPT_SHA, "format_sha256": GEN_FORMAT_SHA,
        "requested_model": model, "returned_model": response.get("model"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "request": body, "response": response,
    }
    try:
        if response.get("model") != model:
            raise ValueError("Returned model differs from requested model")
        record["summary"] = parse_summary(response)
        record["generation_status"] = "completed"
    except (ValueError, KeyError, TypeError) as exc:
        record["summary"] = None
        record["generation_status"] = "needs_review"
        record["problem"] = str(exc)
    save_record(path, record)
    if record["generation_status"] != "completed":
        raise RuntimeError(f"Non-scorable response for {model} {number}: {record['problem']}")
    return f"Saved {model} {number}: {len(record['summary'].split())} words, {response.get('usage', {}).get('total_tokens')} tokens"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 4:
        raise SystemExit("workers must be 1-4")
    manifest, selected = load_selected()
    prompt = frozen(PROMPT, GEN_PROMPT_SHA).decode("utf-8")
    format_config = json.loads(frozen(FORMAT, GEN_FORMAT_SHA))
    if format_config.get("type") != "json_schema" or format_config.get("strict") is not True:
        raise SystemExit("Generation format is not a strict JSON schema")
    jobs = [(model, item) for item in selected for model in MODELS]
    print(f"Validated frozen corpus, sample, prompt and strict schema; {len(jobs)} independent requests", flush=True)
    print(f"Review bills were drawn before generation: {', '.join(manifest['review_selected'])}", flush=True)
    print(f"Models {MODELS}, effort {EFFORT}, max output tokens {MAX_OUTPUT_TOKENS}", flush=True)
    if not args.execute:
        print("Dry run; no API calls made", flush=True)
        return
    key = get_api_key()
    available = {r["id"] for r in api_json("GET", "/models", key).get("data", [])}
    if not set(MODELS).issubset(available):
        raise SystemExit("A frozen generation model is unavailable in this account")
    print("Account model availability rechecked: PASS", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(generate, model, item, prompt, format_config, key): (model, item)
                   for model, item in jobs}
        for future in as_completed(futures):
            print(future.result(), flush=True)
    print("All paired summaries completed", flush=True)


if __name__ == "__main__":
    main()
