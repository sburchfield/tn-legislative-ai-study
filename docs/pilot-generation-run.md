# Education pilot generation run

**Run date:** October 4, 2026, 20:25:48–20:26:21 UTC  
**Status:** Nine model responses generated and structurally validated; the later [automated evaluation run](pilot-evaluation-run.md) is complete.

## Frozen inputs and settings

- Sample: [`data/pilot/education-sample.json`](../data/pilot/education-sample.json), SHA-256 `0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1`.
- Corpus: `data/cleaned/bills.jsonl`, SHA-256 `df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a`.
- Prompt: [`prompts/pilot-summary-v1.txt`](../prompts/pilot-summary-v1.txt), SHA-256 `a8a84c7d3640ce11249e107717a11e24499592c70f24dc2215bc9305b9949889`.
- Output schema: [`prompts/pilot-summary-v1.format.json`](../prompts/pilot-summary-v1.format.json), SHA-256 `65ee03d0a90267593885b0982684a55a9d7f7d40e7ce2a505d3c3c663a72b3a1`.
- API: OpenAI Responses API; one independent request per bill, no tools or prior-response context; `reasoning.effort=medium`, `max_output_tokens=8192`, strict JSON Schema output, `store=false`.
- Model: Requested `gpt-6-sol`. The account's `/v1/models` list exposed `gpt-6-sol` and no dated GPT-6 Sol snapshot immediately before generation. Every response returned `response.model=gpt-6-sol`. This records the API's model identifier but does not make an undated alias immutable.

The generation script is [`scripts/pilot/generate_summaries.py`](../scripts/pilot/generate_summaries.py). Each linked JSON record below contains the full request (without the API key), full raw response, parsed reader-facing `summary`, timestamps, response ID, token usage, model IDs, and source/prompt/schema hashes. The API key remains only in the ignored `.env` file or process environment.

For convenient reading, [`docs/pilot-summaries.md`](pilot-summaries.md) renders all nine unedited summaries from the JSON records. It can be regenerated with `python3 scripts/pilot/render_summaries.py`.

## Structural and length check

All nine API responses had `status=completed`, returned nonempty summaries matching the one-field contract, and used unique response IDs. All stored source-text hashes match the approved sample. These checks establish that the generation pipeline ran; they do not establish information coverage or factual accuracy.

| Cell | Bill | Source words | Summary words | Summary/source | Response record |
| --- | --- | ---: | ---: | ---: | --- |
| Short, minimal | HB2329 | 70 | 32 | 0.457 | [JSON](../data/pilot/responses/HB2329.json) |
| Short, other | HB0709 | 127 | 54 | 0.425 | [JSON](../data/pilot/responses/HB0709.json) |
| Short, other | HB2484 | 100 | 40 | 0.400 | [JSON](../data/pilot/responses/HB2484.json) |
| Medium | HB1772 | 386 | 154 | 0.399 | [JSON](../data/pilot/responses/HB1772.json) |
| Medium | HB0474 | 185 | 108 | 0.584 | [JSON](../data/pilot/responses/HB0474.json) |
| Medium | HB0750 | 232 | 101 | 0.435 | [JSON](../data/pilot/responses/HB0750.json) |
| Long, main | HB0800 | 963 | 273 | 0.283 | [JSON](../data/pilot/responses/HB0800.json) |
| Long, main | HB1889 | 1,118 | 379 | 0.339 | [JSON](../data/pilot/responses/HB1889.json) |
| Long, tail | HB1732 | 2,135 | 263 | 0.123 | [JSON](../data/pilot/responses/HB1732.json) |

The summary/source column uses the same whitespace word count rule used for sampling, so it includes bill headers and boilerplate in the source denominator. Summary length ranged from 32 to 379 words, with a median of 108; the median ratio was 0.400. Across all requests, the API reported 11,665 input tokens, 2,257 output tokens, and 13,922 total tokens. These are generation diagnostics, not pilot findings on readability or quality.

## Subsequent evaluation

The as-filed short bill HB2329 tests whether the summary avoids inventing the unstated substance of the cited law. The 34-section HB1732 tests whether a compressed summary retains material independent changes. HB0800 contains substantial preamble language that the automated evaluator must distinguish from operative provisions. All nine bill-summary pairs were evaluated under the [automated pilot protocol](pilot-evaluation-rubric-draft.md); the separate measures and informal pipeline inspection are recorded in the [evaluation run](pilot-evaluation-run.md). The pilot has no formal human scores or second reviewer.
