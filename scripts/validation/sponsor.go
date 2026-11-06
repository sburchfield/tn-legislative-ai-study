package main

import (
	"regexp"
	"strconv"
	"strings"
)

// asFiledSponsorRe matches the "By [Name]" line following a "HOUSE BILL N"
// header. This is intentionally a fresh, independent implementation of the
// same idea used in scripts/cleaning/sponsor.go (rather than importing
// across the two separate `package main` binaries), so validation can
// catch a divergence between what cleaning computed and what's actually
// derivable from bill_text, instead of trivially agreeing with itself.
func FindAsFiledSponsorInText(billText, billNumber string) (string, bool) {
	if !strings.HasPrefix(billNumber, "HB") {
		return "", false
	}
	numStr := strings.TrimPrefix(billNumber, "HB")
	n, err := strconv.Atoi(numStr)
	if err != nil {
		return "", false
	}

	re := regexp.MustCompile(`(?m)^\s*HOUSE BILL\s+0*` + strconv.Itoa(n) + `\s*\n+\s*By\s+(.+?)\s*$`)
	m := re.FindStringSubmatch(billText)
	if len(m) < 2 {
		return "", false
	}
	name := strings.TrimSpace(m[1])
	if name == "" {
		return "", false
	}
	return name, true
}

// SponsorNamesMatch loosely compares a "current sponsor" name (e.g.
// "William Slater") against an as-filed name (e.g. "Hurt", often just a
// surname), by checking whether any word of the as-filed name appears in
// the current sponsor's full name.
func SponsorNamesMatch(current, asFiled string) bool {
	if current == "" || asFiled == "" {
		return false
	}
	currentLower := strings.ToLower(current)
	for _, word := range strings.Fields(strings.ToLower(asFiled)) {
		if strings.Contains(currentLower, word) {
			return true
		}
	}
	return false
}
