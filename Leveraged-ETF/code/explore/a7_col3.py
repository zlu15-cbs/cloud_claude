"""Re-run Table A7 column (3), Panel A, from the 26-Sep broadspecial index notebook, with its code unchanged.

Cells 2, 3, 4, 11, 12, 13, 14 and 15 of main_Danny_March2026_testing_v3_nonLev_Apr2026_matchEgan_broadspecial.ipynb
are executed verbatim in one namespace. The only substitution is the optimizer object `bfgs` from cell 14, replaced by
the same SciPy BFGS (gtol 1e-7) wrapped to checkpoint every objective evaluation, so a container restart can resume.
Cell 15 (`results = mc_problem.solve(np.identity(1), optimization=bfgs)`) then runs as written: default robust SEs.
Afterwards, at the estimate: clustered SEs (a 'return' solve with se_type='clustered'), the per-market mean own-price
elasticity (A7 reports -2.346), and the 15 Table 5 funds' last-month own elasticities.

    python a7_col3.py PROCESSES      # run from a folder holding the index CSV; writes a7_col3_summary.csv, a7_col3_funds.csv
"""
import json
import os
import sys
import time

import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import pyblp
from pyblp.configurations.optimization import scipy_optimizer

from step1_table5_elasticity import top15

NB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  'main_Danny_March2026_testing_v3_nonLev_Apr2026_matchEgan_broadspecial.ipynb')
CKPT = 'a7_col3_ckpt.json'


def run_cell(nb, ns, i):
    src = '\n'.join(l for l in ''.join(nb['cells'][i]['source']).splitlines() if not l.strip().startswith(('%', '!')))
    exec(compile(src.replace('from IPython.display import display', 'pass'), f'a7_cell{i}', 'exec'), ns)


def main(procs):
    nb = json.load(open(NB))
    ns = {'__name__': '__main__', 'display': lambda *a, **k: None}
    for i in (2, 3, 4, 11, 12, 13, 14):
        run_cell(nb, ns, i)
    print(ns['mc_problem'], flush=True)
    history = json.load(open(CKPT)) if os.path.exists(CKPT) else []

    def bfgs(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(CKPT + '.tmp', 'w'))
            os.replace(CKPT + '.tmp', CKPT)
            return out
        return scipy_optimizer(initial, None, wrapped, iteration_callback, method='BFGS', compute_gradient=True, **opts)

    ns['bfgs'] = pyblp.Optimization(bfgs, {'gtol': 1e-7})  # cell 14's object, with checkpointing
    if history:  # resume: cell 15 starts from np.identity(1); replace that start with the best checkpointed sigma
        best = min(history, key=lambda r: r['obj'])['theta'][0]
        ns['np'] = type('np_shim', (), {'identity': staticmethod(lambda k: np.array([[best]])), '__getattr__': lambda s, a: getattr(np, a)})()
        print(f'resuming from sigma {best:.4f} ({len(history)} checkpointed evaluations)', flush=True)
    t = time.time()
    with pyblp.parallel(procs):
        run_cell(nb, ns, 15)  # results = mc_problem.solve(np.identity(1), optimization=bfgs)
        res = ns['results']
        print(res)
        print(f'cell 15 solve time {time.time() - t:.0f}s', flush=True)
        res_cl = ns['mc_problem'].solve(res.sigma, optimization=pyblp.Optimization('return'), se_type='clustered')
        em = res.compute_elasticities()
        e = res.extract_diagonals(em).flatten()
        avg = float(res.extract_diagonal_means(em).flatten().mean())
    d = ns['product_data'].reset_index(drop=True)
    funds = top15(d)
    last = d.assign(e=e).sort_values('month_t').groupby('product_ids').last().loc[funds.product_ids]
    row = dict(N=len(d), sigma=float(res.sigma[0, 0]), sigma_se_robust=float(res.sigma_se[0, 0]),
               sigma_se_clustered=float(res_cl.sigma_se[0, 0]), objective=float(res.objective),
               converged=bool(res.converged), iterations=int(res.optimization_iterations),
               avg_own_elasticity=avg, share_pos_e=float((e > 0).mean()), share_abs_e_gt1=float((np.abs(e) > 1).mean()))
    for lab, b, s_r, s_c in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten(), res_cl.beta_se.flatten()):
        row[f'b[{lab}]'], row[f'se_robust[{lab}]'], row[f'se_clustered[{lab}]'] = float(b), float(s_r), float(s_c)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    pd.DataFrame([row]).to_csv('a7_col3_summary.csv', index=False)
    out = last[['product_fund_name', 'prices', 'broad_specialized_ind', 'e']].rename(
        columns={'product_fund_name': 'name', 'prices': 'p_last', 'broad_specialized_ind': 'broad', 'e': 'e_last'})
    out['name'] = out.name.str.split(': ').str[-1].str[:45]
    print(out.round(3).to_string())
    out.to_csv('a7_col3_funds.csv')


if __name__ == '__main__':
    main(int(sys.argv[1]))
