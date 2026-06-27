# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2026 Camelia Karimianpour and Simeon Wong
# Part of the MAT188 Standards-Based Grading Starter Kit.
# Code is MIT-licensed (see LICENSE-CODE.txt). The analysis pipeline is
# adapted from Simeon Wong's dtxe/mat188_learning_standards.
# Credit/attribution: see AUTHORS.md and ATTRIBUTION.md.

"""Regenerate the synthetic sample data (30 fake students, deterministic).

The formats imitate real platform exports:
  - sample_data/webwork/*.csv : WeBWorK 'student progress' export layout
  - sample_data/exams/midterm1.csv : Gradescope-style consolidated exam sheet
  - sample_data/tutorials/tutorial_scores.csv : consolidated tutorial sheet
    with SBG grading-group columns
All students, scores, and logins are fictitious.
"""
import csv
import os
import random

random.seed(188)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'sample_data')

FIRST = ['Ada', 'Blaise', 'Carl', 'Daria', 'Emmy', 'Felix', 'Grace', 'Hugo',
         'Ines', 'Jonas', 'Katya', 'Leon', 'Maryam', 'Nash', 'Olga', 'Pierre',
         'Qiu', 'Rosa', 'Sofia', 'Tycho', 'Una', 'Vito', 'Wanda', 'Xen',
         'Yuki', 'Zeno', 'Alan', 'Berta', 'Cole', 'Dina']
LAST = ['Lovelace', 'Pascal', 'Gauss', 'Noether', 'Euler', 'Hopper', 'Banach',
        'Kovalevskaya', 'Hilbert', 'Mirzakhani', 'Turing', 'Germain',
        'Erdos', 'Ramanujan', 'Cartan', 'Galois', 'Riemann', 'Cauchy',
        'Fourier', 'Laplace', 'Abel', 'Jacobi', 'Weyl', 'Frobenius',
        'Dirichlet', 'Kolmogorov', 'Markov', 'Chebyshev', 'Lagrange', 'Bernoulli']

students = []
for i in range(30):
    login = f'student{i+1:02d}'
    students.append({'login_name': login, 'name': f'{FIRST[i]} {LAST[i]}',
                     'email': f'{login}@example.edu', 'sid': 7100000001 + i,
                     'tutorial': f'TUT{(i % 3) + 1:04d}',
                     'ability': random.uniform(0.35, 0.95)})

os.makedirs(f'{DATA}/webwork', exist_ok=True)
os.makedirs(f'{DATA}/exams', exist_ok=True)
os.makedirs(f'{DATA}/tutorials', exist_ok=True)

# ---- roster --------------------------------------------------------------
with open(f'{DATA}/roster.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['login_name', 'name', 'Email', 'sid', 'tutorial'])
    for s in students:
        w.writerow([s['login_name'], s['name'], s['email'], s['sid'], s['tutorial']])

# ---- WeBWorK exports (mimic the real export layout) ----------------------
def ww_export(fname, nprob):
    rows = []
    rows.append(['NO OF FIELDS'] + [''] * (4 + nprob))
    rows.append(['SET NAME', '', '', '', ''] + [os.path.splitext(fname)[0]] * nprob)
    rows.append(['PROB NUMBER', '', '', '', ''] + [str(p + 1) for p in range(nprob)])
    rows.append(['CLOSE DATE', '', '', '', ''] + ['01/01/2030'] * nprob)
    rows.append(['CLOSE TIME', '', '', '', ''] + ['11:00pm EST'] * nprob)
    rows.append(['PROB VALUE', '', '', '', ''] + ['1'] * nprob)
    rows.append(['STUDENT ID', 'login ID', 'LAST NAME', 'FIRST NAME', 'SECTION']
                + ['STATUS'] * nprob)
    for s in students:
        first, last = s['name'].split(' ', 1)
        scores = ['1' if random.random() < s['ability'] else '0'
                  for _ in range(nprob)]
        rows.append([str(s['sid']), s['login_name'], last, first, ''] + scores)
    with open(f'{DATA}/webwork/{fname}', 'w', newline='') as f:
        csv.writer(f).writerows(rows)

ww_export('ww1.csv', 8)
ww_export('ww2.csv', 8)
ww_export('gw1.csv', 6)

# ---- consolidated tutorial sheet ------------------------------------------
# 3 tutorial weeks; 3 grading groups; keys tutW-G-S (S = LS slot in question)
tut_keys = ['tut1-1-1', 'tut1-2-1', 'tut1-3-1',
            'tut2-1-1', 'tut2-1-2', 'tut2-2-1', 'tut2-3-1',
            'tut3-1-1', 'tut3-2-1', 'tut3-3-1']
with open(f'{DATA}/tutorials/tutorial_scores.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['login_name', 'SBG1', 'SBG2', 'SBG3'] + tut_keys)
    for s in students:
        groups = [random.randint(1, 3) for _ in range(3)]
        row = [s['login_name']] + groups
        for k in tut_keys:
            week, grp = int(k.split('-')[0][3:]), int(k.split('-')[1])
            if grp == groups[week - 1]:
                row.append('TRUE' if random.random() < s['ability'] else 'FALSE')
            else:
                row.append('')          # not graded for this student
        w.writerow(row)

# resubmission round: students who failed their graded tut question try again
with open(f'{DATA}/tutorials/resubmission_scores.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['login_name', 'SBG1', 'SBG2', 'SBG3'] + tut_keys)
    for s in students:
        if random.random() < 0.6:        # 60% use the resubmission (cf. CEEA paper)
            groups = [random.randint(1, 3) for _ in range(3)]
            row = [s['login_name']] + groups
            for k in tut_keys:
                week, grp = int(k.split('-')[0][3:]), int(k.split('-')[1])
                ok = random.random() < min(0.95, s['ability'] + 0.25)
                row.append(('TRUE' if ok else 'FALSE')
                           if grp == groups[week - 1] else '')
            w.writerow(row)

# ---- exam sheet (Gradescope-style, Email keyed) ---------------------------
ex_keys = ['ex1-1-1', 'ex1-1-2', 'ex1-2-1', 'ex1-2-2', 'ex1-3-1']
with open(f'{DATA}/exams/midterm1.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Name', 'SID', 'Email'] + ex_keys)
    for s in students:
        marks = ['TRUE' if random.random() < s['ability'] else 'FALSE'
                 for _ in ex_keys]
        w.writerow([s['name'], s['sid'], s['email']] + marks)

# ---- manual overrides ------------------------------------------------------
with open(f'{DATA}/manual_scores.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['login_name', 'score_key', 'correct', 'is_graded', 'comment'])
    w.writerow(['student03', 'tut2-1-1', 'TRUE', 'TRUE', 'petition'])
    w.writerow(['student07', 'ex1-2-1', 'TRUE', 'TRUE', 'regrade request'])

print('sample data written to', DATA)
