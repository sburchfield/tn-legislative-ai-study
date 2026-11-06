# Cross-provider extension: descriptive results and researcher check

**Recorded:** November 3, 2026. This is an exploratory addendum to the [completed Sol/Luna experiment](full-experiment-results.md), not a replacement for it. The same 36 as-filed Tennessee education bills and frozen summary instruction were used for two additional configurations: `claude-sonnet-5-5` through the Claude API and locally served `google/gemma-4-31b-qat` Q4_0 through LM Studio. GPT-6 Astra applied the original source-only proposition inventories and frozen v2 coverage/factuality rubric to all 72 new summaries. The [execution record](cross-provider-extension-run.md), [four-model machine analysis](../data/extension/evaluation/four-model-analysis.json), and [unedited researcher packet](cross-provider-review-packet.md) preserve the method and evidence. The nine pilot bills remain excluded.

The comparisons below are descriptions of these **four model and runtime configurations on these 36 bills**. They are not an overall quality score, a statistical ranking, or evidence of corporate or model-family superiority. Astra's judgments are automated and are not ground truth.

## RQ1: measured linguistic complexity

The source-bill means, counting each bill once, were **18.77** Flesch-Kincaid grade (FK), **24.49** Flesch Reading Ease (FRE), and **12.32** Coleman-Liau Index (CLI). The table gives mean summary scores and mean summary-minus-source changes across 36 paired bills. Lower FK and CLI and higher FRE are the favorable *formula* directions. The final column counts bills whose summary moved favorably on FK / FRE / CLI; it does not measure actual comprehension.

| Model | FK mean (change) | FRE mean (change) | CLI mean (change) | Favorable bills, FK / FRE / CLI |
| --- | ---: | ---: | ---: | ---: |
| GPT-6 Sol | 11.70 (−7.06) | 45.75 (+21.26) | 13.02 (+0.70) | 35 / 34 / 11 |
| GPT-6 Luna | 13.60 (−5.17) | 38.88 (+14.39) | 13.59 (+1.27) | 32 / 31 / 7 |
| Claude Sonnet 5.5 | 10.13 (−8.64) | 56.14 (+31.65) | 10.96 (−1.36) | 36 / 36 / 33 |
| Gemma 4 31B QAT Q4_0 | 13.03 (−5.74) | 38.06 (+13.57) | 13.99 (+1.67) | 36 / 31 / 6 |

On these surface measures, Claude's summaries had the most favorable mean values across all three formulas. The formulas disagree on the other three models: their FK and FRE generally improved over source text, while CLI generally worsened. None of the formulas establishes that readers understood a summary better. The researcher perceived some longer Sonnet summaries as potentially harder to read; on the three reviewed bills, Sonnet's summaries were indeed longer than Gemma's, but all three formulas favored Sonnet. This is a concrete reason to keep formula scores and reader impressions distinct.

## RQ2: information coverage and factual consistency

Astra used the **same 184 core and 131 supporting source propositions for every model**. These pooled counts give `full / partial / omitted` judgments. The bill-mean full fraction weights each of the 36 bills equally; pooled counts give longer bills more influence because they contain more propositions.

| Model | Core full / partial / omitted | Core full fraction, bill mean | Supporting full / partial / omitted | Supporting full fraction, bill mean |
| --- | ---: | ---: | ---: | ---: |
| GPT-6 Sol | 125 / 55 / 4 | 0.810 | 75 / 37 / 19 | 0.815 |
| GPT-6 Luna | 121 / 56 / 7 | 0.761 | 78 / 35 / 18 | 0.825 |
| Claude Sonnet 5.5 | 144 / 38 / 2 | 0.922 | 97 / 21 / 13 | 0.911 |
| Gemma 4 31B QAT Q4_0 | 78 / 89 / 17 | 0.596 | 64 / 34 / 33 | 0.749 |

Claude received more `full` coverage judgments and Gemma fewer, especially for core propositions in long bills. `Partial` does not mean wholly absent; the saved item-level rationales explain which details Astra considered missing. The results describe Astra's application of the frozen rubric, not externally verified completeness.

Astra also broke each summary into its own atomic claims. The numbers of claims differ by model, so raw flag counts cannot be treated as comparable error rates.

| Model | Supported | Contradicted | Not established by supplied bill text | Total claims | Supported fraction, bill mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-6 Sol | 563 | 4 | 12 | 579 | 0.973 |
| GPT-6 Luna | 558 | 11 | 21 | 590 | 0.957 |
| Claude Sonnet 5.5 | 789 | 8 | 37 | 834 | 0.958 |
| Gemma 4 31B QAT Q4_0 | 463 | 22 | 37 | 522 | 0.891 |

Claude generated substantially more claims than the other configurations, consistent with its longer summaries. A `not_established` label can mark an explanatory expansion absent from the source, such as spelling out an acronym, without demonstrating changed legal effect. The claim-level quotes and rationales, rather than these counts alone, are needed to assess any material hallucination concern.

## RQ3: within-bill model differences and compression

Compression is summary whitespace words divided by source whitespace words. A smaller ratio means more shortening, not necessarily better simplification. These means use the same 36 bills for every model.

| Model | All 36 bills | Short 12 | Medium 12 | Long 12 | Long-bill core full fraction, bill mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-6 Sol | 0.427 | 0.502 | 0.442 | 0.337 | 0.653 |
| GPT-6 Luna | 0.443 | 0.462 | 0.496 | 0.369 | 0.609 |
| Claude Sonnet 5.5 | 0.758 | 0.997 | 0.768 | 0.509 | 0.806 |
| Gemma 4 31B QAT Q4_0 | 0.400 | 0.462 | 0.433 | 0.305 | 0.379 |

Claude's longer summaries coincided with higher Astra-rated core coverage; Gemma's stronger compression coincided with more `partial` and `omitted` judgments, especially in the long tertile. These are associations within this fixed prompt and configuration, not an experiment that isolates summary length as a cause. The [machine analysis](../data/extension/evaluation/four-model-analysis.json) includes all six within-bill model-pair differences for each separate measure, overall and by source-length tertile. Gemma's ratio was lower than Claude's for **all 36 bills**, yet Gemma's FK grade was higher for **34 of 36**, and its core-full fraction was lower for **22** and tied for **14**. For comparison with the original Sol arm, the mean Claude-minus-Sol differences were **−1.57 FK grade**, **+10.40 FRE**, **+0.331 compression ratio**, and **+0.112 core-full fraction**; the mean Gemma-minus-Sol differences were **+1.33 FK grade**, **−7.69 FRE**, **−0.027 compression ratio**, and **−0.214 core-full fraction**. Positive and negative signs describe numerical differences, not a combined preference.

## Limited researcher check and Astra comparison

Sam reviewed the six new summaries for the three bills selected before the original generation: **HB1228** (short, 94 source words), **HB0187** (medium, 274), and **HB0522** (long, 634). The [packet](cross-provider-review-packet.md), SHA-256 `84d993ac0543b594f0a5a3347409384fc989f2df65293c0b4bb7cea7bfc1cf0a`, records **“No Problem” for all six** on factual accuracy, material omissions, and changes to substantive meaning. It also records Sam's impression that Sonnet was more descriptive and Gemma seemed comparable on these examples. Those impressions were not formal readability scores or a representative model ranking. No specific problem passages were logged.

The packet's Claude entries leave “New Astra judgments viewed before saving?” blank, while the Gemma entries put “No Problem” in that field. In a subsequent clarification, Sam stated that **no new Astra judgments had been viewed before the notes were saved**. The original packet wording remains unchanged. It records review dates of November 2–3, without clock times. Prior knowledge of the original Sol/Luna Astra findings means this extension check was only partially blinded.

| Reviewed bill | Researcher issue log | New Astra comparison |
| --- | --- | --- |
| HB1228 | No problem observed for Claude or Gemma. | All source propositions were `full` for both; all 9 Claude and 4 Gemma claims were `supported`. |
| HB0187 | No problem observed for either. | Claude had all 7 propositions `full`; Gemma had 1 of 4 core propositions `partial` because it generalized the Senate and House report recipients. All 21 Claude and 17 Gemma claims were `supported`. |
| HB0522 | No problem observed for either. | Claude had 7 of 7 core propositions `full`; Gemma had 3 `full` and 4 `partial`, and Astra marked one supporting proposition `omitted` because Gemma did not mention the system's required alignment with named school discipline and safety provisions. Astra flagged one claim in each summary as `contradicted` for describing notification to a “school's threat assessment team” rather than the specified personnel serving on the LEA's or charter school's threat assessment team. It also marked each summary's expansion of `LEA` `not_established` because the supplied bill never expands the acronym. |

The researcher did not log Astra's HB0522 flags as material issues. This difference does not prove Astra is right or wrong: the check was a brief, problem-only inspection, not item-by-item human scoring, and Astra's recipient distinction needs legal-context judgment beyond this protocol. The one reviewed “long” bill had 634 source words; it does not inspect the sample's extreme long bills. Six summaries from one researcher cannot estimate evaluator accuracy, an error rate, expert agreement, or inter-rater reliability.

## Interpretation boundary and reproduction

This extension supports a narrow descriptive conclusion: under the recorded prompt and runtime settings, Claude produced longer summaries with more favorable formula scores and higher Astra-rated coverage, while the local Gemma configuration produced shorter summaries with lower Astra-rated core coverage and a lower bill-mean supported-claim fraction. The results do not justify calling either provider universally better. The common Astra evaluator is itself an OpenAI model, and the study has no independent claim-level gold standard; provider-specific decoding, quantization, and summary length may contribute to observed differences.

The exact raw generations and Astra assessments are under [`data/extension/`](../data/extension/). `python3 scripts/extension/aggregate_evaluation.py` rebuilds the 72 new metric records only after validating all source and evaluation records; `python3 scripts/extension/analyze_four_models.py` combines those records with the unchanged original 72 and rebuilds the four-model descriptors. The researcher notes remain separate from the machine analysis. No source, summary, inventory, rubric, or automated verdict was edited after seeing the notes.
