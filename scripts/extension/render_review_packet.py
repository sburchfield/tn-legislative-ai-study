"""Render the same three sources and six new summaries without Astra results."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/full"))
from common import GEN_FORMAT_SHA, GEN_PROMPT_SHA, frozen, load_selected, sha  # noqa: E402
from check_generation_feasibility import CLAUDE_MODEL, build_request  # noqa: E402
from generate_full import (FORMAT, GEMMA_MODEL, MAX_OUTPUT_TOKENS,
                           OUTPUT as GENERATION, PROMPT, validate_existing)  # noqa: E402

OUTPUT = ROOT / "docs/cross-provider-review-packet.md"
PROVIDERS = {"claude": CLAUDE_MODEL, "gemma": GEMMA_MODEL}


def main() -> None:
    manifest, selected = load_selected()
    by_number = {item["sample"]["bill_number"]: item for item in selected}
    prompt = frozen(PROMPT, GEN_PROMPT_SHA).decode("utf-8")
    fmt = json.loads(frozen(FORMAT, GEN_FORMAT_SHA))
    lines = [
        "# Cross-provider extension researcher review packet", "",
        f"**Prepared:** {datetime.now(timezone.utc).isoformat()}  ",
        "**Purpose:** Limited researcher sanity check of the six new Claude/Gemma summaries.  ",
        "**Reviewer:** Sam Burchfield. Compare each unedited summary with the exact as-filed source before reading its new Astra judgments.", "",
        "The three bills were selected before the original full experiment in",
        "[`data/full/sample.json`](../data/full/sample.json). Record only factual errors, material omissions, or changes to substantive meaning,",
        "with brief source passages and explanations. If none is found, mark `No problem observed`. This packet contains no Astra judgments.",
        "Earlier Astra findings for these bills may already be known, so this is only partially blinded; it is not expert validation or a reliability test.", "",
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
        for provider, model in PROVIDERS.items():
            path = GENERATION / provider / f"{number}.json"
            body = build_request(provider, model, item, prompt, fmt, MAX_OUTPUT_TOKENS)
            validate_existing(path, item, provider, model, body)
            record = json.loads(path.read_text(encoding="utf-8"))
            summary = record["summary"]
            lines += [
                f"### {model} summary and issue log", "",
                f"Raw response: [`{provider}/{number}.json`](../data/extension/responses/{provider}/{number}.json)  ",
                f"Summary SHA-256: `{sha(summary.encode('utf-8'))}`", "",
                "```text", summary, "```", "",
                "Review date and time: ________  ",
                "New Astra judgments viewed before saving? ________", "",
                "| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |",
                "| --- | --- | --- | --- |", "|  |  |  |  |", "",
                "If none: **No problem observed in this limited check** ________", "",
            ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with three sources and six unedited summaries, without Astra results")


if __name__ == "__main__":
    main()
