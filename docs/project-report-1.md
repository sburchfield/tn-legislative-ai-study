Project Report 1
Tennessee Legislative AI Study
INSC 499 Independent Study
Sam Burchfield
September 18, 2026
Progress to Date
Phase
Status
Research proposal
Complete
Data acquisition
Complete
Data cleaning
Complete
Dataset validation
Complete
Initial literature review
Complete
Research questions
Complete
Experimental design
In progress
Pilot experiment
Next
Full experiment
Pending
Analysis
Pending
Final paper
Pending

1. Project Overview
This independent study investigates the use of large language models (LLMs) to produce plain-language summaries of Tennessee legislative bills. Legislative text is written for legal and governmental purposes and can be difficult for members of the general public to interpret. LLMs may provide a practical method for reducing the linguistic complexity of legislation, but simplification is only useful if the resulting summaries preserve the substantive meaning of the source material.
The project therefore focuses on two related goals: accessibility and information preservation. Rather than treating a lower readability grade level as sufficient evidence of a successful summary, the study will evaluate generated summaries across multiple dimensions, including linguistic complexity, information coverage, factual consistency, and compression. The study will also compare multiple LLMs to determine whether different models produce different tradeoffs between simplification and preservation of meaning.
Project repository: https://github.com/sburchfield/tn-legislative-ai-study
2. Data Collection and Preparation
A major portion of the work completed during the first phase of the project involved creating a reliable corpus of Tennessee legislation for use in the experiment. The project initially used data collected from Tennessee legislative sources and stored in DynamoDB. During review of the dataset, however, several issues made it necessary to reconsider the acquisition and cleaning process. Direct scraping of the Tennessee legislative website was also restricted, so the project transitioned to the LegiScan API as the primary source for legislative data.
The dataset was then cleaned so that the experimental corpus contained bill text and only the metadata necessary for the study. Particular attention was given to selecting the correct version of each bill. During spot checking, an instance was discovered in which an older public chapter had been associated with a bill from the current General Assembly. The selection logic was corrected to prefer Draft or Introduced versions when identifying the as-filed bill text, and regression tests were added to reduce the likelihood of the error recurring.
One remaining metadata limitation is that the sponsor field reflects the sponsor associated with the current bill record, while the selected bill text represents the as-filed version. This distinction is documented and will be considered when determining which metadata fields are used in the analysis.
A custom validation process was implemented in Go to check the completed dataset. The final validation run contained 2,684 records and produced 0 ERROR-level findings. The validation process also produced warnings and a manual-review set for additional spot checking. Based on these checks, the corpus is considered sufficiently clean to proceed to experimental sampling and model evaluation.
3. Literature Review
The initial literature review included seven papers selected for their relevance to legal readability, plain-language and text simplification, long-document summarization, hallucination, factual consistency, and evaluation methodology. The papers were read and annotated, and the most relevant findings were organized into a literature matrix containing each paper's research problem, methodology, evaluation measures, major findings, limitations, and relevance to this study.
One major theme in the literature is that traditional readability formulas provide useful descriptive measures of linguistic complexity but should not be treated as direct measures of human comprehension. Legal-readability research demonstrates the long history of applying readability formulas to legal and governmental text, while more recent work evaluating readability metrics shows that formula-based scores may correlate only weakly with human judgments in plain-language summarization settings. This suggests that the present study should use multiple readability measures and interpret them as indicators rather than ground truth.
A second theme is that simplification can introduce information-quality problems even when the result is easier to read. Prior work on factuality in text simplification distinguishes between information insertion, information deletion, and information substitution. These categories are especially relevant to legislative text because small changes to modal verbs, dates, monetary amounts, thresholds, exceptions, or other legal details can materially alter meaning.
A third theme concerns the evaluation of long-document summaries. The reviewed literature indicates that information coverage and factual consistency are related but distinct concepts. A summary may contain only factually supported statements while still omitting important parts of the source, or it may cover many important points while introducing unsupported or altered claims. As a result, the experimental design will measure information preservation and factual consistency separately rather than combining them into a single quality score.
Taken together, the literature changed the methodological direction of the project. The study will not define success solely as a reduction in grade-level readability. Instead, it will examine whether linguistic simplification occurs alongside adequate coverage and factual faithfulness, with human or expert review used on a manageable sample to help validate the automated evaluation methods.
4. Research Questions
RQ1: To what extent do LLM-generated plain-language summaries reduce the measured linguistic complexity of Tennessee legislative bills?
RQ2: To what extent do LLM-generated plain-language summaries preserve the substantive information and factual consistency of the source legislation?
RQ3: How do different LLMs compare in the tradeoff between reducing linguistic complexity and preserving substantive information and factual consistency?
5. Preliminary Experimental Design
The next phase of the project will convert the research questions into a reproducible experimental protocol. The design described here is preliminary and may be adjusted following a small pilot study.
A reproducible sample will be selected from the validated 2,684-bill corpus. The sampling procedure will be defined before model generation begins so that bills are not selected based on whether they appear easy or difficult to summarize. The final sample size and any stratification criteria will be determined as part of the experimental-design phase.
Multiple LLMs will be asked to generate plain-language summaries of the same source bills using a standardized prompt and consistent generation procedure. The prompt will specify the intended audience and emphasize both accessibility and preservation of substantive meaning. Model identity, version, prompt text, generation settings where available, and generated output will be recorded to support reproducibility.
For RQ1, the original bills and generated summaries will be evaluated using multiple traditional readability or linguistic-complexity measures rather than relying on a single formula. Candidate measures include Flesch-Kincaid Grade Level, Flesch Reading Ease, and additional measures identified in the literature such as Dale-Chall or Coleman-Liau. An LLM-based readability judgment may also be included as a complementary measure, with the distinction between formula-based complexity and human-oriented readability made explicit.
For RQ2, evaluation will distinguish information coverage from factual consistency. Coverage will measure the degree to which substantive information from the source bill is retained in the summary. Factual-consistency evaluation will examine whether claims in the generated summary are supported by the bill and will be informed by the insertion, deletion, and substitution error categories described in the simplification literature. Compression ratio, calculated from summary length relative to source length, will also be recorded because aggressive shortening may be associated with information loss.
For RQ3, results will be compared across models rather than reduced immediately to a single overall quality score. This will allow the analysis to identify tradeoffs, such as a model producing a larger reduction in linguistic complexity while omitting more substantive information, or another model preserving more content while making a smaller change in accessibility.
A subset of bill-summary pairs will be reviewed by a human or domain expert to provide an external check on the automated evaluation methods. The exact sample size and review instrument have not yet been finalized. A pilot experiment will be used to test the generation and evaluation pipeline before the full study is run.
6. Next Steps
Immediate next steps are to finalize the experimental sampling strategy, select the LLMs to be compared, finalize the standardized summarization prompt, and select the exact automated evaluation measures. After these decisions are documented, a small pilot will be run to identify problems in the generation or evaluation pipeline. The methodology will then be revised as necessary and frozen before running the larger experiment. Following generation, the project will analyze readability and linguistic complexity changes, information coverage, factual consistency, compression, model-level differences, and agreement between automated and human or expert evaluation where sufficient review data are available.
References / Literature Reviewed
Cachola, I., Khashabi, D., & Dredze, M. (2025). Evaluating the Evaluators: Are readability metrics good measures of readability?
Devaraj, A., Sheffield, C., Wallace, B. C., & Li, J. J. (2022). Evaluating Factuality in Text Simplification.
The Use of Readability Metrics in Legal Text: A Systematic Literature Review.
Paragraph-level Simplification of Medical Texts.
Stress Testing Factual Consistency Metrics for Long-Document Summarization.
Summary of a Haystack: A Challenge to Long-Context LLMs and RAG Systems.
From Single to Multi: How LLMs Hallucinate in Multi-Document Summarization.
