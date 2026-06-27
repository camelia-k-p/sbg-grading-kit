# Fixed data formats

The pipeline has ONE canonical internal format; everything else is a
converter into it or a view out of it.

## 1. Canonical score table (the hub)

One row per (student, gradeable item, source record):

| column | type | meaning |
|---|---|---|
| `login_name` | str | stable student identifier, consistent across ALL sources |
| `score_key` | str | identifier of the gradeable item (see doc 04) |
| `correct` | bool | did this record demonstrate the item |
| `is_graded` | bool | does this record count as assessed for this student |

Rules:
- Multiple rows per (student, key) are allowed and expected (attempts,
  resubmissions, manual overrides). Evaluation uses `any(correct)` and
  `any(is_graded)` per key, so extra evidence can only help —
  this is how "only eventual mastery matters" is implemented.
- `is_graded=False` records the item existed but did not count for this
  student (e.g. a tutorial question outside their grading group).
- Saved as `output/raw_scores.csv` for auditing every run.

## 2. Standards list — `standards/standards.csv`

| column | meaning |
|---|---|
| `ls_key` | unique standard key, grammar in doc 04 |
| `unit` | unit/chapter tag (redundant with key prefix; convenient for filtering) |
| `type` | classification: COM / CON / VG / WRIT (configurable) |
| `statement` | the student-facing "I can ..." sentence |

## 3. Lookup table — `lookup/standards_lookup_table.csv`

Rows = standards; one column per **modality** (assessment family that you
want reported separately: webwork, gateway, tutorial, exam, ...). Cell
grammar, identical to the MAT188 original:

```
[n_required|]score_key[,score_key...]
```

- `2|gw1-1,gw1-2,gw1-3` -> at least 2 of these 3 correct demonstrates the
  standard in this modality.
- `ww1-4,ww1-5` (no `n|`) -> ALL listed keys required.
- empty cell -> standard not assessed in this modality.

Evaluation per student per (standard, modality), exactly as in
`lsa_v4.py`: keys with no data anywhere in the score table are dropped
from the requirement first (assessment not yet given); among the
remaining keys, let g = number graded for this student and c = number
correct; the standard is achieved iff `c >= 1` and `c/g >= n_required/m`
(m = number of keys). If `g = 0` the result is **NA — not yet assessed**,
which reports show as blank rather than as failure.

An .xlsx with a `grading` sheet (the original MAT188 layout) is accepted
as a drop-in replacement.

## 4. Platform export formats (converter inputs)

**WeBWorK** (`scripts/convert_webwork.py`): the standard "student
progress" CSV export, one file per problem set; the filename becomes the
assessment id (`ww1.csv` -> keys `ww1-1`, `ww1-2`, ... from the PROB
NUMBER row). STATUS == 1 means correct.

**Exams** (`scripts/convert_gradescope.py: parse_exam`): one consolidated
sheet per exam: a student id column (`login_name`/`UTORid`, or `Email`
joined through the roster) plus one TRUE/FALSE column per score key.

**Tutorials** (`parse_tutorials`): one consolidated sheet for the term:
student id column; `SBG1..SBGn` columns giving each student's assigned
grading group per week; one column per tutorial score key `tutW-G-S`.
A key counts as graded for a student only when G equals their assigned
group for week W. With `use_grading_groups: false`, any non-empty mark
counts as graded instead.

**Resubmissions:** a second tutorial-format file listed under
`tutorial_files` in `config.yml`. Appending it adds score rows; mastery
can only increase.

**Manual overrides** — `sample_data/manual_scores.csv`: canonical columns
plus a free `comment` column. Overrides REPLACE platform rows with the
same (login_name, score_key), so they also win over wrong platform data.

## 5. Output — `standards_achieved.csv`

Wide table, one row per student. Columns are a 2-level header
(modality, standard) with values 1 / 0 / blank
(demonstrated / assessed-not-demonstrated / not yet assessed), plus
`summary` columns per modality: `achieved_*`, `tested_*`, `frac_*`.
This file is the interface to grade computation (e.g. "full marks if
frac_tutorial >= 0.7") and to the report generator.
