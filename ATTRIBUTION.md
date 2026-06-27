# How to give credit

If you use, adapt, or build on this material, please credit the authors.
This page gives you **ready-to-copy** credit text for the common cases.
Pick the block that matches what you used, fill in any `[bracketed]`
placeholder, and paste it.

The licenses require attribution: the content is under **CC BY-NC-SA 4.0**
(non-commercial, and adaptations must be shared under the same license)
and the code is under **MIT** (see `LICENSE`). Crediting the right people
for the right part is also just good academic practice.

## Who to credit for what

| If you used... | Credit |
|---|---|
| The standards, labeling scheme, SBG design, or the project as a whole | **Camelia Karimianpour** |
| The Python pipeline, converters, evaluator, or notebook | **Simeon Wong** (with Camelia Karimianpour) |
| The LaTeX system (style packages, worksheet templates) | **Samuel P. Dumas** (with Camelia Karimianpour) |


---

## 1. Quick attribution line (CC BY-NC-SA — the minimum)

Use this when you reuse the standards, lookup tables, docs, or sample
data more or less as-is. It contains the four attribution elements
(title, author, source, license):

> "MAT188 Standards-Based Grading Starter Kit" by Camelia Karimianpour,
> licensed under CC BY-NC-SA 4.0. Source: [link to the repository or page].

If you **changed** it, say so — and note that adaptations must be shared
under the same license (ShareAlike):

> Adapted from "MAT188 Standards-Based Grading Starter Kit" by Camelia
> Karimianpour (CC BY-NC-SA 4.0); modifications by [your name]. This
> adaptation is also licensed under CC BY-NC-SA 4.0. Source: [link].

---

## 2. Using it in your own course

A line for a syllabus, course site, or handout:

> The standards-based grading framework used in this course is adapted
> from the MAT188 Standards-Based Grading system developed by Camelia
> Karimianpour (University of Toronto), with the analysis pipeline by
> Simeon Wong and the LaTeX materials by Samuel P. Dumas. Used under
> CC BY-NC-SA 4.0 (content) / MIT (code).

---

## 3. Using or adapting the Python pipeline

In your README, code comments, or methods section:

> This analysis pipeline is adapted from the MAT188 Standards-Based
> Grading Starter Kit (MIT License) by Camelia Karimianpour and Simeon
> Wong, which builds on Simeon Wong's `dtxe/mat188_learning_standards`.
> Source: [link].

Keeping the existing copyright header at the top of each `.py` file (and
in the `LICENSE-CODE.txt` you redistribute) already satisfies the MIT
attribution requirement.

---

## 4. Using or adapting the LaTeX system

> The standards-based LaTeX environment (learning-standards, question
> bank, and document templates) was created by Samuel P. Dumas and
> Camelia Karimianpour (University of Toronto). Used/adapted under
> CC BY-NC-SA 4.0. Source: [link].

---

## 5. Academic citation

### Plain text

> Karimianpour, C., Wong, S., & Dumas, S. P. ([year]). *MAT188
> Standards-Based Grading Starter Kit* [software and teaching
> materials]. University of Toronto. [link]

### BibTeX

```bibtex
@misc{mat188sbg,
  author       = {Karimianpour, Camelia and Wong, Simeon and Dumas, Samuel P.},
  title        = {{MAT188 Standards-Based Grading Starter Kit}},
  year         = {[year]},
  howpublished = {Software and teaching materials},
  organization = {University of Toronto},
  note         = {Content licensed CC BY-NC-SA 4.0; code licensed MIT},
  url          = {[link]}
}
```

If you used only the Python pipeline, you may also cite the upstream
work it builds on:

```bibtex
@misc{wong_mat188_ls,
  author       = {Wong, Simeon},
  title        = {{mat188\_learning\_standards}},
  howpublished = {Software},
  url          = {https://github.com/dtxe/mat188_learning_standards}
}
```

---

## Notes (please confirm before publishing)

- Replace every `[link]`, `[year]`, and `[your name]` placeholder with
  real values. The repository URL is not yet set, so it is left as a
  placeholder here and in `CITATION.cff`.

