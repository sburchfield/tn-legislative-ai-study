// Command cleaning reads the raw LegiScan export at data/raw/bills.jsonl,
// retains only House bill records (Senate companions are dropped as
// redundant once confirmed identical/available), fills in a House record's
// bill_text from its Senate companion only when the House copy itself is
// missing, normalizes bill_text formatting, and writes the result to
// data/cleaned/bills.jsonl along with dataset statistics.
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
)

// RawRecord mirrors the fields written by scripts/export for a single
// LegiScan bill record.
type RawRecord struct {
	ID                  string   `json:"id"`
	BillNumber          string   `json:"bill_number"`
	Chamber             string   `json:"chamber"` // "H" or "S"
	Title               string   `json:"title"`
	Description         string   `json:"description"`
	Sponsor             string   `json:"sponsor"`
	Subjects            []string `json:"subjects"`
	CompanionBillNumber string   `json:"companion_bill_number"`
	BillText            string   `json:"bill_text"`
	FetchError          string   `json:"fetch_error"`
}

// CleanedRecord is the research schema: the House bill's identifying
// metadata and normalized source legislative text. Senate companion
// records do not appear as their own rows — see dataset-stats.json and
// docs/dataset.md for why, and TextSource/CompanionBillNumber for when a
// record's text actually came from its Senate companion instead of its own
// (missing) House text.
type CleanedRecord struct {
	ID                  string   `json:"id"`
	BillNumber          string   `json:"bill_number"`
	Title               string   `json:"title"`
	Description         string   `json:"description"`
	Sponsor             string   `json:"sponsor"`
	SponsorAsFiled      string   `json:"sponsor_as_filed,omitempty"`
	Subjects            []string `json:"subjects"`
	CompanionBillNumber string   `json:"companion_bill_number,omitempty"`
	TextSource          string   `json:"text_source"` // "house" or "senate_companion_fallback"
	BillText            string   `json:"bill_text"`
}

// Stats captures validation/statistics about the cleaning pass.
type Stats struct {
	RawRecords                  int `json:"raw_records"`
	HouseRecords                int `json:"house_records"`
	SenateRecordsExcluded       int `json:"senate_records_excluded"`
	SenateCompanionFallbackUsed int `json:"senate_companion_fallback_used"`
	FetchErrors                 int `json:"fetch_errors"`
	CleanedRecords              int `json:"cleaned_records"`
	MissingBillText             int `json:"missing_bill_text"`
	MissingBillNumber           int `json:"missing_bill_number"`
	DuplicateIDs                int `json:"duplicate_ids"`
	DuplicateBillNumbers        int `json:"duplicate_bill_numbers"`
	NormalizedBillTextCount     int `json:"normalized_bill_text_records"`
	MissingSponsorAsFiled       int `json:"missing_sponsor_as_filed"`
	SponsorDiffersFromAsFiled   int `json:"sponsor_differs_from_as_filed"`
}

func main() {
	var (
		inPath    = flag.String("in", "data/raw/bills.jsonl", "input raw JSONL path")
		outPath   = flag.String("out", "data/cleaned/bills.jsonl", "output cleaned JSONL path")
		statsPath = flag.String("stats", "data/cleaned/dataset-stats.json", "output stats JSON path")
	)
	flag.Parse()

	raw, err := readRawRecords(*inPath)
	if err != nil {
		log.Fatalf("%v", err)
	}

	stats := Stats{RawRecords: len(raw)}
	byBillNumber := map[string]RawRecord{}
	idSeen := map[string]int{}
	billNumberSeen := map[string]int{}

	for _, r := range raw {
		byBillNumber[r.BillNumber] = r
		if r.ID != "" {
			idSeen[r.ID]++
		}
		if r.BillNumber != "" {
			billNumberSeen[r.BillNumber]++
		}
		if r.FetchError != "" {
			stats.FetchErrors++
		}
		switch r.Chamber {
		case "H":
			stats.HouseRecords++
		case "S":
			stats.SenateRecordsExcluded++
		}
	}
	for _, n := range idSeen {
		if n > 1 {
			stats.DuplicateIDs += n - 1
		}
	}
	for _, n := range billNumberSeen {
		if n > 1 {
			stats.DuplicateBillNumbers += n - 1
		}
	}

	if err := os.MkdirAll(filepath.Dir(*outPath), 0o755); err != nil {
		log.Fatalf("failed to create output directory: %v", err)
	}
	out, err := os.Create(*outPath)
	if err != nil {
		log.Fatalf("failed to create output file %s: %v", *outPath, err)
	}
	defer out.Close()

	w := bufio.NewWriter(out)
	defer w.Flush()

	for _, r := range raw {
		if r.Chamber != "H" {
			continue // Senate-only records are not written; see doc comment above.
		}

		cleanedText := cleanBillText(r.BillText, r.BillNumber)
		textSource := "house"
		textBillNumber := r.BillNumber // which bill number's header appears in cleanedText

		if cleanedText == "" && r.CompanionBillNumber != "" {
			if companion, ok := byBillNumber[r.CompanionBillNumber]; ok && companion.Chamber == "S" {
				companionText := cleanBillText(companion.BillText, companion.BillNumber)
				if companionText != "" {
					cleanedText = companionText
					textSource = "senate_companion_fallback"
					textBillNumber = companion.BillNumber
					stats.SenateCompanionFallbackUsed++
				}
			}
		}

		sponsorAsFiled := ParseAsFiledSponsor(cleanedText, textBillNumber)
		if sponsorAsFiled == "" {
			stats.MissingSponsorAsFiled++
		} else if !sponsorMatches(r.Sponsor, sponsorAsFiled) {
			stats.SponsorDiffersFromAsFiled++
		}

		if cleanedText == "" {
			stats.MissingBillText++
		}
		if r.BillNumber == "" {
			stats.MissingBillNumber++
		}
		if textSource == "house" && cleanedText != r.BillText {
			stats.NormalizedBillTextCount++
		} else if textSource == "senate_companion_fallback" {
			// Compare against the companion's own raw text, since that's
			// the text actually used for this record.
			if companion, ok := byBillNumber[r.CompanionBillNumber]; ok && cleanedText != companion.BillText {
				stats.NormalizedBillTextCount++
			}
		}

		cleaned := CleanedRecord{
			ID:                  r.ID,
			BillNumber:          r.BillNumber,
			Title:               r.Title,
			Description:         r.Description,
			Sponsor:             r.Sponsor,
			SponsorAsFiled:      sponsorAsFiled,
			Subjects:            r.Subjects,
			CompanionBillNumber: r.CompanionBillNumber,
			TextSource:          textSource,
			BillText:            cleanedText,
		}

		line, err := json.Marshal(cleaned)
		if err != nil {
			log.Fatalf("failed to marshal cleaned record for %s: %v", r.BillNumber, err)
		}
		if _, err := w.Write(line); err != nil {
			log.Fatalf("failed to write cleaned record: %v", err)
		}
		if _, err := w.WriteString("\n"); err != nil {
			log.Fatalf("failed to write newline: %v", err)
		}
		stats.CleanedRecords++
	}

	if err := w.Flush(); err != nil {
		log.Fatalf("failed to flush output: %v", err)
	}

	statsJSON, err := json.MarshalIndent(stats, "", "  ")
	if err != nil {
		log.Fatalf("failed to marshal stats: %v", err)
	}
	if err := os.WriteFile(*statsPath, statsJSON, 0o644); err != nil {
		log.Fatalf("failed to write stats file %s: %v", *statsPath, err)
	}

	fmt.Println("Dataset statistics:")
	fmt.Printf("  raw_records:                     %d\n", stats.RawRecords)
	fmt.Printf("  house_records:                    %d\n", stats.HouseRecords)
	fmt.Printf("  senate_records_excluded:          %d\n", stats.SenateRecordsExcluded)
	fmt.Printf("  senate_companion_fallback_used:   %d\n", stats.SenateCompanionFallbackUsed)
	fmt.Printf("  fetch_errors:                     %d\n", stats.FetchErrors)
	fmt.Printf("  cleaned_records:                  %d\n", stats.CleanedRecords)
	fmt.Printf("  missing_bill_text:                %d\n", stats.MissingBillText)
	fmt.Printf("  missing_bill_number:              %d\n", stats.MissingBillNumber)
	fmt.Printf("  duplicate_ids:                    %d\n", stats.DuplicateIDs)
	fmt.Printf("  duplicate_bill_numbers:           %d\n", stats.DuplicateBillNumbers)
	fmt.Printf("  normalized_bill_text_records:     %d\n", stats.NormalizedBillTextCount)
	fmt.Printf("  missing_sponsor_as_filed:         %d\n", stats.MissingSponsorAsFiled)
	fmt.Printf("  sponsor_differs_from_as_filed:    %d\n", stats.SponsorDiffersFromAsFiled)
	fmt.Printf("\nwrote %s and %s\n", *outPath, *statsPath)
}

// sponsorMatches loosely compares LegiScan's current sponsor name (e.g.
// "William Slater") against the name as printed on the bill itself (e.g.
// "Hurt", often just a surname), by checking whether the as-filed name
// appears as a whole word within the current sponsor's name.
func sponsorMatches(currentSponsor, asFiled string) bool {
	if currentSponsor == "" || asFiled == "" {
		return false
	}
	current := strings.ToLower(currentSponsor)
	for _, word := range strings.Fields(strings.ToLower(asFiled)) {
		if strings.Contains(current, word) {
			return true
		}
	}
	return false
}

// cleanBillText strips recurring PDF pagination artifacts specific to this
// bill (anchored to its own bill number) and then applies the general,
// source-agnostic text normalization.
func cleanBillText(text, billNumber string) string {
	text = StripPDFRunningFooters(text, billNumber)
	return NormalizeBillText(text)
}

func readRawRecords(path string) ([]RawRecord, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("failed to open input file %s: %w", path, err)
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 1024*1024), 64*1024*1024)

	var records []RawRecord
	lineNo := 0
	for scanner.Scan() {
		lineNo++
		line := scanner.Text()
		if line == "" {
			continue
		}
		var r RawRecord
		if err := json.Unmarshal([]byte(line), &r); err != nil {
			return nil, fmt.Errorf("failed to parse raw record at line %d: %w", lineNo, err)
		}
		records = append(records, r)
	}
	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("failed reading input file: %w", err)
	}
	return records, nil
}
