# Pilot generation prompt and output format

**Date:** October 4, 2026  
**Status:** Prompt and one-field output format approved on October 4, 2026. All nine pilot responses were generated; see [the generation run](pilot-generation-run.md). The subsequent [automated evaluation run](pilot-evaluation-run.md) is complete.

## Recommendation

Use the same instruction template for all nine sampled bills, with only `bill_number` and cleaned `bill_text` varying. The exact approved instruction text is in [`prompts/pilot-summary-v1.txt`](../prompts/pilot-summary-v1.txt). Send it as the Responses API `instructions` value. Send the user input in this exact wrapper, inserting the selected bill's number and full `bill_text`:

```text
Bill number: {{bill_number}}

<bill_text>
{{bill_text}}
</bill_text>
```

Do not include LegiScan's `description`, sponsor fields, current bill status, or outside statutory material in the generation input. The cleaned text is the as-filed version, whereas `description` can reflect later outcomes. The prompt explicitly treats the bill as a proposal, preserves material legal details, and prevents the model from inventing the contents of statutes that are cited but not reproduced. It requests plain prose for adult residents rather than a target grade level. A fixed word count would be poorly suited to sources ranging from 70 to 2,135 words in the drawn sample, so the prompt asks for proportional concision while preserving distinct provisions.

Approved file hashes (SHA-256):

| File | SHA-256 |
| --- | --- |
| `prompts/pilot-summary-v1.txt` | `a8a84c7d3640ce11249e107717a11e24499592c70f24dc2215bc9305b9949889` |
| `prompts/pilot-summary-v1.format.json` | `65ee03d0a90267593885b0982684a55a9d7f7d40e7ce2a505d3c3c663a72b3a1` |

The approved `data/pilot/education-sample.json` selection manifest has SHA-256 `0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1`; the generation script checks it as well as the corpus and prompt files.

## Output contract

Use [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) through Responses API `text.format`, with the exact proposed format object in [`prompts/pilot-summary-v1.format.json`](../prompts/pilot-summary-v1.format.json). The model's entire successful output should be a JSON object with exactly one string field:

```json
{"summary":"..."}
```

Only the `summary` value is the reader-facing artifact and the input to readability, compression, coverage, and factual-consistency analysis. Bill identity, source hashes, model details, and evaluation annotations belong in separate study records, supplied by the pipeline rather than the summarization model. A model-generated confidence score or self-assessment would not provide independent evidence of quality. Strict schema enforcement controls shape, not truth; the automated source-grounded evaluation and informal manual pipeline check remain necessary.

The one-field format also avoids having a separate model-generated caveat or explanation field that might contain substantive information but be excluded from evaluation. When an as-filed bill text is sparse, the summary should state only what the text supports. For example, HB2329 changes a cited reporting date but does not reproduce the broader school-nurse reporting rule described in LegiScan metadata; the model must not fill in that rule from the description.

## API and reproducibility notes

The [official GPT-6 Sol model page](https://developers.openai.com/api/docs/models/gpt-6-sol) lists Responses API and Structured Outputs support. As checked on October 4, 2026, that page instructs API callers to use `gpt-6-sol` and does not list a dated GPT-6 Sol snapshot. Recheck immediately before generation and use a fixed GPT-6 Sol snapshot if one becomes officially available. If only `gpt-6-sol` is available, record that limitation; saving `response.model` alone does not prove that an alias is immutable.

For each bill, preserve the requested model identifier, the returned `response.model`, response ID and status, creation time, complete raw response, parsed `summary`, token usage, request parameters, corpus and bill-text hashes, prompt and schema hashes or versions, and run timestamp. [The Responses API reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create) documents these response fields and the `instructions`, `input`, and `text` configuration. Use one independent request per bill; do not pass previous response IDs or tools. Treat refusal, failed, or incomplete responses as generation failures rather than scoring them as summaries. Freeze all generation settings and any retry rule before calling the API.

The script [`scripts/pilot/generate_summaries.py`](../scripts/pilot/generate_summaries.py) performs a local dry run by default and requires `--execute` for API calls. It verifies the frozen corpus, prompt, schema, sample IDs, and bill-text hashes; sends one request per bill with `reasoning.effort=medium`, `max_output_tokens=8192`, strict `text.format`, and `store=false`; and saves each full request/response plus parsed summary under `data/pilot/responses/`. It skips matching existing records on a resumed run and stops on any failed, refused, incomplete, or malformed response for manual review. The dry run and nine-bill generation run completed on October 4.

## After generation

The account's accessible model list contained only `gpt-6-sol`, so that was the requested and returned model ID. The run details and per-bill response records are linked in [`docs/pilot-generation-run.md`](pilot-generation-run.md). Evaluate the summaries under a separately documented procedure that keeps readability, coverage, factual consistency, and compression distinct.
