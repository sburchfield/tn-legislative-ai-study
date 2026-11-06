package main

import "testing"

func TestFindAsFiledSponsorInText(t *testing.T) {
	cases := []struct {
		name       string
		billText   string
		billNumber string
		wantName   string
		wantOK     bool
	}{
		{
			name:       "reproduces the real HB0349 case",
			billText:   "HOUSE BILL 349\n\n By Hurt\n\n AN ACT to amend Tennessee Code Annotated, Title 49...",
			billNumber: "HB0349",
			wantName:   "Hurt",
			wantOK:     true,
		},
		{
			name:       "senate companion header ignored when targeting a house bill",
			billText:   "SENATE BILL 328\n By Briggs\n\n HOUSE BILL 349\n\n By Hurt\n\n AN ACT...",
			billNumber: "HB0349",
			wantName:   "Hurt",
			wantOK:     true,
		},
		{
			name:       "no by-line at all",
			billText:   "SECTION 1. Tennessee Code Annotated is amended.",
			billNumber: "HB0349",
			wantName:   "",
			wantOK:     false,
		},
		{
			name:       "senate bill number is out of scope for this function",
			billText:   "SENATE BILL 328\n By Briggs\n\n AN ACT...",
			billNumber: "SB0328",
			wantName:   "",
			wantOK:     false,
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			gotName, gotOK := FindAsFiledSponsorInText(tc.billText, tc.billNumber)
			if gotName != tc.wantName || gotOK != tc.wantOK {
				t.Errorf("FindAsFiledSponsorInText() = (%q, %v), want (%q, %v)", gotName, gotOK, tc.wantName, tc.wantOK)
			}
		})
	}
}

func TestSponsorNamesMatch(t *testing.T) {
	cases := []struct {
		current, asFiled string
		want             bool
	}{
		// Reproduces the real HB0349 case: sponsor changed after filing.
		{"William Slater", "Hurt", false},
		{"William Slater", "Slater", true},
		{"Michele Reneau", "Wright", false},
		{"", "Hurt", false},
		{"William Slater", "", false},
	}
	for _, tc := range cases {
		got := SponsorNamesMatch(tc.current, tc.asFiled)
		if got != tc.want {
			t.Errorf("SponsorNamesMatch(%q, %q) = %v, want %v", tc.current, tc.asFiled, got, tc.want)
		}
	}
}
