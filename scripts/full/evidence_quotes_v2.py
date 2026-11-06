"""Full-study evidence checks with narrow PDF hyphen-wrap normalization.

Version 2 keeps the pilot's structural checks and source/summary substring rule.
Only whitespace after a hyphen between ASCII letters/digits is ignored, because
the cleaned PDF text sometimes wraps statute numbers and K-12 across lines.
Punctuation, words, and digits must still match exactly.
"""

import re

VERSION = "full-evidence-quotes-v2-2026-10-17"


def normalized(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"(?<=[A-Za-z0-9])-\s+(?=[A-Za-z0-9])", "-", collapsed)


def exact_quote(quote: str, text: str) -> bool:
    return bool(quote.strip()) and normalized(quote) in normalized(text)


def validate_source(value: dict, source: str) -> None:
    propositions = value.get("propositions")
    if not isinstance(propositions, list) or not propositions:
        raise ValueError("No source propositions")
    for index, item in enumerate(propositions, 1):
        if item.get("id") != f"P{index}" or item.get("importance") not in ("core", "supporting"):
            raise ValueError(f"Invalid source proposition ID or importance at {index}")
        if not item.get("proposition") or not item.get("section") or not exact_quote(item.get("source_quote", ""), source):
            raise ValueError(f"Missing content or nonmatching source quote for P{index}")


def validate_coverage(value: dict, propositions: list[dict], summary: str) -> None:
    assessments = value.get("assessments")
    if not isinstance(assessments, list) or len(assessments) != len(propositions):
        raise ValueError("Coverage does not assess every source proposition")
    expected = {item["id"] for item in propositions}
    seen = set()
    for item in assessments:
        ident = item.get("proposition_id")
        status = item.get("status")
        if ident not in expected or ident in seen or status not in ("full", "partial", "omitted"):
            raise ValueError("Invalid or duplicate coverage proposition ID/status")
        seen.add(ident)
        quote = item.get("summary_quote", "")
        if status == "omitted":
            if quote.strip():
                raise ValueError(f"Omitted proposition {ident} has a summary quote")
        elif not exact_quote(quote, summary):
            raise ValueError(f"Coverage quote does not match summary for {ident}")
        if not item.get("rationale", "").strip():
            raise ValueError(f"Coverage rationale missing for {ident}")
    if seen != expected:
        raise ValueError("Coverage proposition IDs do not match source inventory")


def validate_factuality(value: dict, source: str, summary: str) -> None:
    claims = value.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("No summary claims")
    for index, item in enumerate(claims, 1):
        verdict = item.get("verdict")
        error_type = item.get("error_type")
        if verdict not in ("supported", "contradicted", "not_established"):
            raise ValueError(f"Invalid verdict for claim {index}")
        if (verdict == "supported") != (error_type == "none"):
            raise ValueError(f"Inconsistent verdict and error type for claim {index}")
        if not item.get("claim") or not item.get("rationale") or not exact_quote(item.get("summary_quote", ""), summary):
            raise ValueError(f"Missing content or nonmatching summary quote for claim {index}")
        source_quote = item.get("source_quote", "")
        if source_quote and not exact_quote(source_quote, source):
            raise ValueError(f"Source quote does not match bill for claim {index}")
