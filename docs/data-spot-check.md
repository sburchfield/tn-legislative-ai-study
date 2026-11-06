# Dataset Spot Check

Generated: 2026-09-05T19:14:46Z

Produced by `scripts/validation` (see `data/validation/dataset-validation.json` for the full machine-readable report). This document is generated — do not hand-edit it; rerun the validation script to refresh it.

## Executive summary

- Total records checked: **2684**
- ERROR-level findings: **0**
- WARNING-level findings: **203**
- Records requiring manual review: **200**
- Safe to proceed with the study: **true**

No ERROR-level findings. WARNING-level findings (if any) reflect known, documented caveats (e.g. sponsor timing) or low-severity formatting artifacts worth a spot check, not blocking issues.

## Random spot-check sample (seed=42, n=20)

Deterministic sample — rerunning the validation script with the same `-seed` reproduces the same set of records.

### HB1204

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 39 and Title 55, relative to driving under the influence of an intoxicant.
- **Sponsor (current):** Sabi Kumar
- **Sponsor (as filed):** Kumar
- **bill_text length:** 869 chars
- **"By ..." line present in text:** true (parsed as "Kumar")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 1400  By Roberts   HOUSE BILL 1204   By Kumar   AN ACT to amend Tennessee Code Annotated, Title 39  and Title 55, relative to driving under the influence  of an intoxicant.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 55-10-406(e)(3)(A)(iv), is amended  by adding the following at the end of the subdivision:   A law enf…

### HB0195

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 71, relative to ambulance services.
- **Sponsor (current):** Brock Martin
- **Sponsor (as filed):** Martin B
- **bill_text length:** 3251 chars
- **"By ..." line present in text:** true (parsed as "Martin B")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 210  By Jackson   HOUSE BILL 195   By Martin B   AN ACT to amend Tennessee Code Annotated, Title 71,  relative to ambulance services.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 71-5-165, is amended by deleting the  section and substituting:   (a) As used in this section:   (1) "Ambulance service provider" means a pub…

### HB0489

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 38; Title 39; Title 40 and Title 55, relative to criminal law.
- **Sponsor (current):** Clay Doggett
- **Sponsor (as filed):** Farmer
- **bill_text length:** 870 chars
- **"By ..." line present in text:** true (parsed as "Farmer")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:**
  - `WARNING` **sponsor_differs_from_as_filed**: current sponsor "Clay Doggett" differs from as-filed sponsor "Farmer" (expected caveat — see docs/dataset.md §4)
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 254  By Gardenhire   HOUSE BILL 489   By Farmer   AN ACT to amend Tennessee Code Annotated, Title 38;  Title 39; Title 40 and Title 55, relative to criminal  law.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 40-36-105(2), is amended by  deleting the subdivision and substituting:   (2) Conduct statewide public education…

### HB1360

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 36; Title 37 and Title 39, relative to child abuse.
- **Sponsor (current):** Mary Littleton
- **Sponsor (as filed):** Stevens
- **bill_text length:** 1293 chars
- **"By ..." line present in text:** true (parsed as "Stevens")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:**
  - `WARNING` **sponsor_differs_from_as_filed**: current sponsor "Mary Littleton" differs from as-filed sponsor "Stevens" (expected caveat — see docs/dataset.md §4)
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 1241  By Jackson   HOUSE BILL 1360   By Stevens   AN ACT to amend Tennessee Code Annotated, Title 36;  Title 37 and Title 39, relative to child abuse.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 37-1-102(b)(1), is amended by  adding the following as a new subdivision:   (C) A person under eighteen (18) years of age wi…

### HB2129

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 9 and Title 49, relative to pre-kindergarten.
- **Sponsor (current):** Rebecca Alexander
- **Sponsor (as filed):** Alexander
- **bill_text length:** 811 chars
- **"By ..." line present in text:** true (parsed as "Alexander")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 2361  By Massey   HOUSE BILL 2129   By Alexander   AN ACT to amend Tennessee Code Annotated, Title 9 and  Title 49, relative to pre-kindergarten.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 49-6-108, is amended by deleting  subdivision (6) and substituting:   (6) Once every three (3) years, provide a report to the gov…

### HB1116

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 38; Title 39; Title 40 and Title 67, relative to crime stoppers programs.
- **Sponsor (current):** Michele Carringer
- **Sponsor (as filed):** Carringer
- **bill_text length:** 7001 chars
- **"By ..." line present in text:** true (parsed as "Carringer")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 804  By Massey   HOUSE BILL 1116   By Carringer   AN ACT to amend Tennessee Code Annotated, Title 38;  Title 39; Title 40 and Title 67, relative to crime  stoppers programs.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Title 40, Chapter 35, Part 1, is amended by  adding the following new section:   (a) In addition to any fine …

### HB1739

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 54 and Title 64, Chapter 9, relative to enforcement of traffic laws on designated private roadways within the megasite of West Tennessee.
- **Sponsor (current):** Johnny Shaw
- **Sponsor (as filed):** Shaw
- **bill_text length:** 3795 chars
- **"By ..." line present in text:** true (parsed as "Shaw")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 1772  By Walley   HOUSE BILL 1739   By Shaw   AN ACT to amend Tennessee Code Annotated, Title 54  and Title 64, Chapter 9, relative to enforcement of  traffic laws on designated private roadways within  the megasite of West Tennessee.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Title 64, Chapter 9, is amended by adding  the f…

### HB1607

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 4, Chapter 29 and Title 52, Chapter 8, relative to the Tennessee commission on aging and disability.
- **Sponsor (current):** Justin Lafferty
- **Sponsor (as filed):** Lafferty
- **bill_text length:** 667 chars
- **"By ..." line present in text:** true (parsed as "Lafferty")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 1550  By Jackson   HOUSE BILL 1607   By Lafferty   AN ACT to amend Tennessee Code Annotated, Title 4,  Chapter 29 and Title 52, Chapter 8, relative to the  Tennessee commission on aging and disability.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 4-29-247(a), is amended by deleting  subdivision (56).   SECTION 2. Tenne…

### HB0324

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 4 and Title 58, Chapter 2, relative to emergency powers of the governor.
- **Sponsor (current):** Rusty Grills
- **Sponsor (as filed):** Barrett
- **bill_text length:** 1543 chars
- **"By ..." line present in text:** true (parsed as "Barrett")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:**
  - `WARNING` **sponsor_differs_from_as_filed**: current sponsor "Rusty Grills" differs from as-filed sponsor "Barrett" (expected caveat — see docs/dataset.md §4)
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 27  By Pody   HOUSE BILL 324   By Barrett   AN ACT to amend Tennessee Code Annotated, Title 4 and  Title 58, Chapter 2, relative to emergency powers  of the governor.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 58-2-107(a)(2), is amended by  deleting the subdivision and substituting:   (2) Pursuant to the authority ve…

### HB0343

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 39 and Title 47, relative to lighters.
- **Sponsor (current):** Kip Capley
- **Sponsor (as filed):** Capley
- **bill_text length:** 2050 chars
- **"By ..." line present in text:** true (parsed as "Capley")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > HOUSE BILL 343   By Capley   AN ACT to amend Tennessee Code Annotated, Title 39  and Title 47, relative to lighters.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Title 47, Chapter 18, Part 1, is amended by  adding the following as a new section:   47-18-136.   (a) As used in this section:   (1) "Counterfeit lighter" means a lighter that i…

### HB0909

- **Title:** AN ACT to amend Tennessee Code Annotated, Section 67-6-103, relative to distribution of revenues.
- **Sponsor (current):** Johnny Garrett
- **Sponsor (as filed):** Garrett
- **bill_text length:** 2745 chars
- **"By ..." line present in text:** true (parsed as "Garrett")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 177  By Briggs   HOUSE BILL 909   By Garrett   AN ACT to amend Tennessee Code Annotated, Section  67-6-103, relative to distribution of revenues.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 67-6-103, is amended by deleting  subdivision (c)(1) and substituting instead:   (1) Notwithstanding another law to the contrary,…

### HB1627

- **Title:** AN ACT to amend Tennessee Code Annotated, Section 36-5-118 and Section 36-5-119, relative to child support.
- **Sponsor (current):** William Lamberth
- **Sponsor (as filed):** Lamberth
- **bill_text length:** 1255 chars
- **"By ..." line present in text:** true (parsed as "Lamberth")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > HOUSE BILL 1627   By Lamberth   AN ACT to amend Tennessee Code Annotated, Section  36-5-118 and Section 36-5-119, relative to child  support.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 36-5-118, is amended by deleting the  section and substituting instead:   Notwithstanding another law to the contrary, the department of human se…

### HB0795

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 5; Title 6; Title 7; Title 9; Title 12; Title 13 and Title 66, relative to development contracts.
- **Sponsor (current):** Kevin Vaughan
- **Sponsor (as filed):** Vaughan
- **bill_text length:** 8044 chars
- **"By ..." line present in text:** true (parsed as "Vaughan")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 731  By Pody   HOUSE BILL 795   By Vaughan   AN ACT to amend Tennessee Code Annotated, Title 5;  Title 6; Title 7; Title 9; Title 12; Title 13 and Title  66, relative to development contracts.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Title 7, is amended by adding the following  as a new chapter 70:   7-70-101.   As used in…

### HB0407

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 10, Chapter 7 and Title 49, relative to incentives for students who obtain testing for certain health conditions.
- **Sponsor (current):** Yusuf Hakeem
- **Sponsor (as filed):** Hakeem
- **bill_text length:** 4201 chars
- **"By ..." line present in text:** true (parsed as "Hakeem")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 189  By Lamar   HOUSE BILL 407   By Hakeem   AN ACT to amend Tennessee Code Annotated, Title 10,  Chapter 7 and Title 49, relative to incentives for  students who obtain testing for certain health  conditions.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Title 49, Chapter 7, Part 1, is amended by  adding the following as a new…

### HB0113

- **Title:** AN ACT to amend Tennessee Code Annotated, Section 39-17-402, relative to testing equipment used to determine the presence of a synthetic opioid.
- **Sponsor (current):** William Lamberth
- **Sponsor (as filed):** Lamberth
- **bill_text length:** 487 chars
- **"By ..." line present in text:** true (parsed as "Lamberth")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > HOUSE BILL 113   By Lamberth   AN ACT to amend Tennessee Code Annotated, Section  39-17-402, relative to testing equipment used to  determine the presence of a synthetic opioid.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 39-17-402(12)(B)(ii), is amended by  deleting ". This subdivision (12)(B)(ii) is repealed on July 1, 2025".  …

### HB1207

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 39, Chapter 17, Part 13, relative to suicide prevention.
- **Sponsor (current):** Sabi Kumar
- **Sponsor (as filed):** Kumar
- **bill_text length:** 9112 chars
- **"By ..." line present in text:** true (parsed as "Kumar")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 1094  By Hensley   HOUSE BILL 1207   By Kumar   AN ACT to amend Tennessee Code Annotated, Title 39,  Chapter 17, Part 13, relative to suicide prevention.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. This act is known and may be cited as the "Suicide Prevention Act of  2025."   SECTION 2. Tennessee Code Annotated, Title 39, Chapter 17, Part 13, is amend…

### HB2515

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 4; Title 5; Title 6; Title 7; Title 11; Title 64; Title 67 and Title 68, relative to solid waste management.
- **Sponsor (current):** Chris Todd
- **Sponsor (as filed):** Todd
- **bill_text length:** 647 chars
- **"By ..." line present in text:** true (parsed as "Todd")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 2546  By Reeves   HOUSE BILL 2515   By Todd   AN ACT to amend Tennessee Code Annotated, Title 4;  Title 5; Title 6; Title 7; Title 11; Title 64; Title 67  and Title 68, relative to solid waste management.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 68-211-107(c), is amended by  adding the following language immediatel…

### HB0459

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 43, Chapter 38; Title 48, Chapter 24; Title 48, Chapter 245; Title 48, Chapter 246; Title 48, Chapter 249; Title 48, Chapter 25; Title 48, Chapter 64; Title 48, Chapter 65 and Title 61, Chapter 3, relative to entities filing documents with the secretary of state.
- **Sponsor (current):** Greg Martin
- **Sponsor (as filed):** Martin G
- **bill_text length:** 9830 chars
- **"By ..." line present in text:** true (parsed as "Martin G")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 306  By Briggs   HOUSE BILL 459   By Martin G   AN ACT to amend Tennessee Code Annotated, Title 43,  Chapter 38; Title 48, Chapter 24; Title 48, Chapter  245; Title 48, Chapter 246; Title 48, Chapter 249;  Title 48, Chapter 25; Title 48, Chapter 64; Title 48,  Chapter 65 and Title 61, Chapter 3, relative to  entities filing documents with the secretary of  state.  BE IT ENACTED BY THE …

### HB0399

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 12 and Title 49, relative to school safety.
- **Sponsor (current):** Rush Bricken
- **Sponsor (as filed):** Bricken
- **bill_text length:** 15678 chars
- **"By ..." line present in text:** true (parsed as "Bricken")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > HOUSE BILL 399   By Bricken   AN ACT to amend Tennessee Code Annotated, Title 12  and Title 49, relative to school safety.   WHEREAS, the alarming rise in school violence incidents, including those at after-school  events, and recent threats have underscored the urgent need for proactive steps to bolster  school safety for Tennessee students and communities, and to ensure secure learning  environm…

### HB0142

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 57, relative to alcoholic beverages.
- **Sponsor (current):** Jake McCalmon
- **Sponsor (as filed):** McCalmon
- **bill_text length:** 1506 chars
- **"By ..." line present in text:** true (parsed as "McCalmon")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 111  By Lowe   HOUSE BILL 142   By McCalmon   AN ACT to amend Tennessee Code Annotated, Title 57,  relative to alcoholic beverages.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Title 57, Chapter 3, Part 2, is amended by  adding the following new section:   (a) Notwithstanding another law to the contrary, a winery licensed unde…

## Targeted edge-case checks

Specifically requested checks against two bills involved in previously-found issues.

### HB0486 — stray 113th GA Public Chapter document check

A LegiScan data anomaly previously caused this bill's selected text to come from a misattached 113th General Assembly (2023) enacted "Public Chapter" PDF instead of its real 114th GA as-filed draft. Confirming the fix held:

### HB0486

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 8, Chapter 14 and Title 9, Chapter 4, relative to district public defenders.
- **Sponsor (current):** Andrew Farmer
- **Sponsor (as filed):** Farmer
- **bill_text length:** 476 chars
- **"By ..." line present in text:** true (parsed as "Farmer")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:** none
- **bill_text excerpt (first ~400 chars):**

  > SENATE BILL 445  By Gardenhire   HOUSE BILL 486   By Farmer   AN ACT to amend Tennessee Code Annotated, Title 8,  Chapter 14 and Title 9, Chapter 4, relative to  district public defenders.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 8-14-204, is amended by deleting  "ten (10) days" and substituting "ten (10) business days".   SEC…

### HB0349 — current-sponsor vs. as-filed-sponsor check

This bill's sponsorship changed after filing, so `sponsor` (current) and `sponsor_as_filed` (from the bill's own "By [Name]" line) are expected to legitimately disagree. Confirming that's represented correctly, not silently "fixed":

### HB0349

- **Title:** AN ACT to amend Tennessee Code Annotated, Title 49, relative to education.
- **Sponsor (current):** William Slater
- **Sponsor (as filed):** Hurt
- **bill_text length:** 352 chars
- **"By ..." line present in text:** true (parsed as "Hurt")
- **Looks like introduced/draft text (not enacted/chaptered):** true
- **Session/General Assembly matches expected:** yes (raw session_id=2161, session_name="114th General Assembly", text_type="Draft")
- **Automated validation flags:**
  - `WARNING` **sponsor_differs_from_as_filed**: current sponsor "William Slater" differs from as-filed sponsor "Hurt" (expected caveat — see docs/dataset.md §4)
- **bill_text excerpt (first ~400 chars):**

  > HOUSE BILL 349   By Hurt   AN ACT to amend Tennessee Code Annotated, Title 49,  relative to education.  BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:   SECTION 1. Tennessee Code Annotated, Section 49-9-1410, is amended by deleting  the section.   SECTION 2. This act takes effect upon becoming a law, the public welfare requiring it.
