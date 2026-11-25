"""Sign-constrained (lognormal) fee random coefficient on Danny's passive sample and five instruments (Tables 7-10
replication package, 24 Nov 2026), next to his normal-RC Table 7.

    python -I step45_lognormal_danny.py PACKAGE_DIR [PROCS]     # PACKAGE_DIR = extracted tables7_10_replication/

Reads only data/prepared/passive.npz and data/draws/passive.npz (allow_pickle=False); runs none of the package's code.
Same 98,110 fund-months, controls, fund + month FE, the five excluded IVs (8 moments), and his 3,000 archived price
draws per month. One-step GMM with W = (Z'Z/N)^-1, the weight of his step 1, so the objective is comparable to his
step-1 objective (100.87 at sigma 2.239).

  1. check: normal RC evaluated at his step-1 sigma (no optimization); the objective should be about 100.87.
  2. lognormal RC: fee coefficient of investor i = -exp(pi + sigma nu_i) < 0 for everyone; X1 = controls, X2 = -fee,
     agent constant. L-BFGS-B with sigma in [0, 3], pi in [-4, 5]; every evaluation checkpointed.
Writes step45_*.csv: estimates, elasticity summaries, the 15 Table 5 funds.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp
from pyblp.configurations.optimization import scipy_optimizer

pyblp.options.verbose = False
CONTROLS = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
X1C = ' + '.join(CONTROLS)
ABSORB = 'C(product_ids) + C(market_ids)'
DANNY_STEP1_SIGMA = 2.238688664247958
ITERATION = pyblp.Iteration('squarem', {'atol': 1e-14, 'max_evaluations': 3000})
BIG3 = ['BlackRock', 'Vanguard', 'State Street Global Advisors']


def load(pkg):
    z = np.load(f'{pkg}/data/prepared/passive.npz', allow_pickle=False)
    keep = ['market_ids', 'product_ids', 'clustering_ids', 'shares', 'prices', 'product_mtna', 'month_t', 'firm_ids'] + CONTROLS
    d = pd.DataFrame({k: z[k] for k in keep})
    for k in range(5):
        d[f'demand_instruments{k}'] = z[f'demand_instruments{k}']
    a = np.load(f'{pkg}/data/draws/passive.npz', allow_pickle=False)
    agents = {'market_ids': a['market_ids'], 'nodes': a['nodes'][:, [0]], 'weights': a['weights']}  # column 0 = price node
    return d, agents


def checkpointed(tag, history):
    ckpt = f'step45_{tag}_ckpt.json'

    def optimizer(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            print(f'  eval {len(history)}: theta {np.round(history[-1]["theta"], 5).tolist()} obj {history[-1]["obj"]:.6g}', flush=True)
            return out
        return scipy_optimizer(initial, bounds, wrapped, iteration_callback, method='L-BFGS-B', compute_gradient=True, **opts)
    return pyblp.Optimization(optimizer, {'gtol': 1e-7})


def summarize(res, d, label, extra):
    e = res.extract_diagonals(res.compute_elasticities()).flatten()
    dd = d.assign(e=e)
    w = dd.product_mtna
    last = dd[dd.month_t == dd.month_t.max()]
    top = last[last.firm_ids.isin(BIG3)].sort_values(['firm_ids', 'product_mtna'], ascending=[True, False]).groupby('firm_ids').head(5)
    P = res.problem.products
    G = np.column_stack([-P.ZD.T @ P.X1, P.ZD.T @ res.xi_by_theta_jacobian]) / len(d)
    LG = np.linalg.cholesky(res.W).T @ G
    sv = np.linalg.svd(LG / np.linalg.norm(LG, axis=0), compute_uv=False)
    bins = pd.cut(dd.prices, [-.001, .03, .05, .10, .20, .50, 10])
    slope = (dd.e / dd.prices).groupby(bins, observed=True).mean()
    row = dict(spec=label, N=len(d), objective=float(res.objective), converged=bool(res.converged),
               mean_own_elasticity_equal_month=float(dd.groupby('market_ids').e.mean().mean()),
               aum_weighted_elasticity=float(np.average(dd.e, weights=w)),
               share_e_pos=float((e > 0).mean()), share_abs_e_lt1=float((np.abs(e) < 1).mean()),
               aum_share_abs_e_lt1=float(w[np.abs(e) < 1].sum() / w.sum()),
               n15_abs_e_gt1=int((top.e.abs() > 1).sum()), min_scaled_singular_value=float(sv.min()),
               **{f'slope_fee{str(b)}': float(v) for b, v in slope.items()}, **extra)
    for t, b, s in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
        row[f'b[{t}]'], row[f'se[{t}]'] = float(b), float(s)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    return row, top[['firm_ids', 'product_ids', 'prices', 'shares', 'e']].assign(spec=label)


def main(pkg, procs):
    d, agents = load(pkg)
    print(f'N={len(d):,}; months {d.market_ids.nunique()}; draws per month {len(agents["weights"]) // d.market_ids.nunique()}', flush=True)
    rows, funds = [], []
    with pyblp.parallel(procs):
        if not os.path.exists('step45_check.csv'):
            t = time.time()
            pr = pyblp.Problem((pyblp.Formulation('0 + prices + ' + X1C, absorb=ABSORB), pyblp.Formulation('0 + prices')), d,
                               agent_data=agents)
            res = pr.solve(np.array([[DANNY_STEP1_SIGMA]]), optimization=pyblp.Optimization('return'), iteration=ITERATION,
                           method='1s', se_type='clustered')
            row, fr = summarize(res, d, 'normal RC at Danny step-1 sigma (check: his objective 100.87)',
                                dict(sigma=DANNY_STEP1_SIGMA, minutes=round((time.time() - t) / 60, 1)))
            pd.DataFrame([row]).to_csv('step45_check.csv', index=False)
            fr.to_csv('step45_check_funds.csv', index=False)
        tag = 'lognormal'
        ckpt = f'step45_{tag}_ckpt.json'
        history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
        # start: median coefficient near his mean slope (-18), little dispersion
        s0, p0 = (min(history, key=lambda r: r['obj'])['theta'] if history else (0.3, float(np.log(18.0))))
        print(f'lognormal start sigma {s0:.4f} pi {p0:.4f} ({len(history)} checkpointed evaluations)', flush=True)
        t = time.time()
        pr = pyblp.Problem((pyblp.Formulation('0 + ' + X1C, absorb=ABSORB), pyblp.Formulation('0 + I(-prices)')), d,
                           agent_formulation=pyblp.Formulation('1'), agent_data=agents, rc_types=['log'])
        opt = pyblp.Optimization('return') if os.environ.get('FINALIZE') == '1' else checkpointed(tag, history)
        res = pr.solve(sigma=np.array([[s0]]), pi=np.array([[p0]]), sigma_bounds=(np.array([[0.0]]), np.array([[3.0]])),
                       pi_bounds=(np.array([[-4.0]]), np.array([[5.0]])), optimization=opt, iteration=ITERATION,
                       method='1s', se_type='clustered')
        print(res, flush=True)
        s, p = float(res.sigma[0, 0]), float(res.pi[0, 0])
        row, fr = summarize(res, d, 'lognormal RC, five IVs, 1-step',
                            dict(sigma=s, sigma_se=float(res.sigma_se[0, 0]), pi=p, pi_se=float(res.pi_se[0, 0]),
                                 median_fee_coef=-float(np.exp(p)), mean_fee_coef=-float(np.exp(p + s * s / 2)),
                                 p10_fee_coef=-float(np.exp(p + 1.2816 * s)), p90_fee_coef=-float(np.exp(p - 1.2816 * s)),
                                 minutes=round((time.time() - t) / 60, 1)))
        pd.DataFrame([row]).to_csv('step45_lognormal_estimate.csv', index=False)
        fr.to_csv('step45_lognormal_funds.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2)
