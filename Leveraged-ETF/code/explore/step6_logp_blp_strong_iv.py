"""Side task: log-price BLP (spec B1, c = 0.01) with stronger instruments for the random coefficient.

Stage 1: the B1 instruments (log(Hausman IV + c) and BLP_IV_newproduct_1 / BLP_IV_rival_funds1) plus local
differentiation instruments (pyblp.build_differentiation_instruments) on the three fund characteristics.
Stage 2: pyblp approximate optimal instruments from the stage-1 estimates, re-solved.
Same sample, controls, FE, integration (MC 3000, seed 623543), BFGS gtol 1e-7 and clustering as the notebooks.

    python step6_logp_blp_strong_iv.py index|lev PROCESSES
"""
import sys
import time

import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, summarize

pyblp.options.verbose = False
C = 0.01
CHARS = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
X1 = f'0 + log(prices + {C}) + ' + ' + '.join(CHARS)
X2 = f'0 + log(prices + {C})'


def main(panel, procs):
    d = add_variables(common.load('index')) if panel == 'index' else common.load('lev')
    funds = top15(d) if panel == 'index' else None
    extra = 'BLP_IV_newproduct_1' if panel == 'index' else 'BLP_IV_rival_funds1'
    d['demand_instruments0'] = np.log(d['demand_instruments0'] + C)
    d['demand_instruments1'] = d[extra]
    diff = pyblp.build_differentiation_instruments(pyblp.Formulation('0 + ' + ' + '.join(CHARS)), d, version='local')
    for k in range(diff.shape[1]):
        d[f'demand_instruments{k + 2}'] = diff[:, k]
    d = d.loc[:, ~d.columns.duplicated()]
    print(f'{panel}: N={len(d)}, excluded instruments: 2 + {diff.shape[1]} differentiation', flush=True)
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    bfgs = pyblp.Optimization('bfgs', {'gtol': 1e-7})
    with pyblp.parallel(procs):
        t = time.time()
        problem = pyblp.Problem((pyblp.Formulation(X1, absorb='C(product_ids) + C(market_ids)'),
                                 pyblp.Formulation(X2)), d, integration=integ)
        res1 = problem.solve(np.ones((1, 1)), optimization=bfgs, se_type='clustered')
        print('=== Stage 1: B1 instruments + differentiation instruments'); print(res1)
        print(f'stage 1 time {time.time() - t:.0f}s', flush=True)
        report(panel, 'stage1_diffIV', res1, d, funds)
        t = time.time()
        opt = res1.compute_optimal_instruments(method='approximate')
        res2 = opt.to_problem().solve(res1.sigma, optimization=bfgs, se_type='clustered')
        print('=== Stage 2: approximate optimal instruments'); print(res2)
        print(f'stage 2 time {time.time() - t:.0f}s', flush=True)
        report(panel, 'stage2_optIV', res2, d, funds)


def report(panel, label, res, d, funds):
    if panel == 'lev':
        print(label, 'mean own-price elasticity (per-market mean):',
              res.extract_diagonal_means(res.compute_elasticities()).flatten().mean(), flush=True)
        return
    row, fund_rows = summarize('B1_logp_' + label, dict(tier='B'), d, res, funds, [], {}, {})
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    f = pd.DataFrame(fund_rows)
    print(f[['name', 'p_last', 'e_last', 'e_mean', 'mu_bertrand_firm_mean']].round(3).to_string(index=False), flush=True)
    pd.DataFrame([row]).to_csv(f'step6_{label}_summary.csv', index=False)
    f.to_csv(f'step6_{label}_funds.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
