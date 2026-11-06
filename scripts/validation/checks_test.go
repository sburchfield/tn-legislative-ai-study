package main

import "testing"

func TestTitleAppearsInText(t *testing.T) {
	cases := []struct {
		name     string
		title    string
		billText string
		want     bool
	}{
		{
			name:     "exact match",
			title:    "AN ACT to amend Tennessee Code Annotated, Title 49, relative to education.",
			billText: "HOUSE BILL 349\n\n By Hurt\n\n AN ACT to amend Tennessee Code Annotated, Title 49,\n relative to education.\n\nBE IT ENACTED...",
			want:     true,
		},
		{
			name:  "hyphenated citation line-wrap is not a false mismatch",
			title: "AN ACT to amend Tennessee Code Annotated, Section 3-2-112, relative to wildlife.",
			billText: "HOUSE BILL 422\n\n By Someone\n\n AN ACT to amend Tennessee Code Annotated, Section 3-\n" +
				" 2-112, relative to wildlife.\n\nBE IT ENACTED...",
			want: true,
		},
		{
			name:     "reproduces the real HB0486-style mismatch (wrong bill's content)",
			title:    "AN ACT to amend Tennessee Code Annotated, Title 8, Chapter 14, relative to district public defenders.",
			billText: "PUBLIC CHAPTER NO. 59\nHOUSE BILL NO. 486\n\nAN ACT to amend Tennessee Code Annotated, Title 2, Chapter 10, relative to campaign finance.",
			want:     false,
		},
		{
			name:     "empty title",
			title:    "",
			billText: "AN ACT to amend...",
			want:     false,
		},
		{
			name:     "empty bill text",
			title:    "AN ACT to amend...",
			billText: "",
			want:     false,
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := TitleAppearsInText(tc.title, tc.billText)
			if got != tc.want {
				t.Errorf("TitleAppearsInText() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestCheckRecordFlagsWrongDocumentType(t *testing.T) {
	rec := CleanedRecord{
		ID:             "1",
		BillNumber:     "HB0486",
		Title:          "AN ACT to amend Tennessee Code Annotated, Title 8, Chapter 14, relative to district public defenders.",
		Sponsor:        "Someone",
		SponsorAsFiled: "Someone",
		BillText:       "PUBLIC CHAPTER NO. 59\nHOUSE BILL NO. 486\n\nAN ACT to amend Tennessee Code Annotated, Title 2, Chapter 10, relative to campaign finance.",
	}
	var errors, warnings []Finding
	counts := map[string]int{}
	checkRecord(rec, RawRecord{}, false, 2161, "114th General Assembly", "114", DefaultMinBillTextLength, &errors, &warnings, counts)

	if counts["wrong_document_type"] == 0 {
		t.Error("expected wrong_document_type to be flagged for PUBLIC CHAPTER text")
	}
	if counts["title_text_mismatch"] == 0 {
		t.Error("expected title_text_mismatch to be flagged when title and text disagree")
	}
}

func TestCheckRecordCleanRecordProducesNoErrors(t *testing.T) {
	rec := CleanedRecord{
		ID:             "1",
		BillNumber:     "HB0349",
		Title:          "AN ACT to amend Tennessee Code Annotated, Title 49, relative to education.",
		Sponsor:        "William Slater",
		SponsorAsFiled: "Hurt",
		BillText: "HOUSE BILL 349\n\n By Hurt\n\n AN ACT to amend Tennessee Code Annotated, Title 49,\n" +
			" relative to education.\n\nBE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:\n\n" +
			" SECTION 1. Tennessee Code Annotated, Section 49-9-1410, is amended by deleting\n\nthe section.",
	}
	var errors, warnings []Finding
	counts := map[string]int{}
	checkRecord(rec, RawRecord{SessionID: 2161, SessionName: "114th General Assembly", TextType: "Draft"}, true, 2161, "114th General Assembly", "114", DefaultMinBillTextLength, &errors, &warnings, counts)

	if len(errors) != 0 {
		t.Errorf("expected no errors for a clean record, got: %+v", errors)
	}
	if counts["sponsor_differs_from_as_filed"] == 0 {
		t.Error("expected the known sponsor/as-filed caveat to be flagged as a warning")
	}
}
