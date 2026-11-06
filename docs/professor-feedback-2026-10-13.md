# Project Report 1 feedback: evaluation responsibility

**Feedback received:** October 13, 2026  
**Documented:** October 17, 2026  
**Status:** Feedback analysis and proposed response. No change to the completed nine-bill pilot protocol or scores.

Dr. Peiling Wang said the report looks good, asked that the project continue to document its steps and actions, and asked for a specific account of **how hallucinations will be evaluated and who will perform that evaluation** for RQ2. This note records the response supported by work already completed and identifies the final-study decision that remains open. The September 18 [Project Report 1](project-report-1.md) is retained as the submitted historical document.

## What has already been done in the pilot

The [journal](journal.md) logs data preparation, sampling, prompt design, generation, and evaluation decisions chronologically. The [generation run](pilot-generation-run.md) records the source and sample hashes, exact prompt and output schema, requested and returned model ID, API settings, response IDs, and unedited summaries. The [evaluation run](pilot-evaluation-run.md) records the evaluator prompts, settings, raw Responses API records, proposition-level and claim-level evidence, dependency versions, calculations, and pipeline findings.

For **factual consistency**, the pilot evaluator was `gpt-6-sol` through the OpenAI Responses API. It split each generated summary into atomic claims and compared each claim only with that bill's cleaned, as-filed `bill_text`. Each claim received `supported`, `contradicted`, or `not_established`, an exact summary excerpt, an exact source excerpt where applicable, a rationale, and an error type for a problem. A script checked that quoted excerpts actually occurred in the corresponding texts before calculating claim counts. The bill text, rather than LegiScan's description or the contents of unreproduced statutes, was the evidence boundary. This procedure flagged a report-scope contradiction in HB1889 and a source-unestablished abbreviation expansion in HB0709. The [protocol](pilot-evaluation-rubric-draft.md) and saved [claim records](../data/pilot/evaluation/llm/factuality/) specify the procedure in full.

For **information coverage**, a separate `gpt-6-sol` pass first extracted source propositions without seeing a summary. A later pass assessed each proposition as `full`, `partial`, or `omitted` against the summary. This keeps missing source information separate from claims that contradict or exceed the source. Readability and compression were calculated separately; neither is a hallucination measure.

The **pilot evaluator** was therefore the API model, operated by the project's reproducible scripts. Informal reading of the nine outputs checked pipeline behavior. It did **not** create formal human judgments, and no second or domain-expert reviewer participated in the pilot. The same model generated and evaluated the summaries, so the pilot's high supported-claim count is **not independent validation of factual accuracy**. Exact-quote checks verify traceability of cited text, not the correctness of a model's interpretation.

## Proposed answer and remaining final-study decision

The professor's question should be answered at two levels:

1. **How and by whom the automated evaluation runs:** apply the frozen, source-grounded coverage and claim-audit procedures to each bill-summary pair; record the evaluator's exact model ID, prompts, outputs, evidence quotes, and code version; report coverage and factual consistency separately. Name the evaluator model explicitly in the final protocol. The pilot used `gpt-6-sol`; the final-study evaluator has not yet been selected.
2. **How the automated evaluator is checked:** decide whether to add an independent check for the final experiment. Because the pilot evaluator was also the generator and the pilot exposed a questionable treatment of harmless explanatory wording plus an overly broad `partial` category, the recommended next step is a **preselected, manageable human validation subset** for the final experiment. A concrete proposal is for Sam Burchfield to check claims against the as-filed bill text using a written, claim-level rubric, without seeing the automated verdict first, then compare judgments and document disagreements. That would be one student reviewer, with no second or domain-expert reviewer implied. The subset size, stratified selection rule, exact rubric, and reviewer assignment would need to be fixed before validation begins. This is a recommendation for discussion, not a change to the completed pilot or an approved final-study decision.

The completed pilot must not be retrospectively labeled as human-scored. A final-study decision on independent validation and the coverage materiality rule should be recorded as a new dated protocol version, preserving the pilot v1 results.

## Concise response draft for discussion with Dr. Wang

> Thank you for the feedback. I have kept a chronological project journal and logged the pilot's sampling, prompts, model identifiers, API responses, and evaluation steps. For the nine-bill pilot, factual consistency was evaluated automatically by GPT-6 Sol: it checked each atomic summary claim against the bill's as-filed text and marked it supported, contradicted, or not established, with source excerpts and reasons. A separate source-first check assessed information omitted from summaries. Informal inspection of outputs only tested whether that pipeline behaved sensibly; the pilot has no formal human scores or second reviewer. Because GPT-6 Sol also generated the summaries, I am treating its verdicts as diagnostic rather than independent proof of accuracy. For the full experiment, I propose to run the documented automated checks on every output and personally validate a prespecified, length-stratified subset against the bill text, using a written claim-level rubric before seeing the automated verdicts. I will fix and report the subset size, selection rule, rubric, and final evaluator model before that experiment begins.

This is a draft for the student to adapt or discuss, not a message sent to the professor. It does not imply that the final-study review plan has been approved.

## October 17 design decision

The later [full-experiment design](full-experiment-design-draft.md) fixes a narrower response to the reviewer question: Astra performs the automated source-grounded evaluation of all Sol and Luna summaries, and Sam personally checks both summaries for **three reproducibly selected bills**, one per length tertile. The six-summary check records factual errors, material omissions, or substantive meaning changes with brief explanations and source passages, before Sam views Astra's judgments. It is a limited researcher sanity check, not expert validation or a basis for inter-rater reliability claims. This supersedes the open-ended human-subset proposal above without changing the completed pilot.
