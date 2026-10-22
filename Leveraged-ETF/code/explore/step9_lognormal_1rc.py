"""Table2_alt, BLP column with ONE random coefficient (Table 2 col 3 analogue) that keeps demand downward-sloping:
lognormal random coefficient on -price for all funds, plus the cheap-tier interaction in the mean utility.

Utility: delta_jt = beta_c * (p_jt * cheap_j) + controls (fund, month FE absorbed);
         mu_ijt = exp(pi + sigma * nu_i) * (-p_jt)       (pyblp rc_types=['log'], pi via an agent constant).
So a non-cheap fund's price coefficient is -exp(pi + sigma nu) < 0 for every consumer, and a cheap fund's is that plus
beta_c. Excluded instruments: Hausman IV, Hausman IV x cheap, extra IV (index: BLP_IV_newproduct_1; LETF:
BLP_IV_rival_funds1) and extra IV x cheap. Monte Carlo 3000 draws, seed 623543, BFGS gtol 1e-7, clustered SE.

    python step9_lognormal_1rc.py PROCESSES index|lev raw20     # checkpointed; rerun the same command to resume
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
from tiers import LETF, raw_entry_tiers

pyblp.options.verbose = False


def main(procs, panel, tier):
    q = int(tier[3:]) / 100
    if panel == 'index':
        d = add_variables(common.load('index'))
        extra = 'BLP_IV_newproduct_1'
        funds = top15(d)
        if tier not in d:
            d[tier] = d.product_ids.map(raw_entry_tiers((q,))[tier]).astype(float)
    else:
        d = common.load('lev')
        extra = 'BLP_IV_rival_funds1'
        funds = None
        d[tier] = d.product_ids.map(raw_entry_tiers((q,), path=LETF, id_col='product_ticker')[tier]).astype(float)
    d['cheap'] = d[tier]
    h, x = d['demand_instruments0'].copy(), d[extra]
    d['demand_instruments0'], d['demand_instruments1'] = h, h * d.cheap
    d['demand_instruments2'], d['demand_instruments3'] = x, x * d.cheap
    X1 = pyblp.Formulation('0 + I(prices*cheap) + product_tracking_err + product_past_1yr_ret + log_product_fund_age',
                           absorb='C(product_ids) + C(market_ids)')
    X2 = pyblp.Formulation('0 + I(-prices)')
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    ckpt = f'step9_{panel}_{tier}_ckpt.json'
    history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
    if history:
        th = min(history, key=lambda r: r['obj'])['theta']
        sigma0, pi0 = np.array([[th[0]]]), np.array([[th[1]]])
    else:  # start: the non-cheap logit IV coefficient (index -8.1, LETF -1.9), sigma 0.5
        sigma0, pi0 = np.array([[0.5]]), np.array([[np.log(8.1 if panel == 'index' else 1.9)]])
    print(f'{panel} {tier}: N={len(d)}, cheap share of funds {d.groupby("product_ids").cheap.first().mean():.3f}; '
          f'start sigma {sigma0.item():.3f} pi {pi0.item():.3f} ({len(history)} checkpointed evaluations)', flush=True)

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
        ids, nodes, weights = integ._build_many(1, np.unique(d.market_ids))
        problem = pyblp.Problem((X1, X2), d, agent_formulation=pyblp.Formulation('1'),
                                agent_data={'market_ids': ids, 'nodes': nodes, 'weights': weights}, rc_types=['log'])
        res = problem.solve(sigma=sigma0, pi=pi0, optimization=pyblp.Optimization(bfgs, {'gtol': 1e-7}),
                            se_type='clustered')
        print(res)
        print(f'solve time {time.time() - t:.0f}s', flush=True)
        em = res.compute_elasticities()
        e = res.extract_diagonals(em).flatten()
        row = dict(spec=f'{tier}_lognormal_1RC_{panel}', N=len(d), sigma=float(res.sigma[0, 0]),
                   sigma_se=float(res.sigma_se[0, 0]), pi=float(res.pi[0, 0]), pi_se=float(res.pi_se[0, 0]),
                   median_price_coef_rest=-float(np.exp(res.pi[0, 0])),
                   avg_own_elasticity=float(res.extract_diagonal_means(em).flatten().mean()),
                   share_abs_e_gt1=float((np.abs(e) > 1).mean()), share_pos_e=float((e > 0).mean()),
                   share_neg_mc=float((res.compute_costs().flatten() < 0).mean()),
                   share_funds_cheap=float(d.groupby('product_ids').cheap.first().mean()))
        for tl, b, s in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
            row[f'b[{tl}]'], row[f'se[{tl}]'] = b, s
        if panel == 'index':
            _, fund_rows = summarize(row['spec'], dict(tier='A'), d, res, funds, [], {}, {})
            pd.DataFrame(fund_rows).to_csv(f'step9_{panel}_{tier}_funds.csv', index=False)
            print(pd.DataFrame(fund_rows)[['name', 'p_last', 'e_last', 'e_mean', 'mu_bertrand_firm_mean',
                                           'mc_bertrand_firm_mean']].round(3).to_string(index=False))
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    pd.DataFrame([row]).to_csv(f'step9_{panel}_{tier}_summary.csv', index=False)


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2], sys.argv[3])
