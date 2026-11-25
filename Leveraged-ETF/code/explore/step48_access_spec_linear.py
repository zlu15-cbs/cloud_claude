"""Toward a preferred passive fee-RC specification on Danny's Tables 7-10 package: linear (Salanie-Wolak) screens.

    python -I step48_access_spec_linear.py PACKAGE_DIR IV_INPUTS_DIR [NAMES_CSV]   # NAMES_CSV: product_ids, product_fund_name

Reads data/prepared/passive.npz and data/iv_inputs/passive_focal.csv.gz (+ certified exits); runs none of his code.

Access flag (access3: 0 retail class, 1 institutional class, 2 ETF), corrected per class:
  ETF if vehicle = 1; otherwise the flag of the class's first record in the panel, or, for classes whose flag
  changes, the last value before Jan 2019 (CRSP's re-flag). Vanguard Admiral classes are coded retail.
Screens (fund FE throughout; controls tracking error, 1-yr return, log age; month-clustered SE; cluster Hansen J):
  T7     Danny's Table 7 analogue: fee and K = p (p/2 - e_t), five IVs, month FE.
  A      + month x access FE (segment-level shifts toward cheap funds, the market-position confound).
  B      A + fee x institutional and fee x ETF (observed investor-type heterogeneity); extra IVs IV0, IV1 x access.
  B-orig B with Danny's original time-varying flag (fixed effects month x original access).
  B-split, B-age: B with the two parts of K entered separately; B with the age K added (Table 10 analogue).
  logit  B without K: fee slope by investor type, and the implied elasticities.
"""
import sys
import numpy as np
import pandas as pd
import pyhdfe

CON = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
IV = [f'demand_instruments{k}' for k in range(5)]
IVX = ['iv0_inst', 'iv0_etf', 'iv1_inst', 'iv1_etf']
IVXO = [c + '_o' for c in IVX]
def load(P, D, names=None):
    """Danny's passive sample with the corrected access flag, K terms and access interactions."""
    z = np.load(f'{P}/data/prepared/passive.npz', allow_pickle=False)
    d = pd.DataFrame({k: z[k] for k in z.files if z[k].dtype.kind != 'U'})
    f = pd.read_csv(f'{D}/passive_focal.csv.gz')
    assert (f.crsp_id.to_numpy() == d.product_ids.to_numpy()).all()
    d['access_orig'] = f.access3.to_numpy()
    d['vehicle'] = f.vehicle.to_numpy()
    d['month'] = f.month.to_numpy()
    d['family'] = f.family.to_numpy()

    # corrected, time-invariant access flag
    g = d.sort_values('month').groupby('product_ids')
    first = g.access_orig.first()
    pre = d[d.month < 2019 * 12].sort_values('month').groupby('product_ids').access_orig.last()
    flips = g.access_orig.nunique() > 1
    acc = first.copy()
    acc[flips] = pre.reindex(acc[flips].index).fillna(first[flips])
    d['access'] = d.product_ids.map(acc)
    d.loc[d.vehicle == 1, 'access'] = 2
    if names:  # optional: product_ids -> fund name map (two columns, no data), to recode Admiral classes
        nm = pd.read_csv(names).set_index('product_ids').product_fund_name
        adm = d.product_ids.map(nm).str.contains('Admiral', na=False) & (d.vehicle == 0)
        d.loc[adm, 'access'] = 0
        print(f'Admiral rows recoded to retail: {int((adm & (d.access_orig != 0)).sum())} of {int(adm.sum())}')
    chg = d.access != d.access_orig
    print(f'flag changes vs original: {int(chg.sum()):,} fund-months, {d.product_ids[chg].nunique()} classes; '
          f'classes that flip in the original: {int(flips.sum())}')
    print('fund-months by corrected access:', d.access.value_counts().sort_index().to_dict())

    d['s0'] = 1 - d.groupby('market_ids').shares.transform('sum')
    d['y'] = np.log(d.shares) - np.log(d.s0)
    w = lambda c: (d.shares * d[c]).groupby(d.market_ids).transform('sum')
    d['e_t'] = w('prices')
    d['K'] = d.prices * (d.prices / 2 - d.e_t)
    d['pp2'], d['mpe'] = d.prices ** 2 / 2, -d.prices * d.e_t
    d['a_t'] = w('log_product_fund_age')
    d['Ka'] = d.log_product_fund_age * (d.log_product_fund_age / 2 - d.a_t)
    for a, nmz in ((1, 'inst'), (2, 'etf')):
        d[nmz] = (d.access == a).astype(float)
        d[f'p_{nmz}'] = d.prices * d[nmz]
        d[f'{nmz}_o'] = (d.access_orig == a).astype(float)
        d[f'p_{nmz}_o'] = d.prices * d[f'{nmz}_o']
        for k in (0, 1):
            d[f'iv{k}_{nmz}'] = d[f'demand_instruments{k}'] * d[nmz]
            d[f'iv{k}_{nmz}_o'] = d[f'demand_instruments{k}'] * d[f'{nmz}_o']
    return d


def tsls(endog, excl, fe, label):
    cols = ['y'] + endog + excl + CON
    R = algs[fe].residualize(d[cols].to_numpy(float))
    y, k, L = R[:, 0], len(endog), len(excl)
    X = np.column_stack([R[:, 1:1 + k], R[:, 1 + k + L:]])
    Zm = np.column_stack([R[:, 1 + k:1 + k + L], R[:, 1 + k + L:]])
    Xh = Zm @ np.linalg.lstsq(Zm, X, rcond=None)[0]
    b = np.linalg.solve(Xh.T @ X, Xh.T @ y)
    u = y - X @ b
    sc = pd.DataFrame(Xh * u[:, None]).groupby(clu).sum().to_numpy()
    Vi = np.linalg.inv(Xh.T @ Xh)
    se = np.sqrt(np.diag(Vi @ sc.T @ sc @ Vi))
    gz = pd.DataFrame(Zm * u[:, None]).groupby(clu).sum().to_numpy()
    gb = gz.sum(0)
    J = float(gb @ np.linalg.pinv(gz.T @ gz) @ gb) if L > k else np.nan
    # Sanderson-Windmeijer-style partial F for each endogenous regressor: F of its first stage on the excluded IVs,
    # after partialling the fitted values of the other endogenous regressors (conditional F)
    Fs = []
    Ze, W = Zm[:, :L], R[:, 1 + k + L:]
    for i in range(k):
        xi = X[:, i]
        others = [Xh[:, j] for j in range(k) if j != i]
        A = np.column_stack(others + [W]) if others else W
        xr = xi - A @ np.linalg.lstsq(A, xi, rcond=None)[0]
        Zr = Ze - A @ np.linalg.lstsq(A, Ze, rcond=None)[0]
        c = np.linalg.lstsq(Zr, xr, rcond=None)[0]
        e = xr - Zr @ c
        se_c = pd.DataFrame(Zr * e[:, None]).groupby(clu).sum().to_numpy()
        Zi = np.linalg.pinv(Zr.T @ Zr)
        V = Zi @ se_c.T @ se_c @ Zi
        Fs.append(float(c @ np.linalg.pinv(V) @ c) / max(L - (k - 1), 1))
    row = dict(spec=label, fe=fe, n_excl=L, J=J, J_df=L - k)
    for i, t in enumerate(endog):
        row[t], row[t + '_se'], row[t + '_F'] = b[i], se[i], Fs[i]
    print(label.ljust(34), ' '.join(f'{t} {b[i]:+.3f} ({se[i]:.3f}) F {Fs[i]:.1f};' for i, t in enumerate(endog)),
          f'J {J:.1f} on {L - k} df' if L > k else 'just identified', flush=True)
    return row, b, u


def main(P, D, names=None):
    global d, algs, clu
    d = load(P, D, names)
    fid = pd.factorize(d.product_ids)[0]
    ids = {'month': pd.factorize(d.market_ids)[0],
           'month_access': pd.factorize(d.market_ids.astype(str) + '_' + d.access.astype(str))[0],
           'month_access_orig': pd.factorize(d.market_ids.astype(str) + '_' + d.access_orig.astype(str))[0]}
    algs = {k: pyhdfe.create(np.column_stack([fid, v]), drop_singletons=False) for k, v in ids.items()}
    clu = ids['month']


    rows = []
    rows.append(tsls(['prices', 'K'], IV, 'month', 'T7 (fee, K; month FE)')[0])
    rows.append(tsls(['prices', 'K'], IV, 'month_access', 'A (+ month x access FE)')[0])
    rows.append(tsls(['prices', 'p_inst', 'p_etf', 'K'], IV + IVX, 'month_access', 'B (+ fee x access)')[0])
    rows.append(tsls(['prices', 'p_inst_o', 'p_etf_o', 'K'], IV + IVXO, 'month_access_orig', 'B-orig (original flag)')[0])
    rows.append(tsls(['prices', 'p_inst', 'p_etf', 'pp2', 'mpe'], IV + IVX, 'month_access', 'B-split (p^2/2, -p e_t)')[0])
    rows.append(tsls(['prices', 'p_inst', 'p_etf', 'K', 'Ka'], IV + IVX, 'month_access', 'B-age (+ age K)')[0])
    rows.append(tsls(['prices', 'K'], IV, 'month_access_orig', 'A-orig (original flag)')[0])
    r, b, _ = tsls(['prices', 'p_inst', 'p_etf'], IV + IVX, 'month_access', 'logit B (no K)')
    rows.append(r)
    slope = b[0] + b[1] * d.inst + b[2] * d.etf
    e = slope * d.prices * (1 - d.shares)
    print('logit B fee slope: retail %.2f, institutional %.2f, ETF %.2f' % (b[0], b[0] + b[1], b[0] + b[2]))
    print('logit B elasticity: mean %.2f; AUM-weighted %.2f; share |e|<1 %.3f; AUM share |e|<1 %.3f' % (
        e.mean(), np.average(e, weights=d.product_mtna), (e.abs() < 1).mean(),
        d.product_mtna[e.abs() < 1].sum() / d.product_mtna.sum()))
    last = d.month_t == d.month_t.max()
    print('logit B elasticity, last month, by access (AUM-weighted):',
          {int(a): round(float(np.average(e[last & (d.access == a)], weights=d.product_mtna[last & (d.access == a)])), 2) for a in (0, 1, 2)})
    pd.DataFrame(rows).to_csv('step48_access_spec_linear.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
