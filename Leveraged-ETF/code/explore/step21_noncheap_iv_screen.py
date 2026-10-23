"""Screen the coauthor's candidate demand instruments for NON-CHEAP funds (and cheap funds, for comparison).

Split-sample logit IV as in step20: within each group (entry tier at the 10th/15th/20th pct), fund FE, month FE and the
three controls are partialled out (Frisch-Waugh), SE clustered by month. For each candidate C (every BLP_IV_* column
in the index CSV with full coverage and within-fund variation; the conduct shifters are excluded because they are
demand shocks by construction):
  first stage   fee on C:      coefficient, F (= t^2, clustered)
  reduced form  delta on C:    coefficient, t (= Anderson-Rubin test of a zero price coefficient, just identified)
  IV            delta on fee instrumented by C alone (just identified), clustered SE
  H + C         two-step efficient GMM with the Hausman IV and C: slope, SE, Kleibergen-Paap-style first-stage
                F (joint Wald / 2) and Hansen J (1 df) -- does C agree with the Hausman IV?
Also: within-fund SD of C (after month FE), corr with the Hausman IV.

    python step21_noncheap_iv_screen.py        # from a folder holding the index CSV; writes step21_*.csv
"""
import numpy as np
import pandas as pd
import pyhdfe
from scipy import stats

import common
from step2_logit_screen import add_variables, CONTROLS, H

d = add_variables(common.load('index'))
d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))
skip = {'BLP_IV_hausman_exp_ratio_x_broad'}
cands = [c for c in d.columns if c.startswith('BLP_IV_') and c not in skip and d[c].notna().all() and d[c].std() > 0]
# log versions of the two rival characteristics the coauthor logs in the 3-RC cell
for c in ('BLP_IV_rival_log_fund_age4', 'BLP_IV_rival_tracking_err4'):
    if c in d and (d[c] > 0).all():
        d['log_' + c] = np.log(d[c])
        cands.append('log_' + c)
print(f'{len(cands)} candidates:', [c.replace("BLP_IV_", "") for c in cands], flush=True)


def resid(dd, cols):
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    M = alg.residualize(dd[cols].to_numpy(float))
    return pd.DataFrame(M - W @ np.linalg.lstsq(W, M, rcond=None)[0], columns=cols, index=dd.index)


def ols_cl(y, x, g):
    b = float((x @ y) / (x @ x))
    u = y - b * x
    return b, float(np.sqrt(((pd.Series(x * u).groupby(g).sum()) ** 2).sum()) / (x @ x))


def iv1(y, p, z, g):
    b = float((z @ y) / (z @ p))
    u = y - b * p
    return b, float(np.sqrt(((pd.Series(z * u).groupby(g).sum()) ** 2).sum()) / abs(z @ p))


def gmm2(y, p, Z, g):
    """Two-step efficient GMM, one endogenous regressor, cluster-robust weight; returns b, se, J, J_p, joint FS F."""
    Zp, Zy = Z.T @ p, Z.T @ y
    W = np.linalg.inv(Z.T @ Z)
    b = float((Zp @ W @ Zy) / (Zp @ W @ Zp))
    u = y - b * p
    sc = pd.DataFrame(Z * u[:, None]).groupby(g).sum().to_numpy()
    W = np.linalg.pinv(sc.T @ sc)
    b = float((Zp @ W @ Zy) / (Zp @ W @ Zp))
    u = y - b * p
    gbar = Z.T @ u
    sc = pd.DataFrame(Z * u[:, None]).groupby(g).sum().to_numpy()
    S = sc.T @ sc
    J = float(gbar @ np.linalg.pinv(S) @ gbar)
    se = float(np.sqrt(1 / (Zp @ np.linalg.pinv(S) @ Zp)))
    # joint first-stage Wald (cluster-robust) / number of instruments
    pi = np.linalg.lstsq(Z, p, rcond=None)[0]
    v = p - Z @ pi
    ZZi = np.linalg.inv(Z.T @ Z)
    scf = pd.DataFrame(Z * v[:, None]).groupby(g).sum().to_numpy()
    V = ZZi @ (scf.T @ scf) @ ZZi
    F = float(pi @ np.linalg.pinv(V) @ pi) / Z.shape[1]
    return b, se, J, float(stats.chi2.sf(J, Z.shape[1] - 1)), F


rows = []
for q in (20, 15, 10):
    for grp, mask in (('not cheap', d[f'raw{q}'] == 0), ('cheap', d[f'raw{q}'] == 1)):
        dd = d[mask].copy()
        R = resid(dd, ['delta', 'prices', H] + cands)
        g = dd.market_ids.to_numpy()
        y, p, h = R.delta.to_numpy(), R.prices.to_numpy(), R[H].to_numpy()
        mm = lambda c: dd[c] - dd.groupby('market_ids')[c].transform('mean')
        for c in [H] + cands:
            z = R[c].to_numpy()
            if z.std() < 1e-10:
                continue
            fs, fs_se = ols_cl(p, z, g)
            rf, rf_se = ols_cl(y, z, g)
            b, se = iv1(y, p, z, g)
            row = dict(cutoff=q, group=grp, candidate=c.replace('BLP_IV_', '').replace('demand_instruments0', 'hausman_exp_ratio (H)'),
                       within_sd=float((mm(c) - mm(c).groupby(dd.product_ids).transform('mean')).std()) if c in dd else np.nan,
                       corr_H=float(np.corrcoef(z, h)[0, 1]), fs=fs, fs_F=(fs / fs_se) ** 2, rf=rf, rf_t=rf / rf_se,
                       iv=b, iv_se=se)
            if c != H:
                bb, ss, J, Jp, F2 = gmm2(y, p, np.column_stack([h, z]), g)
                row.update(H_plus_C_slope=bb, H_plus_C_se=ss, H_plus_C_F=F2, J=J, J_p=Jp)
            rows.append(row)
        print(f'done {q}th pct, {grp}: {dd.product_ids.nunique()} funds', flush=True)
out = pd.DataFrame(rows)
out.to_csv('step21_noncheap_iv_screen.csv', index=False)
pd.set_option('display.width', 250)
pd.set_option('display.max_rows', 500)
cols = ['candidate', 'within_sd', 'corr_H', 'fs_F', 'rf_t', 'iv', 'iv_se', 'H_plus_C_slope', 'H_plus_C_se', 'H_plus_C_F', 'J_p']
for q in (20, 15, 10):
    for grp in ('not cheap', 'cheap'):
        t = out[(out.cutoff == q) & (out.group == grp)].sort_values('fs_F', ascending=False)
        print(f'\n=== {q}th pct, {grp} (sorted by first-stage F of the candidate alone) ===')
        print(t[cols].round(3).to_string(index=False), flush=True)
