// Command export performs a read-only export of Tennessee legislative bill
// data from the LegiScan API (https://legiscan.com/legiscan) for a given
// General Assembly session, downloads each bill's earliest ("as filed")
// text document, extracts plain text from the source PDF via poppler's
// pdftotext, and writes one JSON record per line to data/raw/bills.jsonl.
//
// It never writes to LegiScan or any other external system, and stores
// document content only via the pdftotext conversion required to represent
// a PDF as text — the extracted text is not otherwise altered.
//
// LegiScan is a public API intended for exactly this kind of programmatic,
// read-only reuse (unlike scraping capitol.tn.gov directly, which its
// robots.txt disallows for non-search-engine bots).
package main

import (
	"bufio"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"time"
)

// RawRecord is one exported bill record, written as a single JSON line.
type RawRecord struct {
	ID                  string   `json:"id"`
	BillNumber          string   `json:"bill_number"`
	Chamber             string   `json:"chamber"` // "H" or "S"
	Title               string   `json:"title"`
	Description         string   `json:"description"`
	Sponsor             string   `json:"sponsor"`
	Subjects            []string `json:"subjects,omitempty"`
	CompanionBillNumber string   `json:"companion_bill_number,omitempty"`
	BillText            string   `json:"bill_text"`
	TextDocID           int      `json:"text_doc_id,omitempty"`
	TextType            string   `json:"text_type,omitempty"`
	TextDate            string   `json:"text_date,omitempty"`
	ChangeHash          string   `json:"change_hash"`
	SessionID           int      `json:"session_id"`
	SessionName         string   `json:"session_name"`
	StateLink           string   `json:"state_link,omitempty"`
	LegiscanURL         string   `json:"legiscan_url,omitempty"`
	FetchError          string   `json:"fetch_error,omitempty"`
}

// billNumberRe matches "Bill"-type entries only (HB/SB followed by
// digits), excluding joint resolutions (HJR/SJR), simple resolutions
// (HR/SR), and any other legislative instrument type.
var billNumberRe = regexp.MustCompile(`^([HS])B\d+$`)

func main() {
	var (
		sessionID     = flag.Int("session-id", envInt("LEGISCAN_SESSION_ID", 2161), "LegiScan session id (env: LEGISCAN_SESSION_ID; default is TN's 114th General Assembly, 2025-2026)")
		apiKey        = flag.String("api-key", os.Getenv("LEGISCAN_API_KEY"), "LegiScan API key (env: LEGISCAN_API_KEY)")
		outPath       = flag.String("out", "data/raw/bills.jsonl", "output JSONL file path")
		pdftotextPath = flag.String("pdftotext", "pdftotext", "path to the poppler pdftotext binary")
		limit         = flag.Int("limit", 0, "maximum number of bills to fetch (0 = no limit; useful for testing)")
		delayMs       = flag.Int("delay-ms", 200, "delay in milliseconds between LegiScan API requests")
		fresh         = flag.Bool("fresh", false, "ignore any existing output file and re-fetch every bill from scratch")
	)
	flag.Parse()

	if *apiKey == "" {
		log.Fatal("a LegiScan API key is required: pass -api-key or set LEGISCAN_API_KEY")
	}

	if err := os.MkdirAll(filepath.Dir(*outPath), 0o755); err != nil {
		log.Fatalf("failed to create output directory: %v", err)
	}

	alreadyFetched := map[string]bool{}
	if !*fresh {
		alreadyFetched = loadFetchedIDs(*outPath)
	}

	openFlags := os.O_CREATE | os.O_WRONLY
	if *fresh || len(alreadyFetched) == 0 {
		openFlags |= os.O_TRUNC
	} else {
		openFlags |= os.O_APPEND
	}
	f, err := os.OpenFile(*outPath, openFlags, 0o644)
	if err != nil {
		log.Fatalf("failed to open output file %s: %v", *outPath, err)
	}
	defer f.Close()

	w := bufio.NewWriter(f)
	defer w.Flush()

	client := newLegiscanClient(*apiKey)

	log.Printf("fetching master list for session %d...", *sessionID)
	entries, err := client.getMasterList(*sessionID)
	if err != nil {
		log.Fatalf("failed to fetch master list: %v", err)
	}

	var billEntries []masterListEntry
	for _, e := range entries {
		if billNumberRe.MatchString(e.Number) {
			billEntries = append(billEntries, e)
		}
	}
	log.Printf("master list has %d entries, %d are House/Senate bills (resolutions excluded)", len(entries), len(billEntries))

	if len(alreadyFetched) > 0 {
		log.Printf("resuming: %d bills already present in %s will be skipped", len(alreadyFetched), *outPath)
	}

	start := time.Now()
	fetched, skipped, errored := 0, 0, 0

	for _, entry := range billEntries {
		id := fmt.Sprint(entry.BillID)
		if alreadyFetched[id] {
			skipped++
			continue
		}

		if *limit > 0 && fetched >= *limit {
			log.Printf("reached -limit=%d, stopping", *limit)
			break
		}

		record, fatal, err := fetchBillRecord(client, *pdftotextPath, entry.BillID)
		if fatal {
			log.Printf("stopping early: %v", err)
			break
		}
		if err != nil {
			log.Printf("warning: bill_id %d: %v", entry.BillID, err)
			errored++
		}

		line, err := json.Marshal(record)
		if err != nil {
			log.Fatalf("failed to marshal record for bill_id %d: %v", entry.BillID, err)
		}
		if _, err := w.Write(line); err != nil {
			log.Fatalf("failed to write record: %v", err)
		}
		if _, err := w.WriteString("\n"); err != nil {
			log.Fatalf("failed to write newline: %v", err)
		}
		if err := w.Flush(); err != nil {
			log.Fatalf("failed to flush output: %v", err)
		}

		fetched++
		if fetched%50 == 0 {
			log.Printf("fetched %d/%d bills...", fetched, len(billEntries)-skipped)
		}

		time.Sleep(time.Duration(*delayMs) * time.Millisecond)
	}

	log.Printf("done: fetched %d, skipped (already present) %d, had errors %d, in %s",
		fetched, skipped, errored, time.Since(start).Round(time.Second))
	fmt.Printf("export completed at %s (UTC)\n", time.Now().UTC().Format(time.RFC3339))
}

// fetchBillRecord fetches one bill's detail and text and converts it to a
// RawRecord. The second return value is true when the error is fatal to the
// whole run (e.g. API quota exceeded) and the caller should stop rather
// than continue to the next bill.
func fetchBillRecord(client *legiscanClient, pdftotextPath string, billID int) (RawRecord, bool, error) {
	bill, err := client.getBill(billID)
	if err != nil {
		if fatal := isFatalAPIError(err); fatal {
			return RawRecord{}, true, err
		}
		return RawRecord{
			ID:         fmt.Sprint(billID),
			FetchError: fmt.Sprintf("getBill failed: %v", err),
		}, false, err
	}

	record := RawRecord{
		ID:                  fmt.Sprint(bill.BillID),
		BillNumber:          bill.BillNumber,
		Chamber:             bill.Body,
		Title:               bill.Title,
		Description:         bill.Description,
		Sponsor:             primarySponsor(bill.Sponsors),
		Subjects:            subjectNames(bill.Subjects),
		CompanionBillNumber: companionBillNumber(bill.Sasts),
		ChangeHash:          bill.ChangeHash,
		SessionID:           bill.SessionID,
		SessionName:         bill.Session.SessionName,
		StateLink:           bill.StateLink,
		LegiscanURL:         bill.URL,
	}

	text, ok := earliestText(bill.Texts)
	if !ok {
		record.FetchError = "no text document available"
		return record, false, nil
	}
	record.TextDocID = text.DocID
	record.TextType = text.Type
	record.TextDate = text.Date

	doc, err := client.getBillText(text.DocID)
	if err != nil {
		if fatal := isFatalAPIError(err); fatal {
			return record, true, err
		}
		record.FetchError = fmt.Sprintf("getBillText failed: %v", err)
		return record, false, err
	}

	raw, err := base64.StdEncoding.DecodeString(doc.Doc)
	if err != nil {
		record.FetchError = fmt.Sprintf("failed to decode document: %v", err)
		return record, false, err
	}

	switch doc.Mime {
	case "application/pdf":
		text, err := extractPDFText(pdftotextPath, raw)
		if err != nil {
			record.FetchError = fmt.Sprintf("pdf extraction failed: %v", err)
			return record, false, err
		}
		record.BillText = text
	case "text/html", "text/plain":
		record.BillText = string(raw)
	default:
		record.FetchError = fmt.Sprintf("unsupported document mime type: %s", doc.Mime)
		return record, false, fmt.Errorf("unsupported mime type %s", doc.Mime)
	}

	return record, false, nil
}

// isFatalAPIError reports whether a LegiScan API error should stop the
// entire export run (e.g. the account's query quota has been exhausted)
// rather than just being logged and skipped for this one bill.
func isFatalAPIError(err error) bool {
	lerr, ok := err.(*legiscanError)
	if !ok {
		return false
	}
	msg := lerr.Message
	return containsFold(msg, "quota") || containsFold(msg, "exceed") || containsFold(msg, "limit")
}

func containsFold(s, substr string) bool {
	sl, subl := []rune(s), []rune(substr)
	toLower := func(rs []rune) []rune {
		out := make([]rune, len(rs))
		for i, r := range rs {
			if r >= 'A' && r <= 'Z' {
				r += 'a' - 'A'
			}
			out[i] = r
		}
		return out
	}
	sl, subl = toLower(sl), toLower(subl)
	for i := 0; i+len(subl) <= len(sl); i++ {
		if string(sl[i:i+len(subl)]) == string(subl) {
			return true
		}
	}
	return false
}

// loadFetchedIDs reads an existing output file (if any) and returns the set
// of bill ids already present, so a rerun can resume instead of re-fetching
// everything and burning API quota.
func loadFetchedIDs(path string) map[string]bool {
	ids := map[string]bool{}
	f, err := os.Open(path)
	if err != nil {
		return ids
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 1024*1024), 64*1024*1024)
	for scanner.Scan() {
		line := scanner.Bytes()
		if len(line) == 0 {
			continue
		}
		var r struct {
			ID string `json:"id"`
		}
		if err := json.Unmarshal(line, &r); err != nil {
			continue
		}
		if r.ID != "" {
			ids[r.ID] = true
		}
	}
	return ids
}

func envInt(key string, fallback int) int {
	v := os.Getenv(key)
	if v == "" {
		return fallback
	}
	var n int
	if _, err := fmt.Sscanf(v, "%d", &n); err != nil {
		return fallback
	}
	return n
}
