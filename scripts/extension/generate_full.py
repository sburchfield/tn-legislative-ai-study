"""Generate the frozen Claude or Gemma extension summaries for all 36 bills.

Default mode checks inputs without inference. --execute saves every raw response
and safely reuses completed records. It never alters the original OpenAI run.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/full"))
from common import (CORPUS_SHA, GEN_FORMAT_SHA, GEN_PROMPT_SHA, SAMPLE_SHA,
                    frozen, load_selected, save_record)  # noqa: E402
from check_generation_feasibility import (CLAUDE_API_VERSION, CLAUDE_MODEL,
                                          GEMMA_FILE, GEMMA_FILE_SHA, GEMMA_FILE_SIZE,
                                          build_request, parse_summary, read_key,
                                          request_json)  # noqa: E402

PROMPT = ROOT / "prompts/pilot-summary-v1.txt"
FORMAT = ROOT / "prompts/pilot-summary-v1.format.json"
PREFLIGHT = ROOT / "data/extension/full-input-preflight.json"
OUTPUT = ROOT / "data/extension/responses"
MAX_OUTPUT_TOKENS = 8192
GEMMA_MODEL = "google/gemma-4-31b-qat"
GEMMA_BASE = "http://127.0.0.1:1234/v1"
CONTEXT_LENGTH = 16384


def load_inputs() -> list[dict]:
    _, selected = load_selected()
    receipt = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    expected = {item["sample"]["bill_number"] for item in selected}
    if (receipt.get("status") != "pass" or receipt.get("sample_sha256") != SAMPLE_SHA
            or receipt.get("corpus_sha256") != CORPUS_SHA
            or receipt.get("prompt_sha256") != GEN_PROMPT_SHA
            or receipt.get("format_sha256") != GEN_FORMAT_SHA
            or receipt.get("model") != GEMMA_MODEL
            or receipt.get("loaded_context_tokens") != CONTEXT_LENGTH
            or receipt.get("max_output_tokens") != MAX_OUTPUT_TOKENS
            or len(receipt.get("records", [])) != 36
            or {r["bill_number"] for r in receipt["records"]} != expected
            or not all(r["fits_loaded_context"] for r in receipt["records"])):
        raise SystemExit("Full-sample input/context preflight is absent or inconsistent")
    return selected


def validate_existing(path: Path, item: dict, provider: str, model: str, body: dict) -> None:
    record = json.loads(path.read_text(encoding="utf-8"))
    if (record.get("generation_status") != "completed"
            or record.get("provider") != provider
            or record.get("bill_number") != item["sample"]["bill_number"]
            or record.get("sample_sha256") != SAMPLE_SHA
            or record.get("corpus_sha256") != CORPUS_SHA
            or record.get("bill_text_sha256") != item["sample"]["bill_text_sha256"]
            or record.get("prompt_sha256") != GEN_PROMPT_SHA
            or record.get("format_sha256") != GEN_FORMAT_SHA
            or record.get("requested_model") != model
            or record.get("returned_model") != model
            or record.get("request") != body
            or parse_summary(provider, model, record["response"]) != record.get("summary")):
        raise SystemExit(f"Existing extension record mismatch: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("claude", "gemma"), required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    selected = load_inputs()
    prompt = frozen(PROMPT, GEN_PROMPT_SHA).decode("utf-8")
    fmt = json.loads(frozen(FORMAT, GEN_FORMAT_SHA))
    model = CLAUDE_MODEL if args.provider == "claude" else GEMMA_MODEL
    if args.provider == "gemma" and (not GEMMA_FILE.is_file() or GEMMA_FILE.stat().st_size != GEMMA_FILE_SIZE):
        raise SystemExit("Pinned local Gemma file absent or changed size")
    jobs = [(item, build_request(args.provider, model, item, prompt, fmt, MAX_OUTPUT_TOKENS))
            for item in selected]
    print(f"Frozen 36 sources, prompt/schema and context preflight: PASS; provider={args.provider}", flush=True)
    print(f"Exact requested model={model}; new requests or validated reuse={len(jobs)}", flush=True)
    if not args.execute:
        print("Dry run; no inference calls made", flush=True)
        return
    if args.provider == "claude":
        key = read_key()
        headers = {"x-api-key": key, "anthropic-version": CLAUDE_API_VERSION,
                   "content-type": "application/json", "user-agent": "tn-legislative-ai-study/1.0"}
        url = "https://api.anthropic.com/v1/messages"
        available = request_json("GET", "https://api.anthropic.com/v1/models/" + model, headers)
        if available.get("id") != model:
            raise SystemExit("Claude model is unavailable to this account")
    else:
        headers = {"content-type": "application/json", "user-agent": "tn-legislative-ai-study/1.0"}
        url = GEMMA_BASE + "/chat/completions"
        available = request_json("GET", GEMMA_BASE + "/models", headers)
        if model not in {r.get("id") for r in available.get("data", [])}:
            raise SystemExit("Pinned Gemma model is not served")
        local = request_json("GET", "http://127.0.0.1:1234/api/v1/models", headers)
        entries = [r for r in local.get("models", []) if r.get("key") == model]
        if (len(entries) != 1 or entries[0].get("selected_variant") != model + "@q4_0"
                or len(entries[0].get("loaded_instances", [])) != 1
                or entries[0]["loaded_instances"][0]["config"]["context_length"] != CONTEXT_LENGTH):
            raise SystemExit("Gemma variant or loaded context changed after preflight")
    for item, body in jobs:
        number = item["sample"]["bill_number"]
        path = OUTPUT / args.provider / f"{number}.json"
        if path.exists():
            validate_existing(path, item, args.provider, model, body)
            print(f"Reused {args.provider} {number}", flush=True)
            continue
        response = request_json("POST", url, headers, body)
        record = {
            "provider": args.provider, "bill_number": number, "id": item["sample"]["id"],
            "cell": item["sample"]["cell"], "tertile": item["sample"]["tertile"],
            "bill_text_sha256": item["sample"]["bill_text_sha256"],
            "corpus_sha256": CORPUS_SHA, "sample_sha256": SAMPLE_SHA,
            "prompt_sha256": GEN_PROMPT_SHA, "format_sha256": GEN_FORMAT_SHA,
            "requested_model": model, "returned_model": response.get("model"),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "api_version": CLAUDE_API_VERSION if args.provider == "claude" else None,
            "gemma_file_sha256": GEMMA_FILE_SHA if args.provider == "gemma" else None,
            "gemma_loaded_context_tokens": CONTEXT_LENGTH if args.provider == "gemma" else None,
            "request": body, "response": response,
        }
        try:
            record["summary"] = parse_summary(args.provider, model, response)
            record["generation_status"] = "completed"
        except (ValueError, KeyError, TypeError) as exc:
            record["summary"] = None
            record["generation_status"] = "needs_review"
            record["problem"] = str(exc)
        save_record(path, record)
        if record["generation_status"] != "completed":
            raise RuntimeError(f"Non-scorable extension output for {args.provider} {number}: {record['problem']}")
        print(f"Saved {args.provider} {number}: {len(record['summary'].split())} summary words", flush=True)
    print(f"Completed all 36 {args.provider} summaries", flush=True)


if __name__ == "__main__":
    main()
