# The labeling scheme

Two key families do all the work: **LS keys** name standards, **score
keys** name gradeable items. The lookup table is the only place they meet.

## LS keys (standards)

Grammar (from the MAT188 LaTeX system):

```
<unit>-<TYPE>-<mnemonic>
ch3-COM-linind      "chapter 3, computational, linear independence"
chg-WRIT-matnot     "general (course-wide), writing, matrix notation"
```

- `unit`: chapter/module tag (`ch0`..`ch7`, plus `chg` for course-wide
  standards in MAT188).
- `TYPE`: the standard classification — MAT188 uses COM(putational),
  CON(ceptual), VG (visual/geometry), WRIT(ing).
- `mnemonic`: short human-readable slug, unique within the unit.

These same keys label questions in the LaTeX question bank, rows of the
lookup table, and rows of every student report, so one key follows a
standard through its entire life cycle.

## Score keys (gradeable items)

| pattern | example | reading |
|---|---|---|
| `ww<set>-<problem>` | `ww1-2` | WeBWorK set 1, problem 2 |
| `gw<quiz>-<problem>` | `gw2-5` | gateway quiz 2, problem 5 |
| `tut<week>-<group>-<slot>` | `tut6-2-1` | tutorial week 6, grading group 2, standard-slot 1 |
| `ex<exam>-<question>-<part>` | `ex2-1-2` | midterm 2, question 1, part 2 |

Semantics confirmed by the course coordinator:

- **WeBWorK/gateway:** the export filename is the assessment id; problem
  numbers come from the export. The pipeline never parses meaning out of
  these keys — they are matched verbatim against the lookup table.
- **Tutorials:** not every question is graded for every student; students
  are assigned a **grading group** by tutorial section each week, and the
  middle field says which group a question belongs to. The last field is
  the **standard slot within the question**: it is 1 unless the same
  graded question carries more than one standard (e.g. `tut2-1-1` and
  `tut2-1-2` are two standards assessed on the same submission).
- **Exams:** `ex<exam>-<question>-<part>`; each exam part carries exactly
  ONE standard (unlike tutorial questions). In 2023 the parts were
  lettered (`ex1-1a`); 2024 switched to numeric parts — keys are
  conventions, so either works as long as the lookup table matches.

## Adapting the scheme to your course (the flexible version)

The pipeline treats score keys as opaque strings everywhere except the
tutorial grading-group logic, so you can rename freely. Recommended
generalized grammar:

```
LS key:     <unit>-<TYPE>-<mnemonic>
score key:  <assessment>-<item>[-<slot>]
```

with your own vocabularies for `unit`, `TYPE`, and `assessment` (e.g.
`week3`, `lab`, `quiz`; `PROOF`, `MODEL`). Constraints to keep:

1. **Keys are identifiers, not data.** Never encode anything the pipeline
   must compute on, except the tutorial `-<group>-` field if you use
   grading groups (set `use_grading_groups: false` to drop that logic and
   the constraint with it).
2. **Hyphen-separated, no spaces**, so keys survive spreadsheets, LaTeX,
   filenames, and regexes unchanged.
3. **Filename = assessment id** for WeBWorK-style exports.
4. Keep keys **stable across the term**; they are your foreign keys. If a
   question moves or splits, add a manual-overrides row rather than
   renaming history.
5. One standard per exam part keeps exam grading rubrics binary per
   standard (the MAT188 choice); multi-standard items are fine where a
   single submission is assessed for several standards (tutorial slots).

The regexes that recognize tutorial and exam keys are arguments of the
converter functions (`key_pattern=`), so a course with e.g. `lab4-2-1`
keys only changes a pattern in `config`-level code, not the pipeline.
