package main

import (
	"reflect"
	"testing"
)

func TestGeneralAssemblyMentions(t *testing.T) {
	text := "This bill is before the 114th General Assembly. See also action by the 113th General Assembly."
	got := GeneralAssemblyMentions(text)
	want := []string{"114", "113"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("GeneralAssemblyMentions() = %v, want %v", got, want)
	}
}

func TestWrongGeneralAssemblyMentions(t *testing.T) {
	cases := []struct {
		name     string
		text     string
		expected string
		want     []string
	}{
		{
			name:     "matches expected, no findings",
			text:     "114th General Assembly",
			expected: "114",
			want:     nil,
		},
		{
			name:     "reproduces the real HB0486 case: a prior GA mention",
			text:     "PUBLIC CHAPTER NO. 59\n113th General Assembly",
			expected: "114",
			want:     []string{"113"},
		},
		{
			name:     "no GA mention at all is not flagged",
			text:     "SECTION 1. Tennessee Code Annotated is amended.",
			expected: "114",
			want:     nil,
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := WrongGeneralAssemblyMentions(tc.text, tc.expected)
			if !reflect.DeepEqual(got, tc.want) {
				t.Errorf("WrongGeneralAssemblyMentions(%q, %q) = %v, want %v", tc.text, tc.expected, got, tc.want)
			}
		})
	}
}

func TestContainsPublicChapterMarker(t *testing.T) {
	if !ContainsPublicChapterMarker("State of Tennessee\nPUBLIC CHAPTER NO. 59\nHOUSE BILL NO. 486") {
		t.Error("expected PUBLIC CHAPTER marker to be detected")
	}
	if ContainsPublicChapterMarker("HOUSE BILL 349\n\n By Hurt\n\n AN ACT to amend...") {
		t.Error("expected no PUBLIC CHAPTER marker in a normal draft bill")
	}
}

func TestFindOtherStateMention(t *testing.T) {
	cases := []struct {
		name string
		text string
		want string
	}{
		{
			name: "reproduces a real DynamoDB-era contamination case",
			text: "BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE COMMONWEALTH OF KENTUCKY:",
			want: "Kentucky",
		},
		{
			name: "normal Tennessee text is not flagged",
			text: "BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:",
			want: "",
		},
		{
			name: "New York contamination",
			text: "STATE OF NEW YORK\n________________________________________________________________________",
			want: "New York",
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := FindOtherStateMention(tc.text)
			if got != tc.want {
				t.Errorf("FindOtherStateMention(%q) = %q, want %q", tc.text, got, tc.want)
			}
		})
	}
}

func TestPublicChapterBeforeOwnHeader(t *testing.T) {
	cases := []struct {
		name       string
		text       string
		billNumber string
		want       bool
	}{
		{
			name:       "reproduces the real HB0486 bug: wrong chapter's header precedes this bill's own",
			text:       "State of Tennessee\nPUBLIC CHAPTER NO. 59\nHOUSE BILL NO. 486\n\nBy Someone\n\nAN ACT...",
			billNumber: "HB0486",
			want:       true,
		},
		{
			name: "reproduces the real HB0444 false-positive case: a historical citation after this bill's own header",
			text: "HOUSE BILL 444\n\n By Someone\n\n AN ACT to amend...\n\n WHEREAS, the General Assembly " +
				"expressed the need to protect private property from eminent domain in Public Chapter 863 in 2006",
			billNumber: "HB0444",
			want:       false,
		},
		{
			name:       "no PUBLIC CHAPTER marker at all",
			text:       "HOUSE BILL 100\n\n By Someone\n\n AN ACT to amend...",
			billNumber: "HB0100",
			want:       false,
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := PublicChapterBeforeOwnHeader(tc.text, tc.billNumber)
			if got != tc.want {
				t.Errorf("PublicChapterBeforeOwnHeader() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestWrongGeneralAssemblyMentionsBeforeOwnHeader(t *testing.T) {
	cases := []struct {
		name       string
		text       string
		billNumber string
		want       []string
	}{
		{
			name: "reproduces the real HB1971 false-positive case: a historical citation after this bill's own header",
			text: "HOUSE BILL 1971\n\n By Someone\n\n AN ACT to amend...\n\n WHEREAS, the 110th General " +
				"Assembly enacted Public Chapter 621",
			billNumber: "HB1971",
			want:       nil,
		},
		{
			name:       "a wrong GA mention before this bill's own header is flagged",
			text:       "113th General Assembly\n\nHOUSE BILL 1971\n\n By Someone\n\n AN ACT...",
			billNumber: "HB1971",
			want:       []string{"113"},
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := WrongGeneralAssemblyMentionsBeforeOwnHeader(tc.text, tc.billNumber, "114")
			if !reflect.DeepEqual(got, tc.want) {
				t.Errorf("WrongGeneralAssemblyMentionsBeforeOwnHeader() = %v, want %v", got, tc.want)
			}
		})
	}
}

func TestFindOtherStateMentionBeforeOwnHeader(t *testing.T) {
	cases := []struct {
		name       string
		text       string
		billNumber string
		want       string
	}{
		{
			name:       "reproduces the real HB1966 false-positive case: a policy citation after this bill's own header",
			text:       "HOUSE BILL 1966\n\n By Someone\n\n AN ACT to amend...\n\n WHEREAS, the state of Alabama operates a successful program",
			billNumber: "HB1966",
			want:       "",
		},
		{
			name:       "another state's own document heading before this bill's header is flagged",
			text:       "STATE OF NEW YORK\n________________\n\nHOUSE BILL 1966\n\n By Someone\n\n AN ACT...",
			billNumber: "HB1966",
			want:       "New York",
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := FindOtherStateMentionBeforeOwnHeader(tc.text, tc.billNumber)
			if got != tc.want {
				t.Errorf("FindOtherStateMentionBeforeOwnHeader() = %q, want %q", got, tc.want)
			}
		})
	}
}

func TestCrossCheckRawProvenance(t *testing.T) {
	cases := []struct {
		name    string
		raw     RawRecord
		wantErr bool
	}{
		{
			name:    "correct session and type",
			raw:     RawRecord{SessionID: 2161, SessionName: "114th General Assembly", TextType: "Draft"},
			wantErr: false,
		},
		{
			name:    "wrong session_id",
			raw:     RawRecord{SessionID: 2002, SessionName: "113th General Assembly", TextType: "Draft"},
			wantErr: true,
		},
		{
			name:    "chaptered text type is flagged",
			raw:     RawRecord{SessionID: 2161, SessionName: "114th General Assembly", TextType: "Chaptered"},
			wantErr: true,
		},
		{
			name:    "empty raw record fields are not flagged (no raw data available)",
			raw:     RawRecord{},
			wantErr: false,
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			reason := CrossCheckRawProvenance(tc.raw, 2161, "114th General Assembly")
			if (reason != "") != tc.wantErr {
				t.Errorf("CrossCheckRawProvenance() = %q, wantErr %v", reason, tc.wantErr)
			}
		})
	}
}
