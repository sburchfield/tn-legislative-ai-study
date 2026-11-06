// Command validation inspects the cleaned research dataset and reports
// data-quality findings. It never modifies data/raw or data/cleaned, and
// makes no network calls — it only reads the local JSONL files already
// produced by scripts/export and scripts/cleaning.
package main

// CleanedRecord mirrors the schema written by scripts/cleaning.
type CleanedRecord struct {
	ID                  string   `json:"id"`
	BillNumber          string   `json:"bill_number"`
	Title               string   `json:"title"`
	Description         string   `json:"description"`
	Sponsor             string   `json:"sponsor"`
	SponsorAsFiled      string   `json:"sponsor_as_filed"`
	Subjects            []string `json:"subjects"`
	CompanionBillNumber string   `json:"companion_bill_number"`
	TextSource          string   `json:"text_source"`
	BillText            string   `json:"bill_text"`
}

// RawRecord mirrors the schema written by scripts/export, used here only
// to cross-check a cleaned record's provenance (text_type, session) by id
// — a stronger signal than pattern-matching bill_text alone.
type RawRecord struct {
	ID          string `json:"id"`
	BillNumber  string `json:"bill_number"`
	Chamber     string `json:"chamber"`
	TextType    string `json:"text_type"`
	TextDate    string `json:"text_date"`
	SessionID   int    `json:"session_id"`
	SessionName string `json:"session_name"`
}

// Severity levels for a Finding, in the categories the study asked for.
type Severity string

const (
	SeverityError   Severity = "ERROR"
	SeverityWarning Severity = "WARNING"
)

// Finding is one reported issue, always tied to a specific record.
type Finding struct {
	Severity   Severity `json:"severity"`
	Category   string   `json:"category"`
	BillNumber string   `json:"bill_number"`
	ID         string   `json:"id,omitempty"`
	Message    string   `json:"message"`
}

// Report is the full machine-readable validation output.
type Report struct {
	GeneratedAt         string         `json:"generated_at"`
	ExpectedSessionID   int            `json:"expected_session_id"`
	ExpectedSessionName string         `json:"expected_session_name"`
	TotalRecords        int            `json:"total_records"`
	Counts              map[string]int `json:"counts"`
	Errors              []Finding      `json:"errors"`
	Warnings            []Finding      `json:"warnings"`
	Summary             Summary        `json:"summary"`
}

// Summary is the top-level PASS/WARNING/ERROR rollup the study asked for.
type Summary struct {
	TotalRecordsChecked          int    `json:"total_records_checked"`
	ErrorCount                   int    `json:"error_count"`
	WarningCount                 int    `json:"warning_count"`
	RecordsRequiringManualReview int    `json:"records_requiring_manual_review"`
	SafeToProceed                bool   `json:"safe_to_proceed"`
	Notes                        string `json:"notes"`
}
