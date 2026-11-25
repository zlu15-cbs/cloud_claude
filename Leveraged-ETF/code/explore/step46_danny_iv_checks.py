"""Checks on Danny's passive Tables 7-10 (replication package of 24 Nov 2026), on his prepared data and five IVs.

    python -I step46_danny_iv_checks.py PACKAGE_DIR      # PACKAGE_DIR = extracted tables7_10_replication/

Reads only data/prepared/passive.npz (allow_pickle=False); runs none of the package's code.
  1. Linear (Salanie-Wolak) version of the fee RC: ln(s/s0) on fee and K = p (p/2 - e_t), e_t = inside-share-weighted
     mean fee; fund + month FE, three controls; 2SLS with month-clustered SE and a cluster-robust Hansen J.
     With all five IVs, IV0 plus each other IV (just identified), the two parts of K entered separately, the age K
     added (Table 8 analogue), and fund-specific linear trends.
  2. Within correlations of the fee K with the age and return K.
  3. The fee slope of a plain IV logit with each IV alone, and its first-stage F.
"""
import sys, numpy as np, pandas as pd, pyhdfe
D = sys.argv[1]
z = np.load(f'{D}/data/prepared/passive.npz', allow_pickle=False)
d = pd.DataFrame({k: z[k] for k in z.files if z[k].dtype.kind != 'U'})
d['s0'] = 1 - d.groupby('market_ids').shares.transform('sum')
d['y'] = np.log(d.shares) - np.log(d.s0)
w = lambda c: (d.shares * d[c]).groupby(d.market_ids).transform('sum')
d['e_t'] = w('prices')
d['K'] = d.prices * (d.prices / 2 - d.e_t)
d['pp2'] = d.prices ** 2 / 2
d['mpe'] = -d.prices * d.e_t
d['a_t'] = w('log_product_fund_age'); d['Ka'] = d.log_product_fund_age * (d.log_product_fund_age / 2 - d.a_t)
d['r_t'] = w('product_past_1yr_ret'); d['Kr'] = d.product_past_1yr_ret * (d.product_past_1yr_ret / 2 - d.r_t)
d['t'] = d.month_t - d.month_t.mean()
CON = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
IV = [f'demand_instruments{k}' for k in range(5)]
print(f"N {len(d):,}; s0 mean {d.s0.mean():.3f}; e_t {d.groupby('market_ids').e_t.first().iloc[0]:.3f} -> {d.groupby('market_ids').e_t.first().iloc[-1]:.3f}")
fid, mid = pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]
alg = pyhdfe.create(np.column_stack([fid, mid]), drop_singletons=False)

def resid(cols, trend=False):
    X = alg.residualize(d[cols].to_numpy(float))
    if not trend:
        return X
    t = d.t.to_numpy(); X = X.copy()
    for _ in range(200):  # alternating projections: fund FE + fund slope on t, then month FE
        X0 = X.copy()
        df = pd.DataFrame(X); g = df.groupby(fid)
        tt = pd.Series(t).groupby(fid); tm = tt.transform('mean').to_numpy(); tc = t - tm
        Xm = g.transform('mean').to_numpy()
        b = (pd.DataFrame(X * tc[:, None]).groupby(fid).transform('sum').to_numpy()
             / pd.Series(tc ** 2).groupby(fid).transform('sum').to_numpy()[:, None].clip(1e-12))
        X = X - Xm - b * tc[:, None]
        X = X - pd.DataFrame(X).groupby(mid).transform('mean').to_numpy()
        if np.abs(X - X0).max() < 1e-10: break
    return X

def tsls(endog, excl, trend=False, label=''):
    R = resid(['y'] + endog + excl + CON, trend)
    y = R[:, 0]; k, L = len(endog), len(excl)
    X = np.column_stack([R[:, 1:1 + k], R[:, 1 + k + L:]]); Zm = np.column_stack([R[:, 1 + k:1 + k + L], R[:, 1 + k + L:]])
    Xh = Zm @ np.linalg.lstsq(Zm, X, rcond=None)[0]
    b = np.linalg.solve(Xh.T @ X, Xh.T @ y); u = y - X @ b
    sc = pd.DataFrame(Xh * u[:, None]).groupby(mid).sum().to_numpy(); Vi = np.linalg.inv(Xh.T @ Xh)
    se = np.sqrt(np.diag(Vi @ sc.T @ sc @ Vi))
    # cluster-robust Hansen J
    gz = pd.DataFrame(Zm * u[:, None]).groupby(mid).sum().to_numpy(); gbar = gz.sum(0)
    J = float(gbar @ np.linalg.pinv(gz.T @ gz) @ gbar) if L > k else np.nan
    print(f"{label:58s} " + '  '.join(f"{n} {bb:8.2f} ({s:.2f})" for n, bb, s in zip(endog, b[:k], se[:k])) + (f"  J {J:.1f} df {L-k}" if L > k else ''), flush=True)
    return b, se

def corrs(trend):
    R = resid(['K', 'Ka', 'Kr', 'prices', 'log_product_fund_age'], trend)
    c = np.corrcoef(R.T)
    print(f"  within corr (trend={trend}): K_fee~K_age {c[0,1]:.3f}  K_fee~K_ret {c[0,2]:.3f}  K_fee~fee {c[0,3]:.3f}  K_age~log age {c[1,4]:.3f}  K_fee~log age {c[0,4]:.3f}")

corrs(False)
for tr in (False, True):
    tag = ' + fund trends' if tr else ''
    tsls(['prices'], ['demand_instruments0'], tr, 'IV logit, IV0' + tag)
    tsls(['prices'], IV, tr, 'logit, five IVs' + tag)
    tsls(['prices', 'K'], IV, tr, 'p, K | five IVs' + tag)
    tsls(['prices', 'pp2', 'mpe'], IV, tr, 'p, p^2/2, -p e_t | five IVs' + tag)
    for k in range(1, 5):
        tsls(['prices', 'K'], ['demand_instruments0', f'demand_instruments{k}'], tr, f'p, K | IV0, IV{k}' + tag)
    tsls(['prices', 'K', 'Ka'], IV, tr, 'p, K, K_age | five IVs' + tag)
corrs(True)

# ---- 3. each IV alone (plain IV logit) ----
R = pd.DataFrame(alg.residualize(d[['y', 'prices'] + IV + CON].to_numpy(float)), columns=['y', 'prices'] + IV + CON)
W = R[CON].to_numpy(); part = lambda v: v - W @ np.linalg.lstsq(W, v, rcond=None)[0]
y, p = part(R.y.to_numpy()), part(R.prices.to_numpy())
for k in range(5):
    zk = part(R[IV[k]].to_numpy())
    b = (zk @ y) / (zk @ p); u = y - b * p
    se = np.sqrt((pd.Series(zk * u).groupby(mid).sum() ** 2).sum()) / abs(zk @ p)
    g = pd.Series(zk * p - zk @ p / (zk @ zk) * zk * zk).groupby(mid).sum()
    pi = (zk @ p) / (zk @ zk); ef = p - pi * zk
    F = pi ** 2 / ((pd.Series(zk * ef).groupby(mid).sum() ** 2).sum() / (zk @ zk) ** 2)
    print(f'IV{k} alone: fee slope {b:8.2f} ({se:.2f})  first-stage F {F:7.1f}  first-stage coef sign {np.sign(pi):+.0f}')
