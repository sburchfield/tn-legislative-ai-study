"""Frozen full-study inputs and exact-response helpers."""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/pilot"))
from generate_summaries import api_json, get_api_key, parse_summary, save_record  # noqa: E402

CORPUS = ROOT / "data/cleaned/bills.jsonl"
SAMPLE = ROOT / "data/full/sample.json"
CORPUS_SHA = "df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a"
SAMPLE_SHA = "be2411dd73cfcb20c7e55b9fda2aca02a07e05cbf8e8c335a172e6402672d29c"
GEN_PROMPT_SHA = "a8a84c7d3640ce11249e107717a11e24499592c70f24dc2215bc9305b9949889"
GEN_FORMAT_SHA = "65ee03d0a90267593885b0982684a55a9d7f7d40e7ce2a505d3c3c663a72b3a1"
MODELS = ("gpt-6-sol", "gpt-6-luna")
EVALUATOR = "gpt-6-astra"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frozen(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    actual = sha(data)
    if actual != expected:
        raise SystemExit(f"Frozen input changed: {path.relative_to(ROOT)}: {actual}")
    return data


def load_selected() -> tuple[dict, list[dict]]:
    corpus_bytes = frozen(CORPUS, CORPUS_SHA)
    manifest = json.loads(frozen(SAMPLE, SAMPLE_SHA))
    if (manifest["source_sha256"] != CORPUS_SHA or len(manifest["selected"]) != 36
            or len(manifest["review_selected"]) != 3):
        raise SystemExit("Sample manifest structure changed")
    rows = {r["bill_number"]: r for r in (json.loads(line) for line in corpus_bytes.splitlines() if line.strip())}
    selected = []
    for item in manifest["selected"]:
        row = rows[item["bill_number"]]
        if (row["id"] != item["id"] or sha(row["bill_text"].encode("utf-8")) != item["bill_text_sha256"]
                or len(row["bill_text"].split()) != item["word_count"]):
            raise SystemExit(f"Selected source changed: {item['bill_number']}")
        selected.append({"sample": item, "bill_text": row["bill_text"]})
    return manifest, selected


def generation_path(model: str, number: str) -> Path:
    return ROOT / "data/full/responses" / model / f"{number}.json"


def load_generation(model: str, item: dict) -> dict:
    path = generation_path(model, item["sample"]["bill_number"])
    record = json.loads(path.read_text(encoding="utf-8"))
    if (record.get("generation_status") != "completed" or record.get("requested_model") != model
            or record.get("returned_model") != model or record.get("sample_sha256") != SAMPLE_SHA
            or record.get("bill_text_sha256") != item["sample"]["bill_text_sha256"]
            or record.get("prompt_sha256") != GEN_PROMPT_SHA or record.get("format_sha256") != GEN_FORMAT_SHA):
        raise SystemExit(f"Generation record mismatch: {path}")
    if parse_summary(record["response"]) != record["summary"]:
        raise SystemExit(f"Summary differs from raw response: {path}")
    return record
