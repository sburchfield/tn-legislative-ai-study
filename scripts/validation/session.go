package main

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

// gaOrdinalRe matches a "General Assembly" ordinal mention, e.g.
// "114th General Assembly" or "113th General Assembly".
var gaOrdinalRe = regexp.MustCompile(`(\d+)(?:st|nd|rd|th)\s+General Assembly`)

// publicChapterRe matches the "PUBLIC CHAPTER" marker that appears on
// enacted/chaptered bill text, as opposed to introduced/draft text. This
// is exactly the marker that identified the HB0486 stray-document bug.
var publicChapterRe = regexp.MustCompile(`(?i)PUBLIC CHAPTER`)

// otherStateRe matches a "State of X" / "Commonwealth of X" reference to
// another U.S. state. This alone is not a reliable contamination signal —
// TN bills legitimately cite other states' programs as policy
// justification (e.g. "the state of Alabama operates a successful
// outcomes-based program") — so callers should use
// FindOtherStateMentionBeforeOwnHeader, which only treats this as an error
// when it appears before the bill's own header (see HouseBillHeaderIndex).
var otherStateRe = regexp.MustCompile(
	`(?i)(?:State|Commonwealth) of (` + strings.Join(otherStateNames, "|") + `)`,
)

// otherStateNames lists U.S. state names other than Tennessee. TN bill
// text should never legitimately reference another state's government by
// name in this way; seeing one is a strong signal that the wrong
// document ended up attached to a bill (as happened with a stray
// out-of-state document in the abandoned DynamoDB pipeline).
var otherStateNames = []string{
	"Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
	"Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
	"Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
	"Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
	"Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
	"New Hampshire", "New Jersey", "New Mexico", "New York",
	"North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
	"Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
	"Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
	"Wisconsin", "Wyoming",
}

// GeneralAssemblyMentions returns every distinct "Nth General Assembly"
// ordinal mentioned in text (e.g. ["114", "113"]).
func GeneralAssemblyMentions(text string) []string {
	matches := gaOrdinalRe.FindAllStringSubmatch(text, -1)
	seen := map[string]bool{}
	var out []string
	for _, m := range matches {
		if !seen[m[1]] {
			seen[m[1]] = true
			out = append(out, m[1])
		}
	}
	return out
}

// WrongGeneralAssemblyMentions returns any General-Assembly-ordinal
// mentions in text that do not match expectedOrdinal (e.g. "114"). Note
// this includes legitimate historical citations (e.g. a bill's WHEREAS
// clause noting "the 113th General Assembly enacted Public Chapter 621");
// checkRecord only escalates this to an ERROR when the mention appears
// before the bill's own header (see WrongGeneralAssemblyMentionsBeforeOwnHeader).
func WrongGeneralAssemblyMentions(text, expectedOrdinal string) []string {
	var wrong []string
	for _, ord := range GeneralAssemblyMentions(text) {
		if ord != expectedOrdinal {
			wrong = append(wrong, ord)
		}
	}
	return wrong
}

// ContainsPublicChapterMarker reports whether text contains a "PUBLIC
// CHAPTER" marker anywhere. Like WrongGeneralAssemblyMentions, this alone
// includes legitimate historical citations; see PublicChapterBeforeOwnHeader
// for the position-aware, ERROR-worthy version.
func ContainsPublicChapterMarker(text string) bool {
	return publicChapterRe.MatchString(text)
}

// HouseBillHeaderIndex returns the byte offset of this bill's own
// self-identification header (e.g. "HOUSE BILL 486" or "HOUSE BILL NO.
// 486") in text, or -1 if it isn't found. billNumber must be an "HB..."
// number. Every correctly-selected as-filed House bill document in the
// 114th GA corpus contains this header near the very top; a legitimate
// historical citation of an unrelated Public Chapter or General Assembly
// always appears *after* it (inside a WHEREAS clause), while the HB0486
// stray-document bug had the wrong chapter's header appear *before* it.
func HouseBillHeaderIndex(text, billNumber string) int {
	if !strings.HasPrefix(billNumber, "HB") {
		return -1
	}
	n, err := strconv.Atoi(strings.TrimPrefix(billNumber, "HB"))
	if err != nil {
		return -1
	}
	re := regexp.MustCompile(`(?i)HOUSE BILL\s+(?:NO\.\s*)?0*` + strconv.Itoa(n) + `\b`)
	loc := re.FindStringIndex(text)
	if loc == nil {
		return -1
	}
	return loc[0]
}

// PublicChapterBeforeOwnHeader reports whether a "PUBLIC CHAPTER" marker
// appears before this bill's own header — the pattern seen in the real
// HB0486 stray-document bug — as opposed to later in the text as a
// historical citation of prior law, which is normal and not an error. If
// the bill's own header can't be found at all, any PUBLIC CHAPTER mention
// is treated as suspicious (conservative fallback).
func PublicChapterBeforeOwnHeader(text, billNumber string) bool {
	loc := publicChapterRe.FindStringIndex(text)
	if loc == nil {
		return false
	}
	headerIdx := HouseBillHeaderIndex(text, billNumber)
	return headerIdx == -1 || loc[0] < headerIdx
}

// WrongGeneralAssemblyMentionsBeforeOwnHeader is like
// WrongGeneralAssemblyMentions, but only returns mentions that appear
// before this bill's own header — i.e. actually describing *this*
// document, not a historical citation elsewhere in the body text.
func WrongGeneralAssemblyMentionsBeforeOwnHeader(text, billNumber, expectedOrdinal string) []string {
	headerIdx := HouseBillHeaderIndex(text, billNumber)
	var wrong []string
	for _, m := range gaOrdinalRe.FindAllStringSubmatchIndex(text, -1) {
		ord := text[m[2]:m[3]]
		if ord == expectedOrdinal {
			continue
		}
		if headerIdx == -1 || m[0] < headerIdx {
			wrong = append(wrong, ord)
		}
	}
	return wrong
}

// FindOtherStateMentionBeforeOwnHeader returns the canonical name of the
// first "State of X"/"Commonwealth of X" reference to another U.S. state
// that appears *before* this bill's own header (see HouseBillHeaderIndex),
// or "" if there is none. A real bill's own header is always its first
// substantive content, so a wrong-state reference appearing before it is a
// strong contamination signal (this is exactly how the abandoned DynamoDB
// pipeline's cross-jurisdiction bug presented — e.g. a Kentucky or New
// York document's own header preceding, or replacing, the TN bill's). A
// mention appearing later, in the bill's own body text, is ordinary
// narrative citation (e.g. "the state of Alabama operates a program...")
// and is not flagged by this function.
func FindOtherStateMentionBeforeOwnHeader(text, billNumber string) string {
	m := otherStateRe.FindStringSubmatchIndex(text)
	if m == nil {
		return ""
	}
	headerIdx := HouseBillHeaderIndex(text, billNumber)
	if headerIdx != -1 && m[0] >= headerIdx {
		return ""
	}
	matched := strings.ToLower(text[m[2]:m[3]])
	for _, name := range otherStateNames {
		if strings.ToLower(name) == matched {
			return name
		}
	}
	return text[m[2]:m[3]]
}

// FindOtherStateMention returns the canonical name of the first "State of
// X"/"Commonwealth of X" reference to another U.S. state anywhere in text,
// or "" if none is found. Unlike FindOtherStateMentionBeforeOwnHeader,
// this includes ordinary narrative citations and so is only suitable for
// an informational, non-error signal.
func FindOtherStateMention(text string) string {
	m := otherStateRe.FindStringSubmatch(text)
	if len(m) < 2 {
		return ""
	}
	matched := strings.ToLower(m[1])
	for _, name := range otherStateNames {
		if strings.ToLower(name) == matched {
			return name
		}
	}
	return m[1]
}

// CrossCheckRawProvenance compares a raw record's own recorded session/text
// type against the expected session, returning a human-readable reason if
// something doesn't match, or "" if it looks correct.
func CrossCheckRawProvenance(raw RawRecord, expectedSessionID int, expectedSessionName string) string {
	if raw.SessionID != 0 && raw.SessionID != expectedSessionID {
		return fmt.Sprintf("raw record's session_id %d does not match expected %d (%s)", raw.SessionID, expectedSessionID, expectedSessionName)
	}
	if raw.SessionName != "" && raw.SessionName != expectedSessionName {
		return fmt.Sprintf("raw record's session_name %q does not match expected %q", raw.SessionName, expectedSessionName)
	}
	if raw.TextType != "" && raw.TextType != "Draft" && raw.TextType != "Introduced" {
		return fmt.Sprintf("raw record's selected text_type is %q, not Draft/Introduced", raw.TextType)
	}
	return ""
}
