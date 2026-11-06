"""Dry-run or execute three unscored Claude/Gemma adapter checks on pilot bills.

This script cannot generate the 36-bill extension. Its default mode makes no API
calls. A completed check saves the exact unedited pilot response and settings.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/full"))
from common import (CORPUS, CORPUS_SHA, GEN_FORMAT_SHA, GEN_PROMPT_SHA,
                    frozen, save_record, sha)  # noqa: E402

PILOT = ROOT / "data/pilot/education-sample.json"
PILOT_SHA = "0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1"
PROMPT = ROOT / "prompts/pilot-summary-v1.txt"
FORMAT = ROOT / "prompts/pilot-summary-v1.format.json"
SMOKE_BILLS = ("HB2329", "HB1772", "HB1732")  # original short, medium, long-tail cells
CLAUDE_MODEL = "claude-sonnet-5-5"
CLAUDE_API_VERSION = "2026-10-21"
GEMMA_FILE = Path("/Users/sam/.lmstudio/models/lmstudio-community/gemma-4-31B-it-QAT-GGUF/gemma-4-31B-it-QAT-Q4_0.gguf")
GEMMA_FILE_SHA = "6f63619c9e33826a2a8ab195a344c79ecae7c82341d5567e28fd8863df056a7b"
GEMMA_FILE_SIZE = 17651001280
MAX_OUTPUT_TOKENS = 8192


def read_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("ANTHROPIC_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"\'')
                if key:
                    return key
    raise SystemExit("ANTHROPIC_API_KEY is absent from the process and ignored .env")


def request_json(method: str, url: str, headers: dict, body: dict | None = None) -> dict:
    payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=payload, method=method, headers=headers)
    try:
        with urlopen(request, timeout=300) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Connection failed: {exc.reason}") from exc


def load_inputs() -> tuple[list[dict], str, dict]:
    manifest = json.loads(frozen(PILOT, PILOT_SHA))
    if manifest["source_sha256"] != CORPUS_SHA:
        raise SystemExit("Pilot manifest corpus mismatch")
    corpus = {r["bill_number"]: r for r in
              (json.loads(line) for line in frozen(CORPUS, CORPUS_SHA).splitlines() if line.strip())}
    by_bill = {item["bill_number"]: item for item in manifest["selected"]}
    selected = []
    for number in SMOKE_BILLS:
        sample, row = by_bill[number], corpus[number]
        if (row["id"] != sample["id"]
                or sha(row["bill_text"].encode("utf-8")) != sample["bill_text_sha256"]
                or len(row["bill_text"].split()) != sample["word_count"]):
            raise SystemExit(f"Pilot source mismatch: {number}")
        selected.append({"sample": sample, "bill_text": row["bill_text"]})
    prompt = frozen(PROMPT, GEN_PROMPT_SHA).decode("utf-8")
    format_config = json.loads(frozen(FORMAT, GEN_FORMAT_SHA))
    if (format_config.get("type") != "json_schema" or format_config.get("strict") is not True
            or set(format_config["schema"]["properties"]) != {"summary"}):
        raise SystemExit("Frozen summary format mismatch")
    return selected, prompt, format_config


def build_request(provider: str, model: str, item: dict, prompt: str, fmt: dict,
                  max_output_tokens: int = MAX_OUTPUT_TOKENS) -> dict:
    user_text = f"Bill number: {item['sample']['bill_number']}\n\n<bill_text>\n{item['bill_text']}\n</bill_text>"
    if provider == "claude":
        return {"model": model, "system": prompt,
                "messages": [{"role": "user", "content": user_text}],
                "max_tokens": max_output_tokens,
                "output_config": {"effort": "medium", "format": {
                    "type": "json_schema", "schema": fmt["schema"]}}}
    return {"model": model, "messages": [
        {"role": "system", "content": prompt}, {"role": "user", "content": user_text}],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": fmt["name"], "strict": True, "schema": fmt["schema"]}},
        "reasoning_effort": "none",
        "max_tokens": max_output_tokens, "stream": False}


def parse_summary(provider: str, model: str, response: dict) -> str:
    if response.get("model") != model:
        raise ValueError("Returned model differs from requested model")
    if provider == "claude":
        if response.get("stop_reason") != "end_turn":
            raise ValueError(f"Claude stop reason: {response.get('stop_reason')}")
        parts = [part["text"] for part in response.get("content", []) if part.get("type") == "text"]
        if len(parts) != 1:
            raise ValueError("Expected exactly one Claude text content block")
        content = parts[0]
    else:
        choices = response.get("choices", [])
        if len(choices) != 1 or choices[0].get("finish_reason") != "stop":
            raise ValueError("Expected one complete LM Studio choice")
        content = choices[0]["message"].get("content")
    value = json.loads(content)
    if not isinstance(value, dict) or set(value) != {"summary"} or not isinstance(value["summary"], str):
        raise ValueError("Response did not match the one-field summary contract")
    summary = value["summary"].strip()
    if not summary:
        raise ValueError("Summary is empty")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("claude", "gemma"), required=True)
    parser.add_argument("--gemma-model-id", help="exact ID returned by LM Studio /v1/models")
    parser.add_argument("--gemma-base-url", default="http://127.0.0.1:1234/v1")
    parser.add_argument("--max-output-tokens", type=int, default=MAX_OUTPUT_TOKENS)
    parser.add_argument("--bill", choices=SMOKE_BILLS, action="append",
                        help="limit the check to one or more of the three frozen pilot bills")
    parser.add_argument("--execute", action="store_true", help="make three unscored pilot inference calls")
    args = parser.parse_args()
    if not 1 <= args.max_output_tokens <= MAX_OUTPUT_TOKENS:
        raise SystemExit("--max-output-tokens must be between 1 and 8192")
    selected, prompt, fmt = load_inputs()
    if args.bill:
        requested = set(args.bill)
        selected = [item for item in selected if item["sample"]["bill_number"] in requested]
    model = CLAUDE_MODEL if args.provider == "claude" else args.gemma_model_id
    if args.provider == "gemma":
        if not GEMMA_FILE.is_file() or GEMMA_FILE.stat().st_size != GEMMA_FILE_SIZE:
            raise SystemExit("Pinned Gemma GGUF is absent or has changed size")
    print(f"Frozen pilot sources, prompt, and schema: PASS; bills: {', '.join(item['sample']['bill_number'] for item in selected)}")
    print(f"Provider: {args.provider}; model ID: {model or '(server ID pending)'}; output cap: {args.max_output_tokens}")
    if not args.execute:
        print("Dry run complete; no API or local-model calls made")
        return
    if not model:
        raise SystemExit("--gemma-model-id is required to execute Gemma checks")
    if args.provider == "claude":
        key = read_key()
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": key, "anthropic-version": CLAUDE_API_VERSION,
                   "content-type": "application/json", "user-agent": "tn-legislative-ai-study/1.0"}
    else:
        url = args.gemma_base_url.rstrip("/") + "/chat/completions"
        headers = {"content-type": "application/json", "user-agent": "tn-legislative-ai-study/1.0"}
        available = request_json("GET", args.gemma_base_url.rstrip("/") + "/models", headers)
        if model not in {entry.get("id") for entry in available.get("data", [])}:
            raise SystemExit("Requested Gemma ID is not served by LM Studio")
    for item in selected:
        number = item["sample"]["bill_number"]
        path = ROOT / "data/extension/feasibility" / args.provider / f"{number}.json"
        body = build_request(args.provider, model, item, prompt, fmt, args.max_output_tokens)
        if path.exists():
            record = json.loads(path.read_text(encoding="utf-8"))
            if (record.get("generation_status") != "completed" or record.get("requested_model") != model
                    or record.get("bill_text_sha256") != item["sample"]["bill_text_sha256"]
                    or record.get("prompt_sha256") != GEN_PROMPT_SHA
                    or record.get("format_sha256") != GEN_FORMAT_SHA
                    or record.get("request") != body
                    or parse_summary(args.provider, model, record["response"]) != record.get("summary")):
                raise SystemExit(f"Existing feasibility record mismatch: {path}")
            print(f"Reused {args.provider} {number}", flush=True)
            continue
        response = request_json("POST", url, headers, body)
        record = {"provider": args.provider, "bill_number": number,
                  "bill_text_sha256": item["sample"]["bill_text_sha256"],
                  "corpus_sha256": CORPUS_SHA, "pilot_sample_sha256": PILOT_SHA,
                  "prompt_sha256": GEN_PROMPT_SHA, "format_sha256": GEN_FORMAT_SHA,
                  "requested_model": model, "returned_model": response.get("model"),
                  "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                  "gemma_file_sha256": GEMMA_FILE_SHA if args.provider == "gemma" else None,
                  "api_version": CLAUDE_API_VERSION if args.provider == "claude" else None,
                  "request": body, "response": response}
        try:
            record["summary"] = parse_summary(args.provider, model, response)
            record["generation_status"] = "completed"
        except (ValueError, KeyError, TypeError) as exc:
            record["summary"] = None
            record["generation_status"] = "needs_review"
            record["problem"] = str(exc)
        save_record(path, record)
        if record["generation_status"] != "completed":
            raise RuntimeError(f"Non-scorable feasibility response: {args.provider} {number}: {record['problem']}")
        print(f"Saved unscored {args.provider} {number}: {len(record['summary'].split())} words", flush=True)


if __name__ == "__main__":
    main()
