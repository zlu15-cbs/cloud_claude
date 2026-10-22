"""Step 4: BLP with 1 random coefficient on the price term for a shortlisted spec (index market), and step 5 on LETF.

Mirrors notebook cells 12-16 (X2 = price term, Monte Carlo 3000 draws seed 623543, BFGS gtol 1e-7, clustered SE,
extra instrument BLP_IV_newproduct_1 for the index market / BLP_IV_rival_funds1 for LETF, as in the notebooks), with
the spec's price terms in X1 and the extra instrument interacted with each z (as in the broadspecial notebooks).
Parallel over markets and checkpointed like code/solve_rc3_resumable.py.

    python step4_blp_shortlist.py SPEC PROCESSES [index|lev]
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
from step2_logit_screen import H, add_variables, build, spec_list, summarize

pyblp.options.verbose = False


def main(name, procs, panel):
    sp = spec_list()[name]
    if panel == 'index':
        d = add_variables(common.load('index'))
        extra_iv = 'BLP_IV_newproduct_1'
    else:
        d = common.load('lev')
        d['broad'] = (d.broad_specialized == 'broad-based').astype(float)
        d['big3'] = 0.0
        extra_iv = 'BLP_IV_rival_funds1'
        raws = [z for z in sp['z'] if z.startswith('raw') and z not in d]
        if raws:  # raw-entry tiers from the LETF raw file (cutoffs across leveraged funds)
            from tiers import LETF, raw_entry_tiers
            rt = raw_entry_tiers(tuple(int(z[3:]) / 100 for z in raws), path=LETF, id_col='product_ticker')
            for z in raws:
                d[z] = d.product_ids.map(rt[z]).astype(float)
    funds = top15(d) if panel == 'index' else d.iloc[:0]
    d, formula, endog, excl, exog = build(d, sp)
    form, c = sp.get('form', 'lin'), sp.get('c')
    k0 = len(excl)
    d[f'demand_instruments{k0}'] = d[extra_iv]
    for k, v in enumerate(sp['z'], start=k0 + 1):
        d[f'demand_instruments{k}'] = d[f'demand_instruments{k0}'] * d[v]
    x2 = f'0 + log(prices + {c})' if form == 'log' else '0 + prices'
    ckpt = f'step4_{panel}_{name}_ckpt.json'
    history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
    sigma0 = np.array([[min(history, key=lambda r: r['obj'])['theta'][0]]]) if history else np.ones((1, 1))
    print(f'{name} on {panel}: N={len(d)}  X1: {formula}  X2: {x2}  IVs: {sorted(c_ for c_ in d if c_.startswith("demand_instruments"))}'
          f'  start sigma {sigma0.item():.4f} ({len(history)} checkpointed evaluations)', flush=True)

    def bfgs(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            return out
        return scipy_optimizer(initial, None, wrapped, iteration_callback, method='BFGS', compute_gradient=True, **opts)

    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    t = time.time()
    with pyblp.parallel(procs):
        problem = pyblp.Problem((pyblp.Formulation('0 + ' + formula, absorb='C(product_ids) + C(market_ids)'),
                                 pyblp.Formulation(x2)), d, integration=integ)
        res = problem.solve(sigma0, optimization=pyblp.Optimization(bfgs, {'gtol': 1e-7}), se_type='clustered')
        print(res)
        print(f'solve time {time.time() - t:.0f}s', flush=True)
        sig = {'sigma': float(res.sigma.flatten()[0]), 'sigma_se': float(res.sigma_se.flatten()[0])}
        if panel == 'lev':
            e = res.extract_diagonals(res.compute_elasticities()).flatten()
            row = dict(spec=name + '_BLP1RC_lev', N=len(d), avg_own_elasticity=float(
                res.extract_diagonal_means(res.compute_elasticities()).flatten().mean()), share_pos_e=float((e > 0).mean()),
                share_neg_mc_bertrand_firm=float((res.compute_costs().flatten() < 0).mean()), **sig)
            for tl, b_, s_ in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
                row[f'b[{tl}]'], row[f'se[{tl}]'] = b_, s_
            print(row)
            pd.DataFrame([row]).to_csv(f'step4_lev_{name}_summary.csv', index=False)
            return
        row, fund_rows = summarize(name + '_BLP1RC', dict(tier=sp['tier']), d, res, funds, endog, {}, sig)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    pd.DataFrame([row]).to_csv(f'step4_{name}_summary.csv', index=False)
    pd.DataFrame(fund_rows).to_csv(f'step4_{name}_funds.csv', index=False)
    print(pd.DataFrame(fund_rows).drop(columns=['spec']).round(4).to_string(index=False))


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else 'index')
