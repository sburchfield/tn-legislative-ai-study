"""Build the researcher's source-and-summary packet without Astra judgments."""

from datetime import datetime, timezone

from common import ROOT, MODELS, load_generation, load_selected, sha

OUTPUT = ROOT / "docs/full-experiment-review-packet.md"


def main() -> None:
    manifest, selected = load_selected()
    by_number = {item["sample"]["bill_number"]: item for item in selected}
    lines = [
        "# Full-experiment researcher review packet", "",
        f"**Prepared:** {datetime.now(timezone.utc).isoformat()}  ",
        "**Purpose:** Limited researcher-conducted sanity check for factual accuracy, material omissions, and substantive meaning.  ",
        "**Reviewer:** Sam Burchfield. Complete the six issue logs before viewing any GPT-6 Astra judgments.", "",
        "Use only the exact cleaned as-filed source and unedited summaries below. The selection was frozen before generation in",
        "[`data/full/sample.json`](../data/full/sample.json). Record brief explanations and supporting source passages for any issue.",
        "This packet deliberately contains no automated evaluator results. Save the six completed issue logs before opening",
        "the `data/full/evaluation/llm` records or the automated results report.", "",
    ]
    for number in manifest["review_selected"]:
        item = by_number[number]
        sample = item["sample"]
        lines += [
            f"## {number} — {sample['tertile']}", "",
            f"Subject: {sample['subject']}  ",
            f"Source words: {sample['word_count']}  ",
            f"Source SHA-256: `{sample['bill_text_sha256']}`", "",
            "### Exact as-filed bill text", "", "```text", item["bill_text"], "```", "",
        ]
        for model in MODELS:
            record = load_generation(model, item)
            summary = record["summary"]
            lines += [
                f"### {model} summary and issue log", "",
                f"Response ID: `{record['response']['id']}`  ",
                f"Summary SHA-256: `{sha(summary.encode('utf-8'))}`", "",
                "```text", summary, "```", "",
                "Review date and time: ________  ",
                "Astra judgments viewed before saving? **No**", "",
                "| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |",
                "| --- | --- | --- | --- |", "|  |  |  |  |", "",
                "If none: **No problem observed in this limited check** ________", "",
            ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with three sources and six unedited summaries; no Astra judgments")


if __name__ == "__main__":
    main()
