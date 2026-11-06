package main

import (
	"crypto/sha256"
	"encoding/hex"
	"regexp"
	"strconv"
	"strings"
)

// TextHash returns a stable hash of bill_text, used to group exact
// duplicates cheaply (a single pass + map, no pairwise comparison).
func TextHash(text string) string {
	sum := sha256.Sum256([]byte(text))
	return hex.EncodeToString(sum[:])
}

// ExactDuplicateGroups groups bill numbers that share byte-identical,
// non-empty bill_text. Since the cleaned dataset already keeps House
// records only (Senate companions are dropped, see docs/dataset.md §7),
// two different House bills sharing identical text is unexpected and
// worth a human look — it was never observed as a legitimate case during
// development.
func ExactDuplicateGroups(records []CleanedRecord) map[string][]string {
	byHash := map[string][]string{}
	for _, r := range records {
		if r.BillText == "" {
			continue
		}
		h := TextHash(r.BillText)
		byHash[h] = append(byHash[h], r.BillNumber)
	}
	groups := map[string][]string{}
	for h, bns := range byHash {
		if len(bns) > 1 {
			groups[h] = bns
		}
	}
	return groups
}

var nonAlnumRe = regexp.MustCompile(`[^a-z0-9]+`)

func normalizeForFingerprint(s string) string {
	return nonAlnumRe.ReplaceAllString(strings.ToLower(s), "")
}

// NearDuplicateFingerprint produces a cheap fingerprint for near-duplicate
// detection: a length bucket plus the normalized start and end of the
// text. This is a practical heuristic (not true fuzzy text similarity) —
// it's intended to surface candidates for manual review, not to be a
// precise similarity measure.
func NearDuplicateFingerprint(text string) string {
	norm := normalizeForFingerprint(text)
	const edgeLen = 80
	start := norm
	if len(start) > edgeLen {
		start = start[:edgeLen]
	}
	end := norm
	if len(end) > edgeLen {
		end = end[len(end)-edgeLen:]
	}
	bucket := len(norm) / 500 // round length to nearest 500 normalized chars
	return start + "|" + end + "|" + strconv.Itoa(bucket)
}

// NearDuplicateGroups groups bill numbers whose bill_text fingerprints
// collide (see NearDuplicateFingerprint) but whose text is not already an
// exact duplicate. Only groups of 2+ distinct bill numbers are returned.
func NearDuplicateGroups(records []CleanedRecord, exact map[string][]string) map[string][]string {
	exactBillNumbers := map[string]bool{}
	for _, bns := range exact {
		for _, bn := range bns {
			exactBillNumbers[bn] = true
		}
	}

	byFingerprint := map[string][]string{}
	for _, r := range records {
		if r.BillText == "" || exactBillNumbers[r.BillNumber] {
			continue
		}
		fp := NearDuplicateFingerprint(r.BillText)
		byFingerprint[fp] = append(byFingerprint[fp], r.BillNumber)
	}

	groups := map[string][]string{}
	for fp, bns := range byFingerprint {
		if len(bns) > 1 {
			groups[fp] = bns
		}
	}
	return groups
}
