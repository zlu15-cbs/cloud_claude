"""One RC on the expense ratio + price x cheap, with Chamberlain (approximate) optimal instruments built from the
Hausman fee instrument only. No exogeneity assumption beyond the paper's.

Stage 0: the problem with excluded instruments H, H x cheap, H^2 (the third is needed only for the rank condition
and the price projection), evaluated at a starting sigma (default 0.027, the paper's Table 2 col 3 estimate) with
optimization='return'.
Stage 1: pyblp approximate optimal instruments at that point (E[d xi / d theta | Z] at expected prices), to_problem(),
solved by BFGS (gtol 1e-7) from the same sigma; checkpointed. The result is exactly identified (one optimal
instrument per parameter).

    python step15_optimal_iv.py PROCESSES raw20 [SIGMA0]
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp
from pyblp.configurations.optimization import scipy_optimizer

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, summarize
from tiers import raw_entry_tiers

pyblp.options.verbose = False


def main(procs, tier, sigma0=0.027):
    d = add_variables(common.load('index'))
    q = int(tier[3:]) / 100
    d['cheap'] = d.product_ids.map(raw_entry_tiers((q,))[tier]).astype(float)
    funds = top15(d)
    h = d['demand_instruments0'].copy()
    d['demand_instruments1'] = h * d.cheap
    d['demand_instruments2'] = h ** 2
    X1 = pyblp.Formulation('0 + prices + I(prices*cheap) + product_tracking_err + product_past_1yr_ret + log_product_fund_age',
                           absorb='C(product_ids) + C(market_ids)')
    X2 = pyblp.Formulation('0 + prices')
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    ckpt = f'step15_{tier}_s{sigma0}_ckpt.json'
    history = json.load(open(ckpt)) if os.path.exists(ckpt) else []

    def bfgs(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            return out
        return scipy_optimizer(initial, None, wrapped, iteration_callback, method='BFGS', compute_gradient=True, **opts)

    t = time.time()
    with pyblp.parallel(procs):
        problem = pyblp.Problem((X1, X2), d, integration=integ)
        res0 = problem.solve(np.array([[sigma0]]), optimization=pyblp.Optimization('return'), method='1s')
        print(f'stage 0 at sigma={sigma0}: beta', dict(zip(res0.beta_labels, res0.beta.flatten().round(3))),
              f'({time.time() - t:.0f}s)', flush=True)
        t = time.time()
        opt_iv = res0.compute_optimal_instruments(method='approximate')
        print(f'optimal instruments computed ({time.time() - t:.0f}s): {opt_iv.demand_instruments.shape[1]} columns', flush=True)
        prob1 = opt_iv.to_problem()
        start = np.array([[min(history, key=lambda r: r['obj'])['theta'][0]]]) if history else np.array([[sigma0]])
        print(f'stage 1 start sigma {start.item():.4f} ({len(history)} checkpointed evaluations)', flush=True)
        t = time.time()
        opt = pyblp.Optimization(bfgs, {'gtol': 1e-7})
        if os.environ.get('FINALIZE') == '1':
            opt = pyblp.Optimization('return')
        res = prob1.solve(start, optimization=opt, se_type='clustered')
        print(res)
        print(f'stage 1 solve time {time.time() - t:.0f}s', flush=True)
        em = res.compute_elasticities()
        e = res.extract_diagonals(em).flatten()
        row, fund_rows = summarize(f'{tier}_optIV_1RC', dict(tier='A'), d, res, funds, [], {},
                                   {'sigma': float(res.sigma[0, 0]), 'sigma_se': float(res.sigma_se[0, 0]),
                                    'share_pos_e': float((e > 0).mean())})
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    f = pd.DataFrame(fund_rows)
    print(f[['name', 'p_last', 'e_last', 'e_mean', 'mu_bertrand_firm_mean', 'mc_bertrand_firm_mean']].round(3).to_string(index=False))
    pd.DataFrame([row]).to_csv(f'step15_{tier}_s{sigma0}_summary.csv', index=False)
    f.to_csv(f'step15_{tier}_s{sigma0}_funds.csv', index=False)


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.027)
