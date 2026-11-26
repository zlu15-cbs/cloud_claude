"""Inertia version (Table 7 + lagged share): does a sign-constrained fee coefficient fit as well as the normal one?

    python -I step57_lag_lognormal.py PACKAGE_DIR NAMES_CSV PROCS

The normal random coefficient estimated in step49 (mean -0.46, SD 0.78 per month) is positive for 28% of investors.
Here the fee coefficient is -exp(pi + sigma nu) < 0 for everyone. One-step GMM criterion (2SLS weight, so
comparable across rows) on a grid of (mean, SD) of the fee coefficient, 500 of Danny's draws per month, and the
normal model at its estimate with the same 500 draws. No optimization (the lognormal searches of step44/45 stalled).
Resumes from the CSV. Writes step57_lag_lognormal.csv.
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from step48_access_spec_linear import load, IV

pyblp.options.verbose = False
CON = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
ITERATION = pyblp.Iteration('squarem', {'atol': 1e-14, 'max_evaluations': 3000})
GRID = [(0.46, 0.78), (0.46, 0.40), (0.46, 1.20), (0.70, 1.50), (0.30, 0.78), (0.30, 0.40), (1.00, 2.00), (0.46, 0.20), (0.70, 0.78), (0.46, 3.00)]   # most informative first


def main(P, names, procs):
    d = load(P, f'{P}/data/iv_inputs', names)
    x = d.sort_values(['product_ids', 'month'])
    lag = x.groupby('product_ids').y.shift(1)
    lag[x.groupby('product_ids').month.diff() != 1] = np.nan
    d['y_lag'] = lag
    d = d.dropna(subset=['y_lag']).reset_index(drop=True)
    a = np.load(f'{P}/data/draws/passive.npz', allow_pickle=False)
    keep = (pd.Series(np.arange(len(a['market_ids']))).groupby(a['market_ids']).cumcount().to_numpy() < 500) & np.isin(a['market_ids'], d.market_ids.unique())
    agents = {'market_ids': a['market_ids'][keep], 'nodes': a['nodes'][keep][:, [0]], 'weights': np.full(keep.sum(), 1 / 500)}
    out = 'step57_lag_lognormal.csv'
    rows = pd.read_csv(out).to_dict('records') if os.path.exists(out) else []
    done = {r['label'] for r in rows}
    absorb = 'C(product_ids) + C(market_ids)'

    def record(res, label, extra):
        e = res.extract_diagonals(res.compute_elasticities()).flatten()
        row = dict(label=label, objective=float(res.objective), mean_e=float(e.mean()), aum_e=float(np.average(e, weights=d.product_mtna)),
                   share_e_pos=float((e > 0).mean()), rho=float(dict(zip(res.beta_labels, res.beta.flatten()))['y_lag']), **extra)
        rows.append(row)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
        pd.DataFrame(rows).to_csv(out, index=False)

    with pyblp.parallel(procs):
        pn = pyblp.Problem((pyblp.Formulation('0 + prices + y_lag + ' + ' + '.join(CON), absorb=absorb), pyblp.Formulation('0 + prices')), d, agent_data=agents)
        for s in (0.001, 0.7827):
            lab = f'normal, sigma {s}'
            if lab not in done:
                t = time.time()
                res = pn.solve(np.array([[s]]), optimization=pyblp.Optimization('return'), iteration=ITERATION, method='1s', se_type='clustered')
                b = dict(zip(res.beta_labels, res.beta.flatten()))
                record(res, lab, dict(mean_coef=float(b['prices']), sd_coef=s, secs=round(time.time() - t)))
        pl = pyblp.Problem((pyblp.Formulation('0 + y_lag + ' + ' + '.join(CON), absorb=absorb), pyblp.Formulation('0 + I(-prices)')), d,
                           agent_formulation=pyblp.Formulation('1'), agent_data=agents, rc_types=['log'])
        for mean, sd in GRID:
            lab = f'lognormal, mean -{mean}, SD {sd}'
            if lab in done:
                continue
            s = float(np.sqrt(np.log(1 + (sd / mean) ** 2)))
            p = float(np.log(mean) - s * s / 2)
            t = time.time()
            res = pl.solve(sigma=np.array([[s]]), pi=np.array([[p]]), optimization=pyblp.Optimization('return'), iteration=ITERATION, method='1s', se_type='clustered')
            record(res, lab, dict(mean_coef=-mean, sd_coef=sd, ln_sigma=s, ln_pi=p, median_coef=-float(np.exp(p)), grad_sigma=float(res.gradient.flat[0]),
                                  grad_pi=float(res.gradient.flat[1]), secs=round(time.time() - t)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
