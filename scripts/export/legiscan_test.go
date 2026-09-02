package main

import "testing"

func TestEarliestTextPrefersDraftOverAnomalouslyEarlierChapteredDoc(t *testing.T) {
	// Reproduces the real HB0486 (114th GA) case: LegiScan's texts array
	// included a stray "Chaptered" document from a prior General Assembly
	// (dated 2023, before this session even started) alongside the bill's
	// real 2025 "Draft" text. Pure earliest-by-date would wrongly pick the
	// stray 2023 document.
	texts := []billText{
		{DocID: 3088013, Date: "2025-01-29", Type: "Draft"},
		{DocID: 3214625, Date: "2023-03-24", Type: "Chaptered"},
		{DocID: 3245997, Date: "2025-05-22", Type: "Chaptered"},
	}

	got, ok := earliestText(texts)
	if !ok {
		t.Fatal("expected a text document to be found")
	}
	if got.DocID != 3088013 {
		t.Errorf("expected the Draft doc (3088013) to be selected, got doc_id %d (type %s, date %s)", got.DocID, got.Type, got.Date)
	}
}

func TestEarliestTextFallsBackWhenNoDraftOrIntroducedExists(t *testing.T) {
	texts := []billText{
		{DocID: 200, Date: "2025-05-22", Type: "Chaptered"},
		{DocID: 100, Date: "2025-01-10", Type: "Engrossed"},
	}

	got, ok := earliestText(texts)
	if !ok {
		t.Fatal("expected a text document to be found")
	}
	if got.DocID != 100 {
		t.Errorf("expected the earliest-dated doc (100) as fallback, got doc_id %d", got.DocID)
	}
}

func TestEarliestTextTiesBreakOnLowestDocID(t *testing.T) {
	texts := []billText{
		{DocID: 50, Date: "2025-01-14", Type: "Draft"},
		{DocID: 20, Date: "2025-01-14", Type: "Draft"},
	}

	got, ok := earliestText(texts)
	if !ok {
		t.Fatal("expected a text document to be found")
	}
	if got.DocID != 20 {
		t.Errorf("expected the lowest doc_id (20) to win the tie, got doc_id %d", got.DocID)
	}
}

func TestEarliestTextEmpty(t *testing.T) {
	if _, ok := earliestText(nil); ok {
		t.Error("expected no text document to be found for an empty list")
	}
}
