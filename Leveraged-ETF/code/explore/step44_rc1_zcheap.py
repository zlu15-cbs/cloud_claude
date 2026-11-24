"""One random coefficient on the expense ratio, with NO cheap term in utility, identified by the share-class Hausman IV
Z and Z x cheap (cost shifter x fee level). Sample: the 97,429 fund-months of new_iv.load_new_iv_sample().

Modes:
  frac                    linear IV version (Salanie-Wolak expansion): ln(s/s0) on prices and K = p (p/2 - e_t), controls,
                          fund + month FE; e_t = share-weighted mean fee in month t. Both prices and K are endogenous.
                          Instrument sets: (Z, Z x cheap), (Z, Z x launch fee), (Z, Z^2). Reports alpha, sigma^2,
                          Sanderson-Windmeijer F for each endogenous term, and how well p_bar*p_tilde and p_bar*e_tilde
                          reproduce the within-fund variation in K.
  normal PROCS            BLP, normal RC on prices. X1 = prices + controls, X2 = prices; excluded IVs Z, Z x cheap
                          (5 moments, 5 parameters). Sigma profile on a grid, then BFGS from the best grid point.
  lognormal PROCS [s0 p0] BLP, lognormal RC on -prices: fee coefficient = -exp(pi + sigma nu) < 0 for every investor.
                          X1 = controls, X2 = -prices, agent constant; same IVs (5 moments, 5 parameters). BFGS.
One-step GMM (2SLS weight), Monte Carlo 3000 draws, seed 623543, SE clustered by month. Every objective evaluation is
checkpointed to step44_<mode>_ckpt.json; rerunning resumes from the best point.

    python step44_rc1_zcheap.py frac            # from a folder holding the index CSV; writes step44_*.csv
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp
import pyhdfe
from pyblp.configurations.optimization import scipy_optimizer

from new_iv import load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import first_stage_f, CONTROLS
from tiers import raw_entry_tiers

pyblp.options.verbose = False
X1C = ' + '.join(CONTROLS)


def data():
    d = load_new_iv_sample()
    d['cheap'] = d.raw20
    d['launch_fee'] = d.product_ids.map(raw_entry_tiers((0.20,)).product_exp_ratio).astype(float)
    d['e_t'] = (d.shares * d.prices).groupby(d.market_ids).transform('sum')
    d['K'] = d.prices * (d.prices / 2 - d.e_t)
    d = d.drop(columns=[c for c in d.columns if c.startswith('demand_instruments')])
    d['demand_instruments0'] = d.Z
    d['demand_instruments1'] = d.Z * d.cheap
    return d


def resid(d, cols):
    ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]])
    return pyhdfe.create(ids, drop_singletons=False).residualize(d[cols].to_numpy(float))


def iv2sls(d, endog, excl):
    """2SLS with fund + month FE and the three controls; SE clustered by month."""
    R = resid(d, ['delta'] + endog + excl + CONTROLS)
    y, X, Zm = R[:, 0], R[:, 1:1 + len(endog)], R[:, 1 + len(endog):1 + len(endog) + len(excl)]
    W = R[:, 1 + len(endog) + len(excl):]
    XX, ZZ = np.column_stack([X, W]), np.column_stack([Zm, W])
    Xh = ZZ @ np.linalg.lstsq(ZZ, XX, rcond=None)[0]
    b = np.linalg.solve(Xh.T @ XX, Xh.T @ y)
    u = y - XX @ b
    sc = pd.DataFrame(Xh * u[:, None]).groupby(d.market_ids.to_numpy()).sum().to_numpy()
    Vi = np.linalg.inv(Xh.T @ Xh)
    se = np.sqrt(np.diag(Vi @ (sc.T @ sc) @ Vi))
    return b, se


def frac():
    d = data()
    print(f'N {len(d):,}; mean e_t {d.e_t.mean():.4f}; mean fee {d.prices.mean():.3f}; cheap fund-months {d.cheap.mean():.3f}', flush=True)
    # how the within-fund variation in K splits
    pbar = d.groupby('product_ids').prices.transform('mean')
    d['pp'] = pbar * d.prices
    d['pe'] = pbar * d.e_t
    R = resid(d, ['K', 'pp', 'pe', 'prices'])
    k, pp, pe, p = R.T
    c = lambda a, b: float(np.corrcoef(a, b)[0, 1])
    print(f'within variation of K: corr with p_bar*p_tilde {c(k, pp):.3f}; with -p_bar*e_tilde {c(k, -pe):.3f}; '
          f'with their sum {c(k, pp - pe):.3f}; corr(K~, p~) {c(k, p):.3f}; var share of p_bar*p~ {pp.var() / k.var():.3f}, '
          f'of p_bar*e~ {pe.var() / k.var():.3f}', flush=True)
    d['Zc'], d['Zl'], d['Z2'] = d.Z * d.cheap, d.Z * d.launch_fee, d.Z ** 2
    rows = []
    for name, excl in (('Z, Z x cheap', ['Z', 'Zc']), ('Z, Z x launch fee', ['Z', 'Zl']), ('Z, Z^2', ['Z', 'Z2']),
                       ('Z, Z x cheap, Z^2 (overid.)', ['Z', 'Zc', 'Z2'])):
        b, se = iv2sls(d, ['prices', 'K'], excl)
        f = first_stage_f(d, ['prices', 'K'], excl, CONTROLS)
        s2 = b[1]
        row = dict(instruments=name, alpha=b[0], alpha_se=se[0], sigma2=s2, sigma2_se=se[1], sigma=np.sqrt(s2) if s2 > 0 else np.nan,
                   F_price=f['prices'], F_K=f['K'],
                   slope_p05=b[0] + s2 * (0.05 - d.e_t.mean()), slope_p20=b[0] + s2 * (0.20 - d.e_t.mean()),
                   slope_p50=b[0] + s2 * (0.50 - d.e_t.mean()), slope_p100=b[0] + s2 * (1.00 - d.e_t.mean()),
                   share_upward=float((b[0] + s2 * (d.prices - d.e_t) > 0).mean()))
        rows.append(row)
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    pd.DataFrame(rows).to_csv('step44_frac.csv', index=False)


def describe(res, d, funds, label, extra):
    em = res.compute_elasticities()
    e = res.extract_diagonals(em).flatten()
    mc = res.compute_costs().flatten()
    dd = d.assign(e=e, slope=e / d.prices.to_numpy())
    last = dd.sort_values('month_t').groupby('product_ids').last().loc[funds.product_ids]
    # scaled Jacobian of the moments: [-ZD'X1/N, ZD'(d xi / d theta)/N], whitened by W, columns normalized
    P = res.problem.products
    G = np.column_stack([-P.ZD.T @ P.X1, P.ZD.T @ res.xi_by_theta_jacobian]) / len(d)
    LG = np.linalg.cholesky(res.W).T @ G
    sv = np.linalg.svd(LG / np.linalg.norm(LG, axis=0), compute_uv=False)
    row = dict(spec=label, N=len(d), objective=float(res.objective), converged=bool(res.converged),
               sigma=float(res.sigma[0, 0]), sigma_se=float(res.sigma_se[0, 0]),
               avg_own_elasticity=float(res.extract_diagonal_means(em).flatten().mean()),
               share_pos_e=float((e > 0).mean()), share_abs_e_gt1=float((np.abs(e) > 1).mean()), share_neg_mc=float((mc < 0).mean()),
               slope_cheap=float(dd.slope[dd.cheap == 1].mean()), slope_noncheap=float(dd.slope[dd.cheap == 0].mean()),
               n15_gt1=int((last.e.abs() > 1).sum()), n15_pos=int((last.e > 0).sum()),
               min_scaled_singular_value=float(sv.min()), **extra)
    for t, b, s in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
        row[f'b[{t}]'], row[f'se[{t}]'] = float(b), float(s)
    fr = last[['product_fund_name', 'prices', 'e']].assign(spec=label).reset_index()
    return row, fr


def checkpointed(tag, history):
    ckpt = f'step44_{tag}_ckpt.json'

    def bfgs(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            print(f'  eval {len(history)}: theta {np.round(history[-1]["theta"], 5).tolist()} obj {history[-1]["obj"]:.6g}', flush=True)
            return out
        return scipy_optimizer(initial, None, wrapped, iteration_callback, method='BFGS', compute_gradient=True, **opts)
    return pyblp.Optimization(bfgs, {'gtol': 1e-7})


def normal(procs):
    d = data()
    funds = top15(d)
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    rows, frs = [], []
    with pyblp.parallel(procs):
        pr = pyblp.Problem((pyblp.Formulation('0 + prices + ' + X1C, absorb='C(product_ids) + C(market_ids)'),
                            pyblp.Formulation('0 + prices')), d, integration=integ)
        for s in (0.001, 1, 2, 4, 6, 8, 12):
            t = time.time()
            res = pr.solve(np.array([[s]]), optimization=pyblp.Optimization('return'), method='1s', se_type='clustered')
            row, _ = describe(res, d, funds, f'normal profile sigma={s}', dict(secs=round(time.time() - t)))
            rows.append(row)
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()
                   if k in ('sigma', 'objective', 'b[prices]', 'avg_own_elasticity', 'share_pos_e', 'slope_cheap', 'slope_noncheap', 'n15_gt1', 'secs')}, flush=True)
            pd.DataFrame(rows).to_csv('step44_normal_profile.csv', index=False)
        best = min(rows, key=lambda r: r['objective'])['sigma']
        history = []
        t = time.time()
        res = pr.solve(np.array([[best]]), optimization=checkpointed('normal', history), method='1s', se_type='clustered')
        print(res, flush=True)
        row, fr = describe(res, d, funds, 'normal RC, IVs Z and Z x cheap', dict(minutes=round((time.time() - t) / 60, 1)))
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    print(fr.round(3).to_string(index=False), flush=True)
    pd.DataFrame([row]).to_csv('step44_normal_estimate.csv', index=False)
    fr.to_csv('step44_normal_funds.csv', index=False)


def lognormal(procs, sigma0, pi0):
    d = data()
    funds = top15(d)
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    tag = f'lognormal_s{sigma0}_p{pi0}'
    ckpt = f'step44_{tag}_ckpt.json'
    history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
    if history:
        th = min(history, key=lambda r: r['obj'])['theta']
        sigma0, pi0 = th[0], th[1]
    print(f'{tag}: N={len(d):,}; start sigma {sigma0:.4f} pi {pi0:.4f} ({len(history)} checkpointed evaluations)', flush=True)
    t = time.time()
    with pyblp.parallel(procs):
        ids, nodes, weights = integ._build_many(1, np.unique(d.market_ids))
        pr = pyblp.Problem((pyblp.Formulation('0 + ' + X1C, absorb='C(product_ids) + C(market_ids)'), pyblp.Formulation('0 + I(-prices)')),
                           d, agent_formulation=pyblp.Formulation('1'),
                           agent_data={'market_ids': ids, 'nodes': nodes, 'weights': weights}, rc_types=['log'])
        opt = pyblp.Optimization('return') if os.environ.get('FINALIZE') == '1' else checkpointed(tag, history)
        res = pr.solve(sigma=np.array([[sigma0]]), pi=np.array([[pi0]]), optimization=opt, method='1s', se_type='clustered')
        print(res, flush=True)
        s, p = float(res.sigma[0, 0]), float(res.pi[0, 0])
        row, fr = describe(res, d, funds, f'lognormal RC, IVs Z and Z x cheap ({tag})',
                           dict(pi=p, pi_se=float(res.pi_se[0, 0]), median_fee_coef=-float(np.exp(p)), mean_fee_coef=-float(np.exp(p + s * s / 2)),
                                p10_fee_coef=-float(np.exp(p + 1.2816 * abs(s))), p90_fee_coef=-float(np.exp(p - 1.2816 * abs(s))),
                                minutes=round((time.time() - t) / 60, 1)))
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    print(fr.round(3).to_string(index=False), flush=True)
    pd.DataFrame([row]).to_csv(f'step44_{tag}_estimate.csv', index=False)
    fr.to_csv(f'step44_{tag}_funds.csv', index=False)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'frac':
        frac()
    elif mode == 'normal':
        normal(int(sys.argv[2]))
    else:
        lognormal(int(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 0.5, float(sys.argv[4]) if len(sys.argv) > 4 else 2.3)
