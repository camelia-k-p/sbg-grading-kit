# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2026 Camelia Karimianpour and Simeon Wong
# Part of the MAT188 Standards-Based Grading Starter Kit.
# Code is MIT-licensed (see LICENSE-CODE.txt). The analysis pipeline is
# adapted from Simeon Wong's dtxe/mat188_learning_standards.
# Credit/attribution: see AUTHORS.md and ATTRIBUTION.md.

"""Run the whole SBG pipeline: convert exports -> evaluate -> reports.

    python run_pipeline.py config.yml [--latex]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))
import yaml
import evaluate_standards
import make_reports

cfg_path = sys.argv[1] if len(sys.argv) > 1 else 'config.yml'
with open(cfg_path) as f:
    config = yaml.safe_load(f)
os.makedirs(config['output_dir'], exist_ok=True)

evaluate_standards.run(config)
config['latex'] = '--latex' in sys.argv
make_reports.build(config)
