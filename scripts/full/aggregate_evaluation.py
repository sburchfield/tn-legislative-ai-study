"""Validate all saved records and keep the four full-study measures separate."""

import importlib.util
import json

from common import ROOT, SAMPLE_SHA, CORPUS_SHA, EVALUATOR, MODELS, load_generation, load_selected, sha

spec = importlib.util.spec_from_file_location("full_evaluate_semantic", ROOT / "scripts/full/evaluate_semantic.py")
full_eval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(full_eval)
STAGES, output_path, validate = full_eval.STAGES, full_eval.output_path, full_eval.validate

EVALUATION = ROOT / "data/full/evaluation"
QUOTE_VALIDATOR_SHA = "a0d5e5d3b2f859d14dcfe3a7c90b7201a983e742d4a3cd42477dd85595668da2"


def metric_map(name: str) -> tuple[dict, dict]:
    value = json.loads((EVALUATION / f"{name}.json").read_text(encoding="utf-8"))
    if value["metadata"]["sample_sha256"] != SAMPLE_SHA or value["metadata"]["corpus_sha256"] != CORPUS_SHA:
        raise SystemExit(f"{name} metric metadata differs from frozen inputs")
    rows = {(r["bill_number"], r["model"]): r for r in value["records"]}
    if len(rows) != 72:
        raise SystemExit(f"{name} does not contain 72 distinct pairs")
    return value["metadata"], rows


def evaluator(stage: str, model: str | None, item: dict, summary: str | None,
              propositions: list[dict] | None) -> dict:
    number = item["sample"]["bill_number"]
    path = output_path(stage, model, number)
    record = json.loads(path.read_text(encoding="utf-8"))
    _, prompt_sha, _, format_sha = STAGES[stage]
    summary_sha = sha(summary.encode("utf-8")) if summary is not None else None
    inventory_sha = sha(json.dumps(propositions, ensure_ascii=False).encode("utf-8")) if propositions is not None else None
    if (record.get("evaluation_status") != "completed" or record.get("sample_sha256") != SAMPLE_SHA
            or record.get("requested_model") != EVALUATOR or record.get("returned_model") != EVALUATOR
            or record.get("source_sha256") != item["sample"]["bill_text_sha256"]
            or record.get("summary_sha256") != summary_sha or record.get("inventory_sha256") != inventory_sha
            or record.get("prompt_sha256") != prompt_sha or record.get("format_sha256") != format_sha):
        raise SystemExit(f"Evaluator metadata mismatch: {path}")
    validate(stage, record["parsed"], item, summary, propositions)
    return record


def main() -> None:
    manifest, selected = load_selected()
    quote_audit = json.loads((EVALUATION / "quote-validation-v2.json").read_text(encoding="utf-8"))
    if (quote_audit.get("status") != "complete"
            or quote_audit.get("quote_validator_version") != full_eval.QUOTE_VALIDATOR_VERSION
            or quote_audit.get("quote_validator_sha256") != QUOTE_VALIDATOR_SHA
            or quote_audit.get("counts") != {"source": 36, "coverage": 72, "factuality": 72}):
        raise SystemExit("The uniform v2 quote-validation audit is absent or incomplete")
    readability_metadata, readability = metric_map("readability")
    compression_metadata, compression = metric_map("compression")
    expected = {(item["sample"]["bill_number"], model) for item in selected for model in MODELS}
    if set(readability) != expected or set(compression) != expected:
        raise SystemExit("Basic metrics do not match the paired sample")
    records = []
    for item in selected:
        number = item["sample"]["bill_number"]
        source_record = evaluator("source", None, item, None, None)
        propositions = source_record["parsed"]["propositions"]
        by_id = {p["id"]: p for p in propositions}
        for model in MODELS:
            generation = load_generation(model, item)
            summary = generation["summary"]
            coverage_record = evaluator("coverage", model, item, summary, propositions)
            factuality_record = evaluator("factuality", model, item, summary, None)
            assessments = coverage_record["parsed"]["assessments"]
            claims = factuality_record["parsed"]["claims"]
            coverage = {}
            for importance in ("core", "supporting"):
                subset = [a for a in assessments if by_id[a["proposition_id"]]["importance"] == importance]
                counts = {s: sum(a["status"] == s for a in subset) for s in ("full", "partial", "omitted")}
                coverage[importance] = {"total": len(subset), "counts": counts,
                                        "full_fraction": counts["full"] / len(subset) if subset else None}
            verdicts = {v: sum(c["verdict"] == v for c in claims)
                        for v in ("supported", "contradicted", "not_established")}
            factuality = {
                "total_claims": len(claims), "verdict_counts": verdicts,
                "error_type_counts": {kind: sum(c["error_type"] == kind for c in claims)
                                      for kind in sorted({c["error_type"] for c in claims}) if kind != "none"},
                "supported_fraction": verdicts["supported"] / len(claims),
            }
            records.append({
                "bill_number": number, "cell": item["sample"]["cell"],
                "tertile": item["sample"]["tertile"], "model": model,
                "source_sha256": item["sample"]["bill_text_sha256"],
                "summary_sha256": sha(summary.encode("utf-8")),
                "readability": readability[(number, model)],
                "compression": compression[(number, model)],
                "coverage": coverage, "factuality": factuality,
                "response_ids": {
                    "generation": generation["response"]["id"],
                    "source": source_record["response"]["id"],
                    "coverage": coverage_record["response"]["id"],
                    "factuality": factuality_record["response"]["id"],
                },
            })
    result = {
        "status": "automated_measures_complete_researcher_review_pending",
        "method_note": "Exploratory paired automated measures; no overall quality score. Researcher check is independent and pending.",
        "sample_sha256": SAMPLE_SHA,
        "quote_validator_version": full_eval.QUOTE_VALIDATOR_VERSION,
        "quote_validator_sha256": QUOTE_VALIDATOR_SHA,
        "review_selected": manifest["review_selected"],
        "readability_metadata": readability_metadata,
        "compression_metadata": compression_metadata,
        "records": records,
    }
    path = EVALUATION / "metrics.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Validated and wrote four separate automated measures for {len(records)} paired bill-model records")


if __name__ == "__main__":
    main()
