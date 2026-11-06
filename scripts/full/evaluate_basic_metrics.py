"""Compute pinned readability and compression for all 72 paired summaries."""

import json
import platform

import nltk
import textstat

from common import ROOT, SAMPLE_SHA, CORPUS_SHA, MODELS, load_generation, load_selected, sha
from evaluate_basic_metrics import cmudict_hash, readability

OUTPUT = ROOT / "data/full/evaluation"


def main() -> None:
    if tuple(textstat.__version__) != (0, 7, 13):
        raise SystemExit(f"Expected textstat 0.7.13, got {textstat.__version__}")
    textstat.set_lang("en_US")
    dictionary_hash = cmudict_hash()
    _, selected = load_selected()
    readability_rows = []
    compression_rows = []
    for item in selected:
        number = item["sample"]["bill_number"]
        source = item["bill_text"]
        source_stats = readability(source)
        for model in MODELS:
            generation = load_generation(model, item)
            summary = generation["summary"]
            summary_stats = readability(summary)
            readability_rows.append({
                "bill_number": number, "cell": item["sample"]["cell"],
                "tertile": item["sample"]["tertile"], "model": model,
                "source_sha256": item["sample"]["bill_text_sha256"],
                "summary_sha256": sha(summary.encode("utf-8")),
                "source": source_stats, "summary": summary_stats,
                "changes": {name: summary_stats[name] - source_stats[name] for name in
                            ("flesch_kincaid_grade", "flesch_reading_ease", "coleman_liau_index")},
            })
            source_words = len(source.split())
            summary_words = len(summary.split())
            compression_rows.append({
                "bill_number": number, "cell": item["sample"]["cell"],
                "tertile": item["sample"]["tertile"], "model": model,
                "source_whitespace_words": source_words,
                "summary_whitespace_words": summary_words,
                "summary_to_source_ratio": summary_words / source_words,
            })
    metadata = {
        "corpus_sha256": CORPUS_SHA, "sample_sha256": SAMPLE_SHA,
        "python_version": platform.python_version(),
        "textstat_version": ".".join(map(str, textstat.__version__)),
        "nltk_version": nltk.__version__, "cmudict_zip_sha256": dictionary_hash,
        "input_rule": "full cleaned bill_text and exact generated summary, no preprocessing",
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, rows in (("readability", readability_rows), ("compression", compression_rows)):
        (OUTPUT / f"{name}.json").write_text(
            json.dumps({"metadata": metadata, "records": rows}, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    print(f"Wrote pinned readability and compression metrics for {len(readability_rows)} summaries")


if __name__ == "__main__":
    main()
