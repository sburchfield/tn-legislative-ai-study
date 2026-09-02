# Evaluating AI-Mediated Transformations of Legislative Text

This repository contains the data, code, methodology, and results for an independent research project conducted as part of INSC 493 at the University of Tennessee, Knoxville.

## Project Overview

Legislative documents are often lengthy, complex, and difficult for non-expert audiences to interpret. Large language models (LLMs) provide an opportunity to transform legislative text into more accessible representations, such as summaries and plain-language explanations.

This project examines how AI-mediated transformations affect the accessibility of legislative information. Using Tennessee legislative bills as the source material, the study will compare original legislative text with AI-generated representations using computational measures of readability, linguistic complexity, information density, and information preservation.

The project will also investigate differences between multiple large language models when transforming the same source material.

## Research Questions

### Primary Research Question

**RQ1:** How do AI-mediated transformations of legislative text affect measurable information accessibility compared with the original legislative text?

### Secondary Research Questions

**RQ2:** How do different forms of AI-mediated transformation, such as summaries and plain-language explanations, differ in readability, linguistic complexity, and information preservation?

**RQ3:** To what extent do different large language models vary in their ability to produce accessible representations of legislative text while preserving source information?

## Methodology

The study will use a computational evaluation approach rather than a human-subjects usability study.

The general experimental pipeline is:

1. Collect legislative source documents.
2. Clean and normalize the legislative text and associated metadata.
3. Select a representative research sample.
4. Submit identical source material and prompts to selected LLMs.
5. Store the generated representations along with model and prompt metadata.
6. Evaluate the original and generated texts using computational metrics.
7. Compare results across representations and models.

The exact models, prompts, evaluation metrics, and sampling methodology will be documented as the study progresses.

## Dataset

The source dataset consists of legislative information from the Tennessee General Assembly.

The research dataset is exported from the [LegiScan API](https://legiscan.com/legiscan), a public API for programmatic reuse of state legislative data, whose source for Tennessee bill text is the official PDFs published by the Tennessee General Assembly. The cleaned version retains only the legislative text and metadata required to reproduce the study.

The cleaned dataset includes:

- Bill number / identifier
- Bill title or caption
- Legislative text
- Sponsor and subject metadata
- Companion-bill linkage (House/Senate)

Full provenance, schema, and reproduction instructions are documented in [docs/dataset.md](docs/dataset.md).

## Evaluation

The study will investigate several dimensions of AI-mediated legislative text transformation.

Potential measures include:

### Readability

- Flesch Reading Ease
- Flesch-Kincaid Grade Level
- Gunning Fog Index
- SMOG Index

### Linguistic Characteristics

- Word count
- Sentence count
- Average sentence length
- Lexical characteristics

### Information Transformation

- Compression ratio
- Information density
- Information preservation
- Factual consistency / fidelity

The final evaluation methodology will be informed by the literature review and documented before the full experiment is conducted.

## Repository Structure

```text
.
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── samples/
│
├── docs/
│   ├── methodology.md
│   ├── research-questions.md
│   └── research-journal.md
│
├── literature/
│   └── bibliography.md
│
├── prompts/
│
├── scripts/
│   ├── export/
│   ├── cleaning/
│   └── evaluation/
│
├── results/
│   ├── raw/
│   └── processed/
│
└── README.md