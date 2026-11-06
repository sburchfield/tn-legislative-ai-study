"""Draw the frozen 36-bill experiment and three-bill researcher check."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data/cleaned/bills.jsonl"
PILOT = ROOT / "data/pilot/education-sample.json"
OUTPUT = ROOT / "data/full/sample.json"
CORPUS_SHA = "df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a"
PILOT_SHA = "0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1"
SEED = "INSC499-education-full-2026-10-17-v1"
REVIEW_SEED = "INSC499-education-review-2026-10-17-v1"
EDUCATION_SUBJECTS = (
    "Education", "Education, Curriculum", "Education, Dept. of", "Education, Higher",
    "Education, State Board of", "Local Education Agencies", "Lottery, Scholarships and Programs",
    "Scholarships and Financial Aid", "School Transportation", "School Vouchers",
    "Schools, Charter", "Schools, Home", "Schools, Private", "State Universities", "Students",
    "Teachers, Principals and School Personnel", "Tennessee Higher Education Commission",
    "Tennessee Investment in Student Achievement (TISA)",
)
CELL_COUNTS = {"short_minimal": 5, "short_other": 7, "medium": 12, "long_main": 10, "long_tail": 2}
CELL_SIZES = {"short_minimal": 41, "short_other": 68, "medium": 109, "long_main": 93, "long_tail": 16}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rank(seed: str, row: dict) -> tuple[str, str]:
    return sha(f"{seed}|{row['id']}|{row['bill_number']}".encode("utf-8")), row["bill_number"]


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Draw already exists: {OUTPUT}; do not redraw")
    corpus_bytes = CORPUS.read_bytes()
    pilot_bytes = PILOT.read_bytes()
    if sha(corpus_bytes) != CORPUS_SHA or sha(pilot_bytes) != PILOT_SHA:
        raise SystemExit("Frozen corpus or pilot manifest changed")
    rows = [json.loads(line) for line in corpus_bytes.splitlines() if line.strip()]
    pilot = json.loads(pilot_bytes)
    if len(rows) != 2684 or len({r["bill_number"] for r in rows}) != 2684:
        raise SystemExit("Unexpected corpus size or duplicate bill number")
    eligible = [r for r in rows if len(r["subjects"]) == 1 and r["subjects"][0] in EDUCATION_SUBJECTS]
    if len(eligible) != 336 or any(not r["bill_text"].strip() or r["text_source"] != "house" for r in eligible):
        raise SystemExit("Education eligibility changed")
    for row in eligible:
        row["word_count"] = len(row["bill_text"].split())
    eligible.sort(key=lambda r: (r["word_count"], r["bill_number"]))
    short, medium, long = eligible[:112], eligible[112:224], eligible[224:]
    if (short[-1]["word_count"], medium[0]["word_count"], medium[-1]["word_count"], long[0]["word_count"]) != (163, 165, 432, 433):
        raise SystemExit("Original tertile boundaries changed")
    pilot_numbers = {r["bill_number"] for r in pilot["selected"]}
    if len(pilot_numbers) != 9:
        raise SystemExit("Pilot manifest changed")
    short = [r for r in short if r["bill_number"] not in pilot_numbers]
    medium = [r for r in medium if r["bill_number"] not in pilot_numbers]
    long = [r for r in long if r["bill_number"] not in pilot_numbers]
    if tuple(map(len, (short, medium, long))) != (109, 109, 109):
        raise SystemExit("Unexpected eligible counts after pilot exclusion")
    cells = {
        "short_minimal": [r for r in short if r["word_count"] <= 80],
        "short_other": [r for r in short if r["word_count"] > 80],
        "medium": medium,
        "long_main": [r for r in long if r["word_count"] < 1980],
        "long_tail": [r for r in long if r["word_count"] >= 1980],
    }
    # Check the complete frame and draw without using any generated outcome.
    selected = []
    for cell_name, count in CELL_COUNTS.items():
        cell = cells[cell_name]
        if len(cell) != CELL_SIZES[cell_name]:
            raise SystemExit(f"Unexpected {cell_name} frame size: {len(cell)}")
        for row in sorted(cell, key=lambda r: rank(SEED, r))[:count]:
            selected.append({
                "bill_number": row["bill_number"], "id": row["id"],
                "subject": row["subjects"][0], "cell": cell_name,
                "tertile": "short" if cell_name.startswith("short") else "long" if cell_name.startswith("long") else "medium",
                "word_count": row["word_count"],
                "bill_text_sha256": sha(row["bill_text"].encode("utf-8")),
            })
    if len(selected) != 36 or len({r["bill_number"] for r in selected}) != 36:
        raise SystemExit("Draw did not produce 36 distinct bills")
    review = [min((r for r in selected if r["tertile"] == tertile), key=lambda r: rank(REVIEW_SEED, r))
              for tertile in ("short", "medium", "long")]
    timestamp = datetime.now(timezone.utc).isoformat()
    manifest = {
        "status": "sample_selected_generation_pending", "selected_at_utc": timestamp,
        "source": str(CORPUS.relative_to(ROOT)), "source_sha256": CORPUS_SHA,
        "pilot_manifest_sha256": PILOT_SHA, "pilot_excluded_bill_numbers": sorted(pilot_numbers),
        "education_subjects": list(EDUCATION_SUBJECTS), "education_population_size": 336,
        "post_pilot_population_size": 327,
        "tertile_rule": "Original 336-bill rank tertiles by (len(bill_text.split()), bill_number), 112 each; exclude pilot without re-ranking",
        "word_count_rule": "len(bill_text.split()) on cleaned source text",
        "sample_seed": SEED, "review_seed": REVIEW_SEED,
        "ranking_rule": "SHA-256 of UTF-8 seed|id|bill_number ascending, ties by bill_number; take first n in each cell or tertile",
        "cells": [{"name": name, "population_size": CELL_SIZES[name], "draw_count": count}
                  for name, count in CELL_COUNTS.items()],
        "selected": selected, "review_selected_at_utc": timestamp,
        "review_selected": [r["bill_number"] for r in review],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}; SHA-256 {sha(OUTPUT.read_bytes())}")
    for row in selected:
        marker = " REVIEW" if row["bill_number"] in manifest["review_selected"] else ""
        print(f"{row['cell']:14} {row['bill_number']} {row['word_count']:5} words{marker}")


if __name__ == "__main__":
    main()
