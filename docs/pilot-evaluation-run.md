# Education pilot automated evaluation run

**Run date:** October 4, 2026 (semantic calls 20:55:31–21:00:43 UTC)  
**Status:** All nine bills have automated readability, coverage, factual-consistency, and compression records. This is a pipeline test, not a final study result. The [protocol](pilot-evaluation-rubric-draft.md) supersedes the earlier suggestion of formal human review for this pilot.

## Reproduction and provenance

The approved [sample](../data/pilot/education-sample.json), [unedited summaries](pilot-summaries.md), and cleaned `bill_text` were the only text inputs. The source corpus SHA-256 is `df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a`; the sample manifest SHA-256 is `0b8e28366a34191bbfdab4f281d53c882443998a2827072528a23bf25cb2c6e1`. All nine summary source hashes were checked before evaluation.

- Deterministic metrics: [`evaluate_basic_metrics.py`](../scripts/pilot/evaluate_basic_metrics.py) (SHA-256 `0f4491ac77241b2c86839de995da73c2c0407d65cee5bec3ff07b91bb590750c`), with `textstat==0.7.13`, `en_US`, and the pinned [dependency lock](../requirements-pilot-evaluation.lock) (SHA-256 `24a634f6216fa6d52fa3d3a8487723912595fcbc3d4ee58be74231bdd6b06fde`). NLTK's downloaded `cmudict.zip` SHA-256 was `d07cca47fd72ad32ea9d8ad1219f85301eeaf4568f8b6b73747506a71fb5afd6`. The machine records are [readability](../data/pilot/evaluation/readability.json) and [compression](../data/pilot/evaluation/compression.json).
- Semantic metrics: [`evaluate_semantic.py`](../scripts/pilot/evaluate_semantic.py) (SHA-256 `00720255c1978fb52e7e2d83891be54626e36fcdabf45beb728b57366d12a959`) ran source-only proposition extraction, coverage mapping, and summary-claim factuality audit in that order for each bill. The exact v1 instructions and strict schemas are in `prompts/pilot-eval-{source,coverage,factuality}-v1.*`; their SHA-256 values are frozen in the script and checked on each run. All 27 Responses API calls used `gpt-6-sol`, `reasoning.effort=medium`, `max_output_tokens=16384`, `store=false`; all returned `response.model=gpt-6-sol`. The accessible account exposed no dated GPT-6 Sol snapshot. Each stage and bill has its full request, response, IDs, token usage, timestamp, parsed data, and input/prompt/schema hashes under [`data/pilot/evaluation/llm/`](../data/pilot/evaluation/llm/). All responses completed and passed proposition-ID and exact-quote checks. Total reported semantic evaluation usage was 80,275 tokens across 27 calls.
- [`aggregate_evaluation.py`](../scripts/pilot/aggregate_evaluation.py) (SHA-256 `dbdfce66712c90662e21a84161ef9428fb782092a87cf601b4e654cd6b289663`) rechecks the records and writes the combined but **unscored** [per-bill metric file](../data/pilot/evaluation/metrics.json). It does not create an overall quality score.

To recompute deterministic metrics in a fresh environment, install `requirements-pilot-evaluation.lock`, download NLTK `cmudict` to an `NLTK_DATA` directory, check its ZIP hash above, and run `python3 scripts/pilot/evaluate_basic_metrics.py`. To validate and reuse saved semantic calls, run `python3 scripts/pilot/evaluate_semantic.py --execute` with an OpenAI API key; matching completed records are reused without new calls. Then run `python3 scripts/pilot/aggregate_evaluation.py`. The script's default semantic mode is a no-network frozen-input dry run. A different evaluator or changed prompt requires a new version and separate records.

## Separate diagnostic measures

`FK` is Flesch-Kincaid Grade Level; `CLI` is Coleman-Liau Index. Lower values suggest lower formula-measured complexity. `F/P/O` means full/partial/omitted source propositions. `S/C/N` means supported/contradicted/not-established summary claims. The compression ratio is summary whitespace words divided by full cleaned source whitespace words. The underlying file also contains Flesch Reading Ease, text counts, per-bill fractions, and each evaluator judgment's evidence.

| Bill | FK source → summary | CLI source → summary | Compression | Core F/P/O | Supporting F/P/O | Claims S/C/N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| HB2329 | 11.0 → 5.2 | 9.5 → 7.0 | 0.457 | 1/0/0 | 1/0/0 | 3/0/0 |
| HB0709 | 14.2 → 12.0 | 11.6 → 12.7 | 0.425 | 2/0/0 | 1/0/1 | 3/0/1 |
| HB2484 | 14.7 → 12.0 | 11.6 → 12.0 | 0.400 | 1/0/0 | 1/0/0 | 5/0/0 |
| HB1772 | 23.1 → 13.8 | 13.3 → 12.8 | 0.399 | 5/0/0 | 1/1/1 | 13/0/0 |
| HB0474 | 21.0 → 17.0 | 14.7 → 16.0 | 0.584 | 3/0/0 | 1/0/0 | 11/0/0 |
| HB0750 | 19.8 → 13.1 | 12.7 → 13.6 | 0.435 | 2/0/0 | 2/0/0 | 12/0/0 |
| HB0800 | 20.3 → 15.2 | 15.5 → 17.1 | 0.283 | 2/11/0 | 3/8/0 | 27/0/0 |
| HB1889 | 20.1 → 14.7 | 12.7 → 14.8 | 0.339 | 7/5/0 | 4/4/1 | 37/1/0 |
| HB1732 | 22.7 → 12.6 | 13.9 → 14.6 | 0.123 | 2/5/0 | 4/6/0 | 30/0/0 |

These are automated judgments for a deliberately selected nine-bill pilot. The evaluator is the same model as the generator, so the high supported-claim counts cannot be taken as independent evidence of factual accuracy. The per-bill proposition and claim denominators also vary with bill complexity and extraction granularity; do not compare their fractions as if they were a standardized human gold measure.

## Informal pipeline inspection and decisions for the next design revision

An informal **pipeline sanity check** read the nine summaries and inspected selected evidence records. No human clarity, coverage, or factuality labels or scores were assigned, and no second or expert reviewer participated. The student can use the linked records for further informal pipeline inspection without converting that check into scored pilot data.

1. **Formula disagreement is real.** All nine summaries have lower FK scores and higher Flesch Reading Ease, but only two have lower CLI scores. Legal citations, `SECTION` labels, headers, and source boilerplate affect formula inputs; for the 70-word HB2329, `textstat` counts four source sentences even though the operative change is one sentence. The full-as-filed-text rule was applied consistently, but a consistent preprocessing choice should be assessed before interpreting final-study readability results.
2. **Coverage detects compression losses but the `partial` threshold needs calibration.** HB0800 has 24 extracted propositions, 19 marked partial; HB1732 has 17 propositions, 11 marked partial. The extractor groups many repetitive cross-reference amendments in HB1732, while HB0800 keeps more distinct provisions. Some partial reasons concern omitted statutory citations or adjectives rather than an obviously material change. Before the final experiment, define proposition granularity and which qualifiers are essential, then freeze a revised rubric. Preserve v1 as this pilot's diagnostic record.
3. **The source-only rule surfaces specific claim issues.** HB0709's expansion of `LEA` to “local education agency” is marked `not_established` because that expansion is absent from the supplied bill. HB1889 has one `contradicted` scope claim: its summary says “applicants’ counties of residence,” while the bill limits that report item to parents or guardians who applied **and** whose student received a scholarship. The latter is a meaningful faithfulness signal; the former shows that a strict source boundary may flag ordinary explanatory glosses. The final-study policy for such glosses needs to be explicit.
4. **The four dimensions remain distinct.** HB1889's compression and readability changes coexist with a flagged contradiction. HB0800 and HB1732 are strongly compressed and have many partial-coverage judgments even though their claim audits found no contradiction. This is a pipeline observation, not a study conclusion.

For the next method discussion, retain the four separate automated dimensions and review the consistent text preprocessing, materiality threshold for coverage, and treatment of harmless explanatory glosses. Decide after this pilot whether the final experiment needs an independent evaluator or human/expert validation. This pilot has no formal human-scored component.
