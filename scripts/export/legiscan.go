package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

const legiscanBaseURL = "https://api.legiscan.com/"

// legiscanClient is a minimal, read-only client for the parts of the
// LegiScan API this export needs: enumerating a session's bills and
// fetching each bill's detail and text documents.
type legiscanClient struct {
	apiKey     string
	httpClient *http.Client
}

func newLegiscanClient(apiKey string) *legiscanClient {
	return &legiscanClient{
		apiKey:     apiKey,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

type legiscanAlert struct {
	Message string `json:"message"`
}

// legiscanError is returned when the API responds with status "ERROR".
type legiscanError struct {
	Message string
}

func (e *legiscanError) Error() string {
	return fmt.Sprintf("legiscan API error: %s", e.Message)
}

func (c *legiscanClient) get(op string, params url.Values, out interface{}) error {
	q := url.Values{}
	q.Set("key", c.apiKey)
	q.Set("op", op)
	for k, v := range params {
		q[k] = v
	}

	resp, err := c.httpClient.Get(legiscanBaseURL + "?" + q.Encode())
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected HTTP status %d: %s", resp.StatusCode, string(body))
	}

	// Peek at the status/alert fields before unmarshaling into the
	// caller's specific shape, so API-level errors are reported clearly.
	var envelope struct {
		Status string         `json:"status"`
		Alert  *legiscanAlert `json:"alert"`
	}
	if err := json.Unmarshal(body, &envelope); err != nil {
		return fmt.Errorf("failed to parse response envelope: %w", err)
	}
	if envelope.Status == "ERROR" {
		msg := "unknown error"
		if envelope.Alert != nil && envelope.Alert.Message != "" {
			msg = envelope.Alert.Message
		}
		return &legiscanError{Message: msg}
	}

	if err := json.Unmarshal(body, out); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}
	return nil
}

type masterListEntry struct {
	BillID     int    `json:"bill_id"`
	Number     string `json:"number"`
	ChangeHash string `json:"change_hash"`
}

// getMasterList returns every bill entry for the given session id.
func (c *legiscanClient) getMasterList(sessionID int) ([]masterListEntry, error) {
	var raw struct {
		MasterList map[string]json.RawMessage `json:"masterlist"`
	}
	if err := c.get("getMasterList", url.Values{"id": {fmt.Sprint(sessionID)}}, &raw); err != nil {
		return nil, err
	}

	var entries []masterListEntry
	for key, v := range raw.MasterList {
		if key == "session" {
			continue
		}
		var e masterListEntry
		if err := json.Unmarshal(v, &e); err != nil {
			continue
		}
		entries = append(entries, e)
	}
	return entries, nil
}

type billSponsor struct {
	Name          string `json:"name"`
	SponsorOrder  int    `json:"sponsor_order"`
	SponsorTypeID int    `json:"sponsor_type_id"`
}

type billSubject struct {
	SubjectName string `json:"subject_name"`
}

type billSast struct {
	Type           string `json:"type"`
	SastBillNumber string `json:"sast_bill_number"`
	SastBillID     int    `json:"sast_bill_id"`
}

type billText struct {
	DocID int    `json:"doc_id"`
	Date  string `json:"date"`
	Type  string `json:"type"`
	Mime  string `json:"mime"`
}

type billDetail struct {
	BillID      int    `json:"bill_id"`
	BillNumber  string `json:"bill_number"`
	Body        string `json:"body"`
	Title       string `json:"title"`
	Description string `json:"description"`
	ChangeHash  string `json:"change_hash"`
	SessionID   int    `json:"session_id"`
	Session     struct {
		SessionName string `json:"session_name"`
	} `json:"session"`
	URL       string        `json:"url"`
	StateLink string        `json:"state_link"`
	Sponsors  []billSponsor `json:"sponsors"`
	Subjects  []billSubject `json:"subjects"`
	Sasts     []billSast    `json:"sasts"`
	Texts     []billText    `json:"texts"`
}

// getBill fetches full detail for a single bill.
func (c *legiscanClient) getBill(billID int) (*billDetail, error) {
	var raw struct {
		Bill billDetail `json:"bill"`
	}
	if err := c.get("getBill", url.Values{"id": {fmt.Sprint(billID)}}, &raw); err != nil {
		return nil, err
	}
	return &raw.Bill, nil
}

type billTextDoc struct {
	DocID int    `json:"doc_id"`
	Mime  string `json:"mime"`
	Doc   string `json:"doc"` // base64-encoded document content
}

// getBillText fetches the base64-encoded document content for a text doc_id.
func (c *legiscanClient) getBillText(docID int) (*billTextDoc, error) {
	var raw struct {
		Text billTextDoc `json:"text"`
	}
	if err := c.get("getBillText", url.Values{"id": {fmt.Sprint(docID)}}, &raw); err != nil {
		return nil, err
	}
	return &raw.Text, nil
}

// primarySponsor picks the lead sponsor's name, preferring sponsor_type_id 1
// (primary) with the lowest sponsor_order, falling back to the first listed
// sponsor if no primary is marked.
func primarySponsor(sponsors []billSponsor) string {
	if len(sponsors) == 0 {
		return ""
	}
	best := sponsors[0]
	bestIsPrimary := best.SponsorTypeID == 1
	for _, s := range sponsors[1:] {
		isPrimary := s.SponsorTypeID == 1
		switch {
		case isPrimary && !bestIsPrimary:
			best, bestIsPrimary = s, true
		case isPrimary == bestIsPrimary && s.SponsorOrder < best.SponsorOrder:
			best = s
		}
	}
	return best.Name
}

// subjectNames extracts subject name strings, or nil if there are none.
func subjectNames(subjects []billSubject) []string {
	if len(subjects) == 0 {
		return nil
	}
	names := make([]string, 0, len(subjects))
	for _, s := range subjects {
		names = append(names, s.SubjectName)
	}
	return names
}

// companionBillNumber picks the companion ("Same As/Similar To") bill
// number, preferring an explicit "Crossfiled" relationship (the standard TN
// House/Senate companion-bill link) and otherwise falling back to the first
// listed relationship.
func companionBillNumber(sasts []billSast) string {
	if len(sasts) == 0 {
		return ""
	}
	for _, s := range sasts {
		if s.Type == "Crossfiled" {
			return s.SastBillNumber
		}
	}
	return sasts[0].SastBillNumber
}

// preferredTextTypes lists the LegiScan text types that represent a bill's
// original, as-filed/as-introduced language, in preference order. TN
// almost always uses "Draft" for this; "Introduced" covers the terminology
// LegiScan uses for some other states. Any other type (e.g. "Chaptered",
// "Engrossed", "Enrolled") is a later, amended, or enacted version.
var preferredTextTypes = []string{"Draft", "Introduced"}

// earliestText picks the text document corresponding to the bill's
// original, as-filed/as-introduced language, preferring an explicit
// "Draft"/"Introduced" type match over pure earliest-by-date. This matters
// because LegiScan's own data has been observed to occasionally list a
// stray, misattached document from a *different* bill/session under a
// bill's texts array with an anomalously early date (e.g. a prior General
// Assembly's enacted "Chaptered" text, since TN bill numbers are reused
// each session) — picking the earliest date unconditionally can then
// silently select the wrong bill's text entirely. Within the preferred
// type, ties break on the lowest doc_id for determinism. If no
// Draft/Introduced document exists at all, this falls back to the
// earliest-dated document overall, accepting that residual risk as a rare
// last resort.
func earliestText(texts []billText) (billText, bool) {
	if len(texts) == 0 {
		return billText{}, false
	}

	for _, preferredType := range preferredTextTypes {
		var best billText
		found := false
		for _, t := range texts {
			if t.Type != preferredType {
				continue
			}
			if !found || t.Date < best.Date || (t.Date == best.Date && t.DocID < best.DocID) {
				best, found = t, true
			}
		}
		if found {
			return best, true
		}
	}

	best := texts[0]
	for _, t := range texts[1:] {
		if t.Date < best.Date || (t.Date == best.Date && t.DocID < best.DocID) {
			best = t
		}
	}
	return best, true
}
