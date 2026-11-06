package main

import "testing"

func TestIsWellFormedBillNumber(t *testing.T) {
	cases := []struct {
		in   string
		want bool
	}{
		{"HB0001", true},
		{"HB2638", true},
		{"SB0001", false},  // Senate bills should never appear in the cleaned dataset
		{"HJR0001", false}, // resolutions are out of scope
		{"HB1", false},     // wrong digit width
		{"HB00001", false}, // wrong digit width
		{"hb0001", false},  // wrong case
		{"", false},
		{"HB000A", false},
	}
	for _, tc := range cases {
		got := IsWellFormedBillNumber(tc.in)
		if got != tc.want {
			t.Errorf("IsWellFormedBillNumber(%q) = %v, want %v", tc.in, got, tc.want)
		}
	}
}
