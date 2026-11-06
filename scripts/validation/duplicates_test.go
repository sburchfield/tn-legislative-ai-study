package main

import "testing"

func TestExactDuplicateGroups(t *testing.T) {
	records := []CleanedRecord{
		{BillNumber: "HB0001", BillText: "identical text"},
		{BillNumber: "HB0002", BillText: "identical text"},
		{BillNumber: "HB0003", BillText: "different text"},
		{BillNumber: "HB0004", BillText: ""}, // empty text should never be grouped
		{BillNumber: "HB0005", BillText: ""},
	}
	groups := ExactDuplicateGroups(records)
	if len(groups) != 1 {
		t.Fatalf("expected exactly 1 duplicate group, got %d: %v", len(groups), groups)
	}
	for _, bns := range groups {
		if len(bns) != 2 {
			t.Errorf("expected 2 bill numbers in the duplicate group, got %v", bns)
		}
	}
}

func TestNearDuplicateGroups(t *testing.T) {
	// The fingerprint keys on the normalized start and end of the text
	// (plus a length bucket), so two texts sharing the same opening and
	// closing but differing only in the middle should collide.
	start := "SECTION 1. This is a moderately long bill about Tennessee Code Annotated, " +
		"Title 55, Chapter 8, Part 2, relative to motor vehicle registration and titling " +
		"procedures administered by the department of safety, and for related purposes, "
	end := " provided, however, that nothing in this section shall be construed to affect any " +
		"pending litigation, and this act takes effect upon becoming a law, the public " +
		"welfare requiring it, and applies to all counties in this state uniformly."
	variantA := start + "relative to motor vehicles and the department of safety" + end
	variantB := start + "relative to a completely different subject about licensing boards" + end

	records := []CleanedRecord{
		{BillNumber: "HB0001", BillText: variantA},
		{BillNumber: "HB0002", BillText: variantB},
		{BillNumber: "HB0003", BillText: "SECTION 1. A totally unrelated bill about education funding for schools."},
	}
	exact := ExactDuplicateGroups(records)
	if len(exact) != 0 {
		t.Fatalf("expected no exact duplicates in this fixture, got %v", exact)
	}
	near := NearDuplicateGroups(records, exact)
	found := false
	for _, bns := range near {
		if len(bns) == 2 {
			found = true
		}
	}
	if !found {
		t.Errorf("expected HB0001/HB0002 to be flagged as near-duplicate candidates, got groups: %v", near)
	}
}

func TestNearDuplicateGroupsExcludesExactDuplicates(t *testing.T) {
	records := []CleanedRecord{
		{BillNumber: "HB0001", BillText: "identical text"},
		{BillNumber: "HB0002", BillText: "identical text"},
	}
	exact := ExactDuplicateGroups(records)
	near := NearDuplicateGroups(records, exact)
	if len(near) != 0 {
		t.Errorf("expected exact duplicates to be excluded from near-duplicate groups, got %v", near)
	}
}
