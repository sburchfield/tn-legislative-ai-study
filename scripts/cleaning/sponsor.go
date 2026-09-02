package main

import (
	"regexp"
	"strconv"
	"strings"
)

// ParseAsFiledSponsor extracts the sponsor name as actually printed on the
// bill's own text (e.g. "By Hurt" following "HOUSE BILL 349"), as opposed
// to a bill's current sponsor of record. These can differ: TN allows a
// bill's prime sponsor to change after filing (a "Sponsor change" bill
// history event), but the as-filed document text is frozen at introduction
// and keeps showing whoever filed it. billNumber identifies which
// chamber's heading to look for ("HB..." -> "HOUSE BILL N", "SB..." ->
// "SENATE BILL N") and anchors the match to the specific bill number, so
// a companion's header appearing earlier in the same text isn't matched
// instead. Returns "" if no match is found.
func ParseAsFiledSponsor(billText, billNumber string) string {
	var prefix, numStr string
	switch {
	case strings.HasPrefix(billNumber, "HB"):
		prefix, numStr = "HOUSE BILL", strings.TrimPrefix(billNumber, "HB")
	case strings.HasPrefix(billNumber, "SB"):
		prefix, numStr = "SENATE BILL", strings.TrimPrefix(billNumber, "SB")
	default:
		return ""
	}

	n, err := strconv.Atoi(numStr)
	if err != nil {
		return ""
	}

	re := regexp.MustCompile(`(?m)^\s*` + prefix + `\s+0*` + strconv.Itoa(n) + `\s*\n+\s*By\s+(.+?)\s*$`)
	m := re.FindStringSubmatch(billText)
	if len(m) < 2 {
		return ""
	}
	return strings.TrimSpace(m[1])
}
