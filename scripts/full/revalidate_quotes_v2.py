"""Recheck all 180 Astra raw outputs with the versioned PDF-wrap quote rule.

Promote only the archived-and-retried HB6004 Luna factuality response after
every raw record passes the same structural and evidence checks.
"""

import json
from datetime import datetime, timezone

from common import ROOT, EVALUATOR, MODELS, load_generation, load_selected, save_record, sha
from evaluate_semantic import parse_response
from evidence_quotes_v2 import (VERSION, validate_source, validate_coverage,
                                validate_factuality)

OUTPUT = ROOT / "data/full/evaluation/llm"
RECEIPT = ROOT / "data/full/evaluation/quote-validation-v2.json"
VALIDATOR = ROOT / "scripts/full/evidence_quotes_v2.py"
FAILED_ATTEMPT_1 = OUTPUT / "failed_attempts/factuality/gpt-6-luna/HB6004-attempt1.json"
FAILED_ATTEMPT_2 = OUTPUT / "failed_attempts/factuality/gpt-6-luna/HB6004-attempt2-pre-revalidation.json"
RETRY = OUTPUT / "factuality/gpt-6-luna/HB6004.json"
EXPECTED_VALIDATOR_SHA = "a0d5e5d3b2f859d14dcfe3a7c90b7201a983e742d4a3cd42477dd85595668da2"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def checked_record(path, item, summary=None):
    record = read(path)
    expected_summary_sha = sha(summary.encode("utf-8")) if summary is not None else None
    if (record.get("requested_model") != EVALUATOR or record.get("returned_model") != EVALUATOR
            or record.get("source_sha256") != item["sample"]["bill_text_sha256"]
            or record.get("summary_sha256") != expected_summary_sha):
        raise SystemExit(f"Evaluator provenance mismatch: {path}")
    parsed = parse_response(record["response"])
    if record.get("evaluation_status") == "completed" and record.get("parsed") != parsed:
        raise SystemExit(f"Parsed content differs from raw evaluator output: {path}")
    return record, parsed


def main() -> None:
    if sha(VALIDATOR.read_bytes()) != EXPECTED_VALIDATOR_SHA:
        raise SystemExit("Versioned quote validator changed")
    for path in (FAILED_ATTEMPT_1, FAILED_ATTEMPT_2):
        if not path.exists() or read(path)["evaluation_status"] != "needs_review":
            raise SystemExit(f"Missing original failed attempt: {path}")
    _, selected = load_selected()
    counts = {"source": 0, "coverage": 0, "factuality": 0}
    retry_record = None
    retry_parsed = None
    retry_needs_promotion = False
    for item in selected:
        number = item["sample"]["bill_number"]
        source_path = OUTPUT / "source/source_only" / f"{number}.json"
        source_record, source_parsed = checked_record(source_path, item)
        if source_record.get("evaluation_status") != "completed":
            raise SystemExit(f"Source inventory incomplete: {number}")
        validate_source(source_parsed, item["bill_text"])
        counts["source"] += 1
        propositions = source_parsed["propositions"]
        for model in MODELS:
            summary = load_generation(model, item)["summary"]
            for stage in ("coverage", "factuality"):
                path = OUTPUT / stage / model / f"{number}.json"
                record, parsed = checked_record(path, item, summary)
                if stage == "coverage":
                    validate_coverage(parsed, propositions, summary)
                else:
                    validate_factuality(parsed, item["bill_text"], summary)
                if path == RETRY:
                    if record.get("evaluation_status") == "needs_review":
                        if record.get("problem") != "Source quote does not match bill for claim 12":
                            raise SystemExit("HB6004 retry problem differs from the documented failure")
                        retry_needs_promotion = True
                    elif (record.get("evaluation_status") != "completed"
                          or record.get("quote_validator_version") != VERSION
                          or record.get("initial_validation_problem") != "Source quote does not match bill for claim 12"):
                        raise SystemExit("HB6004 retry status differs from the documented correction")
                    retry_record, retry_parsed = record, parsed
                elif record.get("evaluation_status") != "completed":
                    raise SystemExit(f"Unexpected incomplete evaluator record: {path}")
                counts[stage] += 1
    if counts != {"source": 36, "coverage": 72, "factuality": 72} or retry_record is None:
        raise SystemExit(f"Expected 180 validated records, got {counts}")
    if retry_needs_promotion:
        retry_record["initial_validation_problem"] = retry_record.pop("problem")
        retry_record["parsed"] = retry_parsed
        retry_record["evaluation_status"] = "completed"
        retry_record["quote_validator_version"] = VERSION
        retry_record["validation_correction"] = "PDF extraction whitespace after hyphen between letters/digits only"
        retry_record["revalidated_at_utc"] = datetime.now(timezone.utc).isoformat()
        save_record(RETRY, retry_record)
    receipt = {
        "status": "complete", "validated_at_utc": retry_record["revalidated_at_utc"],
        "quote_validator_version": VERSION, "quote_validator_sha256": EXPECTED_VALIDATOR_SHA,
        "counts": counts, "promoted_record": str(RETRY.relative_to(ROOT)),
        "failed_attempt_1_sha256": sha(FAILED_ATTEMPT_1.read_bytes()),
        "failed_attempt_2_sha256": sha(FAILED_ATTEMPT_2.read_bytes()),
        "rule": "Collapse whitespace; also remove whitespace immediately after a hyphen between ASCII letters/digits; preserve all words, digits, and punctuation.",
    }
    if RECEIPT.exists() and not retry_needs_promotion:
        if read(RECEIPT) != receipt:
            raise SystemExit("Existing quote-validation receipt differs from the revalidated records")
    else:
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {counts}; HB6004 Luna retry {'promoted' if retry_needs_promotion else 'already promoted'} under {VERSION}")


if __name__ == "__main__":
    main()
