# The MAT188 implementation (the course behind this template)

* This template generalizes the system I designed for SBG in MAT188 at University of Toronto implemented in 2023 and 2024.*

## Course setting

MAT188 is first-semester linear algebra for engineering students at the
University of Toronto: roughly 1000 students, 8 lecture sections, 16
tutorials capped at 80 students (TA ratio about 1:20), 16 labs, and a
teaching team of over 40 TAs with lab and tutorial head TAs under a
coordinator.

SBG was introduced gradually ("hyphenated grading"):

- **Fall 2022 (Round I):** SBG in tutorials only.
- **Fall 2023 (Round II):** SBG in tutorials (group work, 12%), SBG
  WeBWorK sets (individual, unsupervised, 5%), and SBG mastery/gateway
  quizzes (individual, supervised, 5%). Midterms and final remained
  summative, but exam questions were still labeled with standards for
  feedback.
- **Fall 2024:** same architecture, refined (the 2024 data formats are the
  ones this template imitates).

## Learning standards

Standards are explicit objectives — "I can ..." statements — written per
chapter and classified by type: **computational**, **conceptual**,
**visual/geometry**, and **writing**. Published examples (CEEA paper):

> "Given a subset of R^n, I can verify whether it is a subspace or not."
> "Given a subspace W of R^n, I can construct a basis for W and find its
> dimension."

Standards reach students through three channels: weekly pre-class
readings (each opens with its standards), tutorial worksheets (each opens
with the subset covered, and every exercise is labeled with its
standards), and exam preparation packages. In the LaTeX system the
standards live in one source bank and are pulled by key everywhere they
appear, so the wording is identical in every channel.

## The reattempt system (mastery, not points)

Per the CMS 2025 talk, each assessment type has its own reattempt design:

- **Tutorials (semi-supervised group SBG):** each week, groups work one
  multi-standard question; the submission is graded for demonstrating one
  or two designated standards. TAs in the room communicate what a
  demonstration looks like. At least one group **resubmission** round is
  graded for identifying and improving the previous work and implementing
  feedback (conceptual and writing standards).
- **Online homework (unsupervised individual SBG):** weekly WeBWorK
  quizzes with multiple attempts; each question is attached to standards
  and a collection of correct answers achieves the standard
  (computational and visual standards; graded automatically).
- **Gateway (supervised individual quiz):** core computational standards;
  an unlimited practice quiz beforehand, two supervised attempts during
  labs; each question measures a single standard.

Demonstrating a standard **anywhere, once** is sufficient — only eventual
mastery matters. In the grade scheme, the SBG component gave full marks
for demonstrating at least 70% of the tutorial standards by term's end
(the tutorial SBG component was 12% of the course grade).

## Behind the scenes (what this template automates)

The course needed: a system to track each student's demonstrated
standards across platforms; a way to communicate progress to students;
and continuous communication with the teaching team. Concretely
(2024 workflow):

1. Per-question marks come from WeBWorK progress exports, a consolidated
   tutorial spreadsheet (with SBG grading-group columns), Gradescope exam
   sheets, and a small manual-overrides file (petitions, regrades).
2. `lsa_v4.py` (Simeon Wong) converts everything to a canonical long
   score table, applies the standards lookup table, and writes
   `standards_achieved.csv`.
3. `make_ls_report_v2.py` renders one report page per student (summary
   counts per modality plus a detailed checkmark table) and the combined
   PDF is uploaded to Gradescope, where each student sees their page.
   Mid-course and final reports were issued, plus a discrepancy-report
   form whose responses fed corrections back into the data.

## Observed outcomes (2022 cohort, CEEA paper)

Tutorials were consistently attended; TAs reported active engagement.
More than 60% of students used at least one resubmission opportunity and
about 30% used all of them. In the survey, 86% used the standards to
prepare for tests; 47% used them to formulate tutorial work; 33% used
them when reviewing feedback; 23% preferred SBG-style feedback while 67%
preferred a fixed rubric (buy-in is real work). Instructors gained
unusually fine-grained insight into which topics the class had actually
mastered, which fed back into curriculum changes.

## Deliberate differences in this template

- Standard statements are stored in `standards/standards.csv`; the MAT188
  original pulls them from a LaTeX standards bank (`\PulledLS`) shared
  with worksheets and readings. The CSV keeps the template dependency-free;
  if you maintain a LaTeX bank, generate the CSV from it.
- The original lookup table is an .xlsx with extra course-specific sheets
  (grading-group assignment by weekday, tutorial dates). The template uses
  a single CSV (the evaluator accepts either).
- Reports here render to HTML by default (PDF via `--latex` optional);
  the original is LaTeX-only because it reuses the course's style files.
