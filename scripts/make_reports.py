# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2026 Camelia Karimianpour and Simeon Wong
# Part of the MAT188 Standards-Based Grading Starter Kit.
# Code is MIT-licensed (see LICENSE-CODE.txt). The analysis pipeline is
# adapted from Simeon Wong's dtxe/mat188_learning_standards.
# Credit/attribution: see AUTHORS.md and ATTRIBUTION.md.

"""Generate per-student learning-standard reports from standards_achieved.csv.

Default output: one self-contained HTML file per student (easy to upload to
an LMS or email). With --latex, also writes a combined.tex modelled on the
MAT188 report (ls_report_header.tex / ls_report_page.tex by Simeon Wong,
https://github.com/dtxe/mat188_learning_standards) that you can compile with
pdflatex to get one PDF with one page per student for Gradescope upload.

Standard statements are read from standards.csv so reports are readable
without the LaTeX standards bank.
"""
import argparse
import re
import os
import pandas as pd
import yaml

CHECK, CROSS, BLANK = '&#10003;', '&#10007;', ''

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Learning Standard Report — {login}</title>
<style>
 body {{ font-family: Georgia, serif; max-width: 50em; margin: 2em auto; }}
 table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
 th, td {{ border: 1px solid #999; padding: .4em .6em; text-align: left; }}
 th {{ background: #eee; }}
 .ach {{ color: #06623b; font-weight: bold; }} .not {{ color: #9b1c1c; }}
 caption {{ text-align:left; font-weight:bold; padding-bottom:.4em; }}
</style></head><body>
<h1>Learning Standard Report</h1>
<p><b>Student:</b> {name} ({login})</p>
<p>{preamble}</p>
<table><caption>Progress summary</caption>
<tr><th>Modality</th><th># demonstrated</th><th># assessed so far</th></tr>
{summary_rows}
</table>
<table><caption>Detailed report</caption>
<tr><th>Learning standard</th>{mod_heads}</tr>
{detail_rows}
</table>
<p style="font-size:smaller">&#10003; demonstrated &nbsp;&middot;&nbsp;
&#10007; assessed, not yet demonstrated &nbsp;&middot;&nbsp;
blank: not yet assessed in this modality.</p>
</body></html>"""


def latex_escape(s: str) -> str:
    """Minimal LaTeX sanitizer for standard statements.

    Statements are plain text but may carry a few math-like tokens
    (R^n, A^T, A^-1, x^*). Escape the LaTeX specials, then wrap simple
    superscripts in math mode so pdflatex does not choke on a raw '^'.
    """
    s = str(s)
    for ch in '&%#_':
        s = s.replace(ch, '\\' + ch)
    # R^n -> blackboard-bold R (nicer rendering)
    s = re.sub(r'R\^(\w+)', r'$\\mathbb{R}^{\1}$', s)
    # other superscripts: A^T, A^-1, x^* -> math mode
    s = re.sub(r'([A-Za-z0-9\)\]])\^(\{[^}]*\}|-?\w+|\*)', r'$\1^{\2}$', s)
    # only a truly stray caret (after a space or at the start) -> literal
    s = re.sub(r'(?<=\s)\^|\A\^', r'\\textasciicircum{}', s)
    return s


def mark(v, latex=False):
    if pd.isna(v):
        return '' if latex else BLANK
    if int(v) == 1:
        return r'\checkmark' if latex else f'<span class="ach">{CHECK}</span>'
    return r'\text{\sffamily X}' if latex else f'<span class="not">{CROSS}</span>'


def build(config):
    out = config['output_dir']
    sa = pd.read_csv(f'{out}/standards_achieved.csv', header=[0, 1], index_col=0)
    standards = pd.read_csv(config['standards_csv']).set_index('ls_key')
    roster = pd.read_csv(config['roster']).set_index('login_name')
    preamble = config.get('report_preamble',
                          'This report lists the learning standards assessed '
                          'so far and whether you have demonstrated them.')

    detail = sa.drop(columns='summary', level=0)
    modalities = sorted(detail.columns.get_level_values('modality').unique())

    html_dir = f'{out}/reports_html'
    os.makedirs(html_dir, exist_ok=True)
    latex_pages = []

    for login, row in detail.iterrows():
        name = roster['name'].get(login, '') if 'name' in roster.columns else ''
        pivot = pd.DataFrame({m: row.get(m) for m in modalities})
        pivot = pivot.dropna(how='all')

        srows = []
        for m in modalities:
            tested = pivot[m].count()
            ach = int(pivot[m].sum()) if tested else 0
            srows.append(f'<tr><td>{m}</td><td>{ach}</td><td>{tested}</td></tr>')

        drows = []
        for ls_key, vals in pivot.iterrows():
            text = standards['statement'].get(ls_key, '')
            cells = ''.join(f'<td>{mark(vals[m])}</td>' for m in modalities)
            drows.append(f'<tr><td><b>{ls_key}</b><br>{text}</td>{cells}</tr>')

        html = PAGE.format(login=login, name=name, preamble=preamble,
                           summary_rows='\n'.join(srows),
                           mod_heads=''.join(f'<th>{m}</th>' for m in modalities),
                           detail_rows='\n'.join(drows))
        with open(f'{html_dir}/{login}.html', 'w') as f:
            f.write(html)

        if config.get('latex'):
            lrows = [fr'\textbf{{{ls_key}}} {latex_escape(standards["statement"].get(ls_key, ""))} & '
                     + ' & '.join(mark(vals[m], latex=True) for m in modalities)
                     + r' \\ \midrule'
                     for ls_key, vals in pivot.iterrows()]
            latex_pages.append(LATEX_PAGE.format(
                name=name or login, login=login,
                mod_heads=' & '.join(fr'\textbf{{{m}}}' for m in modalities),
                ncols='l|' * len(modalities),
                summary='\n'.join(
                    fr'{m} & {int(pivot[m].sum()) if pivot[m].count() else 0} & {pivot[m].count()} \\ \midrule'
                    for m in modalities),
                rows='\n'.join(lrows)))

    print(f'wrote {len(detail)} HTML reports to {html_dir}/')
    if config.get('latex'):
        tex = LATEX_HEADER + '\n'.join(latex_pages) + '\n\\end{document}\n'
        with open(f'{out}/reports_combined.tex', 'w') as f:
            f.write(tex)
        print(f'wrote {out}/reports_combined.tex (compile with pdflatex)')


LATEX_HEADER = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{ltablex,booktabs,amssymb,amsmath}
\begin{document}
"""

LATEX_PAGE = r"""
\setcounter{{page}}{{1}}
{{\Large \centering \textbf{{Learning Standard Report}}\par}}
\medskip
\noindent Student: {name} ({login})
\subsection*{{Progress Summary}}
\begin{{tabularx}}{{\textwidth}}{{||X|l|l||}}
\toprule
\textbf{{Modality}} & \textbf{{\# demonstrated}} & \textbf{{\# assessed}} \\ \midrule \midrule
{summary}
\bottomrule
\end{{tabularx}}
\subsection*{{Detailed Report}}
\begin{{tabularx}}{{\textwidth}}{{||X|{ncols}|}}
\toprule
\textbf{{Learning Standard}} & {mod_heads} \\ \midrule \midrule
{rows}
\bottomrule
\end{{tabularx}}
\newpage
"""

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('--latex', action='store_true')
    args = ap.parse_args()
    with open(args.config) as f:
        config = yaml.safe_load(f)
    config['latex'] = args.latex
    build(config)
