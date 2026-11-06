# Plain-Language Summaries of Tennessee Education Bills: Readability, Information Preservation, and Compression Across Four Language Model Configurations

Sam Burchfield  
INSC 499 Independent Study, University of Tennessee  
November 2026  

## Abstract

Large language models may help residents understand proposed legislation, but shorter and easier-scoring summaries are useful only when they preserve what a bill would do. This study tested four language model configurations on the same 36 as-filed Tennessee education bills: GPT-6 Sol, GPT-6 Luna, Claude Sonnet 5.5, and a locally served Gemma 4 31B QAT model. A separate nine-bill pilot established the sampling, prompting, and evaluation pipeline. Each model summarized every study bill using the same instruction. Three readability formulas measured surface linguistic complexity; a common GPT-6 Astra automated evaluator assessed coverage of source propositions and support for summary claims; and a word-count ratio measured compression. All four configurations improved mean Flesch-Kincaid grade and Flesch Reading Ease relative to the source bills, although the Coleman-Liau Index often disagreed. Information preservation varied more: Astra's bill-level mean full coverage of core propositions ranged from 0.596 for Gemma to 0.922 for Claude. Gemma was more compressed than Claude on all 36 bills, yet had a higher Flesch-Kincaid grade on 34 and lower Astra-rated core coverage on 22, with 14 ties. A limited researcher check found no substantive problem in 12 summaries from three preselected bills but did not establish evaluator accuracy. **The tested models generally reduced formula-measured linguistic complexity, while information preservation varied substantially; greater compression did not necessarily yield better readability or coverage.** These findings are descriptive for the tested bills, prompts, and model settings.

**Keywords:** legislative summarization; plain language; readability; information coverage; factual consistency; large language models.

## Introduction

Legislative bills describe proposed changes to law in language designed for precision and legislative procedure. A reader without legal training may have difficulty identifying which people or agencies a bill affects, what actions it requires or permits, and when a change would take effect. Public-facing bill trackers and civic information systems can place a plain-language summary between a bill and the resident trying to understand it. If that summary omits a condition or misidentifies an agency, the reader may misunderstand the proposal even when the prose is easy to skim. A summary can also describe a cited statute whose contents are absent from the bill text.

This project studies that tension in Tennessee education legislation. It began with a validated corpus of bills from the 114th Tennessee General Assembly and developed a reproducible way to select education bills of different lengths. A nine-bill pilot tested the prompt and evaluation pipeline. The main experiment then compared two OpenAI models on 36 bills. A prospective extension added one Anthropic model and one locally served Google model to the same bills and evaluation method. The extension was recorded before its scored generation, so the added models could be compared with the original outputs without changing the sample or rubric after seeing results.

The study addresses the three questions established in Project Report 1:

1. To what extent do generated plain-language summaries reduce the measured linguistic complexity of Tennessee legislative bills?
2. To what extent do they preserve substantive information and factual consistency with the source legislation?
3. How do different LLMs compare in the tradeoff between reducing linguistic complexity and preserving substantive information and factual consistency?

The central finding is that simplification and preservation do not move together automatically. All four configurations improved some formula scores, but their coverage and factuality judgments differed. The most compressed configuration did not have the most favorable formula scores or the highest coverage.

## Related work

Readability formulas are common in legal-text research, but their use is not a direct test of understanding. Han et al. (2024) surveyed readability measures in legal and regulatory texts and found that applications cluster in a few domains, especially informed-consent documents. Their review supports measuring legal text carefully without assuming that a familiar formula has been validated for every kind of legislation. Cachola et al. (2025) evaluated readability measures for plain-language summaries and found that traditional formulas often correlate poorly with human judgments. In medical-text simplification, Devaraj et al. (2021) likewise showed that differences between technical and lay language can extend beyond surface features captured by established formulas. These studies motivate using several formula measures here and describing them as indicators of linguistic form rather than comprehension scores.

Factual quality is a separate concern. Devaraj et al. (2022) distinguish information insertion, deletion, and substitution in text simplification. This distinction matters for bills: a summary can make only supported statements while leaving out a material requirement, or it can mention the right topic while changing who must act. The present study therefore evaluates source-to-summary **coverage** separately from summary-to-source **factual consistency**. Laban et al. (2024) make coverage an explicit dimension of long-context summarization evaluation, although their multi-document task differs from summarizing one legislative bill. Research on multi-document hallucinations also shows that fluent summaries can introduce unsupported content; its rates should not be transferred to this single-bill setting (Belém et al., 2025).

Automated factuality judgments require their own caution. Mujahid et al. (2026) stress-tested factual-consistency metrics for long-document summaries, including legal material, and found instability under meaning-preserving changes. That work does not evaluate this study's Astra rubric directly, but it reinforces the need to retain source passages and reasons for individual judgments and to avoid treating an automated verdict as legal ground truth.

## Methods

### Corpus, domain, and sample

The research corpus contains **2,684** cleaned Tennessee House bill records from the 114th General Assembly (2025–2026). Text came from as-filed or introduced bill documents retrieved through LegiScan and extracted from the official PDFs. The project corrected a document-version selection error before analysis and validated the final corpus with **zero error-level findings**; remaining warnings were documented, chiefly current-sponsor versus as-filed-sponsor differences. Sponsor fields were not used in summary generation. The models received each bill's cleaned `bill_text`, not a LegiScan description, later bill status, or outside statutory text. This matters because the task was to summarize the **proposal as filed**, not to explain current or enacted law. The [dataset documentation](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/dataset.md) and [validation record](https://github.com/sburchfield/tn-legislative-ai-study/tree/main/data/validation) describe acquisition and checking.

The study **prespecified** an education definition using **18 subject labels** before drawing any study bills. It yielded **336 bills**; the exact label `Education` alone covered only 106. The education subset's bill-text lengths were strongly right-skewed, so the study used original length tertiles and included short amendment-only and long-tail cases. Nine bills were drawn for a diagnostic pilot and excluded from the main experiment. From the remaining 327, a deterministic SHA-256 ranking selected **36 bills**: 12 from each original short, medium, and long tertile, with a prespecified allocation inside the short and long tails. The selected sources ranged from **57 to 3,061 whitespace-separated words**. No bill was replaced based on model performance. The [sampling assessment](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/pilot-sampling-assessment.md), [final design](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/full-experiment-design-draft.md), and [sample manifest](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/data/full/sample.json) contain the inclusion labels, seeds, cell allocation, and text hashes. This purposeful, length-balanced sample supports pipeline and within-bill comparisons; it is not a probability estimate for all Tennessee bills.

### Summary generation

Each of the four configurations generated one summary per selected bill, for **144 summaries**. The original arms used `gpt-6-sol` and `gpt-6-luna` through the OpenAI Responses API. The prospective extension used `claude-sonnet-5-5` through the Claude API and `google/gemma-4-31b-qat` locally through LM Studio, with the downloaded Q4_0 model file recorded by hash. Every request used the same [plain-language instruction](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/prompts/pilot-summary-v1.txt) and a one-field JSON output schema. The instruction asked for neutral prose for adults without legal training, material actors and conditions, and proportional concision; it forbade treating a proposal as enacted law or inferring the contents of statutes merely cited by the bill. Requests were independent, without retrieval, tools, or prior conversation. The raw requests, responses, exact returned model IDs, settings, usage, and unedited summaries were saved.

Provider controls were documented rather than assumed equivalent. Sol and Luna used medium reasoning effort; Claude used its medium effort setting; the local Gemma configuration used reasoning off after an unscored feasibility check showed that default reasoning could consume the output allowance. All arms allowed up to 8,192 output tokens, but their APIs and tokenizers differ. A full-sample preflight confirmed the selected sources fit the loaded Gemma context. The [original execution record](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/full-experiment-run.md) and [extension record](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/cross-provider-extension-run.md) contain the exact settings and hashes.

### Measures and analysis

The study kept four outcomes separate:

1. **Formula-measured linguistic complexity.** `textstat==0.7.13`, configured for U.S. English with a pinned pronunciation dictionary, calculated Flesch-Kincaid Grade Level (FK), Flesch Reading Ease (FRE), and Coleman-Liau Index (CLI) on each full cleaned bill text and exact generated summary. Lower FK and CLI and higher FRE are favorable formula directions. FK and FRE share sentence, word, and syllable inputs, so they are not independent evidence of comprehension. Headers, citations, and enactment language remain in the source text and may affect scores.
2. **Information coverage.** GPT-6 Astra first extracted one source-only inventory of operative propositions per bill, marking each `core` or `supporting`. The same inventory was then used for all four summaries of that bill. Astra marked each proposition `full`, `partial`, or `omitted` using the frozen materiality instructions and saved quoted evidence and a reason. `Partial` means some content was retained but Astra judged a material detail missing or changed; it is not equivalent to complete omission.
3. **Factual consistency.** Astra split each summary into atomic claims and classified each against only the supplied bill text as `supported`, `contradicted`, or `not_established`, with excerpts and reasons. Source omissions belong to coverage rather than this claim-level measure. A versioned validator checked that cited source and summary passages appeared in the supplied texts after narrowly defined PDF line-wrap normalization. Quote matching checks provenance, not the correctness of Astra's interpretation.
4. **Compression.** The ratio is summary whitespace words divided by source whitespace words. A smaller ratio indicates more shortening; it is not a quality score.

The analysis reports descriptive results for the **same 36 bills** for each model, including bill-weighted means and pooled proposition or claim counts. The length tertiles each contain 12 sampled bills. No hypothesis test, confidence interval, composite score, or general model ranking was planned. The [machine analysis](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/data/extension/evaluation/four-model-analysis.json) includes six within-bill model-pair differences and their directional counts for each separate measure. The nine-bill pilot remained a method-development exercise and was not pooled into these results.

### Limited researcher check

A separate prespecified draw chose **HB1228** (short), **HB0187** (medium), and **HB0522** (long) before any full-experiment generation. Sam Burchfield inspected each summary against its as-filed source for factual errors, material omissions, or changes to substantive meaning, with source passages requested for any issue. The [original packet](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/full-experiment-review-packet.md) dates the Sol/Luna reviews to October 31–November 1 and records “No” to viewing Astra judgments before saving each note. The [extension packet](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/cross-provider-review-packet.md) dates the Claude/Gemma reviews to November 2–3. Its Claude Astra-viewing fields are blank, and its Gemma fields say “No Problem” rather than answering that question; Sam subsequently clarified that he had not viewed any **new** Astra judgments before saving those notes. Because the original Astra findings could already be known during the extension review, that second stage was only partially blinded. The check covered **12 summaries on three bills** in two stages. It was a limited researcher sanity check, not formal human scoring, domain-expert validation, or an inter-rater reliability study.

## Results

### RQ1: surface complexity generally fell

Across the 36 source bills, mean FK was **18.77**, mean FRE was **24.49**, and mean CLI was **12.32**. Table 1 shows the model means. Each source is counted once for each model comparison. Compression is included for later comparison, but it is not a readability formula.

**Table 1. Mean formula scores and compression ratio across 36 paired bills**

| Model configuration | FK grade ↓ | FRE ↑ | CLI ↓ | Summary/source word ratio |
| --- | ---: | ---: | ---: | ---: |
| GPT-6 Sol | 11.70 | 45.75 | 13.02 | 0.427 |
| GPT-6 Luna | 13.60 | 38.88 | 13.59 | 0.443 |
| Claude Sonnet 5.5 | 10.13 | 56.14 | 10.96 | 0.758 |
| Gemma 4 31B QAT Q4_0 | 13.03 | 38.06 | 13.99 | 0.400 |

All four models lowered mean FK and raised mean FRE relative to the full bill texts. At the bill level, FK fell for **35/36 Sol**, **32/36 Luna**, **36/36 Claude**, and **36/36 Gemma** summaries. CLI showed a different pattern: it fell for **11/36 Sol**, **7/36 Luna**, **33/36 Claude**, and **6/36 Gemma** summaries. Thus “easier to read” would overstate the evidence. The defensible RQ1 finding is lower **formula-measured** complexity on FK and FRE for most outputs, with disagreement from CLI and no direct measure of reader comprehension.

### RQ2: preservation varied by model and bill length

Astra's common inventories contained **184 core** and **131 supporting** propositions across the 36 bills. Table 2 gives the mean fraction marked `full` within a bill, then averaged equally across bills. These means differ from pooled proposition fractions because long bills contribute more individual propositions. The claim column is the mean within-bill fraction Astra marked `supported`; claim segmentation and claim totals differ across models.

**Table 2. Bill-weighted means of Astra's automated judgments**

| Model configuration | Core propositions full | Supporting propositions full | Summary claims supported |
| --- | ---: | ---: | ---: |
| GPT-6 Sol | 0.810 | 0.815 | 0.973 |
| GPT-6 Luna | 0.761 | 0.825 | 0.957 |
| Claude Sonnet 5.5 | 0.922 | 0.911 | 0.958 |
| Gemma 4 31B QAT Q4_0 | 0.596 | 0.749 | 0.891 |

The pooled core-proposition judgments show the scale of the difference. For Sol, Astra marked **125 full, 55 partial, and 4 omitted**; for Luna, **121, 56, and 7**; for Claude, **144, 38, and 2**; and for Gemma, **78, 89, and 17**. Supporting propositions showed a similar, though smaller, contrast between Claude and Gemma. On the 12 long bills, the mean core-full fraction was **0.806 for Claude**, **0.653 for Sol**, **0.609 for Luna**, and **0.379 for Gemma**. The long-bill result matters because the corpus is length-skewed and dense bills contain more distinct obligations and conditions.

Astra evaluated **579 Sol**, **590 Luna**, **834 Claude**, and **522 Gemma** atomic summary claims. It marked **4, 11, 8, and 22**, respectively, as `contradicted`, and **12, 21, 37, and 37** as `not_established`. Those raw counts are not verified error rates: Claude's longer summaries generated many more claims, and an ordinary explanatory expansion such as spelling out `LEA` can be labeled `not_established` when the bill text does not define it. Coverage and factual consistency therefore answer different parts of RQ2. A concise summary may contain few unsupported claims yet omit a substantial source provision.

### RQ3: more shortening did not ensure better outcomes

Claude's mean summary/source word ratio was **0.758** and Gemma's was **0.400**. The same-bill comparison is especially clear: **Gemma was more compressed than Claude on all 36 bills**, but its FK grade was higher on **34 of 36**. Astra's core-full fraction was lower for Gemma on **22** bills and tied on **14**; it was never higher in this pair. Mean FRE also favored Claude (**56.14 versus 38.06**). The pattern supports the paper's central point that greater shortening did not necessarily produce better formula readability or information coverage. It does not establish that shortening caused the difference, because the tested models and provider settings also differed.

The length strata add context. On the 12 short bills, Claude's mean compression ratio was **0.997**, close to source length, whereas its core propositions were all marked `full` by Astra. On the 12 long bills, Claude's mean ratio was **0.509** and Gemma's **0.305**, while their mean core-full fractions were **0.806** and **0.379**. Shorter output was associated with more partial and omitted propositions in the Gemma configuration. This finding does not imply that the longest possible summary is preferable; the prompt asked for proportional concision, and the study did not manipulate output length independently of model identity.

### Researcher observations

The researcher marked **no substantive problem** for any of the 12 summaries reviewed across the three selected bills. In the extension notes, Sam described Sonnet as more detailed and expressed an impression that the local Gemma summaries seemed comparable on those examples. Those are impressions from three bills, not formal readability scores or evidence of equal performance across the full sample. On those same three bills, Sonnet's summaries were longer than Gemma's but received more favorable values from all three formulas, illustrating that perceived reading effort and formula scores can diverge.

Comparing the saved notes with Astra shows both agreement and different emphases. For HB1228, Astra marked all inventoried propositions and claims fully covered or supported for both extension models. For HB0187, Astra marked one Gemma core proposition `partial` because the summary generalized report recipients; the researcher recorded no material issue. For HB0522, Astra marked several Gemma propositions `partial`, one supporting proposition `omitted`, and flagged a claim in each extension summary about who receives a threat-assessment notification. The researcher did not log those as material problems. These examples cannot adjudicate Astra's accuracy because the review was problem-only rather than an item-by-item independent scoring exercise. The reviewed long bill had **634 words**, far below the longest selected source, so the check does not validate performance on extreme long texts.

## Discussion

The project sought an accessible summary that also retains the bill's substantive action. The two goals should not be collapsed into a single score. The RQ1 results show that all four tested configurations generally reduced FK grade and raised FRE, but CLI disagreed for three of them and no participant comprehension test was conducted. The RQ2 results show a wider spread in Astra-rated coverage and supported-claim fractions. The RQ3 comparison makes the tradeoff concrete: the locally served Gemma configuration shortened every bill more than Claude did, while Claude generally had more favorable formula scores and higher automated coverage. A shorter summary can reduce text without simplifying the difficult words or preserving the legal conditions that matter.

The stronger coverage of Claude's longer summaries should also be read carefully. More words can give a model room to preserve actors, exceptions, reporting recipients, and dates, but the design did not hold model identity constant while varying only output length. Claude also produced more claims, creating more opportunities for Astra to mark a claim `not_established` or `contradicted`. The four-model comparison is therefore about observed configurations under one shared instruction, not an estimate of a universal effect of compression or a ranking of corporations.

The study's source boundary is another deliberate constraint. An as-filed bill may cite a code section without restating its existing contents. The prompt prohibited filling that gap with outside information. This helps prevent unsupported legal explanations, but it also means a summary may be less informative than a broader legal explainer. The intended product in this experiment is a faithful description of what the supplied bill text proposes.

For civic information systems, the findings suggest presenting a generated summary alongside its source bill and provenance, while treating summary length as only one design choice. A system that optimizes for brief text alone could hide conditions or reporting duties even when its output appears fluent. This is a design implication from the descriptive results, not an interface intervention tested here.

## Limitations

The 36 bills were selected from an operational 18-label education subset with deliberate length balancing and tail coverage. They are neither a random sample of all Tennessee legislation nor a representative sample of enacted education law. The source texts include PDF extraction artifacts, headers, citations, and legislative boilerplate that can influence formula scores. FK and FRE share inputs, and none of the three formulas measures whether an adult reader can explain the bill correctly.

Astra is one automated evaluator, and it is an OpenAI model. Using it for every arm makes the rubric common, but its judgments may still favor particular wording or miss legal distinctions. Evidence-quote validation confirms that excerpts come from the supplied texts, not that the verdicts are substantively correct. Counts of atomic claims depend on how Astra splits a summary; the `not_established` category includes source-absent explanatory glosses as well as possible unsupported claims. The three-bill researcher check involved one student, no formal claim-by-claim scoring, and no expert or second reviewer. It cannot establish factual error rates, evaluator accuracy, or inter-rater reliability. The extension check was only partially blinded because the original models' Astra results could be known.

The four arms also differ in provider APIs, decoding controls, and local quantization. Gemma was tested as one Q4_0 file with reasoning off, rather than as every Gemma deployment. OpenAI model identifiers in the original account had no dated snapshots available at execution, although exact requested and returned identifiers were saved. The experiment did not manipulate summary length independently, test multiple prompts, or measure actual public comprehension. These limits confine the conclusions to the recorded configurations and documents.

## Conclusion

On the same 36 Tennessee education bills, four language model configurations generally reduced **formula-measured linguistic complexity**, especially on Flesch-Kincaid grade and Flesch Reading Ease. Their preservation of source propositions and support for summary claims varied substantially. The clearest comparison was between Claude and local Gemma: Gemma compressed every bill more, yet Claude more often received favorable formula scores and Astra-rated core coverage. **Greater compression did not necessarily produce better readability or coverage.** A useful legislative summary should be judged on how clearly it communicates *and* on whether it preserves the actors, conditions, and legal effects present in the source. A reader study would be needed to establish actual comprehension, and independent legal review would be needed to verify factual accuracy beyond the limited checks performed here.

## References

Belém, C. G., Pezeshkpour, P., Iso, H., Maekawa, S., Bhutani, N., & Hruschka, E. (2025). From single to multi: How LLMs hallucinate in multi-document summarization. In *Findings of the Association for Computational Linguistics: NAACL 2025* (pp. 5291–5324). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.findings-naacl.293

Cachola, I., Khashabi, D., & Dredze, M. (2025). Evaluating the evaluators: Are readability metrics good measures of readability? In *Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing* (pp. 24011–24027). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.emnlp-main.1225

Devaraj, A., Marshall, I., Wallace, B., & Li, J. J. (2021). Paragraph-level simplification of medical texts. In *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies* (pp. 4972–4984). Association for Computational Linguistics. https://doi.org/10.18653/v1/2021.naacl-main.395

Devaraj, A., Sheffield, W., Wallace, B., & Li, J. J. (2022). Evaluating factuality in text simplification. In *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 7331–7345). Association for Computational Linguistics. https://doi.org/10.18653/v1/2022.acl-long.506

Han, Y., Ceross, A., & Bergmann, J. H. M. (2024). *The use of readability metrics in legal text: A systematic literature review* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2411.09497

Laban, P., Fabbri, A., Xiong, C., & Wu, C.-S. (2024). Summary of a haystack: A challenge to long-context LLMs and RAG systems. In *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing* (pp. 9885–9903). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.emnlp-main.552

Mujahid, Z. M., Wright, D., & Augenstein, I. (2026). Stress testing factual consistency metrics for long-document summarization. In *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 31914–31933). Association for Computational Linguistics. https://doi.org/10.18653/v1/2026.acl-long.1472

## Study materials and reproducibility

The public project repository is **https://github.com/sburchfield/tn-legislative-ai-study**. It includes the exact [36-bill manifest](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/data/full/sample.json), [generation prompt](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/prompts/pilot-summary-v1.txt), [full-study design](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/full-experiment-design-draft.md), [extension protocol and execution record](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/cross-provider-extension-run.md), [original results](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/full-experiment-results.md), and [four-model analysis](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/data/extension/evaluation/four-model-analysis.json). The raw model responses and Astra records are under `data/full/` and `data/extension/`. The [journal](https://github.com/sburchfield/tn-legislative-ai-study/blob/main/docs/journal.md) records sampling, pilot adjustments, API interruptions, validation, reviewer notes, and later analysis-only additions. The November 4 direction-count addition changed only the derived paired analysis; it did not change the source texts, generated summaries, evaluator rubric, or verdicts.
