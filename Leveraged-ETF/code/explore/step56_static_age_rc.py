"""Static passive BLP without a fee random coefficient: random coefficient on log fund age only.

    python -I step56_static_age_rc.py PACKAGE_DIR PROCS

Danny's Table 7 column (4) has random coefficients on the fee and on log age; his fee SD is 0.049 (SE 20.5), a corner.
This is the same model with the fee random coefficient removed: mean utility fee, tracking error, past return,
log age; fund and month FE; his five instruments; his 3,000 archived draws per month (age column). One-step GMM
(2SLS weight), then two-step with the heteroskedasticity-robust weight (his convention); SE clustered by month.
Every evaluation is checkpointed; rerunning resumes from the best point. Reads prepared arrays only.
Writes step56_static_age_rc.csv and step56_static_age_rc_funds.csv (elasticities of the 15 Table 5 funds).
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
CON = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
ITERATION = pyblp.Iteration('squarem', {'atol': 1e-14, 'max_evaluations': 3000})
BIG3 = ['BlackRock', 'Vanguard', 'State Street Global Advisors']


def checkpointed(ckpt, history):
    def optimizer(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt, 'w'))
            print(f'  eval {len(history)}: theta {np.round(history[-1]["theta"], 5).tolist()} obj {history[-1]["obj"]:.6g}', flush=True)
            return out
        return scipy_optimizer(initial, bounds, wrapped, iteration_callback, method='L-BFGS-B', compute_gradient=True, **opts)
    return pyblp.Optimization(optimizer, {'gtol': 1e-6})


def summarize(res, d, label, extra):
    e = res.extract_diagonals(res.compute_elasticities()).flatten()
    dd = d.assign(e=e)
    last = dd[dd.month_t == dd.month_t.max()]
    top = last[last.firm_ids.isin(BIG3)].sort_values(['firm_ids', 'product_mtna'], ascending=[True, False]).groupby('firm_ids').head(5)
    P = res.problem.products
    G = np.column_stack([-P.ZD.T @ P.X1, P.ZD.T @ res.xi_by_theta_jacobian]) / len(d)
    LG = np.linalg.cholesky(res.W).T @ G
    sv = np.linalg.svd(LG / np.linalg.norm(LG, axis=0), compute_uv=False)
    row = dict(spec=label, N=len(d), objective=float(res.objective), sigma_age=float(res.sigma[0, 0]), sigma_age_se=float(res.sigma_se[0, 0]),
               mean_own_elasticity_equal_month=float(dd.groupby('market_ids').e.mean().mean()),
               aum_weighted_elasticity=float(np.average(dd.e, weights=dd.product_mtna)), share_e_pos=float((e > 0).mean()),
               aum_share_abs_e_lt1=float(dd.product_mtna[np.abs(e) < 1].sum() / dd.product_mtna.sum()),
               n15_abs_e_gt1=int((top.e.abs() > 1).sum()), min_scaled_singular_value=float(sv.min()), **extra)
    for t, b, se in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
        row[f'b[{t}]'], row[f'se[{t}]'] = float(b), float(se)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    return row, top[['firm_ids', 'product_ids', 'prices', 'e']].assign(spec=label)


def main(P, procs):
    z = np.load(f'{P}/data/prepared/passive.npz', allow_pickle=False)
    d = pd.DataFrame({k: z[k] for k in z.files if z[k].dtype.kind != 'U'})
    d['firm_ids'] = z['firm_ids']
    a = np.load(f'{P}/data/draws/passive.npz', allow_pickle=False)
    agents = {'market_ids': a['market_ids'], 'nodes': a['nodes'][:, [1]], 'weights': a['weights']}     # column 1: log age
    rows, funds = [], []
    with pyblp.parallel(procs):
        pr = pyblp.Problem((pyblp.Formulation('0 + prices + ' + ' + '.join(CON), absorb='C(product_ids) + C(market_ids)'),
                            pyblp.Formulation('0 + log_product_fund_age')), d, agent_data=agents)
        ck1 = 'step56_step1_ckpt.json'
        h1 = json.load(open(ck1)) if os.path.exists(ck1) else []
        s0 = min(h1, key=lambda r: r['obj'])['theta'][0] if h1 else 1.5
        t = time.time()
        opt = pyblp.Optimization('return') if os.environ.get('FINALIZE') == '1' else checkpointed(ck1, h1)
        res1 = pr.solve(np.array([[s0]]), sigma_bounds=(np.array([[0.2]]), np.array([[4.0]])), optimization=opt, iteration=ITERATION, method='1s', se_type='clustered')
        r, f = summarize(res1, d, 'static, age RC only, one-step', dict(minutes=round((time.time() - t) / 60, 1)))
        rows.append(r), funds.append(f)
        pd.DataFrame(rows).to_csv('step56_static_age_rc.csv', index=False)
        t = time.time()
        s1 = float(res1.sigma[0, 0])
        res2 = pr.solve(np.array([[s1]]), sigma_bounds=(np.array([[0.2]]), np.array([[4.0]])), W=res1.updated_W,
                        optimization=checkpointed('step56_step2_ckpt.json', []), iteration=ITERATION, method='1s', se_type='clustered')
        r, f = summarize(res2, d, 'static, age RC only, two-step (robust weight)', dict(J=float(res2.objective), J_df=3, minutes=round((time.time() - t) / 60, 1)))
        rows.append(r), funds.append(f)
    pd.DataFrame(rows).to_csv('step56_static_age_rc.csv', index=False)
    pd.concat(funds).to_csv('step56_static_age_rc_funds.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
