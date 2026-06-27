# SBG Grading Kit — Standards-Based Grading pipeline and student reports

A minimal, self-contained kit for the **grading** side of a standards-based
course: it tracks which learning standards each student has demonstrated and
produces individualized progress reports. This is a **grading toolkit, not a
course-content template** — it does not contain readings, tutorials, or exam
questions; that course material is authored separately.

Concretely it provides a labeled list of learning standards, a question
labeling scheme, a lookup table connecting assessment questions to
standards, a Python pipeline that computes per-student mastery from
platform exports (WeBWorK, Gradescope, Crowdmark, Quercus Grader etc), support for **re-attempts /
re-submissions until mastery**, and individualized student progress reports
(HTML and PDF).

It is a generalized, anonymized distillation of the system designed and used in
**MAT188 (Linear Algebra, ~1000 students, University of Toronto)** by
Camelia Karimianpour and collaborators. The analysis pipeline is adapted
from [dtxe/mat188_learning_standards](https://github.com/dtxe/mat188_learning_standards)
by Simeon Wong, created specifically for this course. 

## Quick start

```bash
pip install pandas pyyaml openpyxl       # or: uv sync
python run_pipeline.py config.yml        # runs on the bundled sample data
```

Outputs land in `output/`:

| File | What it is |
|---|---|
| `raw_scores.csv` | every (student, question, correct, graded) record, canonical long format |
| `standards_achieved.csv` | one row per student, one column per standard x modality, plus summaries |
| `reports_html/<student>.html` | individual progress report per student |
| `reports_combined.tex` (with `--latex`) | one-page-per-student PDF source for LMS upload |

Or open `colab/sbg_pipeline.ipynb` in Google Colab to run everything in
the browser.

## Repository layout

```
config.yml                  pipeline configuration (file paths, options)
run_pipeline.py             one-command driver: convert -> evaluate -> report
make_sample_data.py         regenerates the synthetic sample data
standards/standards.csv     the learning standards (key, type, statement)
standards/standards.placeholder.csv   12 generic sample standards: a minimal
                            starting point if you'd rather build your own from
                            scratch than edit the full real list above
lookup/standards_lookup_table.csv   standard x modality -> required questions
lookup/standards_lookup_table.placeholder.csv   the matching lookup for the
                            12 placeholder standards (kept in sync with the
                            placeholder file above)
scripts/
  convert_webwork.py        WeBWorK 'student progress' export -> canonical scores
  convert_gradescope.py     Gradescope-style exam/tutorial sheets -> canonical scores
  evaluate_standards.py     canonical scores + lookup -> standards_achieved.csv
  make_reports.py           standards_achieved -> per-student HTML / LaTeX reports
sample_data/                30 fictitious students in realistic export formats
docs/
  01-standards-based-grading.md   what SBG is, with references
  02-the-mat188-implementation.md the real course this template is based on
  03-data-format.md               the fixed data formats, precisely specified
  04-labeling-scheme.md           the labeling system and how to adapt it
```

## The pipeline in one paragraph

Every gradeable item on every assessment gets a **score key** (e.g.
`ww1-2`, `tut3-2-1`, `ex1-2-1`). Converters turn each platform's export
into one canonical long table: `login_name, score_key, correct,
is_graded`. The **lookup table** says, for each learning standard and each
assessment modality, which score keys demonstrate the standard and how
many of them must be correct (`2|ww1-1,ww1-2,ww1-3` = "2 of these 3").
The evaluator applies those rules per student and writes a wide
`standards_achieved.csv` (1 = demonstrated, 0 = assessed but not yet
demonstrated, blank = not yet assessed). Because evaluation takes the best
evidence across *all* score records, appending a resubmission file can
only add demonstrations, never remove them — *only eventual mastery
matters*. The report generator then renders one progress report per
student.

## Adapting it to your course

1. Write your standards in `standards/standards.csv` (see
   `docs/04-labeling-scheme.md` for the key grammar).
2. Label your assessment questions with score keys and record them in
   `lookup/standards_lookup_table.csv`.
3. Point `config.yml` at your real exports; add converters if your
   platform differs (each one is ~50 lines).
4. Decide your grade mapping (e.g. MAT188 gave full marks for the SBG
   component at >= 70% of standards demonstrated).

## Credits and provenance

- Course design, learning standards system, and papers: Camelia
  Karimianpour (University of Toronto), the lead author, credited
  throughout.
- Analysis pipeline (Python): Simeon Wong,
  [dtxe/mat188_learning_standards](https://github.com/dtxe/mat188_learning_standards).
- LaTeX system: Samuel P. Dumas (in the companion `MAT188-Restructured`
  repository).
- This template was assembled from the real MAT188 2023/2024 materials
  with all student data replaced by synthetic records.

See `AUTHORS.md` for the full contributor roles and
`docs/01-standards-based-grading.md` for the research literature.

## License

Dual-licensed so the software is maximally reusable while the teaching
materials carry a clear attribution requirement:

- **Code** (Python pipeline, scripts, notebook) — MIT License
  (`LICENSE-CODE.txt`).
- **Content** (standards, lookup tables, docs, sample data) — Creative
  Commons Attribution-NonCommercial-ShareAlike 4.0 International,
  CC BY-NC-SA 4.0 (`LICENSE-CONTENT.txt`): non-commercial use with
  credit, and adaptations shared under the same license.

See `LICENSE` for the split.

## How to cite / give credit

If you use or adapt this material, please credit the authors —
**ATTRIBUTION.md** has ready-to-copy text (plain language and BibTeX),
including which contributor to credit for the code vs. the LaTeX vs. the
overall design. GitHub will also surface a citation from `CITATION.cff`.
