# Cross-provider extension researcher review packet

**Prepared:** 2026-11-02T16:16:07.245427+00:00  
**Purpose:** Limited researcher sanity check of the six new Claude/Gemma summaries.  
**Reviewer:** Sam Burchfield. Compare each unedited summary with the exact as-filed source before reading its new Astra judgments.

The three bills were selected before the original full experiment in
[`data/full/sample.json`](../data/full/sample.json). Record only factual errors, material omissions, or changes to substantive meaning,
with brief source passages and explanations. If none is found, mark `No problem observed`. This packet contains no Astra judgments.
Earlier Astra findings for these bills may already be known, so this is only partially blinded; it is not expert validation or a reliability test.

## HB1228 — short

Subject: Education  
Source words: 94  
Source SHA-256: `d05fdc89c0acb748c26536bc284419ca43df186e6b6db3868279b11f4859f9f2`

### Exact as-filed bill text

```text
SENATE BILL 820
 By Hensley

 HOUSE BILL 1228

 By Lafferty

 AN ACT to amend Tennessee Code Annotated, Title 8;
 Title 49 and Title 62, relative to tenure.

BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:

 SECTION 1. Tennessee Code Annotated, Section 49-8-301(a), is amended by adding

the following as the last sentence of the subsection:

 The board may produce and make available, electronically or in a printed, physical

 medium, a copy of the tenure policy.

 SECTION 2. This act takes effect upon becoming a law, the public welfare requiring it.
```

### claude-sonnet-5-5 summary and issue log

Raw response: [`claude/HB1228.json`](../data/extension/responses/claude/HB1228.json)  
Summary SHA-256: `bc5c6dae6741f6d423d9a16dab66c95389b90eba9a1e984fcd7f7fc4ac20e06d`

```text
This bill would add one sentence to Tennessee Code Annotated, Section 49-8-301(a). The new sentence says the board may produce and make available a copy of the tenure policy, either electronically or in a printed, physical form. The text says the board "may" do this, so it is a permission and not a requirement. The bill does not show what the rest of the section says or which board it means. The bill would take effect as soon as it becomes law.
```

Review date and time: 11/02/26 
New Astra judgments viewed before saving? ________

| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |
| --- | --- | --- | --- |
|  |  |  |  |

If none: **No problem observed in this limited check** No Problem

### google/gemma-4-31b-qat summary and issue log

Raw response: [`gemma/HB1228.json`](../data/extension/responses/gemma/HB1228.json)  
Summary SHA-256: `62f6ae513015972eff617b7d07f552a6d6a511aac7be290dea4e6cb7e1d68129`

```text
This bill would amend Tennessee Code Annotated, Section 49-8-301(a) to allow the board to produce and provide copies of the tenure policy in either electronic or printed physical formats. The act would take effect as soon as it becomes law.
```

Review date and time: 11/02/26   
New Astra judgments viewed before saving? No Problem

Notes: the sonnet reply is by far the most descriptive but words like "permission and not a requirement" might make the reading more complex. the local 31 B is comparble to the OpenAI flagship models. 

| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |
| --- | --- | --- | --- |
|  |  |  |  |

If none: **No problem observed in this limited check** No Problem

## HB0187 — medium

Subject: Education  
Source words: 274  
Source SHA-256: `5bd9334ab51ceec0460951e439a3418ffeddd3b3569b5b73be30b9e872b10adc`

### Exact as-filed bill text

```text
HOUSE BILL 187

 By Maberry

 AN ACT to amend Tennessee Code Annotated, Section
 49-1-905 and Section 49-1-910, relative to
 comptroller reports.

BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:

 SECTION 1. Tennessee Code Annotated, Section 49-1-905(g), is amended by deleting

subdivision (6) and substituting:

 (6) The office of the comptroller of the treasury shall review the foundational

 literacy skills plans submitted to the department for approval to ensure the plans comply

 with the requirements of subsection (f) and the rules promulgated by the state board. As

 part of the review, the comptroller, or the comptroller's designee, shall examine whether

 the plans were initially approved or denied by the department and the nature of any plan

 revisions or amendments required by the department for approval. The comptroller shall

 include its findings from the review in the report required pursuant to § 49-1-910.

 SECTION 2. Tennessee Code Annotated, Section 49-1-910, is amended by deleting the

section and substituting:

 The office of the comptroller of the treasury shall review data, practices, and

 outcomes related to this part. The department of education shall provide any information

 requested by the office of the comptroller of the treasury to the comptroller's office as

 soon as practicable. Every three (3) years, the comptroller shall submit a report detailing

 the findings of the review to the chair of the education committee of the senate, the chair

 of the committee of the house of representatives having jurisdiction over student literacy,

 and the state board of education and publish the report on the comptroller's website.

 SECTION 3. This act takes effect upon becoming a law, the public welfare requiring it.
```

### claude-sonnet-5-5 summary and issue log

Raw response: [`claude/HB0187.json`](../data/extension/responses/claude/HB0187.json)  
Summary SHA-256: `69f7d7fbb25e10651bb7ff5b572dbd238f2ce4080112a359811bb5a625e2f87c`

```text
This bill would change two Tennessee education laws about reviews done by the state comptroller of the treasury. It would replace existing text in both sections.

First, the comptroller's office would review the foundational literacy skills plans that are sent to the Department of Education for approval. The review would check that the plans meet the requirements of subsection (f) of the same section and the rules set by the State Board of Education. The comptroller or a designee would also look at whether the department first approved or denied each plan. They would look at what kinds of revisions or amendments the department required before approval. The comptroller would put these findings in the report required by § 49-1-910.

Second, the bill would replace § 49-1-910 entirely. The comptroller's office would review data, practices, and outcomes related to this part of the code. The Department of Education would have to give the comptroller's office any information it requests as soon as practicable. Every three years, the comptroller would submit a report on the findings to the chair of the Senate education committee, the chair of the House committee that handles student literacy, and the State Board of Education. The comptroller would also publish the report on its website. The bill does not show what the replaced text said.

The bill would take effect as soon as it becomes law.
```

Review date and time: 11/03/26
New Astra judgments viewed before saving? ________

| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |
| --- | --- | --- | --- |
|  |  |  |  |

If none: **No problem observed in this limited check** No Problem

### google/gemma-4-31b-qat summary and issue log

Raw response: [`gemma/HB0187.json`](../data/extension/responses/gemma/HB0187.json)  
Summary SHA-256: `04eb5485e51138959976c5f13d6bfefbb574baca278421fae34e54570d2df908`

```text
This bill would change how the office of the comptroller of the treasury reviews and reports on foundational literacy skills plans. The comptroller would be required to review plans submitted to the department for approval to ensure they meet specific requirements and state board rules. This review must examine whether the department initially approved or denied the plans and any required revisions. These findings must be included in the comptroller's reports.

Additionally, the bill would require the comptroller to review data, practices, and outcomes related to this part of the law, with the department of education providing requested information as soon as practicable. Every three years, the comptroller must publish a report of these findings on its website and submit it to the state board of education and the chairs of the relevant senate and house committees. The act would take effect as soon as it becomes law.
```

Review date and time: 11/03/26
New Astra judgments viewed before saving? No Problem

| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |
| --- | --- | --- | --- |
|  |  |  |  |

If none: **No problem observed in this limited check** No Problem

Notes: Again the sonnet summary is more descriptive but at the risk of readablity and the 31B local model seems to be comparable to the flagship models

## HB0522 — long

Subject: Education  
Source words: 634  
Source SHA-256: `45d053172313a90bb317be8f9aa9f4289f063c307b60b6febb2859c02c41e402`

### Exact as-filed bill text

```text
SENATE BILL 386
 By Taylor

 HOUSE BILL 522

 By Reedy

 AN ACT to amend Tennessee Code Annotated, Title 16;
 Title 37 and Title 49, relative to student behavior.

BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:

 SECTION 1. Tennessee Code Annotated, Title 49, Chapter 6, Part 3, is amended by

adding the following as a new section:

 (a) This section is known and may be cited as the "Early Behavioral Intervention

 and Reporting Act."

 (b) As used in this section, "early warning signs" means evidence of a student's

 safety, health, or behavioral issues and includes, but is not limited to, indicators of a

 student engaging in or being the victim of harassment, intimidation, bullying, or cyber-

 bullying; making or receiving threats of violence; and exhibiting signs of substance

 abuse, mental health issues, self-harm, or suicidal ideation.

 (c) Each LEA and public charter school shall implement a computer-based

 system that teachers and school staff must use to input data of early warning signs

 demonstrated by students enrolled in the LEA or public charter school. Each LEA and

 public charter school shall ensure that each teacher and school staff member is trained

 to identify early warning signs and on how to input data into the computer-based system.

 (d) The computer-based system implemented pursuant to subsection (c) must:

 (1) Align with the requirements in § 49-6-4503; the School Discipline Act,

 compiled in part 41 of this chapter; and the school safety plans adopted by the

 LEA or public charter school pursuant to the Schools Against Violence in

 Education (SAVE) Act, compiled in part 8 of this chapter;

 (2) Include a database that is capable of receiving and maintaining

 student data entered by teachers and school staff on the early warning signs

 demonstrated by its students; and

 (3) Immediately notify the LEA's or public charter school's personnel

 serving on the LEA's or public charter school's threat assessment team created

 pursuant to § 49-6-2701 when an early warning sign is entered into the system

 for a student.

 (e) The LEA or public charter school personnel receiving a notification of an

 early warning sign of a student pursuant to subdivision (d)(3) shall review the

 notification, and any notifications of the student previously received, and determine

 whether further action is needed to address the student's behavior of an early warning

 sign.

 (f) Each LEA and public charter school shall annually submit a report to the

 department of education summarizing the data collected in the immediately preceding

 school year and the interventions provided, if any.

 (g) Reports made pursuant to this section must comply with the Family

 Educational Rights and Privacy Act (FERPA) (20 U.S.C. § 1232g); § 10-7-504; the Data

 Accessibility, Transparency, and Accountability Act, compiled in chapter 1, part 7 of this

 title; and all other relevant privacy laws.

 (h) If the commissioner of education finds that an LEA or public charter school is

 not complying with this section, then the commissioner may withhold state funds, in an

 amount determined by the commissioner, from the LEA or public charter school until the

 LEA or public charter school is in compliance with this section.

 SECTION 2. Tennessee Code Annotated, Section 49-6-2701, is amended by adding

"and public charter school" after "Each LEA", adding "or public charter school" after "LEA"

wherever it appears in the section, adding "or public charter school's" after "LEA's" in subsection

(b), adding "or public charter school governing body" after "local board of education" in

subsection (e), and adding "or the director of the public charter school" after "the director of

schools" in subsection (e).

 SECTION 3. Tennessee Code Annotated, Section 49-6-2702(b), is amended by adding

"or public charter school" after "LEA" and adding "or public charter school's" after "LEA's".

 SECTION 4. This act takes effect July 1, 2025, the public welfare requiring it.
```

### claude-sonnet-5-5 summary and issue log

Raw response: [`claude/HB0522.json`](../data/extension/responses/claude/HB0522.json)  
Summary SHA-256: `82bd0ba90b8350500fd1cafb394fbca2391ec46a30eb5c6e90e139690cbc0cd9`

```text
This bill would create the "Early Behavioral Intervention and Reporting Act" for Tennessee public schools. It defines "early warning signs" as evidence of a student's safety, health, or behavior problems. Examples include bullying, harassment, or cyberbullying (as a victim or participant), threats of violence, substance abuse, mental health issues, self-harm, and suicidal thoughts. The list is not limited to these examples.

Each local education agency (LEA) and public charter school would have to set up a computer-based system. Teachers and school staff would be required to use it to enter data on early warning signs shown by their students. Each LEA and charter school would also have to train every teacher and staff member to spot early warning signs and to enter data into the system.

The system would have to line up with section 49-6-4503, the School Discipline Act, and the school safety plans adopted under the SAVE Act. It would need a database that can receive and keep the entered student data. It would also have to immediately notify the members of the school's threat assessment team whenever an early warning sign is entered for a student. Those personnel would have to review the notice and any earlier notices for that student. They would then decide whether more action is needed to address the student's behavior.

Each LEA and charter school would send the Department of Education an annual report. It would summarize the data collected in the prior school year and any interventions provided. Reports would have to follow FERPA, section 10-7-504, the Data Accessibility, Transparency, and Accountability Act, and other relevant privacy laws. If the commissioner of education finds an LEA or charter school is not complying, the commissioner may withhold state funds, in an amount the commissioner decides, until it complies.

The bill also amends sections 49-6-2701 and 49-6-2702(b) by adding public charter schools, and their governing bodies or directors where the text names boards or directors of schools, alongside LEAs. The bill would take effect July 1, 2025.
```

Review date and time: 11/03/26  
New Astra judgments viewed before saving? ________

| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |
| --- | --- | --- | --- |
|  |  |  |  |

If none: **No problem observed in this limited check** No Problem

### google/gemma-4-31b-qat summary and issue log

Raw response: [`gemma/HB0522.json`](../data/extension/responses/gemma/HB0522.json)  
Summary SHA-256: `5dff658bbeba7bf981fa61f6f6386f033aa746a09fc3c10f2c0550f1eb81e04a`

```text
This bill would create the Early Behavioral Intervention and Reporting Act, requiring every local education agency (LEA) and public charter school to use a computer-based system for tracking student "early warning signs." Early warning signs include evidence of health, safety, or behavioral issues, such as substance abuse, mental health issues, suicidal ideation, self-harm, threats of violence, or instances of bullying and harassment. LEAs and public charter schools must train staff to identify these signs and enter them into the system. The system must maintain a database and immediately notify the school's threat assessment team when a sign is entered. Personnel receiving these notifications must review them and determine if further action is necessary. LEAs and public charter schools must submit annual reports to the department of education summarizing the collected data and any interventions provided, while complying with privacy laws including FERPA. The commissioner of education may withhold state funds from any LEA or public charter school that does not comply with these requirements. Additionally, the bill amends Tennessee Code Annotated Sections 49-6-2701 and 49-6-2702(b) to include public charter schools and their directors or governing bodies in provisions previously applying to LEAs and local boards of education. This act would take effect July 1, 2025.
```

Review date and time: 11/03/26 
New Astra judgments viewed before saving? No Problem

| Concern(s) | Summary passage or `not present` | Source passage or source limitation | Brief explanation |
| --- | --- | --- | --- |
|  |  |  |  |

Notes: Again the sonnet summary is more descriptive but at the risk of readablity and the 31B local model seems to be comparable to the flagship models

If none: **No problem observed in this limited check** No problem
