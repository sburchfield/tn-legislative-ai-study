# Education pilot: sampling assessment and approved draw

**Date:** October 4, 2026  
**Corpus:** `data/cleaned/bills.jsonl` (SHA-256 `df2cc9d71ab3aee3cf50c57a2748a922bc3f83206403a98dab58ebb33f5a7d5a`)  
**Status:** The 18-label inclusion rule and tail-aware nine-bill draw were approved on October 4, 2026. See `scripts/pilot/select_education_sample.py` for the frozen selection procedure and `data/pilot/education-sample.json` for the machine-readable result. The selected source texts were reviewed for integrity. No summaries have been generated.

## Corpus and subject definition

The cleaned corpus contains 2,684 House bills from the 114th Tennessee General Assembly. `subjects` is a JSON list, but every record in this snapshot has exactly one LegiScan subject label; none are missing. The exact label `Education` appears on 106 bills. Using only that label would omit bills labeled for local education agencies, teachers, higher education, schools, scholarships, and related areas.

For this assessment, the **candidate education subset** consists of the following 18 exact subject labels (336 bills total):

| Subject label | Bills |
| --- | ---: |
| Education | 106 |
| Education, Curriculum | 15 |
| Education, Dept. of | 35 |
| Education, Higher | 33 |
| Education, State Board of | 2 |
| Local Education Agencies | 68 |
| Lottery, Scholarships and Programs | 8 |
| Scholarships and Financial Aid | 7 |
| School Transportation | 5 |
| School Vouchers | 10 |
| Schools, Charter | 9 |
| Schools, Home | 1 |
| Schools, Private | 2 |
| State Universities | 2 |
| Students | 4 |
| Teachers, Principals and School Personnel | 17 |
| Tennessee Higher Education Commission | 4 |
| Tennessee Investment in Student Achievement (TISA) | 8 |

This is an operational subject based definition, not a claim that every bill affecting education is captured. For example, 156 bills mentioning Title 49 in their titles have other subject labels; Title 49 alone is also too broad because some titles list many code titles for unrelated omnibus subjects. Nine bills in the subset do not mention Title 49 in their titles. This fixed label list is the approved pilot scope.

## Source text length

Length is the number of whitespace separated words in cleaned `bill_text` (equivalent to Python `len(bill_text.split())`), including the bill header, title, and enactment language. Percentiles below use linear interpolation between sorted observations. This is a reproducible sampling measure, not a tokenizer estimate or a measure of substantive content. For the 336 bill candidate subset:

| Statistic | Words |
| --- | ---: |
| Minimum | 57 |
| 10th percentile | 76 |
| 25th percentile | 119.5 |
| Median | 268.5 |
| 75th percentile | 544.2 |
| 90th percentile | 998.5 |
| 95th percentile | 1,925.2 |
| 99th percentile | 3,171.5 |
| Maximum | 5,894 |

If sorted by word count (breaking ties by `bill_number`), the 336 records divide evenly into rank tertiles:

| Band | Rank | Word range | Median words | Mean words |
| --- | ---: | ---: | ---: | ---: |
| Short | 1–112 | 57–163 | 94 | 97.5 |
| Medium | 113–224 | 165–432 | 268.5 | 277.4 |
| Long | 225–336 | 433–5,894 | 736 | 1,082.0 |

There are no ties across either boundary (163/165 and 432/433 words). The distribution is strongly right skewed. Seventeen bills are at least 1,980 words (the longest 5% by rank), and 29 exceed the conventional 1.5 × IQR upper fence of about 1,181 words. Length alone does not make these records invalid. The longest, HB2533, is a multi section education bill of 5,894 words; its text has a substantive ending and was not flagged by the existing validation.

## Data quality and interpretation issues

All 336 candidate records have an ID, bill number, title, description, subject, and nonempty bill text. All use their own House text, with no Senate fallback. The September 5 validation report checked the full 2,684 record corpus and found zero errors. Within the candidate subset, its 27 warnings concern the documented current sponsor versus as-filed sponsor difference; there are no other warnings. The existing validation found no exact or near duplicate text groups in the whole corpus.

Forty-two candidate bills are 80 words or fewer. Inspection of examples such as HB0349, HB0665, and HB0154 shows that some repeal a cited code section without reproducing the repealed section. Their as-filed text supports a summary of the legal operation and citation, but not a description of the prior section's substance without an additional source. This is a useful prompt and faithfulness test, not a reason to silently exclude them. Some `description` fields also describe later bill outcomes (for example, HB2422 begins "As enacted") while `bill_text` is the as-filed version. The pilot should treat `bill_text` as the source for generation and source grounded evaluation, and should not use `description` to fill gaps in the as-filed text.

## Approved pilot draw

Rank tertiles are reasonable as the main length framework: they are balanced, have clean boundaries, and cover meaningfully different source lengths. A simple three from each tertile is less useful for a pipeline test because the long band spans 433–5,894 words and a random three from it has about a 61% chance of missing the longest 5% entirely.

For a nine bill **pilot stress test**, draw reproducibly within these cells:

- Short: one from the 42 bills of at most 80 words, and two from the other 70 short tertile bills.
- Medium: three from the 112 medium tertile bills.
- Long: two from the 95 long tertile bills below 1,980 words, and one from the 17 bills at or above 1,980 words.

This intentionally covers both the sparse amendment/repeal edge case and a genuinely long source. It is not a representative estimate of the education bill population, so pilot results should be interpreted diagnostically. The seed is frozen as `INSC499-education-pilot-2026-10-04-v1`. Within each cell, rank records by the SHA-256 digest of the UTF-8 string `seed|id|bill_number` in ascending order and take the required number. This deterministic pseudorandom rule avoids dependence on a programming language's random-number generator. The script verifies the corpus hash and expected cell sizes before drawing, then saves bill IDs, word counts, cells, text hashes, and the seed. Do not replace a draw based on summary quality or desired outcome. Review source integrity and repeat proposals against prespecified rules before generation.

The pilot will check linguistic complexity/readability, information coverage, factual consistency, and compression with automated measures. Manual inspection of the nine outputs will check whether that evaluation pipeline behaves sensibly, without producing formal human scores; the need for human or expert validation in the final experiment will be decided after the pilot. The single model pilot cannot answer the cross model comparison in RQ3; it can check whether the common prompt, logging, and evaluation procedure are ready for that later comparison. The approved prompt and nine generated summaries are documented in `docs/pilot-generation-design.md` and `docs/pilot-generation-run.md`.

## Draw result and source review

The approved rule selected these nine bills. The cell order shown here is also the order in the machine-readable manifest; order is not a ranking of bill quality.

| Cell | Bill | Words | Subject |
| --- | --- | ---: | --- |
| Short, minimal | HB2329 | 70 | Education, Dept. of |
| Short, other | HB0709 | 127 | Education |
| Short, other | HB2484 | 100 | Education |
| Medium | HB1772 | 386 | Education, Higher |
| Medium | HB0474 | 185 | Education, Higher |
| Medium | HB0750 | 232 | Education |
| Long, main | HB0800 | 963 | Education |
| Long, main | HB1889 | 1,118 | School Vouchers |
| Long, tail | HB1732 | 2,135 | Teachers, Principals and School Personnel |

After drawing, each selected record was checked against the saved text hash and its House text source, title, opening and ending, and section structure. All nine text hashes match the frozen corpus, all have a substantive legislative ending, and none has a validation error. The only validation warning among the nine is the known current versus as-filed sponsor difference for HB2329, which does not affect its text. Their titles and sampled content show distinct proposals; no sampled bill was replaced.

The draw includes useful stress cases for the later prompt and evaluation work. HB2329's 70-word text changes a reporting date from July 31 to July 1; it does not reproduce the underlying nurse staffing rule mentioned in LegiScan's description. HB0800 includes a substantial preamble, so the automated evaluator must distinguish background claims from operative changes. HB1732 contains 34 numbered sections and many cross-references, making it a demanding coverage test. These features were observed after the draw and did not influence selection.
