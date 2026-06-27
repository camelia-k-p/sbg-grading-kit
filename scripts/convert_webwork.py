# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2026 Camelia Karimianpour and Simeon Wong
# Part of the MAT188 Standards-Based Grading Starter Kit.
# Code is MIT-licensed (see LICENSE-CODE.txt). The analysis pipeline is
# adapted from Simeon Wong's dtxe/mat188_learning_standards.
# Credit/attribution: see AUTHORS.md and ATTRIBUTION.md.

"""Convert a WeBWorK 'student progress' CSV export into canonical long scores.

WeBWorK export layout (one file per problem set):
  - several metadata rows (SET NAME, PROB NUMBER, CLOSE DATE, ...)
  - a header row starting with 'STUDENT ID' (cols: STUDENT ID, login ID,
    LAST NAME, FIRST NAME, SECTION, then one STATUS/#corr/#incorr block
    per problem)
  - one row per student

The export FILENAME (without extension) becomes the assessment id:
  ww1.csv -> score_keys ww1-1, ww1-2, ...   (problem numbers from row 'PROB NUMBER')

Canonical output columns: login_name, score_key, correct, is_graded
A problem is 'correct' when its STATUS == 1 (all parts correct).
Adapted from wwparse_v2.py in https://github.com/dtxe/mat188_learning_standards
"""
import os
import pandas as pd


def parse_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename, header=[6, 2])
    df.columns = pd.MultiIndex.from_tuples([
        (col[1].strip() if col[1].strip().isdigit() else 'ID', col[0].strip())
        for col in df.columns
    ])

    set_name = os.path.splitext(os.path.basename(filename))[0].split('_')[-1]

    # drop any residual header rows: data starts after the row whose
    # STUDENT ID cell literally repeats 'STUDENT ID'
    marker = df[df[('ID', 'STUDENT ID')].astype(str).str.startswith('STUDENT ID').fillna(False)]
    if len(marker):
        df = df.iloc[marker.index[0] + 1:]

    problem_cols = [c for c in df.columns if c[1] == 'STATUS']

    long_df = pd.melt(df, id_vars=[('ID', 'login ID')], value_vars=problem_cols,
                      var_name='problem_num', value_name='score')
    long_df.columns = ['login_name', 'problem_num', 'score']
    long_df['score'] = pd.to_numeric(long_df['score'].astype(str).str.strip(),
                                     errors='coerce')
    long_df['score_key'] = long_df['problem_num'].astype(int).map(
        lambda x: f'{set_name}-{x:d}')
    long_df['login_name'] = long_df['login_name'].astype(str).str.strip()
    long_df['correct'] = long_df['score'] == 1
    long_df['is_graded'] = True
    long_df = long_df[long_df['login_name'].ne('') & long_df['login_name'].ne('nan')]
    return (long_df[['login_name', 'score_key', 'correct', 'is_graded']]
            .sort_values(['login_name', 'score_key']).reset_index(drop=True))


if __name__ == '__main__':
    import sys
    print(parse_csv(sys.argv[1]).head(20))
