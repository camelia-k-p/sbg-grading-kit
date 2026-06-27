# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2026 Camelia Karimianpour and Simeon Wong
# Part of the MAT188 Standards-Based Grading Starter Kit.
# Code is MIT-licensed (see LICENSE-CODE.txt). The analysis pipeline is
# adapted from Simeon Wong's dtxe/mat188_learning_standards.
# Credit/attribution: see AUTHORS.md and ATTRIBUTION.md.

"""Convert Gradescope-style exports into canonical long scores.

Two shapes are supported:

1. EXAM sheet (one file per exam):
   columns: Email (or login_name), then one column per score_key
   e.g.  ex1-1-1, ex1-1-2, ...   cells TRUE/FALSE/1/0/blank
   Every present cell counts as graded.

2. TUTORIAL consolidated sheet (one file for the whole term):
   columns: login_name (or UTORid), SBG1..SBGn (grading-group assignment
   per tutorial week), then one column per tutorial score_key tutW-G-S.
   A question counts as graded for a student only when its grading group G
   matches the student's assigned group for week W (column SBGW).
   This mirrors lsa_v4.py in https://github.com/dtxe/mat188_learning_standards
"""
import re
import pandas as pd

TRUTHY = {'TRUE': True, 'FALSE': False, True: True, False: False,
          1: True, 0: False, 1.0: True, 0.0: False, '1': True, '0': False}


def _read(path):
    return pd.read_excel(path) if str(path).lower().endswith('.xlsx') else pd.read_csv(path)


def _login_col(df, roster=None):
    """Return df with a login_name column (joining via roster email if needed)."""
    for c in ('login_name', 'UTORid', 'utorid'):
        if c in df.columns:
            return df.rename(columns={c: 'login_name'})
    if 'Email' in df.columns and roster is not None:
        df = df.merge(roster[['Email', 'login_name']], how='left', on='Email')
        return df
    raise ValueError('no login_name/UTORid column and no roster to map Email')


def parse_exam(path, key_pattern=r'^ex\d+-\d+-\d+$', roster=None) -> pd.DataFrame:
    df = _login_col(_read(path), roster)
    key_cols = [c for c in df.columns if re.match(key_pattern, str(c))]
    long_df = df.melt(id_vars='login_name', value_vars=key_cols,
                      var_name='score_key', value_name='raw')
    long_df['correct'] = long_df['raw'].map(TRUTHY)
    long_df = long_df.dropna(subset=['login_name', 'correct'])
    long_df['is_graded'] = True
    return long_df[['login_name', 'score_key', 'correct', 'is_graded']]


def parse_tutorials(path, key_pattern=r'^tut\d{1,2}[\.\-]\d[\.\-]\d{1,2}$',
                    roster=None, use_grading_groups=True) -> pd.DataFrame:
    df = _login_col(_read(path), roster)
    key_cols = [c for c in df.columns if re.match(key_pattern, str(c))]
    long_df = df.melt(id_vars='login_name', value_vars=key_cols,
                      var_name='score_key', value_name='raw')
    long_df['correct'] = long_df['raw'].map(TRUTHY)
    long_df['score_key'] = long_df['score_key'].str.replace('.', '-', regex=False)

    parts = long_df['score_key'].str.extract(r'tut(\d{1,2})-(\d)-\d{1,2}')
    long_df['week'] = parts[0].astype(int)
    long_df['group'] = parts[1].astype(int)

    sbg_cols = [c for c in df.columns if re.match(r'^SBG\d{1,2}$', str(c))]
    if use_grading_groups and sbg_cols:
        assigned = df.melt(id_vars='login_name', value_vars=sbg_cols,
                           var_name='week', value_name='assigned_group')
        assigned['week'] = assigned['week'].str.extract(r'SBG(\d{1,2})').astype(int)
        long_df = long_df.merge(assigned, how='left', on=['login_name', 'week'])
        long_df['is_graded'] = long_df['group'] == long_df['assigned_group']
        long_df['correct'] = long_df['correct'].astype('boolean').fillna(False).astype(bool)
    else:
        # without grading groups: graded == has a mark
        long_df['is_graded'] = long_df['correct'].notna() & (long_df['correct'] == True)

    long_df = long_df.dropna(subset=['login_name'])
    return long_df[['login_name', 'score_key', 'correct', 'is_graded']]
