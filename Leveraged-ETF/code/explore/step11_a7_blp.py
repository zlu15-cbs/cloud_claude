"""Table A7 Panel A col 3 (BLP with expense ratio x broad-based), from the broadspecial index notebook.

Runs the notebook's own prep cells unmodified (2, 3, 4, 11: data, broad indicator, instruments Hausman, Hausman x broad,
BLP_IV_newproduct_1, BLP_IV_newproduct_1 x broad), then solves with the notebook's settings (Monte Carlo 3000 draws,
seed 623543, BFGS gtol 1e-7, default robust SEs), in parallel and checkpointed.

    python step11_a7_blp.py 2rc PROCESSES   # notebook cell 15 as written: X2 = prices + I(prices*broad), sigma0 = I(2)
    python step11_a7_blp.py 1rc PROCESSES   # one RC on the expense ratio: X2 = prices, sigma0 = 1
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp
from pyblp.configurations.optimization import scipy_optimizer

import matplotlib
matplotlib.use('Agg')

NB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  'main_Danny_March2026_testing_v3_nonLev_Apr2026_matchEgan_broadspecial.ipynb')


def prep():
    nb = json.load(open(NB))
    ns = {'__name__': '__main__', 'display': lambda *a, **k: None}
    for i in (2, 3, 4, 11):
        src = '\n'.join(l for l in ''.join(nb['cells'][i]['source']).splitlines() if not l.strip().startswith(('%', '!')))
        exec(compile(src.replace('from IPython.display import display', 'pass'), f'a7_cell{i}', 'exec'), ns)
    return ns['product_data'].reset_index(drop=True)


def main(mode, procs):
    d = prep()
    X1 = pyblp.Formulation('0 + prices + I(prices*broad_specialized_ind) + product_tracking_err + product_past_1yr_ret'
                           ' + log_product_fund_age', absorb='C(product_ids) + C(market_ids)')
    X2 = pyblp.Formulation('0 + prices + I(prices*broad_specialized_ind)' if mode == '2rc' else '0 + prices')
    k = 2 if mode == '2rc' else 1
    ckpt = f'step11_a7_{mode}_ckpt.json'
    history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
    sigma0 = np.diag(min(history, key=lambda r: r['obj'])['theta']) if history else np.identity(k)
    print(f'A7 {mode}: N={len(d)}, IVs {sorted(c for c in d if c.startswith("demand_instruments"))}, '
          f'start sigma {np.diag(sigma0)} ({len(history)} checkpointed evaluations)', flush=True)

    def bfgs(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            return out
        return scipy_optimizer(initial, None, wrapped, iteration_callback, method='BFGS', compute_gradient=True, **opts)

    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    opt = pyblp.Optimization(bfgs, {'gtol': 1e-7})
    if os.environ.get('FINALIZE') == '1':
        opt = pyblp.Optimization('return')
        print('FINALIZE: evaluating at the best checkpointed point', flush=True)
    t = time.time()
    with pyblp.parallel(procs):
        problem = pyblp.Problem((X1, X2), d, integration=integ)
        res = problem.solve(sigma0, optimization=opt)  # notebook: default (robust) SEs
        print(res)
        print(f'solve time {time.time() - t:.0f}s', flush=True)
        em = res.compute_elasticities()
        e = res.extract_diagonals(em).flatten()
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    s = dict(zip(res.beta_labels, res.beta_se.flatten()))
    row = dict(mode=mode, objective=float(res.objective), avg_own_e=float(res.extract_diagonal_means(em).flatten().mean()),
               share_pos_e=float((e > 0).mean()), share_abs_e_gt1=float((np.abs(e) > 1).mean()),
               sigma=[float(v) for v in np.diag(res.sigma)], sigma_se=[float(v) for v in np.diag(res.sigma_se)],
               **{f'b[{k}]': v for k, v in b.items()}, **{f'se[{k}]': v for k, v in s.items()})
    print(row)
    pd.DataFrame([row]).to_csv(f'step11_a7_{mode}_summary.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
