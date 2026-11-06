// Command validation inspects the cleaned research dataset (and, where
// available, its raw counterpart) and reports data-quality findings. It is
// read-only: it never modifies data/raw, data/cleaned, or any source
// legislative text, and makes no network calls.
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sort"
	"time"
)

func main() {
	var (
		cleanedPath         = flag.String("cleaned", "data/cleaned/bills.jsonl", "path to the cleaned dataset")
		rawPath             = flag.String("raw", "data/raw/bills.jsonl", "path to the raw dataset, used for session/provenance cross-checks (optional)")
		outPath             = flag.String("out", "data/validation/dataset-validation.json", "path to write the machine-readable validation report")
		spotCheckOutPath    = flag.String("spotcheck-out", "docs/data-spot-check.md", "path to write the human-readable spot-check report")
		sampleSize          = flag.Int("sample-size", 20, "number of records to include in the random spot-check sample")
		seed                = flag.Int64("seed", 42, "random seed for the deterministic spot-check sample")
		minTextLen          = flag.Int("min-text-length", DefaultMinBillTextLength, "bill_text length below which a record is flagged as suspiciously short")
		expectedSessionID   = flag.Int("expected-session-id", 2161, "expected LegiScan session_id (114th TN General Assembly by default)")
		expectedSessionName = flag.String("expected-session-name", "114th General Assembly", "expected LegiScan session_name")
		expectedGAOrdinal   = flag.String("expected-ga-ordinal", "114", "expected General Assembly ordinal number, as it appears in bill text (e.g. \"114\" for \"114th General Assembly\")")
	)
	flag.Parse()

	cleaned, err := readCleanedRecords(*cleanedPath)
	if err != nil {
		log.Fatalf("%v", err)
	}

	rawByID, rawErr := readRawRecordsByID(*rawPath)
	hasRaw := rawErr == nil
	if rawErr != nil {
		log.Printf("warning: could not read raw dataset at %s (%v) — session/provenance cross-checks will be skipped", *rawPath, rawErr)
	}

	var errors, warnings []Finding
	counts := map[string]int{}

	idSeen := map[string]int{}
	billNumberSeen := map[string]int{}

	for _, rec := range cleaned {
		if rec.ID != "" {
			idSeen[rec.ID]++
		}
		if rec.BillNumber != "" {
			billNumberSeen[rec.BillNumber]++
		}
		if rec.BillNumber == "" {
			warnings = append(warnings, Finding{Severity: SeverityWarning, Category: "missing_bill_number", ID: rec.ID, Message: "bill_number is empty"})
			counts["missing_bill_number"]++
		}

		raw, ok := rawByID[rec.ID]
		checkRecord(rec, raw, hasRaw && ok, *expectedSessionID, *expectedSessionName, *expectedGAOrdinal, *minTextLen, &errors, &warnings, counts)
	}

	for id, n := range idSeen {
		if n > 1 {
			errors = append(errors, Finding{Severity: SeverityError, Category: "duplicate_id", ID: id, Message: fmt.Sprintf("id %q appears %d times", id, n)})
			counts["duplicate_id"]++
		}
	}
	for bn, n := range billNumberSeen {
		if n > 1 {
			errors = append(errors, Finding{Severity: SeverityError, Category: "duplicate_bill_number", BillNumber: bn, Message: fmt.Sprintf("bill_number %q appears %d times", bn, n)})
			counts["duplicate_bill_number"]++
		}
	}

	exactDupGroups := ExactDuplicateGroups(cleaned)
	for _, bns := range exactDupGroups {
		warnings = append(warnings, Finding{Severity: SeverityWarning, Category: "exact_duplicate_text", BillNumber: bns[0], Message: fmt.Sprintf("bill_text is byte-identical across bill numbers %v", bns)})
		counts["exact_duplicate_text"]++
	}
	nearDupGroups := NearDuplicateGroups(cleaned, exactDupGroups)
	for _, bns := range nearDupGroups {
		warnings = append(warnings, Finding{Severity: SeverityWarning, Category: "near_duplicate_text", BillNumber: bns[0], Message: fmt.Sprintf("bill_text looks like a possible near-duplicate across bill numbers %v (heuristic match, verify manually)", bns)})
		counts["near_duplicate_text"]++
	}

	sortFindings(errors)
	sortFindings(warnings)

	reviewSet := map[string]bool{}
	for _, f := range errors {
		reviewSet[f.BillNumber] = true
	}
	for _, f := range warnings {
		reviewSet[f.BillNumber] = true
	}

	report := Report{
		GeneratedAt:         time.Now().UTC().Format(time.RFC3339),
		ExpectedSessionID:   *expectedSessionID,
		ExpectedSessionName: *expectedSessionName,
		TotalRecords:        len(cleaned),
		Counts:              counts,
		Errors:              errors,
		Warnings:            warnings,
		Summary: Summary{
			TotalRecordsChecked:          len(cleaned),
			ErrorCount:                   len(errors),
			WarningCount:                 len(warnings),
			RecordsRequiringManualReview: len(reviewSet),
			SafeToProceed:                len(errors) == 0,
		},
	}
	if report.Summary.SafeToProceed {
		report.Summary.Notes = "No ERROR-level findings. WARNING-level findings (if any) reflect known, documented caveats (e.g. sponsor timing) or low-severity formatting artifacts worth a spot check, not blocking issues."
	} else {
		report.Summary.Notes = "ERROR-level findings were found. Review the errors list before using this dataset for the study."
	}

	if err := os.MkdirAll(filepath.Dir(*outPath), 0o755); err != nil {
		log.Fatalf("failed to create output directory: %v", err)
	}
	reportJSON, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		log.Fatalf("failed to marshal report: %v", err)
	}
	if err := os.WriteFile(*outPath, reportJSON, 0o644); err != nil {
		log.Fatalf("failed to write report to %s: %v", *outPath, err)
	}

	printConsoleSummary(report)

	if err := writeSpotCheckReport(*spotCheckOutPath, cleaned, rawByID, hasRaw, report, *sampleSize, *seed, *expectedGAOrdinal); err != nil {
		log.Fatalf("failed to write spot-check report: %v", err)
	}

	fmt.Printf("\nwrote %s and %s\n", *outPath, *spotCheckOutPath)
}

func sortFindings(findings []Finding) {
	sort.Slice(findings, func(i, j int) bool {
		if findings[i].Category != findings[j].Category {
			return findings[i].Category < findings[j].Category
		}
		return findings[i].BillNumber < findings[j].BillNumber
	})
}

func printConsoleSummary(r Report) {
	fmt.Println("Dataset validation summary:")
	fmt.Printf("  total_records_checked:            %d\n", r.Summary.TotalRecordsChecked)
	fmt.Printf("  error_count:                      %d\n", r.Summary.ErrorCount)
	fmt.Printf("  warning_count:                    %d\n", r.Summary.WarningCount)
	fmt.Printf("  records_requiring_manual_review:  %d\n", r.Summary.RecordsRequiringManualReview)
	fmt.Printf("  safe_to_proceed:                  %v\n", r.Summary.SafeToProceed)
	fmt.Println()
	fmt.Println("Findings by category:")
	categories := make([]string, 0, len(r.Counts))
	for c := range r.Counts {
		categories = append(categories, c)
	}
	sort.Strings(categories)
	for _, c := range categories {
		fmt.Printf("  %-32s %d\n", c, r.Counts[c])
	}
}

func readCleanedRecords(path string) ([]CleanedRecord, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("failed to open cleaned dataset %s: %w", path, err)
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 1024*1024), 64*1024*1024)

	var records []CleanedRecord
	lineNo := 0
	for scanner.Scan() {
		lineNo++
		line := scanner.Text()
		if line == "" {
			continue
		}
		var r CleanedRecord
		if err := json.Unmarshal([]byte(line), &r); err != nil {
			return nil, fmt.Errorf("failed to parse cleaned record at line %d: %w", lineNo, err)
		}
		records = append(records, r)
	}
	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("failed reading cleaned dataset: %w", err)
	}
	return records, nil
}

func readRawRecordsByID(path string) (map[string]RawRecord, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 1024*1024), 64*1024*1024)

	byID := map[string]RawRecord{}
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}
		var r RawRecord
		if err := json.Unmarshal([]byte(line), &r); err != nil {
			continue
		}
		if r.ID != "" {
			byID[r.ID] = r
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return byID, nil
}
