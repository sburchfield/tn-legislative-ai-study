"""Generate the approved education pilot summaries with the Responses API.

The default action is a local dry run. Use --list-sol-models to inspect the
account's available GPT-6 Sol IDs and --execute to make paid API requests.
"""

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data/cleaned/bills.jsonl"
SAMPLE = ROOT / "data/pilot/education-sample.json"
PROMPT = ROOT / "prompts/pilot-summary-v1.txt"
FORMAT = ROOT / "prompts/pilot-summary-v1.format.json"
OUTPUT_DIR = ROOT / "data/pilot/responses"
API_ROOT = "https://api.openai.com/v1"

EXPECTED_CORPUS_SHA256 = "df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a"
EXPECTED_SAMPLE_SHA256 = "0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1"
EXPECTED_PROMPT_SHA256 = "a8a84c7d3640ce11249e107717a11e24499592c70f24dc2215bc9305b9949889"
EXPECTED_FORMAT_SHA256 = "65ee03d0a90267593885b0982684a55a9d7f7d40e7ce2a505d3c3c663a72b3a1"

REASONING_EFFORT = "medium"
MAX_OUTPUT_TOKENS = 8192


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_frozen(path: Path, expected_hash: str) -> bytes:
    data = path.read_bytes()
    actual_hash = sha256(data)
    if actual_hash != expected_hash:
        raise SystemExit(f"Frozen input changed: {path.relative_to(ROOT)} (SHA-256 {actual_hash})")
    return data


def get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"\'')
                if key:
                    return key
    raise SystemExit("OPENAI_API_KEY is not available in the process or ignored .env file")


def api_json(method: str, path: str, api_key: str, body: dict | None = None) -> dict:
    payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(
        API_ROOT + path,
        data=payload,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "tn-legislative-ai-study/1.0",
        },
    )
    try:
        with urlopen(request, timeout=300) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"OpenAI API connection failed: {exc.reason}") from exc


def load_inputs() -> tuple[list[dict], dict, str]:
    corpus_bytes = read_frozen(CORPUS, EXPECTED_CORPUS_SHA256)
    prompt_text = read_frozen(PROMPT, EXPECTED_PROMPT_SHA256).decode("utf-8")
    format_config = json.loads(read_frozen(FORMAT, EXPECTED_FORMAT_SHA256))
    sample = json.loads(read_frozen(SAMPLE, EXPECTED_SAMPLE_SHA256))
    if sample["source_sha256"] != EXPECTED_CORPUS_SHA256 or len(sample["selected"]) != 9:
        raise SystemExit("Sample manifest does not match the frozen corpus or nine-bill draw")

    by_number = {
        row["bill_number"]: row
        for row in (json.loads(line) for line in corpus_bytes.splitlines() if line.strip())
    }
    selected = []
    for item in sample["selected"]:
        row = by_number[item["bill_number"]]
        if row["id"] != item["id"] or sha256(row["bill_text"].encode("utf-8")) != item["bill_text_sha256"]:
            raise SystemExit(f"Sample text or ID changed for {item['bill_number']}")
        selected.append({"sample": item, "bill_text": row["bill_text"]})
    return selected, format_config, prompt_text


def build_request(model: str, prompt_text: str, format_config: dict, item: dict) -> dict:
    bill_number = item["sample"]["bill_number"]
    user_input = f"Bill number: {bill_number}\n\n<bill_text>\n{item['bill_text']}\n</bill_text>"
    return {
        "model": model,
        "instructions": prompt_text,
        "input": user_input,
        "reasoning": {"effort": REASONING_EFFORT},
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "text": {"format": format_config},
        "store": False,
    }


def parse_summary(response: dict) -> str:
    if response.get("status") != "completed" or response.get("error"):
        raise ValueError(f"Response status is {response.get('status')!r}")
    parts = []
    for output_item in response.get("output", []):
        if output_item.get("type") != "message":
            continue
        for content in output_item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content["text"])
            elif content.get("type") == "refusal":
                raise ValueError("Model refused the request")
    if not parts:
        raise ValueError("No output_text content in response")
    value = json.loads("".join(parts))
    if not isinstance(value, dict) or set(value) != {"summary"} or not isinstance(value["summary"], str):
        raise ValueError("Response did not match the one-field summary contract")
    summary = value["summary"].strip()
    if not summary:
        raise ValueError("Summary is empty")
    return summary


def save_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-6-sol", help="exact requested GPT-6 Sol model ID")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="make Responses API calls")
    mode.add_argument("--list-sol-models", action="store_true", help="list accessible GPT-6 Sol model IDs")
    args = parser.parse_args()

    if args.list_sol_models:
        result = api_json("GET", "/models", get_api_key())
        ids = sorted(item["id"] for item in result.get("data", []) if item.get("id", "").startswith("gpt-6-sol"))
        print("Accessible GPT-6 Sol model IDs:")
        for model_id in ids:
            print(model_id)
        return

    selected, format_config, prompt_text = load_inputs()
    print(f"Frozen corpus, prompt, schema, and {len(selected)} sampled bill texts: PASS")
    print(f"Requested model: {args.model}; reasoning effort: {REASONING_EFFORT}; max output tokens: {MAX_OUTPUT_TOKENS}")
    if not args.execute:
        print("Dry run complete. No API calls made.")
        return

    api_key = get_api_key()
    for item in selected:
        bill_number = item["sample"]["bill_number"]
        path = OUTPUT_DIR / f"{bill_number}.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if (existing.get("requested_model") != args.model
                    or existing.get("bill_text_sha256") != item["sample"]["bill_text_sha256"]
                    or existing.get("prompt_sha256") != EXPECTED_PROMPT_SHA256
                    or existing.get("format_sha256") != EXPECTED_FORMAT_SHA256):
                raise SystemExit(f"Existing response record conflicts with frozen settings: {path}")
            print(f"Skipping existing {bill_number}")
            continue

        request_body = build_request(args.model, prompt_text, format_config, item)
        response = api_json("POST", "/responses", api_key, request_body)
        record = {
            "bill_number": bill_number,
            "id": item["sample"]["id"],
            "cell": item["sample"]["cell"],
            "bill_text_sha256": item["sample"]["bill_text_sha256"],
            "corpus_sha256": EXPECTED_CORPUS_SHA256,
            "prompt_sha256": EXPECTED_PROMPT_SHA256,
            "format_sha256": EXPECTED_FORMAT_SHA256,
            "requested_model": args.model,
            "returned_model": response.get("model"),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "request": request_body,
            "response": response,
        }
        try:
            record["summary"] = parse_summary(response)
            record["generation_status"] = "completed"
        except (ValueError, KeyError, TypeError) as exc:
            record["summary"] = None
            record["generation_status"] = "needs_review"
            record["problem"] = str(exc)
        save_record(path, record)
        print(f"Saved {bill_number}: {record['generation_status']} (model {record['returned_model']})")
        if record["generation_status"] != "completed":
            raise SystemExit(f"Stopped after a non-scorable response for {bill_number}; review {path}")


if __name__ == "__main__":
    main()
