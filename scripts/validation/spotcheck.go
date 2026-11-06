package main

import (
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// SampleIndices deterministically picks sampleSize distinct indices in
// [0, n) using seed, returned in ascending order (for a readable report —
// the seed, not the output order, is what makes the sample reproducible).
func SampleIndices(n, sampleSize int, seed int64) []int {
	if sampleSize > n {
		sampleSize = n
	}
	r := rand.New(rand.NewSource(seed))
	perm := r.Perm(n)[:sampleSize]
	sort.Ints(perm)
	return perm
}

func snippet(s string, n int) string {
	s = strings.TrimSpace(s)
	if len(s) <= n {
		return s
	}
	return s[:n] + "…"
}

func findingsFor(billNumber string, errors, warnings []Finding) []Finding {
	var out []Finding
	for _, f := range errors {
		if f.BillNumber == billNumber {
			out = append(out, f)
		}
	}
	for _, f := range warnings {
		if f.BillNumber == billNumber {
			out = append(out, f)
		}
	}
	return out
}

func writeChecklistEntry(sb *strings.Builder, rec CleanedRecord, rawByID map[string]RawRecord, hasRaw bool, report Report, expectedGAOrdinal string) {
	raw, hasRawForRecord := rawByID[rec.ID]

	asFiledSponsor, byLinePresent := FindAsFiledSponsorInText(rec.BillText, rec.BillNumber)
	looksLikeDraft := !ContainsPublicChapterMarker(rec.BillText)
	if hasRaw && hasRawForRecord && raw.TextType != "" {
		looksLikeDraft = looksLikeDraft && (raw.TextType == "Draft" || raw.TextType == "Introduced")
	}

	sessionMatch := "not checked (no raw record found)"
	if hasRaw && hasRawForRecord {
		if reason := CrossCheckRawProvenance(raw, report.ExpectedSessionID, report.ExpectedSessionName); reason == "" {
			sessionMatch = fmt.Sprintf("yes (raw session_id=%d, session_name=%q, text_type=%q)", raw.SessionID, raw.SessionName, raw.TextType)
		} else {
			sessionMatch = "NO — " + reason
		}
	}
	if wrong := WrongGeneralAssemblyMentions(rec.BillText, expectedGAOrdinal); len(wrong) > 0 {
		sessionMatch += fmt.Sprintf("; also bill_text mentions GA ordinal(s) %v, expected %s", wrong, expectedGAOrdinal)
	}

	fmt.Fprintf(sb, "### %s\n\n", rec.BillNumber)
	fmt.Fprintf(sb, "- **Title:** %s\n", rec.Title)
	fmt.Fprintf(sb, "- **Sponsor (current):** %s\n", orNone(rec.Sponsor))
	fmt.Fprintf(sb, "- **Sponsor (as filed):** %s\n", orNone(rec.SponsorAsFiled))
	fmt.Fprintf(sb, "- **bill_text length:** %d chars\n", len(rec.BillText))
	fmt.Fprintf(sb, "- **\"By ...\" line present in text:** %v", byLinePresent)
	if byLinePresent {
		fmt.Fprintf(sb, " (parsed as %q)", asFiledSponsor)
	}
	sb.WriteString("\n")
	fmt.Fprintf(sb, "- **Looks like introduced/draft text (not enacted/chaptered):** %v\n", looksLikeDraft)
	fmt.Fprintf(sb, "- **Session/General Assembly matches expected:** %s\n", sessionMatch)

	flags := findingsFor(rec.BillNumber, report.Errors, report.Warnings)
	if len(flags) == 0 {
		sb.WriteString("- **Automated validation flags:** none\n")
	} else {
		sb.WriteString("- **Automated validation flags:**\n")
		for _, f := range flags {
			fmt.Fprintf(sb, "  - `%s` **%s**: %s\n", f.Severity, f.Category, f.Message)
		}
	}
	fmt.Fprintf(sb, "- **bill_text excerpt (first ~400 chars):**\n\n  > %s\n\n", strings.ReplaceAll(snippet(rec.BillText, 400), "\n", " "))
}

func orNone(s string) string {
	if s == "" {
		return "_(none)_"
	}
	return s
}

func writeSpotCheckReport(path string, records []CleanedRecord, rawByID map[string]RawRecord, hasRaw bool, report Report, sampleSize int, seed int64, expectedGAOrdinal string) error {
	byBillNumber := map[string]CleanedRecord{}
	for _, r := range records {
		byBillNumber[r.BillNumber] = r
	}

	var sb strings.Builder

	sb.WriteString("# Dataset Spot Check\n\n")
	fmt.Fprintf(&sb, "Generated: %s\n\n", report.GeneratedAt)
	sb.WriteString("Produced by `scripts/validation` (see `data/validation/dataset-validation.json` for the full machine-readable report). This document is generated — do not hand-edit it; rerun the validation script to refresh it.\n\n")

	sb.WriteString("## Executive summary\n\n")
	fmt.Fprintf(&sb, "- Total records checked: **%d**\n", report.Summary.TotalRecordsChecked)
	fmt.Fprintf(&sb, "- ERROR-level findings: **%d**\n", report.Summary.ErrorCount)
	fmt.Fprintf(&sb, "- WARNING-level findings: **%d**\n", report.Summary.WarningCount)
	fmt.Fprintf(&sb, "- Records requiring manual review: **%d**\n", report.Summary.RecordsRequiringManualReview)
	fmt.Fprintf(&sb, "- Safe to proceed with the study: **%v**\n\n", report.Summary.SafeToProceed)
	fmt.Fprintf(&sb, "%s\n\n", report.Summary.Notes)

	fmt.Fprintf(&sb, "## Random spot-check sample (seed=%d, n=%d)\n\n", seed, sampleSize)
	sb.WriteString("Deterministic sample — rerunning the validation script with the same `-seed` reproduces the same set of records.\n\n")

	indices := SampleIndices(len(records), sampleSize, seed)
	for _, i := range indices {
		writeChecklistEntry(&sb, records[i], rawByID, hasRaw, report, expectedGAOrdinal)
	}

	sb.WriteString("## Targeted edge-case checks\n\n")
	sb.WriteString("Specifically requested checks against two bills involved in previously-found issues.\n\n")

	sb.WriteString("### HB0486 — stray 113th GA Public Chapter document check\n\n")
	sb.WriteString("A LegiScan data anomaly previously caused this bill's selected text to come from a misattached 113th General Assembly (2023) enacted \"Public Chapter\" PDF instead of its real 114th GA as-filed draft. Confirming the fix held:\n\n")
	if rec, ok := byBillNumber["HB0486"]; ok {
		writeChecklistEntry(&sb, rec, rawByID, hasRaw, report, expectedGAOrdinal)
	} else {
		sb.WriteString("_HB0486 was not found in the cleaned dataset._\n\n")
	}

	sb.WriteString("### HB0349 — current-sponsor vs. as-filed-sponsor check\n\n")
	sb.WriteString("This bill's sponsorship changed after filing, so `sponsor` (current) and `sponsor_as_filed` (from the bill's own \"By [Name]\" line) are expected to legitimately disagree. Confirming that's represented correctly, not silently \"fixed\":\n\n")
	if rec, ok := byBillNumber["HB0349"]; ok {
		writeChecklistEntry(&sb, rec, rawByID, hasRaw, report, expectedGAOrdinal)
	} else {
		sb.WriteString("_HB0349 was not found in the cleaned dataset._\n\n")
	}

	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	return os.WriteFile(path, []byte(sb.String()), 0o644)
}
