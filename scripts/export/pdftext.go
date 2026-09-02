package main

import (
	"bytes"
	"context"
	"fmt"
	"os/exec"
	"time"
)

// extractPDFText shells out to the poppler `pdftotext` utility to convert
// PDF bytes to plain text, preserving word/line spacing via -layout. This
// is a read-only, external conversion step (no network access), required
// because the source documents are only available as PDFs.
func extractPDFText(pdftotextPath string, pdfBytes []byte) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, pdftotextPath, "-layout", "-", "-")
	cmd.Stdin = bytes.NewReader(pdfBytes)

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("pdftotext failed: %w (stderr: %s)", err, stderr.String())
	}

	return stdout.String(), nil
}
