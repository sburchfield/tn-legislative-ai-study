"""Describe four-model outcomes within the same 36 bills, without a composite."""

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/full"))
from common import SAMPLE_SHA, load_selected  # noqa: E402

ORIGINAL = ROOT / "data/full/evaluation/metrics.json"
EXTENSION = ROOT / "data/extension/evaluation/metrics.json"
OUTPUT = ROOT / "data/extension/evaluation/four-model-analysis.json"
MODELS = ("gpt-6-sol", "gpt-6-luna", "claude-sonnet-5-5", "google/gemma-4-31b-qat")
READABILITY = ("flesch_kincaid_grade", "flesch_reading_ease", "coleman_liau_index")
PAIRS = (("gpt-6-sol", "gpt-6-luna"),
         ("gpt-6-sol", "claude-sonnet-5-5"),
         ("gpt-6-luna", "claude-sonnet-5-5"),
         ("gpt-6-sol", "google/gemma-4-31b-qat"),
         ("gpt-6-luna", "google/gemma-4-31b-qat"),
         ("claude-sonnet-5-5", "google/gemma-4-31b-qat"))


def measures(row: dict) -> dict:
    summary = row["readability"]["summary"]
    return {"flesch_kincaid_grade": summary["flesch_kincaid_grade"],
            "flesch_reading_ease": summary["flesch_reading_ease"],
            "coleman_liau_index": summary["coleman_liau_index"],
            "compression_ratio": row["compression"]["summary_to_source_ratio"],
            "core_full_fraction": row["coverage"]["core"]["full_fraction"],
            "supporting_full_fraction": row["coverage"]["supporting"]["full_fraction"],
            "supported_claim_fraction": row["factuality"]["supported_fraction"]}


def describe(values: list[float]) -> dict:
    return {"n": len(values), "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "minimum": min(values) if values else None,
            "maximum": max(values) if values else None}


def group(rows: list[dict]) -> dict:
    bills = sorted({row["bill_number"] for row in rows})
    by_key = {(row["bill_number"], row["model"]): row for row in rows}
    if len(rows) != len(by_key) or len(by_key) != len(bills) * len(MODELS):
        raise SystemExit("Group has missing or duplicate bill-model records")
    result = {"bills": len(bills), "by_model": {}, "paired_differences": {}}
    names = tuple(measures(rows[0]))
    for model in MODELS:
        model_rows = [by_key[(bill, model)] for bill in bills]
        descriptors = {name: describe([value for row in model_rows
                                       if (value := measures(row)[name]) is not None])
                       for name in names}
        source_changes = {name: describe([row["readability"]["changes"][name]
                                          for row in model_rows]) for name in READABILITY}
        coverage = {importance: {
            "total_propositions": sum(row["coverage"][importance]["total"] for row in model_rows),
            "counts": {status: sum(row["coverage"][importance]["counts"][status]
                                   for row in model_rows)
                       for status in ("full", "partial", "omitted")},
        } for importance in ("core", "supporting")}
        factuality = {
            "total_claims": sum(row["factuality"]["total_claims"] for row in model_rows),
            "verdict_counts": {verdict: sum(row["factuality"]["verdict_counts"][verdict]
                                           for row in model_rows)
                               for verdict in ("supported", "contradicted", "not_established")},
        }
        result["by_model"][model] = {"measure_descriptives": descriptors,
                                      "source_readability_changes": source_changes,
                                      "coverage": coverage, "factuality": factuality}
    for older, newer in PAIRS:
        key = f"{newer}_minus_{older}"
        result["paired_differences"][key] = {}
        for name in names:
            differences = []
            for bill in bills:
                a, b = measures(by_key[(bill, older)])[name], measures(by_key[(bill, newer)])[name]
                if a is not None and b is not None:
                    differences.append(b - a)
            result["paired_differences"][key][name] = {
                **describe(differences),
                "direction_counts": {
                    "newer_lower": sum(value < 0 for value in differences),
                    "equal": sum(value == 0 for value in differences),
                    "newer_higher": sum(value > 0 for value in differences),
                },
            }
    return result


def main() -> None:
    _, selected = load_selected()
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    extension = json.loads(EXTENSION.read_text(encoding="utf-8"))
    if (original["sample_sha256"] != SAMPLE_SHA or extension["sample_sha256"] != SAMPLE_SHA
            or extension["status"] != "automated_extension_complete_researcher_review_pending"):
        raise SystemExit("Original or extension metrics are not complete for frozen sample")
    rows = original["records"] + extension["records"]
    expected = {item["sample"]["bill_number"] for item in selected}
    if len(rows) != 144 or {row["bill_number"] for row in rows} != expected:
        raise SystemExit("Expected 144 four-model metric records")
    for bill in expected:
        subset = [row for row in rows if row["bill_number"] == bill]
        if ({row["model"] for row in subset} != set(MODELS)
                or len({row["source_sha256"] for row in subset}) != 1):
            raise SystemExit(f"Model or source mismatch for {bill}")
        for importance in ("core", "supporting"):
            if len({row["coverage"][importance]["total"] for row in subset}) != 1:
                raise SystemExit(f"Source proposition denominator mismatch for {bill}")
    result = {
        "status": "automated_four_model_analysis_complete_researcher_review_pending",
        "sample_sha256": SAMPLE_SHA, "models": MODELS,
        "note": "Exploratory automated descriptions; each paired difference is within the same bill. No composite score, inferential ranking, or human validation claim.",
        "overall": group(rows),
        "by_tertile": {tertile: group([row for row in rows if row["tertile"] == tertile])
                       for tertile in ("short", "medium", "long")},
    }
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Wrote four-model paired descriptors for 36 bills, overall and by length tertile")


if __name__ == "__main__":
    main()
