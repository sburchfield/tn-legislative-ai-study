"""Summarize frozen paired automated outcomes without a composite score."""

import json
import statistics

from common import ROOT, SAMPLE_SHA, MODELS, load_selected

INPUT = ROOT / "data/full/evaluation/metrics.json"
OUTPUT = ROOT / "data/full/evaluation/paired-analysis.json"


def measures(row: dict) -> dict:
    r = row["readability"]["summary"]
    return {
        "flesch_kincaid_grade": r["flesch_kincaid_grade"],
        "flesch_reading_ease": r["flesch_reading_ease"],
        "coleman_liau_index": r["coleman_liau_index"],
        "compression_ratio": row["compression"]["summary_to_source_ratio"],
        "core_full_fraction": row["coverage"]["core"]["full_fraction"],
        "supporting_full_fraction": row["coverage"]["supporting"]["full_fraction"],
        "supported_claim_fraction": row["factuality"]["supported_fraction"],
    }


def describe(values: list[float]) -> dict:
    return {"n": len(values), "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "minimum": min(values) if values else None, "maximum": max(values) if values else None}


def group(rows: list[dict]) -> dict:
    bills = {r["bill_number"] for r in rows}
    by_key = {(r["bill_number"], r["model"]): r for r in rows}
    if len(by_key) != len(bills) * 2:
        raise SystemExit("Paired group has a missing or duplicate bill-model record")
    result = {"bills": len(bills), "source_readability": {},
              "by_model": {}, "paired_luna_minus_sol": {}}
    measure_names = tuple(measures(rows[0]))
    readability_names = ("flesch_kincaid_grade", "flesch_reading_ease",
                         "coleman_liau_index")
    for name in readability_names:
        result["source_readability"][name] = describe([
            by_key[(number, "gpt-6-sol")]["readability"]["source"][name]
            for number in sorted(bills)])
    for model in MODELS:
        model_rows = [by_key[(number, model)] for number in sorted(bills)]
        descriptors = {name: describe([value for row in model_rows
                                       if (value := measures(row)[name]) is not None])
                       for name in measure_names}
        coverage = {importance: {
            "total_propositions": sum(row["coverage"][importance]["total"] for row in model_rows),
            "counts": {status: sum(row["coverage"][importance]["counts"][status] for row in model_rows)
                       for status in ("full", "partial", "omitted")},
        } for importance in ("core", "supporting")}
        factuality = {
            "total_claims": sum(row["factuality"]["total_claims"] for row in model_rows),
            "verdict_counts": {verdict: sum(row["factuality"]["verdict_counts"][verdict] for row in model_rows)
                               for verdict in ("supported", "contradicted", "not_established")},
        }
        source_changes = {}
        for name in readability_names:
            changes = [row["readability"]["changes"][name] for row in model_rows]
            favorable = sum(change > 0 if name == "flesch_reading_ease" else change < 0
                            for change in changes)
            source_changes[name] = {"summary_minus_source": describe(changes),
                                    "favorable_direction_count": favorable}
        result["by_model"][model] = {"measure_descriptives": descriptors,
                                      "source_readability_changes": source_changes,
                                      "coverage": coverage, "factuality": factuality}
    for name in measure_names:
        differences = []
        for number in sorted(bills):
            sol = measures(by_key[(number, "gpt-6-sol")])[name]
            luna = measures(by_key[(number, "gpt-6-luna")])[name]
            if sol is not None and luna is not None:
                differences.append(luna - sol)
        result["paired_luna_minus_sol"][name] = describe(differences)
    return result


def main() -> None:
    manifest, selected = load_selected()
    metrics = json.loads(INPUT.read_text(encoding="utf-8"))
    if (metrics["sample_sha256"] != SAMPLE_SHA
            or metrics["status"] != "automated_measures_complete_researcher_review_pending"):
        raise SystemExit("Automated metrics are incomplete or based on another sample")
    rows = metrics["records"]
    expected = {(i["sample"]["bill_number"], model) for i in selected for model in MODELS}
    if len(rows) != 72 or {(r["bill_number"], r["model"]) for r in rows} != expected:
        raise SystemExit("Expected exactly 72 paired metric records")
    result = {
        "status": "automated_analysis_complete",
        "sample_sha256": SAMPLE_SHA, "review_selected": manifest["review_selected"],
        "quote_validator_version": metrics["quote_validator_version"],
        "note": "Exploratory automated estimates, calculated separately from the researcher's saved issue logs. Source readability is counted once per bill. Separate measures, paired within bill; no composite quality score or inferential claim.",
        "overall": group(rows),
        "by_tertile": {tertile: group([r for r in rows if r["tertile"] == tertile])
                       for tertile in ("short", "medium", "long")},
    }
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Wrote paired descriptive analysis for 36 bills, overall and by original length tertile")


if __name__ == "__main__":
    main()
