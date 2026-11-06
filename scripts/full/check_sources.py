"""Recheck the frozen full-study draw against exact validated source texts."""

import json
import re
from pathlib import Path

from common import ROOT, load_selected

VALIDATION = ROOT / "data/validation/dataset-validation.json"


def main() -> None:
    manifest, selected = load_selected()
    if len(selected) != 36 or len({i["sample"]["bill_number"] for i in selected}) != 36:
        raise SystemExit("Expected 36 unique full-study bills")
    by_tertile = {t: [i for i in selected if i["sample"]["tertile"] == t]
                  for t in ("short", "medium", "long")}
    if any(len(items) != 12 for items in by_tertile.values()):
        raise SystemExit("Full-study tertile allocation changed")
    corpus = {r["bill_number"]: r for r in (json.loads(line) for line in
              (ROOT / "data/cleaned/bills.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    for item in selected:
        number = item["sample"]["bill_number"]
        source = item["bill_text"]
        record = corpus[number]
        numeric = str(int(number[2:]))
        if (record["text_source"] != "house" or not source.strip()
                or not re.search(r"\bHOUSE BILL\s+" + numeric + r"\b", source[:300])
                or "BE IT ENACTED" not in source):
            raise SystemExit(f"Source-integrity check failed: {number}")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    selected_numbers = {i["sample"]["bill_number"] for i in selected}
    errors = [r for r in (validation["errors"] or []) if r["bill_number"] in selected_numbers]
    warnings = [r for r in (validation["warnings"] or []) if r["bill_number"] in selected_numbers]
    if errors or any(r["category"] != "sponsor_differs_from_as_filed" for r in warnings):
        raise SystemExit(f"Selected records have unexpected validation findings: {errors or warnings}")
    print(f"PASS: {len(selected)} exact sources, 12 per tertile; 0 validation errors")
    print(f"Expected sponsor-metadata warnings: {', '.join(r['bill_number'] for r in warnings) or 'none'}")
    print(f"Review bills: {', '.join(manifest['review_selected'])}")


if __name__ == "__main__":
    main()
