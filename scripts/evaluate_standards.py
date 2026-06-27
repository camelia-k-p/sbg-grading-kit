# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2026 Camelia Karimianpour and Simeon Wong
# Part of the MAT188 Standards-Based Grading Starter Kit.
# Code is MIT-licensed (see LICENSE-CODE.txt). The analysis pipeline is
# adapted from Simeon Wong's dtxe/mat188_learning_standards.
# Credit/attribution: see AUTHORS.md and ATTRIBUTION.md.

"""Evaluate which learning standards each student has demonstrated.

Inputs
  scores : canonical long table (login_name, score_key, correct, is_graded)
  lookup : standards lookup table; rows = LS keys, one column per modality,
           cells = '[n_required|]key1,key2,...'  (no n -> all keys required)
  standards : standards.csv (ls_key, statement, ...) used for report text

Rule (identical to lsa_v4.py, https://github.com/dtxe/mat188_learning_standards):
  for a standard x modality with requirement n|k1..km,
  among the keys that were GRADED for this student, the standard is achieved
  when at least one is correct AND (#correct / #graded) >= n/m.
  If none of the keys were graded for this student, the result is NA
  (not yet assessed) rather than 0.

Output: standards_achieved.csv — one row per student, one column per
standard x modality, plus summary columns (achieved/tested/fraction per
modality).
"""
import numpy as np
import pandas as pd


def parse_req(cell):
    """'2|gw1-1,gw1-2,gw1-3' -> (2, [...]);  'ww1-2,ww1-3' -> (2, [...])"""
    if pd.isna(cell) or not str(cell).strip():
        return None
    cell = str(cell).strip()
    if '|' in cell:
        n, keys = cell.split('|', 1)
        keys = [k.strip() for k in keys.split(',') if k.strip()]
        return int(n), keys
    keys = [k.strip() for k in cell.split(',') if k.strip()]
    return len(keys), keys


def load_lookup(path):
    df = (pd.read_excel(path, sheet_name='grading')
          if str(path).lower().endswith('.xlsx') else pd.read_csv(path))
    df = df[df['standard'].notna()]
    modalities = [c for c in df.columns
                  if c not in ('standard',) and not str(c).startswith('Unnamed')
                  and df[c].apply(lambda v: isinstance(v, str) and any(ch in str(v) for ch in '-|,')).any()]
    long = df.melt(id_vars='standard', value_vars=modalities,
                   var_name='modality', value_name='reqs').dropna(subset=['reqs'])
    long['parsed'] = long['reqs'].map(parse_req)
    return long.dropna(subset=['parsed'])


def evaluate(scores: pd.DataFrame, lookup_long: pd.DataFrame) -> pd.DataFrame:
    known_keys = set(scores['score_key'].unique())

    # ignore lookup keys with no data anywhere (e.g. assessments not yet given)
    def prune(parsed):
        n, keys = parsed
        keys = [k for k in keys if k in known_keys]
        return (min(n, len(keys)), keys) if keys else None
    lookup_long = lookup_long.assign(parsed=lookup_long['parsed'].map(prune))
    lookup_long = lookup_long.dropna(subset=['parsed'])

    by_student = dict(tuple(scores.groupby('login_name')))
    rows = {}
    for student, sdf in by_student.items():
        sdf = sdf.set_index('score_key')
        out = {}
        for _, r in lookup_long.iterrows():
            n_req, keys = r['parsed']
            graded, correct = 0, 0
            for k in keys:
                if k in sdf.index:
                    block = sdf.loc[[k]]
                    g = bool(block['is_graded'].any())
                    c = bool(block['correct'].any())
                else:
                    g, c = True, False   # graded by default (matches lsa_v4)
                graded += g
                correct += c
            if graded == 0:
                val = np.nan
            else:
                val = int(correct >= 1 and correct / graded >= n_req / len(keys))
            out[(r['modality'], r['standard'])] = val
        rows[student] = out

    result = pd.DataFrame.from_dict(rows, orient='index')
    result.columns = pd.MultiIndex.from_tuples(result.columns,
                                               names=['modality', 'standard'])
    result = result.sort_index()

    for m in result.columns.get_level_values('modality').unique():
        block = result[m]
        result[('summary', f'achieved_{m}')] = block.sum(axis=1, skipna=True)
        result[('summary', f'tested_{m}')] = block.count(axis=1)
        result[('summary', f'frac_{m}')] = block.mean(axis=1, skipna=True).round(3)
    return result


def run(config):
    import glob as g
    import convert_webwork, convert_gradescope

    roster = pd.read_csv(config['roster'])
    scores = []
    for f in sorted(g.glob(config.get('webwork_glob', ''))):
        print('webwork:', f)
        scores.append(convert_webwork.parse_csv(f))
    for f in sorted(g.glob(config.get('exam_glob', ''))):
        print('exam:', f)
        scores.append(convert_gradescope.parse_exam(f, roster=roster))
    tut = config.get('tutorial_files', [])
    for f in ([tut] if isinstance(tut, str) else tut):
        print('tutorials:', f)
        scores.append(convert_gradescope.parse_tutorials(
            f, roster=roster,
            use_grading_groups=config.get('use_grading_groups', True)))
    scores = pd.concat(scores, ignore_index=True)

    # manual overrides win over platform data
    if config.get('manual_scores'):
        manual = pd.read_csv(config['manual_scores'])
        mkey = set(zip(manual['login_name'], manual['score_key']))
        keep = [t not in mkey for t in zip(scores['login_name'], scores['score_key'])]
        scores = pd.concat([scores[keep], manual[scores.columns]], ignore_index=True)

    scores = scores[scores['login_name'].isin(roster['login_name'])]
    scores.to_csv(config['output_dir'] + '/raw_scores.csv', index=False)

    result = evaluate(scores, load_lookup(config['lookup_table']))
    result = result[result.index.isin(roster['login_name'])]
    result.to_csv(config['output_dir'] + '/standards_achieved.csv')
    print('wrote', config['output_dir'] + '/standards_achieved.csv',
          result.shape)
    return result


if __name__ == '__main__':
    import argparse, os, sys, yaml
    sys.path.insert(0, os.path.dirname(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    args = ap.parse_args()
    with open(args.config) as f:
        config = yaml.safe_load(f)
    os.makedirs(config['output_dir'], exist_ok=True)
    run(config)
