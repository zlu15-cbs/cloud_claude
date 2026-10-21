"""Shared helpers for the price-heterogeneity exploration.

load(panel) runs the Oct2026 notebook's own prep cells (2, 3, 4) unmodified, as code/solve_rc3_resumable.py does,
and returns product_data. Run from a folder that holds the panel's CSV.
"""
import json
import os

import matplotlib
matplotlib.use('Agg')

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOKS = {'index': 'main_Danny_Oct2026_index_market.ipynb', 'lev': 'main_Danny_Oct2026_leveraged_market.ipynb'}


def run_cells(panel, cells, ns=None):
    nb = json.load(open(os.path.join(CODE, NOTEBOOKS[panel])))
    ns = ns if ns is not None else {'__name__': '__main__', 'display': lambda *a, **k: None}
    for i in cells:
        src = '\n'.join(l for l in ''.join(nb['cells'][i]['source']).splitlines() if not l.strip().startswith(('%', '!')))
        exec(compile(src.replace('from IPython.display import display', 'pass'), f'{panel}_cell{i}', 'exec'), ns)
    return ns


def load(panel):
    return run_cells(panel, [2, 3, 4])['product_data'].reset_index(drop=True)
