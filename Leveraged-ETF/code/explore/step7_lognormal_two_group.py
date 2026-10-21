"""Two-group fee interaction (A9: cheapest third of funds by fee at their first month) in BLP with lognormal price
coefficients, so that demand slopes down for every simulated consumer.

Utility: X1 = controls (fund and month FE absorbed); X2 = -p*(1 - cheap), -p*cheap, each with a lognormal random
coefficient (pyblp rc_types='log'): alpha_ig = exp(pi_g + sigma_g * nu_ig). The means pi_g enter through a constant
in the agent formulation. Excluded instruments: Hausman IV and BLP_IV_newproduct_1, each split by group (4 for
4 nonlinear parameters). Monte Carlo 3000 draws, seed 623543, BFGS gtol 1e-7, clustered SE, as in the notebooks.

    python step7_lognormal_two_group.py PROCESSES
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

pyblp.options.verbose = False


def main(procs):
    d = add_variables(common.load('index'))
    funds = top15(d)
    g = d['fee_t1']
    d['rest'] = 1 - g  # X2 terms are written in prices so pyblp can differentiate them
    h, n1 = d['demand_instruments0'].copy(), d['BLP_IV_newproduct_1']
    d['demand_instruments0'], d['demand_instruments1'] = h * (1 - g), h * g
    d['demand_instruments2'], d['demand_instruments3'] = n1 * (1 - g), n1 * g
    X1 = pyblp.Formulation('0 + product_tracking_err + product_past_1yr_ret + log_product_fund_age',
                           absorb='C(product_ids) + C(market_ids)')
    X2 = pyblp.Formulation('0 + I(-prices*rest) + I(-prices*fee_t1)')
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    # start: logit IV A9 loadings (-11.1 rest, -56.4 cheap) -> pi = log(11.1), log(56.4); sigma 0.5
    ckpt = 'step7_ckpt.json'
    history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
    if history:
        best = min(history, key=lambda r: r['obj'])['theta']
        sigma0, pi0 = np.diag(best[:2]), np.array(best[2:]).reshape(2, 1)
    else:
        sigma0, pi0 = np.diag([0.5, 0.5]), np.array([[np.log(11.1)], [np.log(56.4)]])
    print(f'N={len(d)}; start sigma {np.diag(sigma0)}, pi {pi0.flatten()} ({len(history)} checkpointed evaluations)',
          flush=True)

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
        # agents exactly as pyblp builds Monte Carlo agents itself (primitives.py: integration._build_many)
        ids, nodes, weights = integ._build_many(2, np.unique(d.market_ids))
        agents = {'market_ids': ids, 'nodes': nodes, 'weights': weights}
        problem = pyblp.Problem((X1, X2), d, agent_formulation=pyblp.Formulation('1'), agent_data=agents,
                                rc_types=['log', 'log'])
        print(problem, flush=True)
        res = problem.solve(sigma=sigma0, pi=pi0, optimization=pyblp.Optimization(bfgs, {'gtol': 1e-7}),
                            se_type='clustered')
        print(res)
        print(f'solve time {time.time() - t:.0f}s', flush=True)
        row, fund_rows = summarize('A9_lognormal_BLP', dict(tier='A'), d, res, funds, [], {}, {})
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    f = pd.DataFrame(fund_rows)
    print(f[['name', 'p_last', 'e_last', 'e_mean', 'mu_bertrand_firm_mean', 'mc_bertrand_firm_mean']].round(3)
          .to_string(index=False))
    pd.DataFrame([row]).to_csv('step7_summary.csv', index=False)
    f.to_csv('step7_funds.csv', index=False)


if __name__ == '__main__':
    main(int(sys.argv[1]))
