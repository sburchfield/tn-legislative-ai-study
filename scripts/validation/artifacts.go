package main

import "regexp"

// These patterns detect artifacts that scripts/cleaning's normalization is
// supposed to already remove. Finding any of them in the cleaned dataset
// signals a normalization regression, not (necessarily) a source-data
// problem — the cleaned dataset should never contain these.
var (
	angleBracketRe       = regexp.MustCompile(`[<>]`)
	undecodedEntityRe    = regexp.MustCompile(`&[a-zA-Z]+;|&#\d+;`)
	leftoverFooterLineRe = regexp.MustCompile(`(?m)^\s*(\d{4,8}|-\s?\d{1,3}\s?-)\s*$`)
	doubleSpaceRe        = regexp.MustCompile(`  `)
	tripleNewlineRe      = regexp.MustCompile(`\n{3,}`)
)

// ArtifactFlags reports which known artifact patterns are present in text.
type ArtifactFlags struct {
	AngleBracket    bool
	UndecodedEntity bool
	LeftoverFooter  bool
	DoubleSpace     bool
	TripleNewline   bool
}

// Any reports whether at least one artifact flag is set.
func (f ArtifactFlags) Any() bool {
	return f.AngleBracket || f.UndecodedEntity || f.LeftoverFooter || f.DoubleSpace || f.TripleNewline
}

// DetectArtifacts scans text for leftover formatting artifacts that should
// have been removed by cleaning's normalization.
func DetectArtifacts(text string) ArtifactFlags {
	return ArtifactFlags{
		AngleBracket:    angleBracketRe.MatchString(text),
		UndecodedEntity: undecodedEntityRe.MatchString(text),
		LeftoverFooter:  leftoverFooterLineRe.MatchString(text),
		DoubleSpace:     doubleSpaceRe.MatchString(text),
		TripleNewline:   tripleNewlineRe.MatchString(text),
	}
}
