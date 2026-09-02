# Dataset

This document describes the provenance, schema, and processing steps for the
research corpus used in this study, and how to reproduce it.

## 1. Source

The source data is Tennessee General Assembly bill text and metadata,
retrieved from the **LegiScan API** (https://legiscan.com/legiscan), a
public API that aggregates U.S. state legislative data specifically for
programmatic, read-only reuse. LegiScan's own source for Tennessee bill
text is the official PDF documents published by the Tennessee General
Assembly at `capitol.tn.gov`.

**This project previously exported data from an internal DynamoDB table
used by the TNBills civic information platform.** That approach was
abandoned after auditing the exported data and finding it unreliable for
research use: roughly half of records had no bill text at all, some
`bill_text` values contained statutory text from *other states*
(e.g. Kentucky, New York) under a Tennessee bill's identifier, and
House/Senate companion bills — which should be textually identical — were
found to differ in every checked case. These all appear to be defects in
that internal pipeline rather than anything about the underlying
legislation. Scraping `capitol.tn.gov` directly to bypass this was
considered and rejected: its `robots.txt` disallows automated crawling for
all user agents except a small allowlist of major search engines, and this
project does not do that. LegiScan was chosen because it is designed and
offered specifically for this kind of programmatic access, and validation
against the same bills (see §8) confirmed official companion bills *are*
word-for-word identical once instead sourced from the original PDFs.

## 2. Export

The research corpus is a point-in-time export produced with the read-only
script at [`scripts/export/`](../scripts/export/). For each bill in a
given LegiScan session (General Assembly), the export:

1. Calls LegiScan's `getMasterList` to enumerate the session's bills,
   keeping only actual Bills (`HB####` / `SB####`) and excluding
   resolutions (`HJR`, `SJR`, `HR`, `SR`), which are a different kind of
   legislative instrument outside this study's scope.
2. Calls `getBill` for each one, capturing its title, description, primary
   sponsor, subjects, and its companion bill number (LegiScan's "Same
   As/Similar To" / "Crossfiled" relationship — the same companion link
   shown on the bill's official `capitol.tn.gov` page).
3. Calls `getBillText` for the bill's as-filed/as-introduced text document
   (LegiScan type `Draft` or `Introduced`; not any later amended,
   engrossed, or enacted version), which returns the official PDF as
   base64-encoded bytes. This is deliberately *not* simply "the
   earliest-dated document": during the full 114th GA export, one bill
   (`HB0486`) was found to have a stray, misattached document in
   LegiScan's own data — a 113th General Assembly enacted "Public Chapter"
   PDF (TN bill numbers are reused each session) dated 2023, years before
   this bill was even filed. Picking by earliest date alone would have
   silently pulled in a completely unrelated bill's text under `HB0486`'s
   identity. Requiring an explicit `Draft`/`Introduced` type match avoids
   this; see `earliestText` in
   [`scripts/export/legiscan.go`](../scripts/export/legiscan.go) and its
   tests.
4. Extracts plain text from the PDF via poppler's `pdftotext -layout`
   (a local, external, read-only conversion — no network access), which is
   necessary to represent the PDF as text in the JSONL export and, per
   testing, correctly preserves word spacing unlike the prior pipeline.

The export never writes to LegiScan or capitol.tn.gov, and never alters
document content beyond this necessary PDF-to-text conversion. It streams
results and is resumable: rerunning it skips bills already present in the
output file (unless `-fresh` is passed), so an interrupted run — e.g. from
hitting an API quota — can continue later without wasting quota re-fetching
already-exported bills.

Each export run prints the export date/time (UTC) on completion. This
should be recorded alongside the exported files so the corpus snapshot
date is traceable.

The default scope is TN's **114th General Assembly (2025-2026)**, LegiScan
session id `2161`, containing 5,430 House/Senate bills (of 9,159 total
master-list entries, the remainder being resolutions). This can be changed
via `-session-id` (see §9).

## 3. Raw record schema

Each line of `data/raw/bills.jsonl` is one bill:

| Field                  | Description                                                        |
|-------------------------|---------------------------------------------------------------------|
| `id`                    | LegiScan `bill_id`                                                   |
| `bill_number`           | e.g. `HB0001`, `SB0001`                                              |
| `chamber`               | `H` or `S`                                                            |
| `title`                 | Bill title/caption                                                    |
| `description`           | Short bill description                                               |
| `sponsor`                | Primary sponsor's name                                               |
| `subjects`               | Subject tags                                                          |
| `companion_bill_number` | The linked House/Senate companion bill's number, if any             |
| `bill_text`              | Text extracted from the bill's earliest PDF document                |
| `text_doc_id`, `text_type`, `text_date` | LegiScan document identifiers for the text used     |
| `change_hash`            | LegiScan's own data-versioning hash (not a research field)          |
| `session_id`, `session_name` | LegiScan session identifiers                                    |
| `state_link`, `legiscan_url` | Links to the official and LegiScan bill pages                  |
| `fetch_error`            | Set (and `bill_text` left empty) if fetching/extracting failed for this bill |

## 4. Fields retained for research

The cleaned research dataset (`data/cleaned/bills.jsonl`) retains, per
House bill:

- `id`
- `bill_number`
- `title`
- `description`
- `sponsor` — the bill's **current** prime sponsor of record, from
  LegiScan's own metadata (which reflects sponsor changes over the bill's
  lifetime — TN allows these)
- `sponsor_as_filed` — the sponsor **as printed on the bill's own as-filed
  text** (the "By [Name]" line, usually just a surname), parsed directly
  from `bill_text`. This is frozen at introduction and does not reflect
  later sponsor changes. See below — these two fields disagree for 192 of
  2,684 bills (7.2%) in the 114th GA export.
- `subjects`
- `companion_bill_number`
- `text_source` — `"house"` if the bill's own text was used, or
  `"senate_companion_fallback"` if the House copy was missing and its
  Senate companion's text was used instead (see §7)
- `bill_text`

**Why `sponsor` and `sponsor_as_filed` can disagree:** spot-checking
`HB0349` found `sponsor` = "William Slater" but its `bill_text` printed
"By Hurt". This isn't a data error — the bill's own history shows a
"Sponsor change" event over a year after the bill was filed. `sponsor`
reflects who currently owns the bill; `sponsor_as_filed` reflects who
filed the specific as-introduced document `bill_text` is drawn from. Which
one is "correct" depends on the research question — use `sponsor_as_filed`
for anything tied to the text itself (e.g. author-attribution studies of
`bill_text`), and `sponsor` for anything about current bill ownership.
`missing_sponsor_as_filed` in the stats file tracks how many records this
couldn't be parsed for (0 in the 114th GA export — the "By [Name]" line
was present and parseable for every record).

## 5. Fields excluded, and why

- **`change_hash`**, **`text_doc_id`/`text_type`/`text_date`**,
  **`session_id`/`session_name`**, **`state_link`/`legiscan_url`** — API/
  provenance bookkeeping with no research value, dropped in cleaning.
- **`fetch_error`** — an operational flag for records where fetching
  failed; excluded from the research schema since it fails closed already
  (an empty `bill_text`).

Unlike the abandoned DynamoDB source, this pipeline has no equivalent of
the old `impact_analysis` / `layman_summary` / `summary` fields (existing
AI-generated derivatives) — LegiScan does not provide them, so there is
nothing to deliberately exclude here. This is still worth stating
explicitly: this study's own AI-mediated transformations must be generated
from `bill_text` under controlled experimental conditions (fixed models,
fixed prompts, documented methodology), not by reusing any third party's
pre-existing derived text.

## 6. Text normalization (`bill_text`)

The cleaning script ([`scripts/cleaning/normalize.go`](../scripts/cleaning/normalize.go))
applies conservative, deterministic normalization. It is **not** an LLM and
does not rewrite, summarize, paraphrase, or otherwise alter legislative
language. Two passes run in sequence:

**1. `StripPDFRunningFooters`** — removes the per-page running
header/footer that `pdftotext` carries over from the official PDF: the
bill's own number, an internal document control number, and a dashed page
number (e.g. `SB0431` / `001315` / `-1-`), each recurring on every page,
either on separate lines or combined on one line depending on the PDF's
column layout. This match is anchored to the specific bill's own number,
so it cannot be mistaken for unrelated content elsewhere in the text.

**2. `NormalizeBillText`** — the general-purpose pass (also handles HTML
if it's ever present in a source again):
- Normalizes line endings (`\r\n`, `\r` → `\n`).
- Removes `<script>...</script>` / `<style>...</style>` blocks and HTML
  comments.
- Converts block-level HTML tags to newlines, then strips remaining tags —
  this also removes unfilled document mail-merge placeholders like
  `<BillNo> <Sponsor>`, seen in "Draft" PDFs where a bill's companion had
  not yet been assigned a sponsor at filing time (a real, observed
  artifact, not hypothetical — see `normalize_test.go`).
- Decodes HTML entities.
- Removes non-printable control characters, non-breaking spaces, and a
  leading byte-order mark.
- Collapses runs of horizontal whitespace to a single space, strips
  trailing per-line whitespace, and collapses 3+ blank lines to one.
- Trims leading/trailing whitespace from the whole document.

When it is unclear whether something is formatting or substantive content,
the normalizer preserves it — see
[`scripts/cleaning/normalize_test.go`](../scripts/cleaning/normalize_test.go),
which includes cases confirming real code citations (e.g.
`67-5-603(a)(1)`) and embedded numbers are never mistaken for page-footer
artifacts.

## 7. House/Senate companion handling

Only House bill records (`chamber == "H"`) are written to the cleaned
dataset. This was a deliberate, requested design choice, validated against
real data before implementing it:

- Official PDFs for a House bill and its Senate companion were compared
  word-for-word (`HB0001` vs. `SB0001`, 114th GA) and found **identical**
  except for the order of the "SENATE BILL N / HOUSE BILL N" header lines
  and the per-page bill-number footer stamp — both artifacts already
  stripped by normalization (§6). This confirms companion bills are true
  duplicates once sourced from the official PDF, unlike what the abandoned
  DynamoDB pipeline showed.
- For each House record: if its own `bill_text` is non-empty after
  cleaning, it's used (`text_source: "house"`). If it's empty and the
  bill has a companion, the companion's cleaned `bill_text` is used
  instead (`text_source: "senate_companion_fallback"`), maximizing text
  coverage without introducing duplicate content.
- Senate-only records (no House companion at all) are dropped entirely —
  this is a deliberate exclusion, not a silent one: `senate_records_excluded`
  in the stats file counts every Senate record omitted this way, and
  `senate_companion_fallback_used` counts how many actually supplied text
  a House record was otherwise missing.

## 8. Dataset statistics

After each cleaning run, statistics are printed to stdout and written to
`data/cleaned/dataset-stats.json`:

- `raw_records` — total records read from the raw export (House + Senate).
- `house_records` — House bill records.
- `senate_records_excluded` — Senate bill records, none of which are
  written to the cleaned dataset (see §7).
- `senate_companion_fallback_used` — of those excluded Senate records, how
  many supplied `bill_text` for a House record that would otherwise be
  empty.
- `fetch_errors` — raw records where fetching/extraction failed
  (`fetch_error` is set).
- `cleaned_records` — records written to the cleaned dataset (equals
  `house_records`).
- `missing_bill_text` — cleaned records with empty `bill_text` even after
  the Senate-companion fallback.
- `missing_bill_number`, `duplicate_ids`, `duplicate_bill_numbers` —
  data-quality checks, as before.
- `normalized_bill_text_records` — records where normalization changed
  `bill_text` from its raw form.
- `missing_sponsor_as_filed` — records where the "By [Name]" line couldn't
  be parsed from `bill_text` (see §4).
- `sponsor_differs_from_as_filed` — records where `sponsor` and
  `sponsor_as_filed` name different people (see §4).

## 9. Records excluded from the cleaned dataset

Two categories, both deliberate and documented (not silent):

1. **Resolutions** (`HJR`, `SJR`, `HR`, `SR`) are excluded at the export
   stage — never fetched at all — since they are a different legislative
   instrument outside this study's "bills" scope.
2. **Senate-only bill records** are excluded at the cleaning stage per §7.

No record is dropped for having missing/empty fields; missingness is
reported via statistics (§8) instead, so sampling/filtering decisions can
be made deliberately later, with reasoning documented at that time.

## 10. How to rerun the export

Requires:
- A free LegiScan API key (register at legiscan.com/legiscan), set as
  `LEGISCAN_API_KEY` in your environment or a local `.env` file (never
  committed — see `.gitignore`).
- The poppler `pdftotext` utility on `PATH` (e.g. `brew install poppler`
  on macOS, `apt-get install poppler-utils` on Debian/Ubuntu).

```bash
go run ./scripts/export \
  -session-id 2161 \
  -out data/raw/bills.jsonl \
  -delay-ms 200
```

`-session-id` defaults to `2161` (TN's 114th General Assembly, 2025-2026).
`-limit N` fetches only the first N bills, useful for testing. `-fresh`
ignores any existing output and re-fetches everything from scratch; by
default, reruns resume and skip bills already present in `-out`. A full
run over ~5,430 bills takes on the order of tens of minutes and makes
roughly two LegiScan API calls per bill (`getBill` + `getBillText`); if you
hit your account's query quota partway through, the run stops cleanly and
can simply be rerun later to continue where it left off.

## 11. How to rerun the cleaning process

```bash
go run ./scripts/cleaning \
  -in data/raw/bills.jsonl \
  -out data/cleaned/bills.jsonl \
  -stats data/cleaned/dataset-stats.json
```

All three flags have the defaults shown above, so `go run ./scripts/cleaning`
with no flags is equivalent.
