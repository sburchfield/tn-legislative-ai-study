package main

import "regexp"

// billNumberRe is the expected format for a cleaned record's bill_number:
// "HB" followed by exactly 4 digits (e.g. "HB0001"). The cleaned dataset
// should contain House bills only (see docs/dataset.md §7).
var billNumberRe = regexp.MustCompile(`^HB\d{4}$`)

// IsWellFormedBillNumber reports whether s matches the expected cleaned
// House-bill-number format.
func IsWellFormedBillNumber(s string) bool {
	return billNumberRe.MatchString(s)
}
