"""Reproduce the approved nine-bill education pilot draw from the frozen corpus."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/cleaned/bills.jsonl"
OUTPUT = ROOT / "data/pilot/education-sample.json"
EXPECTED_SOURCE_SHA256 = "df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a"
SEED = "INSC499-education-pilot-2026-10-04-v1"

EDUCATION_SUBJECTS = (
    "Education",
    "Education, Curriculum",
    "Education, Dept. of",
    "Education, Higher",
    "Education, State Board of",
    "Local Education Agencies",
    "Lottery, Scholarships and Programs",
    "Scholarships and Financial Aid",
    "School Transportation",
    "School Vouchers",
    "Schools, Charter",
    "Schools, Home",
    "Schools, Private",
    "State Universities",
    "Students",
    "Teachers, Principals and School Personnel",
    "Tennessee Higher Education Commission",
    "Tennessee Investment in Student Achievement (TISA)",
)

CELL_ORDER = (
    ("short_minimal", 1, 42),
    ("short_other", 2, 70),
    ("medium", 3, 112),
    ("long_main", 2, 95),
    ("long_tail", 1, 17),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    source_hash = sha256(source_bytes)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"Corpus hash changed: {source_hash}")

    records = [json.loads(line) for line in source_bytes.splitlines() if line.strip()]
    if len(records) != 2684 or len({r["bill_number"] for r in records}) != 2684:
        raise SystemExit("Unexpected corpus size or duplicate bill numbers")
    if any(len(r["subjects"]) != 1 for r in records):
        raise SystemExit("Expected exactly one subject per record")

    eligible = [r for r in records if r["subjects"][0] in EDUCATION_SUBJECTS]
    if len(eligible) != 336 or any(not r["bill_text"].strip() or r["text_source"] != "house" for r in eligible):
        raise SystemExit("Education subset or source-text eligibility changed")

    for r in eligible:
        r["word_count"] = len(r["bill_text"].split())
    eligible.sort(key=lambda r: (r["word_count"], r["bill_number"]))
    short, medium, long = eligible[:112], eligible[112:224], eligible[224:]
    if (short[-1]["word_count"], medium[0]["word_count"], medium[-1]["word_count"], long[0]["word_count"]) != (163, 165, 432, 433):
        raise SystemExit("Length tertile boundaries changed")

    cells = {
        "short_minimal": [r for r in short if r["word_count"] <= 80],
        "short_other": [r for r in short if r["word_count"] > 80],
        "medium": medium,
        "long_main": [r for r in long if r["word_count"] < 1980],
        "long_tail": [r for r in long if r["word_count"] >= 1980],
    }

    selected = []
    for cell_name, draw_count, expected_size in CELL_ORDER:
        cell = cells[cell_name]
        if len(cell) != expected_size:
            raise SystemExit(f"Cell {cell_name} changed size: {len(cell)}")
        # SHA-256 ranks all eligible bill IDs uniformly and reproducibly for
        # this prespecified seed; the lowest ranks are selected without replacement.
        ranked = sorted(
            cell,
            key=lambda r: (
                sha256(f"{SEED}|{r['id']}|{r['bill_number']}".encode("utf-8")),
                r["bill_number"],
            ),
        )
        for r in ranked[:draw_count]:
            selected.append({
                "bill_number": r["bill_number"],
                "id": r["id"],
                "subject": r["subjects"][0],
                "word_count": r["word_count"],
                "cell": cell_name,
                "bill_text_sha256": sha256(r["bill_text"].encode("utf-8")),
            })

    if len(selected) != 9 or len({r["bill_number"] for r in selected}) != 9:
        raise SystemExit("Expected nine distinct bills")

    manifest = {
        "status": "sample_selected_generation_pending",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "seed": SEED,
        "selection_rule": "SHA-256 of UTF-8 seed|id|bill_number, ascending within each cell; take the first n",
        "word_count_rule": "len(bill_text.split()) on cleaned source text",
        "education_subjects": list(EDUCATION_SUBJECTS),
        "population_size": len(eligible),
        "cells": [{"name": name, "population_size": size, "draw_count": count} for name, count, size in CELL_ORDER],
        "selected": selected,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(selected)} bills")
    for r in selected:
        print(f"{r['cell']:14} {r['bill_number']} {r['word_count']:5} words  {r['subject']}")


if __name__ == "__main__":
    main()
