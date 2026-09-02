package main

import "testing"

func TestParseAsFiledSponsor(t *testing.T) {
	cases := []struct {
		name       string
		billText   string
		billNumber string
		want       string
	}{
		{
			name:       "house bill, simple case",
			billText:   "HOUSE BILL 349\n\n By Hurt\n\n AN ACT to amend...",
			billNumber: "HB0349",
			want:       "Hurt",
		},
		{
			name:       "house bill with a senate companion header first",
			billText:   "SENATE BILL 328\n By Briggs\n\n HOUSE BILL 349\n\n By Hurt\n\n AN ACT to amend...",
			billNumber: "HB0349",
			want:       "Hurt",
		},
		{
			name:       "senate bill number targets the senate header",
			billText:   "SENATE BILL 328\n By Briggs\n\n HOUSE BILL 349\n\n By Hurt\n\n AN ACT to amend...",
			billNumber: "SB0328",
			want:       "Briggs",
		},
		{
			name:       "compound surname",
			billText:   "HOUSE BILL 528\n\n By Helton-Haynes\n\n AN ACT to amend...",
			billNumber: "HB0528",
			want:       "Helton-Haynes",
		},
		{
			name:       "multiple co-sponsors on the by-line",
			billText:   "HOUSE BILL 100\n\n By Smith, Jones\n\n AN ACT to amend...",
			billNumber: "HB0100",
			want:       "Smith, Jones",
		},
		{
			name:       "no match returns empty string",
			billText:   "some unrelated text with no header",
			billNumber: "HB0349",
			want:       "",
		},
		{
			name:       "unrecognized bill number prefix returns empty string",
			billText:   "HOUSE BILL 349\n By Hurt",
			billNumber: "HJR0001",
			want:       "",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := ParseAsFiledSponsor(tc.billText, tc.billNumber)
			if got != tc.want {
				t.Errorf("ParseAsFiledSponsor(%q, %q) = %q, want %q", tc.billText, tc.billNumber, got, tc.want)
			}
		})
	}
}

func TestSponsorMatches(t *testing.T) {
	cases := []struct {
		current, asFiled string
		want             bool
	}{
		{"William Slater", "Hurt", false},
		{"William Slater", "Slater", true},
		{"Michele Reneau", "Wright", false},
		{"", "Hurt", false},
		{"William Slater", "", false},
	}
	for _, tc := range cases {
		got := sponsorMatches(tc.current, tc.asFiled)
		if got != tc.want {
			t.Errorf("sponsorMatches(%q, %q) = %v, want %v", tc.current, tc.asFiled, got, tc.want)
		}
	}
}
