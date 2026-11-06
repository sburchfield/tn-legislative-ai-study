"""Validate and combine four separate automated measures for 72 new summaries."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/full"))
from common import (CORPUS_SHA, EVALUATOR, GEN_FORMAT_SHA, GEN_PROMPT_SHA,
                    SAMPLE_SHA, frozen, load_selected, sha)  # noqa: E402
from check_generation_feasibility import (CLAUDE_MODEL, build_request)  # noqa: E402
from generate_full import (FORMAT, GEMMA_MODEL, MAX_OUTPUT_TOKENS as GEN_MAX,
                           OUTPUT as GENERATION, PROMPT, validate_existing)  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts/pilot"))
spec = importlib.util.spec_from_file_location("frozen_full_eval", ROOT / "scripts/full/evaluate_semantic.py")
full_eval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(full_eval)

EVALUATION = ROOT / "data/extension/evaluation"
PROVIDERS = {"claude": CLAUDE_MODEL, "gemma": GEMMA_MODEL}


def metric_map(name: str) -> tuple[dict, dict]:
    value = json.loads((EVALUATION / f"{name}.json").read_text(encoding="utf-8"))
    metadata = value["metadata"]
    if metadata["sample_sha256"] != SAMPLE_SHA or metadata["corpus_sha256"] != CORPUS_SHA:
        raise SystemExit(f"{name} metric metadata mismatch")
    rows = {(r["bill_number"], r["provider"]): r for r in value["records"]}
    if len(rows) != 72:
        raise SystemExit(f"{name} does not contain 72 distinct extension records")
    return metadata, rows


def evaluator(stage: str, provider: str | None, item: dict, summary: str | None,
              propositions: list[dict] | None) -> dict:
    number = item["sample"]["bill_number"]
    path = (full_eval.output_path("source", None, number) if stage == "source" else
            EVALUATION / "llm" / stage / provider / f"{number}.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    _, prompt_sha, _, format_sha = full_eval.STAGES[stage]
    summary_sha = sha(summary.encode("utf-8")) if summary is not None else None
    inventory_sha = sha(json.dumps(propositions, ensure_ascii=False).encode("utf-8")) if propositions is not None else None
    if (record.get("evaluation_status") != "completed"
            or record.get("sample_sha256") != SAMPLE_SHA
            or record.get("requested_model") != EVALUATOR
            or record.get("returned_model") != EVALUATOR
            or record.get("source_sha256") != item["sample"]["bill_text_sha256"]
            or record.get("summary_sha256") != summary_sha
            or record.get("inventory_sha256") != inventory_sha
            or record.get("prompt_sha256") != prompt_sha
            or record.get("format_sha256") != format_sha
            or (stage != "source" and record.get("quote_validator_version") != full_eval.QUOTE_VALIDATOR_VERSION)
            or (provider is not None and
                (record.get("generator_provider") != provider
                 or record.get("generator_model") != PROVIDERS[provider]))):
        raise SystemExit(f"Evaluator metadata mismatch: {path}")
    parsed = full_eval.parse_response(record["response"])
    if parsed != record["parsed"]:
        raise SystemExit(f"Evaluator raw/parsed mismatch: {path}")
    full_eval.validate(stage, parsed, item, summary, propositions)
    return record


def main() -> None:
    manifest, selected = load_selected()
    source_audit = json.loads((ROOT / "data/full/evaluation/quote-validation-v2.json").read_text(encoding="utf-8"))
    if (source_audit.get("status") != "complete"
            or source_audit.get("quote_validator_version") != full_eval.QUOTE_VALIDATOR_VERSION
            or source_audit.get("counts", {}).get("source") != 36):
        raise SystemExit("Original source-inventory quote audit is absent or incomplete")
    prompt = frozen(PROMPT, GEN_PROMPT_SHA).decode("utf-8")
    fmt = json.loads(frozen(FORMAT, GEN_FORMAT_SHA))
    readability_metadata, readability = metric_map("readability")
    compression_metadata, compression = metric_map("compression")
    expected = {(item["sample"]["bill_number"], provider)
                for item in selected for provider in PROVIDERS}
    if set(readability) != expected or set(compression) != expected:
        raise SystemExit("Deterministic metrics do not match the extension sample")
    records = []
    for item in selected:
        number = item["sample"]["bill_number"]
        source_record = evaluator("source", None, item, None, None)
        propositions = source_record["parsed"]["propositions"]
        by_id = {p["id"]: p for p in propositions}
        for provider, model in PROVIDERS.items():
            gen_path = GENERATION / provider / f"{number}.json"
            body = build_request(provider, model, item, prompt, fmt, GEN_MAX)
            validate_existing(gen_path, item, provider, model, body)
            generation = json.loads(gen_path.read_text(encoding="utf-8"))
            summary = generation["summary"]
            coverage_record = evaluator("coverage", provider, item, summary, propositions)
            factuality_record = evaluator("factuality", provider, item, summary, None)
            assessments = coverage_record["parsed"]["assessments"]
            claims = factuality_record["parsed"]["claims"]
            coverage = {}
            for importance in ("core", "supporting"):
                subset = [a for a in assessments if by_id[a["proposition_id"]]["importance"] == importance]
                counts = {status: sum(a["status"] == status for a in subset)
                          for status in ("full", "partial", "omitted")}
                coverage[importance] = {"total": len(subset), "counts": counts,
                                        "full_fraction": counts["full"] / len(subset) if subset else None}
            verdicts = {verdict: sum(c["verdict"] == verdict for c in claims)
                        for verdict in ("supported", "contradicted", "not_established")}
            factuality = {
                "total_claims": len(claims), "verdict_counts": verdicts,
                "error_type_counts": {kind: sum(c["error_type"] == kind for c in claims)
                                      for kind in sorted({c["error_type"] for c in claims}) if kind != "none"},
                "supported_fraction": verdicts["supported"] / len(claims),
            }
            records.append({
                "bill_number": number, "cell": item["sample"]["cell"],
                "tertile": item["sample"]["tertile"], "provider": provider, "model": model,
                "source_sha256": item["sample"]["bill_text_sha256"],
                "summary_sha256": sha(summary.encode("utf-8")),
                "readability": readability[(number, provider)],
                "compression": compression[(number, provider)],
                "coverage": coverage, "factuality": factuality,
                "response_ids": {
                    "generation": generation["response"].get("id"),
                    "source": source_record["response"]["id"],
                    "coverage": coverage_record["response"]["id"],
                    "factuality": factuality_record["response"]["id"],
                },
            })
    result = {
        "status": "automated_extension_complete_researcher_review_pending",
        "method_note": "Exploratory automated measures; original Astra source inventories reused. Separate dimensions, no overall quality score or inferential ranking.",
        "sample_sha256": SAMPLE_SHA,
        "quote_validator_version": full_eval.QUOTE_VALIDATOR_VERSION,
        "review_selected": manifest["review_selected"],
        "readability_metadata": readability_metadata,
        "compression_metadata": compression_metadata,
        "records": records,
    }
    path = EVALUATION / "metrics.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Validated and wrote four separate automated measures for {len(records)} extension records")


if __name__ == "__main__":
    main()
