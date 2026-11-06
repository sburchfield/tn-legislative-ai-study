"""Aggregate the four separate pilot measures from validated saved records."""

import hashlib
import json
from pathlib import Path

from evaluate_semantic import (
    OUTPUT_DIR as LLM_DIR,
    load_pairs,
    validate_coverage,
    validate_factuality,
    validate_source,
)


ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = ROOT / "data/pilot/evaluation"


def load_metric(name: str) -> dict:
    return json.loads((EVALUATION_DIR / f"{name}.json").read_text(encoding="utf-8"))


def load_evaluator(stage: str, number: str) -> dict:
    path = LLM_DIR / stage / f"{number}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("evaluation_status") != "completed" or record.get("bill_number") != number:
        raise SystemExit(f"Evaluator record incomplete or mismatched: {path}")
    return record


def main() -> None:
    pairs = load_pairs()
    readability = load_metric("readability")
    compression = load_metric("compression")
    read_by_number = {row["bill_number"]: row for row in readability["records"]}
    comp_by_number = {row["bill_number"]: row for row in compression["records"]}
    expected = {pair["number"] for pair in pairs}
    if set(read_by_number) != expected or set(comp_by_number) != expected:
        raise SystemExit("Basic metric records do not match the pilot sample")

    rows = []
    for pair in pairs:
        number = pair["number"]
        records = {stage: load_evaluator(stage, number) for stage in ("source", "coverage", "factuality")}
        for stage, record in records.items():
            if (record.get("source_sha256") != pair["sample"]["bill_text_sha256"]
                    or record.get("summary_sha256") != hashlib.sha256(pair["summary"].encode()).hexdigest()
                    or not record.get("returned_model")):
                raise SystemExit(f"Evaluator input/model mismatch: {stage} {number}")
        propositions = records["source"]["parsed"]["propositions"]
        assessments = records["coverage"]["parsed"]["assessments"]
        claims = records["factuality"]["parsed"]["claims"]
        validate_source(records["source"]["parsed"], pair["source"])
        validate_coverage(records["coverage"]["parsed"], propositions, pair["summary"])
        validate_factuality(records["factuality"]["parsed"], pair["source"], pair["summary"])
        by_id = {item["id"]: item for item in propositions}
        coverage = {}
        for importance in ("core", "supporting"):
            selected = [a for a in assessments if by_id[a["proposition_id"]]["importance"] == importance]
            counts = {status: sum(a["status"] == status for a in selected) for status in ("full", "partial", "omitted")}
            coverage[importance] = {
                "total": len(selected),
                "counts": counts,
                "full_fraction": counts["full"] / len(selected) if selected else None,
            }
        factuality = {
            "total_claims": len(claims),
            "verdict_counts": {verdict: sum(c["verdict"] == verdict for c in claims)
                               for verdict in ("supported", "contradicted", "not_established")},
            "error_type_counts": {kind: sum(c["error_type"] == kind for c in claims)
                                  for kind in sorted({c["error_type"] for c in claims}) if kind != "none"},
        }
        factuality["supported_fraction"] = factuality["verdict_counts"]["supported"] / len(claims)
        rows.append({
            "bill_number": number,
            "cell": pair["sample"]["cell"],
            "readability": read_by_number[number],
            "compression": comp_by_number[number],
            "coverage": coverage,
            "factuality": factuality,
            "evaluator_models": {stage: record["returned_model"] for stage, record in records.items()},
            "evaluator_response_ids": {stage: record["response"].get("id") for stage, record in records.items()},
        })
    result = {
        "method_note": "Exploratory automated pilot metrics; evaluator uses same model family as summarizer. Manual inspection is pipeline QA only.",
        "readability_metadata": readability["metadata"],
        "compression_metadata": compression["metadata"],
        "records": rows,
    }
    path = EVALUATION_DIR / "metrics.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote separate readability, compression, coverage, and factuality metrics for {len(rows)} bills")


if __name__ == "__main__":
    main()
