package main

import (
	"strings"
	"testing"
)

func TestNormalizeBillText(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{
			name: "plain text is unchanged",
			in:   "This bill amends Tennessee Code Annotated, Title 55.",
			want: "This bill amends Tennessee Code Annotated, Title 55.",
		},
		{
			name: "html paragraphs become line breaks",
			in:   "<p>Section 1.</p><p>Section 2.</p>",
			want: "Section 1.\nSection 2.",
		},
		{
			name: "html entities are decoded",
			in:   "Fees &amp; charges shall not exceed &#36;100.",
			want: "Fees & charges shall not exceed $100.",
		},
		{
			name: "style tags and their content are removed",
			in:   "<style>body { color: red; }</style><p>Section 1.</p>",
			want: "Section 1.",
		},
		{
			name: "script tags and their content are removed",
			in:   "<script>alert('x')</script>Section 1.",
			want: "Section 1.",
		},
		{
			name: "multiple whitespace characters collapse to one space",
			in:   "Section    1.     Be it enacted.",
			want: "Section 1. Be it enacted.",
		},
		{
			name: "line breaks and CRLF are normalized",
			in:   "Section 1.\r\n\r\n\r\nSection 2.\rSection 3.",
			want: "Section 1.\n\nSection 2.\nSection 3.",
		},
		{
			name: "legislative punctuation and numbers are preserved",
			in:   "SECTION 1. Tennessee Code Annotated, Section 55-8-101(a)(1), is amended by deleting subdivision (a)(1).",
			want: "SECTION 1. Tennessee Code Annotated, Section 55-8-101(a)(1), is amended by deleting subdivision (a)(1).",
		},
		{
			name: "malformed html is stripped without losing surrounding text",
			in:   "Section 1 <div class=\"foo\" >is amended<br>as follows:",
			want: "Section 1 is amended\nas follows:",
		},
		{
			name: "empty string stays empty",
			in:   "",
			want: "",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := NormalizeBillText(tc.in)
			if got != tc.want {
				t.Errorf("NormalizeBillText(%q)\n  got:  %q\n  want: %q", tc.in, got, tc.want)
			}
		})
	}
}

// TestNormalizeBillTextPreservesSubstance is a broader guard against the
// normalization function accidentally removing legislative content: every
// alphanumeric token present in a realistic bill excerpt (ignoring markup)
// must still be present in the normalized output.
func TestNormalizeBillTextPreservesSubstance(t *testing.T) {
	in := `<html><head><style>.x{color:#fff}</style></head><body>
<p>SECTION 1.&nbsp;Tennessee Code Annotated, Title 39, Chapter 17, Part 4, is amended
by adding the following as a new section:</p>
<p>(a)&nbsp;A person commits an offense who knowingly violates &sect; 39-17-417.</p>
<p>(b)&nbsp;A violation of this section is a Class A misdemeanor.</p>
</body></html>`

	got := NormalizeBillText(in)

	tokens := []string{
		"SECTION", "1.", "Tennessee", "Code", "Annotated,", "Title", "39,",
		"Chapter", "17,", "Part", "4,", "amended", "adding", "following",
		"new", "section:", "(a)", "person", "commits", "offense", "knowingly",
		"violates", "39-17-417.", "(b)", "violation", "this", "section",
		"Class", "misdemeanor.",
	}

	for _, tok := range tokens {
		if !strings.Contains(got, tok) {
			t.Errorf("expected normalized output to contain %q, got: %q", tok, got)
		}
	}

	if strings.Contains(got, "<") || strings.Contains(got, ">") {
		t.Errorf("expected all HTML tags to be removed, got: %q", got)
	}
	if strings.Contains(got, "color:#fff") {
		t.Errorf("expected style block content to be removed, got: %q", got)
	}
}

func TestNormalizeBillTextIsIdempotent(t *testing.T) {
	in := "<p>Section 1.</p>   Extra   spaces.\r\n\r\n\r\nMore text."
	once := NormalizeBillText(in)
	twice := NormalizeBillText(once)
	if once != twice {
		t.Errorf("expected normalization to be idempotent:\n  once:  %q\n  twice: %q", once, twice)
	}
}

// TestNormalizeBillTextRemovesUnfilledMailMergePlaceholders documents a
// real artifact observed in LegiScan/TN capitol.tn.gov "Draft" PDFs: when a
// bill's companion hasn't been assigned a sponsor yet at draft time, the
// document template leaves a literal "<BillNo> <Sponsor>" placeholder
// instead of real text. This is removed as a side effect of general
// tag-shaped-bracket stripping (the same mechanism that strips real HTML
// tags from the older HTML-sourced data), which is correct here since the
// placeholder is a document-generation artifact, not legislative content.
func TestNormalizeBillTextRemovesUnfilledMailMergePlaceholders(t *testing.T) {
	in := "<BillNo> <Sponsor>\n\n\nHOUSE BILL 1007\n\nBy Hicks\n\nAN ACT to amend Tennessee Code Annotated."
	got := NormalizeBillText(in)
	if strings.Contains(got, "<BillNo>") || strings.Contains(got, "<Sponsor>") {
		t.Errorf("expected unfilled mail-merge placeholder to be removed, got: %q", got)
	}
	for _, tok := range []string{"HOUSE BILL 1007", "By Hicks", "AN ACT to amend Tennessee Code Annotated."} {
		if !strings.Contains(got, tok) {
			t.Errorf("expected real content %q to be preserved, got: %q", tok, got)
		}
	}
}

func TestStripPDFRunningFooters(t *testing.T) {
	cases := []struct {
		name       string
		in         string
		billNumber string
		want       string
	}{
		{
			name: "separate-line footer block is removed",
			in: "SECTION 1. Some text continues.\n\n\n" +
				"                                              SB0431\n" +
				"                                              001315\n" +
				"                                               -1-\n" +
				"deleting the language and substituting instead.",
			billNumber: "SB0431",
			want: "SECTION 1. Some text continues.\n\n\n" +
				"deleting the language and substituting instead.",
		},
		{
			name:       "page number and control number combined on one line",
			in:         "some text\n                                        -2-                                        000208\nmore text",
			billNumber: "HB0001",
			want:       "some text\nmore text",
		},
		{
			name:       "double-digit page number with spaced dashes",
			in:         "some text\n                                              - 10 -                                    000208\nmore text",
			billNumber: "HB0001",
			want:       "some text\nmore text",
		},
		{
			name:       "unrelated bill number is not stripped",
			in:         "some text\nHB0002\nmore text",
			billNumber: "HB0001",
			want:       "some text\nHB0002\nmore text",
		},
		{
			name:       "a real code citation is not mistaken for a footer",
			in:         "Tennessee Code Annotated, Section 67-5-603(a)(1), is amended.",
			billNumber: "SB0431",
			want:       "Tennessee Code Annotated, Section 67-5-603(a)(1), is amended.",
		},
		{
			name:       "a real 4-8 digit number embedded in a sentence is not stripped",
			in:         "the department must award a maximum of 20000 scholarships this year",
			billNumber: "HB0001",
			want:       "the department must award a maximum of 20000 scholarships this year",
		},
		{
			name:       "empty bill number is a no-op",
			in:         "some text\nHB0001\nmore text",
			billNumber: "",
			want:       "some text\nHB0001\nmore text",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := StripPDFRunningFooters(tc.in, tc.billNumber)
			if got != tc.want {
				t.Errorf("StripPDFRunningFooters(%q, %q)\n  got:  %q\n  want: %q", tc.in, tc.billNumber, got, tc.want)
			}
		})
	}
}

func TestCleanBillTextPipelineOnRealisticPDFExtract(t *testing.T) {
	in := "                                                                         SENATE BILL 1\n" +
		"                                                                           By Johnson\n\n\n" +
		"                                            HOUSE BILL 1\n\n" +
		"                                             By Lamberth\n\n\n" +
		"                                         AN ACT to amend Tennessee Code Annotated, Title 4,\n" +
		"SECTION 1. This act is known and may be cited as the \"Education Freedom Act of 2025.\"\n\n\n" +
		"                                                HB0001\n" +
		"                                                000208\n" +
		"                                                 -1-\n" +
		"49-6-3501. Short title.\n"

	stripped := StripPDFRunningFooters(in, "HB0001")
	got := NormalizeBillText(stripped)

	for _, tok := range []string{"SENATE BILL 1", "HOUSE BILL 1", "By Johnson", "By Lamberth",
		"AN ACT to amend Tennessee Code Annotated, Title 4,",
		"SECTION 1. This act is known and may be cited as the \"Education Freedom Act of 2025.\"",
		"49-6-3501. Short title."} {
		if !strings.Contains(got, tok) {
			t.Errorf("expected cleaned text to contain %q, got: %q", tok, got)
		}
	}
	for _, tok := range []string{"000208", "-1-"} {
		if strings.Contains(got, tok) {
			t.Errorf("expected page-footer artifact %q to be removed, got: %q", tok, got)
		}
	}
}
