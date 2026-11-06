# Full experiment: descriptive results and researcher check

**Recorded:** November 1, 2026. This report interprets the frozen 36-bill full-experiment sample and the six source-only issue logs completed by Sam Burchfield. The [design](full-experiment-design-draft.md), [execution record](full-experiment-run.md), [review packet](full-experiment-review-packet.md), and [machine-readable paired analysis](../data/full/evaluation/paired-analysis.json) provide the methods and underlying records. The nine pilot bills are excluded. These are exploratory descriptions, with no overall quality score or statistical inference.

## RQ1: measured linguistic complexity

The table gives **means across 36 bills**, counting each source once. Changes compare each unedited summary with its own full as-filed source. Lower Flesch-Kincaid Grade Level (FK) and Coleman-Liau Index (CLI), and higher Flesch Reading Ease (FRE), indicate a more favorable *formula* result. They do not establish reader comprehension.

| Measure | Source | Sol summary | Sol minus source | Luna summary | Luna minus source | Bills changing favorably, Sol / Luna |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FK grade | 18.77 | 11.70 | −7.06 | 13.60 | −5.17 | 35 / 32 |
| FRE | 24.49 | 45.75 | +21.26 | 38.88 | +14.39 | 34 / 31 |
| CLI | 12.32 | 13.02 | +0.70 | 13.59 | +1.27 | 11 / 7 |

FK and FRE generally move in the favorable direction for both models, while CLI generally moves in the unfavorable direction. This formula disagreement, also seen in the pilot, is central to interpreting RQ1: the summaries are shorter and score better on two formulas, but a single readability value cannot stand in for actual clarity. Bill formatting and legal citations also affect these surface measures. The source-to-summary changes and direction counts are included overall and by original length tertile in `paired-analysis.json`.

## RQ2: information coverage and factual consistency

GPT-6 Astra produced one source-only proposition inventory per bill and applied that same inventory to the two summaries. These **pooled proposition counts** describe Astra's judgments; longer bills contribute more propositions.

| Proposition importance | Source propositions | Sol full / partial / omitted | Luna full / partial / omitted |
| --- | ---: | ---: | ---: |
| Core | 184 | 125 / 55 / 4 | 121 / 56 / 7 |
| Supporting | 131 | 75 / 37 / 19 | 78 / 35 / 18 |

At the bill level, the mean fraction of core propositions Astra marked `full` was **0.810 for Sol** and **0.761 for Luna**; the corresponding supporting fractions were **0.815** and **0.825**. The bill-level means weight each bill equally, so they should not be confused with the pooled counts above. Many judgments were `partial`, especially in longer bills; a `partial` judgment needs its recorded rationale, not automatic treatment as a wholly missing provision.

| Atomic summary claims judged by Astra | Supported | Contradicted | Not established by supplied text | Total |
| --- | ---: | ---: | ---: | ---: |
| Sol | 563 | 4 | 12 | 579 |
| Luna | 558 | 11 | 21 | 590 |

The models generated different numbers of atomic claims, and Astra's claim boundaries are its own. These counts are **automated source-grounded judgments**, not measured factual error rates or proof that one model is more accurate. In particular, `not_established` includes explanatory expansions absent from the supplied bill text, which need not change the bill's legal effect. The saved claim-level rationales and evidence remain necessary for interpreting individual flags.

## RQ3: paired model differences and compression

Every Sol/Luna difference below is calculated **within the same bill** and then averaged across bills; a positive value means Luna is higher. Compression is summary whitespace words divided by source whitespace words. A smaller ratio is not automatically preferable.

| Original source length | Bills | Luna − Sol FK grade | Luna − Sol FRE | Luna − Sol CLI | Luna − Sol compression ratio | Luna − Sol core-full fraction | Luna − Sol supported-claim fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All | 36 | +1.89 | −6.87 | +0.57 | +0.015 | −0.049 | −0.016 |
| Short | 12 | +2.62 | −11.43 | +1.37 | −0.040 | 0.000 | +0.009 |
| Medium | 12 | +1.76 | −5.37 | +0.29 | +0.054 | −0.102 | −0.028 |
| Long | 12 | +1.30 | −3.81 | +0.07 | +0.032 | −0.044 | −0.030 |

The overall mean compression ratios were **0.427 for Sol** and **0.443 for Luna**. Sol generally received more favorable formula readability scores, while Astra's separate coverage and factuality judgments show smaller, mixed differences. The three-bill researcher notes below illustrate why a formula preference should not be described as a reader preference. These exploratory differences do not establish a general model ranking.

## Independent, limited researcher check

The three bills were selected reproducibly before generation: **HB1228 (short), HB0187 (medium), and HB0522 (long)**. Sam reviewed both summaries against each as-filed source and marked **“No problem observed” for all six** on the requested issues: factual accuracy, material omission, and substantive-meaning change. The packet records review dates (October 31 or November 1), but not clock times, and marks that Astra judgments had not been viewed before saving. Sam subsequently confirmed that the HB0187 comment about lost “context and meaning” was a **readability/context preference**, not a reported material omission or substantive change. Sam also clarified that “Astra” in that note meant **Luna**; Astra's evaluation had not been viewed. The original issue logs and wording remain preserved in the packet.

The comparison with Astra is qualitative:

| Bill | Researcher observation | Astra comparison |
| --- | --- | --- |
| HB1228 | No issue in either summary. Sam preferred Luna's readability despite Sol's more exact statutory citation. | All inventoried propositions were `full`; all 3 Sol and 4 Luna claims were `supported`. |
| HB0187 | No issue logged. Sam found Luna easier to understand than Sol's unexplained statutory reference. | Luna had all 7 propositions `full` and all 15 claims `supported`. For Sol, Astra marked 3 of 7 propositions `partial` and 2 of 15 claims `not_established`, concerning the scope of the comptroller's review/report and the wording of the House recipient. Sam did not log these as material problems. |
| HB0522 | No issue in either summary. Sam found comparable detail and noted that Sol uses more exact code citations. | Astra marked some propositions `partial` in both summaries, with no omissions or contradictions. It marked one abbreviation expansion in each summary `not_established` because the supplied bill does not expand `LEA`; that flag alone does not demonstrate a change in legal effect. |

Thus, the check illustrates both agreement and differences in emphasis. It does **not** validate Astra's 72-summary judgments: one researcher reviewed only six summaries, did not formally score every proposition or claim, and was not a domain-expert panel. There is no inter-rater reliability estimate or statistically meaningful estimate of an error rate. Astra is a different OpenAI model from both generators, but its interpretation remains automated and may overstate or miss material issues. The study covers as-filed texts in a selected Tennessee education subset and two models from one provider; results should not be generalized to enacted law, all bills, or all readers.

## Reproduction boundary

`python3 scripts/full/analyze_paired.py` derives all tabulated descriptive values from the frozen [`metrics.json`](../data/full/evaluation/metrics.json), using the sample manifest and paired bill IDs. It now includes each source's readability values once per bill, summary-minus-source changes, and favorable-direction counts alongside the original paired model and evaluator measures. The researcher notes are separate from that machine analysis; no rubric, model output, evaluator verdict, or original issue log was edited in response to the comparison.
