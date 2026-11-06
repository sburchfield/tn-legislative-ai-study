# Tennessee Legislative AI Study

INSC 499 independent study, University of Tennessee, Knoxville — Sam Burchfield, 2026.

This repository contains the dataset, frozen methods, raw model outputs, evaluation records, and [final paper draft](docs/final-paper.md) for a study of plain-language summaries of Tennessee education bills.

## Main finding

The four tested model configurations generally reduced formula-measured linguistic complexity, but information preservation varied substantially. Greater compression did not necessarily produce better readability or coverage. These are descriptive findings for the sampled bills and recorded model settings, not a general ranking of model providers.

## Research questions

1. To what extent do LLM-generated plain-language summaries reduce the measured linguistic complexity of Tennessee legislative bills?
2. To what extent do they preserve the substantive information and factual consistency of the source legislation?
3. How do different LLMs compare in the tradeoff between reducing linguistic complexity and preserving substantive information and factual consistency?

## Study at a glance

- **Corpus:** 2,684 validated, cleaned as-filed House bills from the 114th Tennessee General Assembly. [Provenance and schema](docs/dataset.md).
- **Domain:** 336 bills in a frozen 18-label education subject set. A separate nine-bill [pilot](docs/pilot-evaluation-run.md) tested the pipeline.
- **Scored sample:** 36 education bills, excluding the pilot, selected reproducibly with 12 in each original source-length tertile. [Design](docs/full-experiment-design-draft.md) and [manifest](data/full/sample.json).
- **Summarizers:** GPT-6 Sol, GPT-6 Luna, Claude Sonnet 5.5, and local Gemma 4 31B QAT Q4_0, each producing one summary for every scored bill under the same [instruction](prompts/pilot-summary-v1.txt).
- **Evaluation:** Three pinned readability formulas; source-proposition coverage and claim-level factual consistency judged by GPT-6 Astra; and a whitespace-word compression ratio. The dimensions remain separate. One researcher performed a limited, source-based problem check on 12 summaries from three preselected bills; it is not expert validation.

## Results and reproduction

The [final paper](docs/final-paper.md) presents the method, results, limitations, and literature. The [original Sol/Luna results](docs/full-experiment-results.md) and [cross-provider extension results](docs/cross-provider-extension-results.md) provide detailed descriptive tables and reviewer comparisons. Exact generation and evaluation settings, raw-response logging, hashes, API interruptions, and validation are recorded in the [original run](docs/full-experiment-run.md), [extension run](docs/cross-provider-extension-run.md), and [chronological journal](docs/journal.md).

The frozen corpus is in `data/cleaned/`; sample manifests, raw responses, and automated evaluation records are under `data/pilot/`, `data/full/`, and `data/extension/`. Scripts for validation, selection, generation, evaluation, and analysis are under `scripts/`. The original and extension metric files are [`data/full/evaluation/metrics.json`](data/full/evaluation/metrics.json) and [`data/extension/evaluation/metrics.json`](data/extension/evaluation/metrics.json); the [four-model paired analysis](data/extension/evaluation/four-model-analysis.json) is derived from them. The full-study design and execution records specify the commands and exact frozen inputs needed to validate or rebuild these derived files.
