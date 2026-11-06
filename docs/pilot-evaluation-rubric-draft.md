# Education pilot automated evaluation protocol

**Date:** October 4, 2026  
**Status:** Implemented for the nine-bill pilot. The [evaluation run](pilot-evaluation-run.md) records the outputs and pipeline findings. Automated measures are the pilot method. Manual inspection is a pipeline sanity check only; it produces no formal human scores. The final study's need for human or expert validation will be decided after this pilot.

## Scope and source boundary

Evaluate the nine generated `summary` strings against their corresponding cleaned, as-filed `bill_text` values. Do not use LegiScan `description`, current status, or the unstated contents of cited statutes as evidence. Save the input hashes, evaluator prompts and schemas, evaluator model IDs, raw responses, extraction details, and calculated measures for reproduction. Keep readability, coverage, factual consistency, and compression in separate columns and analyses. Do not construct one overall quality score.

The pilot tests whether the evaluation procedures operate sensibly across very short, medium, and long bills. Its automated results are diagnostic; nine deliberately tail-aware bills cannot estimate performance across the education corpus or answer RQ3's cross-model question.

## 1. Readability and linguistic complexity (RQ1)

Compute Flesch-Kincaid Grade Level, Flesch Reading Ease, and Coleman-Liau Index for each full cleaned source text and each summary using `textstat==0.7.13` with its `en_US` setting. The full installed dependency set is frozen in `requirements-pilot-evaluation.lock`; the CMU pronunciation dictionary used by the English syllable counter is NLTK `cmudict`, with downloaded ZIP SHA-256 `d07cca47fd72ad32ea9d8ad1219f85301eeaf4568f8b6b73747506a71fb5afd6`. Also save library word count, sentence count, syllable count, and character count so unusual scores can be traced to parsing. Report score changes by bill; treat the formulas as surface-complexity indicators, not measures of actual comprehension. Flesch-Kincaid and Flesch Reading Ease share inputs and must not be counted as independent evidence.

Use the text exactly as stored for the primary calculation, without deleting citations, captions, section markers, or boilerplate from only one side. Inspect how `textstat` parses the nine pairs, particularly the 70-word bill and the 34-section bill. If formula behavior is implausible because of legislative formatting, record that as a pipeline finding and define one consistent preprocessing revision before the larger experiment. Do not silently adjust individual bills after seeing their scores.

## 2. Information coverage (RQ2)

Use a separate, source-only automated extraction pass to build atomic material propositions from each bill before showing the evaluator its generated summary. A proposition should specify the actor, action or legal change, and qualifiers needed to preserve meaning (scope, conditions, exceptions, amounts, dates). The extractor must supply an exact source quote and section reference and label the proposition `core` or `supporting`. It should group repetitive cross-reference-only edits when they express one underlying change and avoid counting headings or boilerplate as substantive units. This source-first step reduces, but does not eliminate, summary-conditioned inventory bias.

In a second automated pass, compare each proposition with the summary and label it `full`, `partial`, or `omitted`, with a summary quote for `full` or `partial` and a reason for `partial`. Report counts and the `full / total` fraction separately for core and supporting propositions, along with partial and omitted counts. Preserve the proposition-level evidence. A factually supported summary can still omit material source information, so coverage remains separate from factual consistency. The proposition inventory is an automated proxy, not a human gold standard.

## 3. Factual consistency (RQ2)

Use an automated claim audit that decomposes the summary into atomic claims. For each claim, assign `supported`, `contradicted`, or `not_established` against the supplied bill text, with an exact summary quote, source quote where relevant, and a brief rationale. For a contradiction or unsupported addition, classify the issue as insertion, substitution, or a specific change in actor, scope, modality, quantity/date, condition, or exception. Report verdict counts and `supported / total claims`, retaining all claim-level evidence. Do not score omissions here; they belong in coverage. Claims about the unreproduced contents of a cited statute are `not_established`, even if they happen to match LegiScan's description.

The same GPT-6 Sol model can perform these evaluator passes in the narrow pilot while the study uses only one *summarization* model. Its judgments are not independent ground truth because it is also the generator. Record this dependence explicitly, constrain evaluator outputs to auditable evidence quotes, validate quote matches programmatically, and use informal manual inspection to look for rubber-stamping or missed errors. Whether a distinct evaluator or human/expert validation is needed for the final study remains a later decision.

## 4. Compression

Compute `summary whitespace words / cleaned bill_text whitespace words`, retaining both counts. This is the same reproducible counting rule used for sampling and the generation run. The source denominator includes title/header and enactment boilerplate, so the ratio is a length measure rather than a pure measure of substantive compression. Examine it alongside coverage rather than treating more compression as automatically better.

## Informal manual pipeline check

Read the nine outputs and their automated evidence records only to determine whether the pipeline behaves sensibly: whether sentence/word parsing breaks on legal citations, whether source propositions cover the operative changes, whether evidence quotes really match, and whether factuality verdicts are plausible. Record observed pipeline problems and possible revisions in a dated note. Do not assign human clarity ratings, coverage labels, factuality labels, adjudicated scores, or inter-rater statistics for this pilot. No second or domain-expert reviewer is part of the pilot methodology.

## Implementation controls

Freeze evaluator instructions, schemas, `textstat` version, and calculation code before running the automated evaluation. Use one evaluator model ID and settings for all nine pairs, save its returned model ID for every call, and keep raw evaluator responses. A failed or malformed evaluator response is a pipeline error to investigate; it is not a zero score. Validate proposition IDs and exact evidence quotes before computing fractions. Document any revised method as a new version rather than overwriting the original results.
