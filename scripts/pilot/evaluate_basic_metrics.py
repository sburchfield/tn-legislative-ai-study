"""Compute pilot readability and compression measures without an API call."""

import hashlib
import json
import math
import os
import platform
from pathlib import Path

import nltk
import textstat


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data/cleaned/bills.jsonl"
SAMPLE = ROOT / "data/pilot/education-sample.json"
RESPONSES = ROOT / "data/pilot/responses"
OUTPUT_DIR = ROOT / "data/pilot/evaluation"

EXPECTED_CORPUS_SHA256 = "df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a"
EXPECTED_SAMPLE_SHA256 = "0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1"
EXPECTED_CMUDICT_SHA256 = "d07cca47fd72ad32ea9d8ad1219f85301eeaf4568f8b6b73747506a71fb5afd6"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_bytes(path: Path, expected_hash: str) -> bytes:
    data = path.read_bytes()
    if sha256(data) != expected_hash:
        raise SystemExit(f"Frozen input changed: {path.relative_to(ROOT)}")
    return data


def cmudict_hash() -> str:
    for base in nltk.data.path:
        candidate = Path(base) / "corpora/cmudict.zip"
        if candidate.is_file():
            digest = sha256(candidate.read_bytes())
            if digest != EXPECTED_CMUDICT_SHA256:
                raise SystemExit(f"CMU dictionary changed: {digest}")
            return digest
    raise SystemExit("NLTK cmudict.zip missing; set NLTK_DATA to its parent directory")


def readability(text: str) -> dict:
    values = {
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "coleman_liau_index": textstat.coleman_liau_index(text),
        "library_word_count": textstat.lexicon_count(text),
        "sentence_count": textstat.sentence_count(text),
        "syllable_count": textstat.syllable_count(text),
        "character_count": textstat.char_count(text),
        "letter_count": textstat.letter_count(text),
    }
    if any(isinstance(value, float) and not math.isfinite(value) for value in values.values()):
        raise SystemExit("Non-finite readability result")
    return values


def main() -> None:
    if tuple(textstat.__version__) != (0, 7, 13):
        raise SystemExit(f"Expected textstat 0.7.13, got {textstat.__version__}")
    textstat.set_lang("en_US")
    dictionary_hash = cmudict_hash()
    corpus_bytes = checked_bytes(CORPUS, EXPECTED_CORPUS_SHA256)
    sample = json.loads(checked_bytes(SAMPLE, EXPECTED_SAMPLE_SHA256))
    by_number = {
        r["bill_number"]: r
        for r in (json.loads(line) for line in corpus_bytes.splitlines() if line.strip())
    }
    readability_rows = []
    compression_rows = []
    for item in sample["selected"]:
        number = item["bill_number"]
        source = by_number[number]["bill_text"]
        record = json.loads((RESPONSES / f"{number}.json").read_text(encoding="utf-8"))
        if record["generation_status"] != "completed" or record["bill_text_sha256"] != sha256(source.encode("utf-8")):
            raise SystemExit(f"Generation record mismatch for {number}")
        summary = record["summary"]
        source_stats = readability(source)
        summary_stats = readability(summary)
        readability_rows.append({
            "bill_number": number,
            "cell": item["cell"],
            "source": source_stats,
            "summary": summary_stats,
            "changes": {
                name: summary_stats[name] - source_stats[name]
                for name in ("flesch_kincaid_grade", "flesch_reading_ease", "coleman_liau_index")
            },
        })
        source_words = len(source.split())
        summary_words = len(summary.split())
        compression_rows.append({
            "bill_number": number,
            "cell": item["cell"],
            "source_whitespace_words": source_words,
            "summary_whitespace_words": summary_words,
            "summary_to_source_ratio": summary_words / source_words,
        })

    metadata = {
        "corpus_sha256": EXPECTED_CORPUS_SHA256,
        "sample_sha256": EXPECTED_SAMPLE_SHA256,
        "python_version": platform.python_version(),
        "textstat_version": ".".join(map(str, textstat.__version__)),
        "nltk_version": nltk.__version__,
        "cmudict_zip_sha256": dictionary_hash,
        "input_rule": "full cleaned bill_text and exact generated summary, no preprocessing",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "readability.json").write_text(
        json.dumps({"metadata": metadata, "records": readability_rows}, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "compression.json").write_text(
        json.dumps({"metadata": metadata, "records": compression_rows}, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote readability and compression metrics for {len(readability_rows)} bills")


if __name__ == "__main__":
    main()
