package main

import (
	"fmt"
	"regexp"
	"strings"
)

// DefaultMinBillTextLength is the "suspiciously short" threshold for
// bill_text. It's deliberately below the shortest legitimate bill_text
// observed in the 114th GA corpus (352 characters) so it doesn't fire on
// real short bills, while still catching truncated/near-empty text.
const DefaultMinBillTextLength = 200

// hyphenLineWrapRe matches a hyphen immediately followed by whitespace —
// the artifact left when a hyphenated citation (e.g. "3-2-112") wraps
// across a PDF line ("3-\n2-112"). scripts/cleaning's whitespace collapse
// turns that newline into a space rather than rejoining the citation; this
// is a real, minor cleaning gap (not a validation bug), noted in the
// generated report rather than silently worked around in bill_text itself.
// It's applied here only to a scratch copy of the text, for comparison
// purposes, and never to the stored data.
var hyphenLineWrapRe = regexp.MustCompile(`-\s+`)

var whitespaceRe = regexp.MustCompile(`\s+`)

func normalizeForComparison(s string) string {
	s = hyphenLineWrapRe.ReplaceAllString(s, "-")
	s = whitespaceRe.ReplaceAllString(s, " ")
	return strings.ToLower(strings.TrimSpace(s))
}

// TitleAppearsInText reports whether title is present (after the
// comparison-only normalization above) within bill_text. This is a
// precise check, not a fuzzy one: LegiScan's title field is the bill's own
// printed caption, which is reproduced verbatim near the top of bill_text
// — so on real, correctly-matched records this should always be true.
func TitleAppearsInText(title, billText string) bool {
	if title == "" || billText == "" {
		return false
	}
	return strings.Contains(normalizeForComparison(billText), normalizeForComparison(title))
}

// checkRecord runs every per-record check against one cleaned record
// (cross-referencing its raw counterpart when available) and appends any
// findings to the running lists. It never modifies rec or raw.
func checkRecord(rec CleanedRecord, raw RawRecord, hasRaw bool, expectedSessionID int, expectedSessionName, expectedGAOrdinal string, minTextLen int, errors, warnings *[]Finding, counts map[string]int) {
	add := func(sev Severity, category, msg string) {
		f := Finding{Severity: sev, Category: category, BillNumber: rec.BillNumber, ID: rec.ID, Message: msg}
		if sev == SeverityError {
			*errors = append(*errors, f)
		} else {
			*warnings = append(*warnings, f)
		}
		counts[category]++
	}

	if !IsWellFormedBillNumber(rec.BillNumber) {
		add(SeverityError, "malformed_bill_number", fmt.Sprintf("bill_number %q does not match expected HB#### format", rec.BillNumber))
	}
	if rec.Title == "" {
		add(SeverityError, "missing_title", "title is empty")
	}
	if rec.Sponsor == "" {
		add(SeverityWarning, "missing_sponsor", "sponsor is empty")
	}
	if rec.SponsorAsFiled == "" {
		add(SeverityWarning, "missing_sponsor_as_filed", "sponsor_as_filed is empty")
	}

	switch {
	case rec.BillText == "":
		add(SeverityError, "empty_bill_text", "bill_text is empty")
	case len(rec.BillText) < minTextLen:
		add(SeverityWarning, "short_bill_text", fmt.Sprintf("bill_text is %d chars, below the %d-char suspicious-length threshold", len(rec.BillText), minTextLen))
	}

	if rec.BillText != "" && rec.Title != "" && !TitleAppearsInText(rec.Title, rec.BillText) {
		add(SeverityError, "title_text_mismatch", "title caption does not appear in bill_text — possible wrong document or metadata/text mismatch")
	}

	if rec.BillText != "" {
		if parsed, ok := FindAsFiledSponsorInText(rec.BillText, rec.BillNumber); ok {
			if rec.SponsorAsFiled != "" && !strings.EqualFold(parsed, rec.SponsorAsFiled) {
				add(SeverityError, "sponsor_as_filed_reparse_mismatch", fmt.Sprintf("stored sponsor_as_filed %q does not match independently re-parsed %q", rec.SponsorAsFiled, parsed))
			}
		} else {
			add(SeverityError, "sponsor_as_filed_not_derivable", "no \"By [Name]\" line could be found/inferred in bill_text for this bill number")
		}

		if rec.Sponsor != "" && rec.SponsorAsFiled != "" && !SponsorNamesMatch(rec.Sponsor, rec.SponsorAsFiled) {
			add(SeverityWarning, "sponsor_differs_from_as_filed", fmt.Sprintf("current sponsor %q differs from as-filed sponsor %q (expected caveat — see docs/dataset.md §4)", rec.Sponsor, rec.SponsorAsFiled))
		}

		if PublicChapterBeforeOwnHeader(rec.BillText, rec.BillNumber) {
			add(SeverityError, "wrong_document_type", "bill_text contains a \"PUBLIC CHAPTER\" marker before this bill's own header — looks like enacted/chaptered text, not an introduced/draft bill")
		} else if ContainsPublicChapterMarker(rec.BillText) {
			add(SeverityWarning, "public_chapter_citation", "bill_text cites a \"PUBLIC CHAPTER\" after its own header — likely a normal historical reference to prior law, not a wrong document, but worth a glance")
		}

		if wrong := WrongGeneralAssemblyMentionsBeforeOwnHeader(rec.BillText, rec.BillNumber, expectedGAOrdinal); len(wrong) > 0 {
			add(SeverityError, "wrong_general_assembly", fmt.Sprintf("bill_text mentions General Assembly ordinal(s) %v before this bill's own header, expected %s", wrong, expectedGAOrdinal))
		} else if wrong := WrongGeneralAssemblyMentions(rec.BillText, expectedGAOrdinal); len(wrong) > 0 {
			add(SeverityWarning, "general_assembly_citation", fmt.Sprintf("bill_text cites General Assembly ordinal(s) %v after this bill's own header — likely a normal historical reference, not a wrong document, but worth a glance", wrong))
		}

		if state := FindOtherStateMentionBeforeOwnHeader(rec.BillText, rec.BillNumber); state != "" {
			add(SeverityError, "cross_jurisdiction_text", fmt.Sprintf("bill_text references %q before this bill's own header — possible wrong-state document", state))
		} else if state := FindOtherStateMention(rec.BillText); state != "" {
			add(SeverityWarning, "other_state_citation", fmt.Sprintf("bill_text cites %q after this bill's own header — likely a normal policy-comparison reference, not a wrong document, but worth a glance", state))
		}

		artifacts := DetectArtifacts(rec.BillText)
		if artifacts.AngleBracket {
			add(SeverityWarning, "artifact_angle_bracket", "bill_text contains an unremoved '<' or '>' character")
		}
		if artifacts.UndecodedEntity {
			add(SeverityWarning, "artifact_undecoded_entity", "bill_text contains an undecoded HTML entity")
		}
		if artifacts.LeftoverFooter {
			add(SeverityWarning, "artifact_leftover_footer", "bill_text contains a leftover PDF page-footer-shaped line")
		}
		if artifacts.DoubleSpace {
			add(SeverityWarning, "artifact_double_space", "bill_text contains a double space")
		}
		if artifacts.TripleNewline {
			add(SeverityWarning, "artifact_triple_newline", "bill_text contains 3+ consecutive newlines")
		}
	}

	if hasRaw {
		if reason := CrossCheckRawProvenance(raw, expectedSessionID, expectedSessionName); reason != "" {
			add(SeverityError, "wrong_session_provenance", reason)
		}
	}
}
