"""Render the saved, unedited pilot summaries as a reviewable Markdown page."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "data/pilot/education-sample.json"
RESPONSES = ROOT / "data/pilot/responses"
OUTPUT = ROOT / "docs/pilot-summaries.md"


def main() -> None:
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    lines = [
        "# Education pilot summaries (unedited model output)",
        "",
        "These are the nine summaries generated on October 4, 2026 with the approved prompt and output format. They have passed structural checks but have **not** been scored for readability, information coverage, or factual consistency. See [the generation run](pilot-generation-run.md) for provenance and API settings. The linked JSON files are the authoritative response records.",
        "",
    ]
    for item in sample["selected"]:
        bill_number = item["bill_number"]
        record = json.loads((RESPONSES / f"{bill_number}.json").read_text(encoding="utf-8"))
        if record["generation_status"] != "completed" or record["bill_text_sha256"] != item["bill_text_sha256"]:
            raise SystemExit(f"Missing or inconsistent response for {bill_number}")
        lines.extend([
            f"## {bill_number}",
            "",
            f"{item['cell'].replace('_', ' ').title()} · {item['word_count']:,} source words · {len(record['summary'].split()):,} summary words · [raw response](../data/pilot/responses/{bill_number}.json)",
            "",
            record["summary"],
            "",
        ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(sample['selected'])} unedited summaries")


if __name__ == "__main__":
    main()
