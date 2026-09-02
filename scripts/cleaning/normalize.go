package main

import (
	"html"
	"regexp"
	"strings"
)

// scriptStyleRe matches <script>...</script> and <style>...</style> blocks,
// including their content, case-insensitively, across newlines.
var scriptStyleRe = regexp.MustCompile(`(?is)<(script|style)\b[^>]*>.*?</(script|style)>`)

// tagRe matches any HTML/XML tag.
var tagRe = regexp.MustCompile(`(?s)<[^>]+>`)

// commentRe matches HTML comments, including MS Word/Office conditional comments.
var commentRe = regexp.MustCompile(`(?s)<!--.*?-->`)

// controlCharRe matches non-printable control characters other than
// tab (\t), newline (\n), and carriage return (\r), which are handled
// separately during line-ending/whitespace normalization.
var controlCharRe = regexp.MustCompile(`[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]`)

// blankLinesRe collapses 3+ consecutive newlines down to a single blank line.
var blankLinesRe = regexp.MustCompile(`\n{3,}`)

// spacesTabsRe collapses runs of horizontal whitespace (spaces/tabs) into one space.
var spacesTabsRe = regexp.MustCompile(`[ \t]+`)

// trailingSpaceRe strips trailing horizontal whitespace at the end of a line.
var trailingSpaceRe = regexp.MustCompile(`(?m)[ \t]+$`)

// pdfControlNumberPattern matches the 4-8 digit internal document/control
// number poppler's pdftotext places in the page footer of TN bill PDFs
// (e.g. "001315"). pdfPageNumberPattern matches the dashed page number
// (e.g. "-1-", "- 10 -") that appears alongside it.
const (
	pdfControlNumberPattern = `\d{4,8}`
	pdfPageNumberPattern    = `-\s?\d{1,3}\s?-`
)

// StripPDFRunningFooters removes the repeated per-page header/footer block
// that poppler's pdftotext carries over from the official TN bill PDFs:
// the bill's own number, an internal control number, and a dashed page
// number, each appearing alone on a line (or combined on one line,
// depending on how pdftotext judged the PDF's column layout on a given
// page). These are pagination artifacts, not legislative text, so they are
// removed; every other line is preserved untouched. billNumber anchors the
// match to this specific bill (e.g. "SB0431") to avoid any risk of
// mistaking substantive content elsewhere in the bill for a footer.
func StripPDFRunningFooters(text string, billNumber string) string {
	if text == "" || billNumber == "" {
		return text
	}

	text = strings.ReplaceAll(text, "\r\n", "\n")
	text = strings.ReplaceAll(text, "\r", "\n")

	billNum := regexp.QuoteMeta(strings.TrimSpace(billNumber))
	footerLineRe := regexp.MustCompile(`(?i)^(` +
		billNum + `|` +
		pdfControlNumberPattern + `|` +
		pdfPageNumberPattern + `|` +
		pdfPageNumberPattern + `\s+` + pdfControlNumberPattern + `|` +
		pdfControlNumberPattern + `\s+` + pdfPageNumberPattern +
		`)$`)

	lines := strings.Split(text, "\n")
	kept := make([]string, 0, len(lines))
	for _, line := range lines {
		if footerLineRe.MatchString(strings.TrimSpace(line)) {
			continue
		}
		kept = append(kept, line)
	}
	return strings.Join(kept, "\n")
}

// NormalizeBillText conservatively cleans formatting artifacts out of raw
// legislative source text without altering its substantive content.
//
// It removes HTML tags, style/script blocks, HTML comments, and decodes
// HTML entities; normalizes line endings and collapses excessive
// whitespace. It intentionally does NOT reword, summarize, paraphrase, or
// otherwise alter the legislative language itself. When in doubt, content
// is preserved rather than removed.
func NormalizeBillText(s string) string {
	if s == "" {
		return s
	}

	// Normalize line endings first so downstream regexes only deal with \n.
	s = strings.ReplaceAll(s, "\r\n", "\n")
	s = strings.ReplaceAll(s, "\r", "\n")

	// Remove script/style blocks (and their content) before stripping tags,
	// since their content is not part of the document text.
	s = scriptStyleRe.ReplaceAllString(s, "")

	// Remove HTML comments.
	s = commentRe.ReplaceAllString(s, "")

	// Strip remaining HTML/XML tags, replacing block-level tags with a
	// newline so paragraph/line structure is preserved rather than words
	// being smashed together.
	s = strings.NewReplacer(
		"<br>", "\n", "<br/>", "\n", "<br />", "\n",
		"<BR>", "\n", "<BR/>", "\n", "<BR />", "\n",
		"</p>", "\n", "</P>", "\n",
		"</div>", "\n", "</DIV>", "\n",
	).Replace(s)
	s = tagRe.ReplaceAllString(s, "")

	// Decode HTML entities (e.g. &amp;, &nbsp;, &#167;) after tags are
	// removed, so entities that were inside attributes don't leak into text.
	s = html.UnescapeString(s)

	// Remove non-printable control/formatting artifacts left over from
	// document conversion, while preserving tab/newline/carriage-return.
	s = controlCharRe.ReplaceAllString(s, "")

	// Non-breaking spaces and similar artifacts normalize to a regular space.
	s = strings.ReplaceAll(s, "\u00a0", " ")
	s = strings.ReplaceAll(s, "\ufeff", "") // BOM

	// Collapse excessive horizontal whitespace and trailing line whitespace.
	s = spacesTabsRe.ReplaceAllString(s, " ")
	s = trailingSpaceRe.ReplaceAllString(s, "")

	// Collapse 3+ blank lines down to a single blank line.
	s = blankLinesRe.ReplaceAllString(s, "\n\n")

	// Trim leading/trailing whitespace from the whole document.
	s = strings.TrimSpace(s)

	return s
}
