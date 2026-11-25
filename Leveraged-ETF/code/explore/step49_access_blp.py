"""BLP version of the candidate passive specification from step48, on Danny's Tables 7-10 package.

    python -I step49_access_blp.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV PROCS SPEC

SPEC  B      fee with a normal random coefficient; fee x institutional, fee x ETF (written prices:inst, prices:etf so
             pyblp treats them as endogenous); controls; fund FE and
             month x access FE (corrected flag); IVs: Danny's five + IV0 and IV1 x {institutional, ETF} (9).
      T7     Danny's Table 7 on the same code path (fee RC; month FE; five IVs), for comparison.
      B-orig B with Danny's original, time-varying flag.
      T7-lag Table 7 plus the lagged log share ratio in mean utility (inertia); fund-months without a previous
             month are dropped. One menu: no vehicle-specific term. See step51/step52. Reports the long-run fee
             coefficient b/(1 - rho) and sigma/sqrt(1 - rho) (partial adjustment toward a static target).
      S2     two segments, no retail / institutional flag: fee RC; fee x ETF; fund FE and month x ETF FE;
             IVs: Danny's five + IV0 and IV1 x ETF (7). See step50d_two_segment.py for why.
Stage 1: profile of the one-step criterion over sigma, 500 of his archived draws per month (no optimization).
Stage 2: L-BFGS-B on sigma within +-2 of the profile minimum, all 3,000 draws, one-step weight; every evaluation
         checkpointed. Stage 3: two-step GMM at the stage-2 sigma (weight from step-1 residuals, clustered by month),
         re-optimized; its criterion is the J statistic.
Reads only prepared arrays and IV input panels (allow_pickle=False); runs none of the package's code.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp
from pyblp.configurations.optimization import scipy_optimizer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from step48_access_spec_linear import load, IV, IVX, IVXO  # noqa: E402

pyblp.options.verbose = False
CON = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
ITERATION = pyblp.Iteration('squarem', {'atol': 1e-14, 'max_evaluations': 3000})
GRID = (0.5, 2.0, 4.0, 6.0, 8.0, 10.0)
BIG3 = ['BlackRock', 'Vanguard', 'State Street Global Advisors']


def spec(name):
    if name == 'B':
        return ['prices:inst', 'prices:etf'], IV + IVX, 'C(product_ids) + C(month_access)'
    if name == 'B-orig':
        return ['prices:inst_o', 'prices:etf_o'], IV + IVXO, 'C(product_ids) + C(month_access_orig)'
    if name == 'S2':
        return ['prices:etf'], IV + ['iv0_etf', 'iv1_etf'], 'C(product_ids) + C(month_etf)'
    return [], IV, 'C(product_ids) + C(market_ids)'


def problem(d, agents, name):
    extra, ivs, absorb = spec(name)
    if name == 'T7-lag':
        extra = ['y_lag']
    dd = d.copy()
    for k in [c for c in dd.columns if c.startswith('demand_instruments')]:
        dd = dd.rename(columns={k: '_' + k})
    for i, c in enumerate(ivs):
        dd[f'demand_instruments{i}'] = d[c].to_numpy()
    x1 = '0 + prices + ' + ' + '.join(extra + CON)
    return pyblp.Problem((pyblp.Formulation(x1, absorb=absorb), pyblp.Formulation('0 + prices')), dd, agent_data=agents)


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
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    s = float(res.sigma[0, 0])
    from scipy.stats import norm
    # interaction terms must be written as functions of prices so that pyblp treats them as endogenous
    bi = next((v for k, v in b.items() if 'inst' in k and 'prices' in k), 0.0)  # pyblp label: inst*prices
    be = next((v for k, v in b.items() if 'etf' in k and 'prices' in k), 0.0)
    mean_by = {a: b['prices'] + bi * (a == 1) + be * (a == 2) for a in (0, 1, 2)}
    if 'y_lag' in b:
        extra = dict(extra, rho=float(b['y_lag']), long_run_mean_fee_coef=float(b['prices'] / (1 - b['y_lag'])),
                     long_run_sigma=float(s / np.sqrt(1 - b['y_lag'])), long_run_aum_weighted_elasticity=float(np.average(dd.e, weights=w) / (1 - b['y_lag'])))
    row = dict(spec=label, N=len(d), objective=float(res.objective), sigma=s,
               sigma_se=float(res.sigma_se[0, 0]) if np.isfinite(res.sigma_se[0, 0]) else np.nan,
               **{f'mean_fee_coef_access{a}': float(m) for a, m in mean_by.items()},
               **{f'share_pos_coef_access{a}': float(norm.cdf(m / s)) if s > 0 else float(m > 0) for a, m in mean_by.items()},
               mean_own_elasticity_equal_month=float(dd.groupby('market_ids').e.mean().mean()),
               aum_weighted_elasticity=float(np.average(dd.e, weights=w)),
               share_e_pos=float((e > 0).mean()), share_abs_e_lt1=float((np.abs(e) < 1).mean()),
               aum_share_abs_e_lt1=float(w[np.abs(e) < 1].sum() / w.sum()),
               n15_abs_e_gt1=int((top.e.abs() > 1).sum()), min_scaled_singular_value=float(sv.min()),
               **{f'aum_e_last_access{a}': float(np.average(last.e[last.access == a], weights=last.product_mtna[last.access == a])) for a in (0, 1, 2)},
               **extra)
    for t, bb, se in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
        row[f'b[{t}]'], row[f'se[{t}]'] = float(bb), float(se)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    return row, top[['firm_ids', 'product_ids', 'access', 'prices', 'e']].assign(spec=label)


def checkpointed(ckpt, history):
    def optimizer(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            print(f'  eval {len(history)}: theta {np.round(history[-1]["theta"], 5).tolist()} obj {history[-1]["obj"]:.6g}', flush=True)
            return out
        return scipy_optimizer(initial, bounds, wrapped, iteration_callback, method='L-BFGS-B', compute_gradient=True, **opts)
    return pyblp.Optimization(optimizer, {'gtol': 1e-6})


def main(P, D, names, procs, name):
    d = load(P, D, names)
    d['month_access'] = d.market_ids.astype(str) + '_' + d.access.astype(int).astype(str)
    grid = GRID
    if name == 'T7-lag':
        x = d.sort_values(['product_ids', 'month'])
        lag = x.groupby('product_ids').y.shift(1)
        lag[x.groupby('product_ids').month.diff() != 1] = np.nan
        d['y_lag'] = lag
        grid = (0.25, 0.5, 1.0, 2.0, 4.0)
    d['month_etf'] = d.market_ids.astype(str) + '_' + d.etf.astype(int).astype(str)
    d['month_access_orig'] = d.market_ids.astype(str) + '_' + d.access_orig.astype(int).astype(str)
    z = np.load(f'{P}/data/prepared/passive.npz', allow_pickle=False)
    d['firm_ids'] = z['firm_ids']
    if name == 'T7-lag':
        d = d.dropna(subset=['y_lag']).reset_index(drop=True)
    a = np.load(f'{P}/data/draws/passive.npz', allow_pickle=False)
    full = {'market_ids': a['market_ids'], 'nodes': a['nodes'][:, [0]], 'weights': a['weights']}
    order = pd.Series(np.arange(len(a['market_ids']))).groupby(a['market_ids']).cumcount().to_numpy()
    keep = order < 500
    sub = {'market_ids': a['market_ids'][keep], 'nodes': a['nodes'][keep][:, [0]], 'weights': np.full(keep.sum(), 1 / 500)}
    live = np.isin(a['market_ids'], d.market_ids.unique())      # the lag drops the first month altogether
    full = {k: v[live] for k, v in full.items()}
    sub = {k: v[live[keep]] for k, v in sub.items()}
    tag = name.replace('-', '_')
    print(f'{name}: N={len(d):,}; IVs {len(spec(name)[1])}', flush=True)
    with pyblp.parallel(procs):
        prof_file = f'step49_{tag}_profile_d500.csv'
        rows = pd.read_csv(prof_file).to_dict('records') if os.path.exists(prof_file) else []
        done = {round(r['sigma'], 6) for r in rows}
        pr = problem(d, sub, name)
        for s in grid:
            if round(s, 6) in done:
                continue
            t = time.time()
            res = pr.solve(np.array([[s]]), optimization=pyblp.Optimization('return'), iteration=ITERATION, method='1s', se_type='clustered')
            row, _ = summarize(res, d, f'{name} profile sigma={s} (500 draws)', dict(gradient=float(res.gradient.flat[0]), secs=round(time.time() - t)))
            rows.append(row)
            pd.DataFrame(rows).to_csv(prof_file, index=False)
        s0 = min(rows, key=lambda r: r['objective'])['sigma']
        ckpt = f'step49_{tag}_ckpt.json'
        history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
        if history:
            s0 = min(history, key=lambda r: r['obj'])['theta'][0]
        lo, hi = max(s0 - 2, 0.0), s0 + 2
        print(f'stage 2 from sigma {s0:.4f}, bounds [{lo:.2f}, {hi:.2f}]', flush=True)
        t = time.time()
        pr = problem(d, full, name)
        opt = pyblp.Optimization('return') if os.environ.get('FINALIZE') == '1' else checkpointed(ckpt, history)
        res1 = pr.solve(np.array([[s0]]), sigma_bounds=(np.array([[lo]]), np.array([[hi]])), optimization=opt,
                        iteration=ITERATION, method='1s', se_type='clustered')
        row1, fr1 = summarize(res1, d, f'{name}, one-step, 3000 draws', dict(minutes=round((time.time() - t) / 60, 1)))
        pd.DataFrame([row1]).to_csv(f'step49_{tag}_step1.csv', index=False)
        fr1.to_csv(f'step49_{tag}_step1_funds.csv', index=False)
        t = time.time()
        W2 = res1.updated_W
        s1 = float(res1.sigma[0, 0])
        hist2 = []
        res2 = pr.solve(np.array([[s1]]), sigma_bounds=(np.array([[max(s1 - 2, 0.0)]]), np.array([[s1 + 2]])), W=W2,
                        optimization=checkpointed(f'step49_{tag}_step2_ckpt.json', hist2), iteration=ITERATION,
                        method='1s', se_type='clustered')
        row2, fr2 = summarize(res2, d, f'{name}, two-step, 3000 draws', dict(J=float(res2.objective), J_df=len(spec(name)[1]) - len(spec(name)[0]) - 2,
                                                                            minutes=round((time.time() - t) / 60, 1)))
        pd.DataFrame([row2]).to_csv(f'step49_{tag}_step2.csv', index=False)
        fr2.to_csv(f'step49_{tag}_step2_funds.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
