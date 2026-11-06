# Full experiment design

**Finalized:** October 17, 2026  
**Status:** Revised methodology finalized before execution. The draw, paired generation, automated evaluation, six-summary researcher check, and [descriptive interpretation](full-experiment-results.md) are complete. Details, including a versioned evidence-quote validation correction, are in the [execution log](full-experiment-run.md). The filename retains `-draft` for existing links. The nine-bill [pilot](pilot-evaluation-run.md) remains separate and unchanged.

## Scope and sample

The study retains the [approved 18-label education definition](pilot-sampling-assessment.md) within the cleaned, as-filed 114th Tennessee General Assembly corpus. This definition identifies 336 bills. Exclude all nine bills used to develop and test the pilot method from the full experiment. The remaining 327 comprise 109 bills in each **original** source-length tertile; do not recalculate the tertile boundaries after exclusion. Source length is `len(bill_text.split())`, including the header and enactment language.

Select **36 bills**, 12 from each original tertile, before generation. Within the short tertile, select five bills of at most 80 words and seven other short bills. Select 12 medium bills. Within the long tertile, select ten bills below 1,980 words and two at or above 1,980 words. This approximately preserves the pilot frame's within-tertile edge-case proportions while including short amendment-only texts and long bills. The five cell sizes are 5 + 7 + 12 + 10 + 2 = 36. This is an exploratory sample, not a powered estimate for all education legislation.

Use the frozen sample seed `INSC499-education-full-2026-10-17-v1`. In each cell, rank eligible bills by SHA-256 of the UTF-8 string `seed|id|bill_number`, ascending, breaking a hash tie by `bill_number`; take the required number without replacement. Save the selected bill IDs, cells, word counts, text hashes, source-corpus hash, seed, and rule in a manifest. Check each selected source for integrity before generation; do not replace a bill because its summary or evaluation later looks difficult. The executed draw is in [`data/full/sample.json`](../data/full/sample.json).

## Paired summary generation (RQ1–RQ3)

Generate one summary of each selected bill with **`gpt-6-sol`** and one with **`gpt-6-luna`** through the OpenAI Responses API: 72 summaries total. Use the same [approved pilot summary prompt](../prompts/pilot-summary-v1.txt), [one-field JSON output schema](../prompts/pilot-summary-v1.format.json), and `reasoning.effort=medium` for both models. Make an independent request for every bill and model, with no tools or prior-response context. Keep the source text and generated summaries unedited. Record requested and returned model IDs, prompt/schema/source hashes, settings, response IDs, timestamps, token usage, and raw responses. The October 17 account check found these model IDs but no dated GPT-6 snapshot; recheck before execution and record the exact returned identifier on every call. This comparison is between two OpenAI models and does not establish results for other providers.

## Automated evaluation

Use **`gpt-6-astra`** as the one common automated evaluator for both models' summaries, with the Responses API, fixed settings, strict structured outputs, and no outside sources. Evaluate each summary only against its cleaned, as-filed `bill_text`; do not use LegiScan descriptions, later bill status, or unstated contents of cited statutes. Record Astra's requested and returned model IDs, prompt/schema hashes, full requests/responses, evidence, and timestamps. A quote-matching script verifies that cited passages appear in the supplied text; it cannot verify the evaluator's interpretation. An incomplete or malformed response is a pipeline error to investigate, not a low score. The execution revealed PDF line-wrap whitespace after hyphens; the [versioned validation correction](full-experiment-run.md#credit-replenishment-and-evidence-check-retry) is documented separately from this prespecified design and was applied uniformly to all 180 saved records.

Keep the four existing dimensions **separate**. Do not create an overall quality score.

1. **Linguistic complexity/readability (RQ1):** Apply the pilot's pinned `textstat` implementation to the full, exactly stored bill text and each unedited summary. Report Flesch-Kincaid Grade Level, Flesch Reading Ease, and Coleman-Liau Index with the underlying counts. The pilot showed that formulas can disagree and legal formatting affects parsing; interpret them as surface measures, not comprehension.
2. **Information coverage (RQ2):** Astra creates one source-only inventory of operative material propositions per bill **before** seeing either model's summary. Reuse that same inventory for both summaries. Each proposition states the actor, action, and qualifiers needed to preserve its substantive meaning, with an exact source quote and `core` or `supporting` label. Group repeated cross-reference edits with the same effect. Astra then marks each proposition `full`, `partial`, or `omitted` for each summary, with a summary quote and reason. `Full` requires the action and material qualifiers, not every citation or minor adjective; `partial` means a meaningful part is present but a material detail is missing or changed. A citation remains material when the amendment target cannot otherwise be identified. Report core and supporting counts separately. The clarified [source](../prompts/full-eval-source-v2.txt) and [coverage](../prompts/full-eval-coverage-v2.txt) instructions implement this rule.
3. **Factual consistency/faithfulness (RQ2):** Astra breaks each summary into atomic claims and marks each `supported`, `contradicted`, or `not_established` against the supplied bill text. It records exact summary and source excerpts where available, a brief rationale, and a specific error type for a problem. Omissions belong to coverage, not factual consistency. An explanatory expansion absent from the source remains `not_established`; discuss such cases in interpretation rather than adding another score or silently discarding them. Use the [factuality instructions](../prompts/full-eval-factuality-v2.txt) and schema. Report claim counts and verdicts, retaining claim-level evidence.
4. **Compression:** Report the pilot's `summary whitespace words / source whitespace words` ratio and both counts. A lower ratio is not automatically better.

The v2 evaluator wording clarifies the pilot's overly broad `partial` coverage judgments without adding another metric. The original pilot v1 prompts and records remain intact. These prompt and schema SHA-256 values are frozen for this design:

| Artifact | SHA-256 |
| --- | --- |
| `prompts/pilot-summary-v1.txt` | `a8a84c7d3640ce11249e107717a11e24499592c70f24dc2215bc9305b9949889` |
| `prompts/pilot-summary-v1.format.json` | `65ee03d0a90267593885b0982684a55a9d7f7d40e7ce2a505d3c3c663a72b3a1` |
| `prompts/full-eval-source-v2.txt` | `e60639a7b1cc45f710854a2953c71879cab08de1ffc6263661fcdea88e8badaf` |
| `prompts/full-eval-source-v2.format.json` | `744aacd831094d7b3ec5b57303bae790617526ba8025f82be7e65765e492186e` |
| `prompts/full-eval-coverage-v2.txt` | `843a969af3d218c859abfa5c323a5c53b39f49df547a8b10a7f3eb59a7fccf65` |
| `prompts/full-eval-coverage-v2.format.json` | `d48bc7aa5bba9079c7b4936a57d07033b3f2fd96b9495ec9b67ea5f4053cd915` |
| `prompts/full-eval-factuality-v2.txt` | `cf94d6026e90bc3c1c2a9ced75353faddbe5497bab4b3b7c86dfe07f0de7775b` |
| `prompts/full-eval-factuality-v2.format.json` | `7e29c626820e84e8c549e146c6fdfd80c30fd12daae2930302452153da40ea17` |

Check these hashes and strict schemas before execution. A necessary later correction must receive a new version and a dated journal entry; do not tune rules after seeing full-experiment outcomes.

## Limited researcher-conducted sanity check

Select **three of the 36 sampled bills before generating any summaries: one short, one medium, and one long**. Use the separate frozen seed `INSC499-education-review-2026-10-17-v1`. Within each original tertile's 12 sampled bills, rank by SHA-256 of `review_seed|id|bill_number`, ascending, with the same tie rule; take the first. Save the three bill IDs, seed, ranking rule, and selection timestamp in the manifest before generation. Do not select or replace cases based on model outputs or Astra flags. The pre-generation review draw selected HB1228, HB0187, and HB0522.

Sam Burchfield will personally inspect **both model summaries for each selected bill, six summaries total**, against the as-filed source. Use the [review form](full-experiment-human-review-form-draft.md) only to note problems in **factual accuracy, material omissions, or changes to substantive meaning**. For each problem, record the summary passage, supporting or conflicting source passage where one exists, and a brief explanation. Record `no problem observed` if none is found. Complete and timestamp these notes **without viewing Astra's judgments**; compare with Astra afterward only to identify illustrative agreements or missed issues. This is a **limited researcher-conducted sanity check**, not expert validation, an independent gold standard, formal scoring of all claims, or statistically meaningful inter-rater reliability testing. One researcher and three bills cannot estimate the automated evaluator's accuracy or the population rate of factual errors.

## Analysis and execution boundary

Compare Sol and Luna on the **same 36 bills**, reporting paired differences for the separate automated outcomes, overall and by source-length tertile. Keep proposition and claim denominators visible. Describe the six-summary researcher check qualitatively, without including its notes in a numeric model ranking. The sample and same-provider model pair limit generalization; formula scores do not measure reader comprehension, and Astra's judgments remain automated estimates even though it is a different model from the two generators.

The method was recorded here before execution. The frozen inputs and strict schemas were checked in a dry run before the draw, generation, and Astra audits recorded in the [execution log](full-experiment-run.md). Log every later action and any necessary versioned correction in [the journal](journal.md); preserve all pilot records.
