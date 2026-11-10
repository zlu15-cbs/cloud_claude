"""Replicate V2, the recommended logit-IV demand model for the index market (Table 2 Panel A sample), and its downstream
results: scale, marginal costs, where the negative MCs sit, and the conduct test.

    python replicate_V2.py --index-csv nonLev_funds_product_month_level_v2_patched.csv \
                           --crsp CRSP_fund_summary_2026_qtrly_combined.csv

Inputs (both are Danny's own files):
  --index-csv  the index-fund product-month CSV that main_Danny_Oct2026_index_market.ipynb reads (cell 3)
  --crsp       CRSP quarterly fund summary (lipper_class, lipper_asset_cd, crsp_obj_cd, fund_name, inst_fund, retail_fund)
Options:
  --donor-mmf all     (default) money market funds are dropped from the estimation sample, the supply side AND the
                      instrument's donor pool
  --donor-mmf sample  drop from the donor pool only the 4 money market funds that are in the Table 2 sample
                      (reproduces our first V2 run: alpha -3.607)
  --no-conduct        skip the pyRVtest runs (the slow part)
Outputs (prefix V2_): demand.csv, table5.csv, scale.csv, mc.csv, where.csv, conduct.csv, Z.csv, rows_without_Z.csv,
money_market_funds.csv. Tested with pyblp 1.3.0, pyRVtest 0.3.2, pandas 2.x, numpy 1.26/2.x, pyhdfe 0.2.
"""
import argparse
import contextlib
import io
import re
import time

import numpy as np
import pandas as pd
import pyblp
import pyhdfe
from scipy import stats

pyblp.options.verbose = False
T0 = time.time()


def log(msg):
    print(f'[{time.time() - T0:6.0f}s] {msg}', flush=True)


# =====================================================================================================================
# 0. Sample: Danny's notebook main_Danny_Oct2026_index_market.ipynb, cells 3 and 4, verbatim (display calls removed)
# =====================================================================================================================
def load_sample(path):
    product_data = pd.read_csv(path)
    product_data["market_ids"] = product_data.groupby(["month_t"]).ngroup() + 1
    product_data["log_product_fund_age"] = np.log(product_data["product_fund_age"])
    product_data["product_tracking_err"] = abs(product_data["product_tracking_err"])
    product_data = product_data.dropna(subset=['Conduct_IV_csent_index_resid'])
    product_data['clustering_ids'] = product_data.market_ids
    product_data = product_data.rename(columns={
        'product_exp_ratio': 'prices', 'market_share': 'shares_old', 'BLP_IV_hausman_exp_ratio': 'demand_instruments0',
        'firm_f': 'firm_ids', 'product_j': 'product_ids'})
    product_data["shares"] = product_data["product_mtna"] / product_data["market_share_m_denom_alt1"]
    product_data = product_data.loc[product_data['shares'] >= 0.0001]
    product_data = product_data.loc[product_data['month_t'] >= 2010]
    product_data = product_data.loc[product_data['month_t'] <= (2024 + 8 / 12)]
    product_data = product_data[product_data['prefer'].isin([1, 2, 3, 4, 5])]
    product_data = product_data.loc[product_data['prices'] > 0]
    product_data["rotator"] = (product_data["Conduct_IV_neg_vw_ind_resid_1m"] + product_data["Conduct_IV_neg_vw_ind_resid_2to5m"]
                               + product_data["Conduct_IV_neg_vw_ind_resid_6to12m"])
    d = product_data.reset_index(drop=True)
    d['month_key'] = np.round(d.month_t * 12).astype(int)
    return d


# =====================================================================================================================
# 1. Money market funds: "money market" in a CRSP fund name AND, in some quarter, a money-market Lipper class
#    (MM, ITM, IUS, UST, IMM) or CRSP style code IM*. They are not index funds.
# =====================================================================================================================
MM_LIPPER = ['MM', 'ITM', 'IUS', 'UST', 'IMM']


def money_market_funds(crsp, funds):
    c = crsp[crsp.crsp_fundno.isin(funds)]
    by_name = set(c.loc[c.fund_name.fillna('').str.contains('money market', case=False), 'crsp_fundno'])
    by_code = set(c.loc[c.lipper_class.isin(MM_LIPPER) | c.crsp_obj_cd.fillna('').str.startswith('IM'), 'crsp_fundno'])
    return sorted(by_name & by_code)


# =====================================================================================================================
# 2. Cheap indicator gene_idx: the fund's expense ratio in its first month with a recorded fee in the full index CSV
#    (all years, before any sample filter) is <= that month's 20th percentile across all funds in the CSV with a fee.
# =====================================================================================================================
def gene_idx(raw_all):
    cut = raw_all.groupby('month_t').product_exp_ratio.quantile(0.20)
    entry = raw_all.sort_values('month_t').groupby('product_j').first()
    return (entry.product_exp_ratio <= entry.month_t.map(cut) + 1e-9).astype(float).rename('gene_idx')


# =====================================================================================================================
# 3. Asset class (six classes), one per tracked index (market_m_index)
#    fund level: the fund's most common Lipper class over its CRSP quarters, mapped by lipper_class(); if no Lipper class,
#    its most common CRSP style code mapped by crsp_class(); if neither, the name/cluster rule classify_fallback().
#    index level: the most common fund-level class among all funds in the CSV tracking that index.
# =====================================================================================================================
LIP_ALLOC = ('FX', 'B', 'BT', 'GX', 'CV')
LIP_REAL = ('RE', 'GRE', 'IRE', 'AU', 'CMG', 'CMP', 'CME', 'CMM', 'CMA', 'CMD', 'RR')
LIP_OTHER = ('LSE', 'OS', 'AED', 'AGM', 'ABR', 'AMS', 'MFF', 'EMN', 'DSB', 'DL', 'ALT', 'CRX', 'EMP')
LIP_INTL = ('EM', 'EU', 'CH', 'LT', 'JA', 'XJ', 'PC', 'INR', 'FM', 'IF', 'GL', 'GEI', 'GSME', 'GTK', 'GNR', 'GFS', 'GH', 'GIF')


def lipper_class(code, asset_cd):
    c = str(code)
    if c in LIP_OTHER:
        return 'other'
    if c.startswith(('MAT', 'MTA')) or c in LIP_ALLOC:
        return 'allocation'
    if c in LIP_REAL:
        return 'real_asset'
    if asset_cd in ('TX', 'MB'):            # taxable bond, municipal bond (incl. money market)
        return 'bond'
    if c in LIP_INTL or c.startswith(('IML', 'ILC', 'ISM', 'IEI', 'IFCE', 'IFGE', 'GML', 'GLC', 'GLV', 'GLG')):
        return 'intl_equity'
    if c == 'nan':
        return np.nan
    return 'us_equity'


def crsp_class(code):  # CRSP style code (MFDB Guide, Appendix A)
    c = str(code)
    if c[:4] in ('EDSR', 'EFSR', 'EDSO', 'EFSO', 'EDSC', 'EFSC'):
        return 'real_asset'
    if c.startswith('ED'):
        return 'us_equity'
    if c.startswith('EF'):
        return 'intl_equity'
    if c.startswith('I') or c == 'OM':
        return 'bond'
    if c.startswith('M'):
        return 'allocation'
    if c.startswith('O'):
        return 'other'
    return np.nan


CLUSTER = {1: 'us_equity', 5: 'us_equity', 6: 'us_equity', 7: 'us_equity', 10: 'us_equity', 11: 'us_equity', 12: 'us_equity',
           23: 'us_equity', 3: 'intl_equity', 9: 'intl_equity', 46: 'intl_equity',
           2: 'bond', 16: 'bond', 25: 'bond', 26: 'bond', 52: 'bond', 17: 'allocation', 21: 'real_asset'}
KW = [
    ('allocation', r'target date|target retirement|retirement|lifestrategy|life strategy|allocation|balanced|lifecycle|life cycle|lifepath|multi-asset|target \d{4}'),
    ('real_asset', r'\bgold\b|silver|precious|commodit|\boil\b|natural gas|reit\b|real estate|realty|infrastructure|metals'),
    ('bond', r'bond|treasury|treas\b|govt|government|municipal|muni\b|tips\b|inflation|corporate|aggregate|fixed income|high yield|credit|mortgage|securitized|floating rate|duration|t-bill|money market|\bagg\b|ultra short|income fund'),
    ('intl_equity', r'international|intl|emerging|developed|ex-us|ex us|ex-u\.s|world|global|europe|euro|japan|china|india|brazil|pacific|asia|eafe|acwi|canada|mexico|korea|taiwan|germany|united kingdom|\buk\b|france|australia|latin|frontier|foreign|\bem\b'),
]
IDX_BOND = re.compile(r'^(L[A-Z0-9]*TR(UU)?|LMBITR|IBOX|C0A0|H0A0|BCOM)', re.I)


def classify_fallback(df):
    """Used only where a fund has neither a Lipper class nor a CRSP style code (0.04% of rows)."""
    ac = df.market_m_cluster.map(CLUSTER)
    name = df.product_fund_name.fillna('').str.lower()
    out = pd.Series(np.nan, index=df.index, dtype=object)
    for cls, pat in KW:
        hit = name.str.contains(pat, regex=True) & out.isna()
        out[hit] = cls
    idx = df.market_m_index.fillna('').astype(str)
    out[out.isna() & idx.str.match(IDX_BOND)] = 'bond'
    out[idx.str.startswith('BCOM') & ac.isna()] = 'real_asset'
    return ac.fillna(out).fillna('us_equity')


def mode_per_index(raw, cls):
    key_i = raw.market_m_index.fillna('_none_' + raw.product_j.astype(str))
    t = pd.DataFrame({'i': key_i, 'cls': cls, 'pj': raw.product_j})[cls.notna()].drop_duplicates('pj')
    return key_i.map(t.groupby('i').cls.agg(lambda s: s.value_counts().index[0])).fillna(cls)


# =====================================================================================================================
# 4. Share class: ETF if ETF_ind = 1; else institutional if CRSP inst_fund = Y; else retail if CRSP retail_fund = Y
#    (CRSP flags matched by crsp_fundno and calendar quarter); else the name rule below (about 0.3% of mutual-fund rows).
# =====================================================================================================================
def share_class_keywords(raw):
    nm = raw.product_fund_name.fillna('').str.lower()
    mf = raw.ETF_ind == 0
    inst = mf & nm.str.contains(r'institutional|inst\b|class i\b|premier|select|class k\b|class z\b|class y\b|class r6|admiral')
    retail = mf & ~inst & nm.str.contains(r'investor|retail|class a\b|class c\b|class r\b|class t\b|service|advisor')
    return np.select([~mf, inst, retail], ['etf', 'inst', 'retail'], 'mf_other')


# =====================================================================================================================
# 5. Hausman instrument Z_jt = median expense ratio of donor funds k in month t with
#      same family (firm_f_old) as j, same share class as j, different asset class from j.
#    Donors: every fund in the index CSV with a recorded fee in month t (not only Table 2 funds), money market funds excluded.
#    Z is missing (row not used in demand) when j has no firm_f_old or no such donor exists that month.
# =====================================================================================================================
def leave_out(r, fam, ac, sc, name):
    keys = [fam, 'month_t'] + ([sc] if sc else [])
    rr = r[r[fam].notna()]
    tab = pd.concat([rr[rr[ac] != a].groupby(keys).product_exp_ratio.median().rename(name).reset_index().assign(**{ac: a})
                     for a in sorted(rr[ac].dropna().unique())])
    k = r[['product_j', 'month_t', ac] + keys[:1] + keys[2:]].merge(tab, on=keys + [ac], how='left')
    return k[name].to_numpy()


def build_instrument(index_csv, crsp_path, drop):
    raw = pd.read_csv(index_csv, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                          'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
    raw = raw[raw.product_exp_ratio.notna() & ~raw.product_j.isin(drop)].reset_index(drop=True)
    lp = pd.read_csv(crsp_path, usecols=['crsp_fundno', 'lipper_class', 'lipper_asset_cd', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
    lp['crsp_fundno'] = lp.crsp_fundno.astype(float).astype(int)
    lp = lp[lp.crsp_fundno.isin(raw.product_j)]
    lmode = lp.dropna(subset=['lipper_class']).groupby('crsp_fundno').lipper_class.agg(lambda s: s.value_counts().index[0])
    acd = lp.dropna(subset=['lipper_class']).drop_duplicates('lipper_class').set_index('lipper_class').lipper_asset_cd
    omode = lp.dropna(subset=['crsp_obj_cd']).groupby('crsp_fundno').crsp_obj_cd.agg(lambda s: s.value_counts().index[0])
    lc = raw.product_j.map(lmode)
    fund_cls = pd.Series([lipper_class(c, acd.get(c)) for c in lc], index=raw.index)
    fund_cls = fund_cls.fillna(raw.product_j.map(omode).map(crsp_class)).fillna(classify_fallback(raw))
    raw['asset_class'] = mode_per_index(raw, fund_cls)
    raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
    fl = pd.read_csv(crsp_path, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund'], encoding='latin-1')
    fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})
    raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
    mf = raw.ETF_ind == 0
    raw['share_class'] = np.select([~mf, raw.inst_fund == 'Y', raw.retail_fund == 'Y'], ['etf', 'inst', 'retail'],
                                   share_class_keywords(raw))
    raw['Z'] = leave_out(raw, 'firm_f_old', 'asset_class', 'share_class', 'Z')
    return raw


def why_no_z(d, raw):
    """Reason a Table 2 row has no Z: (a) no family code, (b) family has no fund in another asset class that month,
    (c) family has such funds but none in the same share class."""
    g = ['firm_f_old', 'month_t']
    n_ft = raw.groupby(g).size()
    n_fta = raw.groupby(g + ['asset_class']).size()
    n_fts = raw.groupby(g + ['share_class']).size()
    n_ftsa = raw.groupby(g + ['share_class', 'asset_class']).size()
    mi = pd.MultiIndex.from_frame
    oth = n_ft.reindex(mi(d[g])).to_numpy() - n_fta.reindex(mi(d[g + ['asset_class']])).to_numpy()
    oth_sc = n_fts.reindex(mi(d[g + ['share_class']])).to_numpy() - n_ftsa.reindex(mi(d[g + ['share_class', 'asset_class']])).fillna(0).to_numpy()
    return np.select([d.Z.notna(), d.firm_f_old.isna(), np.nan_to_num(oth) <= 0, np.nan_to_num(oth_sc) <= 0],
                     ['has Z', 'a no family code', 'b no family fund in another asset class', 'c none in the same share class'], 'other')


# =====================================================================================================================
# 6. Demand: logit IV, delta = a p + a_x p*gene_idx + |TE| + past 1y return + log age + fund FE + month FE;
#    excluded instruments Z and Z*gene_idx; SE clustered by month; Sanderson-Windmeijer F, cluster-robust.
# =====================================================================================================================
CONTROLS = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']


def resid(dd, cols):
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    M = alg.residualize(dd[cols].to_numpy(float))
    return M - W @ np.linalg.lstsq(W, M, rcond=None)[0]


def cl_wald(y, X, g):
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    u = y - X @ b
    sc = pd.DataFrame(X * u[:, None]).groupby(g).sum().to_numpy()
    V = XtXi @ (sc.T @ sc) @ XtXi
    return float(b @ np.linalg.pinv(V) @ b)


def sw_f(dd, endog, excl):
    X, Z, g = resid(dd, endog), resid(dd, excl), dd.market_ids.to_numpy()
    k, L = len(endog), len(excl)
    out = {}
    for j, name in enumerate(endog):
        x = X[:, j]
        Xo = np.delete(X, j, axis=1)
        Pz = Z @ np.linalg.lstsq(Z, Xo, rcond=None)[0]
        x = x - Xo @ np.linalg.lstsq(Pz, x, rcond=None)[0]
        out[name] = cl_wald(x, Z, g) / (L - k + 1)
    return out


def fit_demand(d):
    dd = d.drop(columns=[c for c in d.columns if c.startswith('demand_instruments')]).reset_index(drop=True)
    dd['demand_instruments0'] = dd.Z.to_numpy(float)
    dd['demand_instruments1'] = dd.Z.to_numpy(float) * dd.gene_idx
    dd['px'] = dd.prices * dd.gene_idx
    res = pyblp.Problem(pyblp.Formulation(' + '.join(['prices', 'I(prices*gene_idx)'] + CONTROLS),
                                          absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')
    f = sw_f(dd, ['prices', 'px'], ['demand_instruments0', 'demand_instruments1'])
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    se = dict(zip(res.beta_labels, res.beta_se.flatten()))
    kx = next(k for k in b if 'gene_idx' in k)
    E = res.compute_elasticities()
    own = res.extract_diagonals(E).flatten()
    out = dict(N=len(dd), funds=dd.product_ids.nunique(), alpha=b['prices'], se_alpha=se['prices'], alpha_x=b[kx], se_alpha_x=se[kx],
               cheap_total=b['prices'] + b[kx], share_cheap=float(dd.gene_idx.mean()), F_price=f['prices'], F_px=f['px'],
               min_F=min(f.values()), share_pos_e=float((own > 0).mean()), avg_e=float(res.extract_diagonal_means(E).mean()))
    out.update({f'b_{c}': b[c] for c in CONTROLS})
    out.update({f'se_{c}': se[c] for c in CONTROLS})
    return out, res, dd


def lead_tests(dd, res):
    """Regress xi_{j,t} on Z_{j,t+k} (residualized on controls and FE), fund-demeaned; t-stat clustered by month."""
    dd = dd.assign(xi=res.xi.flatten())
    dd['zt'] = resid(dd, ['Z'])[:, 0]
    out = {}
    for k in (12, 24, 36):
        lag = dd[['product_ids', 'month_key', 'xi']].assign(month_key=dd.month_key + k)
        m = dd[['product_ids', 'month_key', 'zt', 'market_ids']].merge(lag, on=['product_ids', 'month_key'])
        y = (m.xi - m.groupby('product_ids').xi.transform('mean')).to_numpy()
        x = (m.zt - m.groupby('product_ids').zt.transform('mean')).to_numpy()
        b = (x @ y) / (x @ x)
        u = y - b * x
        se = np.sqrt(((pd.Series(x * u).groupby(m.market_ids.to_numpy()).sum()) ** 2).sum()) / (x @ x)
        out[f'lead{k}_t'] = float(b / se)
    return out


BIG3 = ('BlackRock', 'Vanguard', 'State Street Global Advisors')


def table5(res, dd, d_all):
    """Own elasticity, in its last market, of the top 5 funds by AUM in the last month for each Big 3 firm (Table 5)."""
    last = d_all[d_all.month_t == d_all.month_t.max()]
    top = last[last.firm_ids.isin(BIG3)].sort_values(['firm_ids', 'product_mtna'], ascending=[True, False]).groupby('firm_ids').head(5)
    rows = []
    for _, f in top[top.product_ids.isin(dd.product_ids)].iterrows():
        obs = dd[dd.product_ids == f.product_ids].sort_values('month_t').iloc[-1]
        in_mkt = dd[dd.market_ids == obs.market_ids].reset_index(drop=True)
        pos = int(np.flatnonzero(in_mkt.product_ids.to_numpy() == f.product_ids)[0])
        e = res.compute_elasticities(market_id=obs.market_ids)[pos, pos]
        rows.append(dict(firm=f.firm_ids, product_ids=f.product_ids, name=f.product_fund_name, month_t=obs.month_t,
                         price=obs.prices, share=obs.shares, cheap=obs.gene_idx, own_elasticity=e))
    return pd.DataFrame(rows)


# =====================================================================================================================
# 7. Supply side on all Table 2 rows except money market funds
#    markups from the logit FOC with ownership by firm_ids and profit weight kappa among the Big 3;
#    MC = p + eta log(TNA) - markup; eta by 2SLS (rotator) under each conduct candidate; pyRVtest conduct test.
# =====================================================================================================================
CONDUCT = {'PC': None, 'B0': 0.0, 'B25': 0.25, 'B50': 0.50, 'B65': 0.65}
CONDUCT_IV = {
    'main: rival2 x csent_index': '0 + BLP_IV_rival_funds2*Conduct_IV_csent_index_resid',
    'rival2 x bab_usa': '0 + BLP_IV_rival_funds2*Conduct_IV_bab_usa_resid',
    'rival2 x fmax': '0 + BLP_IV_rival_funds2*Conduct_IV_fmax_resid',
    'rival2 x rotator': '0 + BLP_IV_rival_funds2*rotator',
    'rival2 x csent_income3': '0 + BLP_IV_rival_funds2*Conduct_IV_csent_income3_resid',
    'rival3 x csent_index': '0 + BLP_IV_rival_funds3*Conduct_IV_csent_index_resid',
}


def markups(d, alpha, kappa):
    mu = np.zeros(len(d))
    if kappa is None:
        return mu
    for _, idx in d.groupby('market_ids').indices.items():
        s, a, f = d.shares.to_numpy()[idx], alpha[idx], d.firm_ids.to_numpy()[idx]
        J = -np.outer(s, s) * a[None, :]          # J[j,k] = ds_j/dp_k = -alpha_k s_j s_k, j != k
        J[np.diag_indices_from(J)] = a * s * (1 - s)
        same = f[:, None] == f[None, :]
        big = np.isin(f, BIG3)
        Om = np.where(same, 1.0, np.where(big[:, None] & big[None, :], kappa, 0.0))
        mu[idx] = -np.linalg.solve(Om * J.T, s)
    return mu


def winsor_by_year(x, year, lo=0.01, hi=0.99):
    x = pd.Series(x)
    q = x.groupby(year).quantile([lo, hi]).unstack()
    return x.clip(year.map(q[lo]).to_numpy(), year.map(q[hi]).to_numpy()).to_numpy()


def scale_iv(d, mc):
    """2SLS: MC (winsorized 1/99 within calendar year) on log AUM (instrument: rotator), |TE|, log age; fund + month FE;
    SE clustered by month (CR1, fixest-style small-sample factor). eta = -coefficient on log AUM."""
    y = winsor_by_year(mc, np.floor(d.month_t).reset_index(drop=True))
    X = np.column_stack([np.log(d.product_mtna.to_numpy()), d.product_tracking_err.to_numpy(), d.log_product_fund_age.to_numpy()])
    Z = np.column_stack([d.rotator.to_numpy(), X[:, 1:]])
    ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    yt, Xt, Zt = alg.residualize(y[:, None])[:, 0], alg.residualize(X), alg.residualize(Z)
    Pz = Zt @ np.linalg.lstsq(Zt, Xt, rcond=None)[0]
    b = np.linalg.lstsq(Pz, yt, rcond=None)[0]
    u = yt - Xt @ b
    A = np.linalg.inv(Pz.T @ Pz)
    g = d.market_ids.to_numpy()
    sc = pd.DataFrame(Pz * u[:, None]).groupby(g).sum().to_numpy()
    G, n = len(np.unique(g)), len(y)
    k = X.shape[1] + d.product_ids.nunique()
    V = A @ (sc.T @ sc) @ A * (G / (G - 1)) * ((n - 1) / (n - k))
    se = float(np.sqrt(V[0, 0]))
    return dict(eta=float(-b[0]), eta_se=se, eta_p=float(2 * stats.t.sf(abs(b[0] / se), G - 1)))


def neg_stats(d, mc):
    neg = pd.Series(mc < 0, index=d.index)
    return dict(neg_share=float(neg.groupby(d.market_ids).mean().mean()), neg_share_pooled=float(neg.mean()),
                share_below_m010=float((mc < -0.10).mean()), share_below_m020=float((mc < -0.20).mean()),
                share_below_m030=float((mc < -0.30).mean()), share_below_m060=float((mc < -0.60).mean()),
                mc_p1=float(np.percentile(mc, 1)), mc_min=float(mc.min()), mc_mean=float(mc.mean()))


def kappa_fn(k):
    return lambda f, g: 1.0 if f == g else (k if (f in BIG3 and g in BIG3) else 0.0)


def conduct_test(d, mus, etas):
    import pyRVtest
    names = list(CONDUCT)
    forms = [pyRVtest.ModelFormulation(model_downstream='perfect_competition', ownership_downstream='firm_ids')] + \
            [pyRVtest.ModelFormulation(model_downstream='bertrand', ownership_downstream='firm_ids',
                                       kappa_specification_downstream=kappa_fn(CONDUCT[m])) for m in names[1:]]
    with contextlib.redirect_stdout(io.StringIO()):
        prob = pyRVtest.Problem(
            cost_formulation=pyRVtest.Formulation('0 + log_product_fund_age + product_tracking_err + product_past_1yr_ret',
                                                  absorb='C(product_ids) + C(market_ids)'),
            instrument_formulation=tuple(pyRVtest.Formulation(f) for f in CONDUCT_IV.values()),
            model_formulations=tuple(forms), product_data=d.copy(), demand_results=None)
        logq = np.log(d.product_mtna.to_numpy())
        prob.markups = [(mus[m] - etas[m] * logq).reshape(-1, 1) for m in names]   # MC_m = p - mu_m + eta_m log TNA
        res = prob.solve(demand_adjustment=False, clustering_adjustment=True)
    rows = []
    for l, ivname in enumerate(CONDUCT_IV):
        p, T, F = np.asarray(res.MCS_pvalues[l]).flatten(), np.asarray(res.TRV[l]), np.asarray(res.F[l])
        for i, m in enumerate(names):
            rows.append(dict(iv_set=ivname, candidate=m, mcs_p=float(p[i]), selected=bool(p[i] >= 0.05),
                             **{f'TRV_vs_{n}': float(T[i, j]) for j, n in enumerate(names)},
                             **{f'F_vs_{n}': float(F[i, j]) for j, n in enumerate(names)}))
    return pd.DataFrame(rows)


# =====================================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--index-csv', default='nonLev_funds_product_month_level_v2_patched.csv')
    ap.add_argument('--crsp', default='CRSP_fund_summary_2026_qtrly_combined.csv')
    ap.add_argument('--donor-mmf', choices=['all', 'sample'], default='all')
    ap.add_argument('--no-conduct', action='store_true')
    ap.add_argument('--out', default='V2')
    a = ap.parse_args()
    pd.set_option('display.width', 220, 'display.max_columns', 30, 'display.max_colwidth', 60)

    d_all = load_sample(a.index_csv)
    log(f'Table 2 Panel A sample: {len(d_all):,} fund-months (expected 108,300)')
    raw_all = pd.read_csv(a.index_csv, usecols=['product_j', 'month_t', 'product_exp_ratio', 'product_fund_name']).dropna(subset=['product_exp_ratio'])
    crsp = pd.read_csv(a.crsp, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    mmf = money_market_funds(crsp, set(raw_all.product_j))
    mmf_sample = sorted(set(mmf) & set(d_all.product_ids))
    (raw_all[raw_all.product_j.isin(mmf)].groupby('product_j')
     .agg(fund_months_in_csv=('month_t', 'size'), name=('product_fund_name', 'last'))
     .assign(in_table2=lambda x: x.index.isin(mmf_sample)).to_csv(f'{a.out}_money_market_funds.csv'))
    log(f'money market funds: {len(mmf)} in the index CSV, {len(mmf_sample)} in the Table 2 sample {mmf_sample} '
        f'({d_all.product_ids.isin(mmf_sample).sum()} fund-months)')
    drop = mmf if a.donor_mmf == 'all' else mmf_sample

    cheap = gene_idx(raw_all)
    raw = build_instrument(a.index_csv, a.crsp, drop)
    log(f'instrument built on {len(raw):,} donor-pool rows')
    d = d_all[~d_all.product_ids.isin(mmf_sample)].reset_index(drop=True)
    d = d.join(cheap, on='product_ids')
    d = d.merge(raw[['product_j', 'month_t', 'Z', 'asset_class', 'share_class']].rename(columns={'product_j': 'product_ids'}),
                on=['product_ids', 'month_t'], how='left')
    d['why'] = why_no_z(d, raw)
    d[['product_ids', 'month_t', 'firm_f_old', 'asset_class', 'share_class', 'gene_idx', 'Z']].to_csv(f'{a.out}_Z.csv', index=False)
    why = d.groupby('why').agg(fund_months=('product_ids', 'size'), funds=('product_ids', 'nunique'),
                              share_cheap=('gene_idx', 'mean'), mean_fee=('prices', 'mean'))
    why.to_csv(f'{a.out}_rows_without_Z.csv')
    log(f'supply rows (Table 2 minus money market funds): {len(d):,}; demand rows (Z defined): {d.Z.notna().sum():,}\n{why}')

    # ---------------- demand
    est = d[d.Z.notna()].reset_index(drop=True)
    o, res, dd = fit_demand(est)
    o.update(lead_tests(dd, res))
    t5 = table5(res, dd, d_all)
    o['table5_abs_e_gt1'] = f'{int((t5.own_elasticity.abs() > 1).sum())}/{len(t5)}'
    o['donor_mmf'] = a.donor_mmf
    pd.DataFrame([o]).to_csv(f'{a.out}_demand.csv', index=False)
    t5.to_csv(f'{a.out}_table5.csv', index=False)
    log(f"demand: N {o['N']:,} | alpha {o['alpha']:.3f} ({o['se_alpha']:.3f}) | alpha_x {o['alpha_x']:.3f} ({o['se_alpha_x']:.3f}) "
        f"| cheap total {o['cheap_total']:.2f} | min F {o['min_F']:.1f} | avg e {o['avg_e']:.2f} | share e>0 {o['share_pos_e']:.4f} "
        f"| Table 5 |e|>1 {o['table5_abs_e_gt1']} | leads t {o['lead12_t']:.2f} / {o['lead24_t']:.2f} / {o['lead36_t']:.2f}")
    print(t5.round(3).to_string(index=False), flush=True)

    # ---------------- supply side: all Table 2 rows except money market funds
    p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
    alpha = o['alpha'] + o['alpha_x'] * d.gene_idx.to_numpy()
    mus = {m: markups(d, alpha, k) for m, k in CONDUCT.items()}
    scale = {m: scale_iv(d, p - mus[m]) for m in CONDUCT}
    pd.DataFrame([dict(candidate=m, **scale[m]) for m in CONDUCT]).to_csv(f'{a.out}_scale.csv', index=False)
    nm = d.product_fund_name.fillna('').str.lower()
    groups = {'firm': np.where(d.firm_ids.isin(BIG3), d.firm_ids, 'other firms'),
              'SPY': d.product_fund_name.fillna('').str.startswith('SPDR S&P 500 ETF Trust'),
              'cheap': d.gene_idx, 'asset_class': d.asset_class.fillna('no Z / no class'),
              'size': np.select([nm.str.contains('small|micro'), nm.str.contains('mid')], ['small/micro', 'mid'], 'other')}
    mcs, wh = [], []
    for m in CONDUCT:
        mc = p + scale[m]['eta'] * logq - mus[m]
        mcs.append(dict(candidate=m, eta=scale[m]['eta'], mean_markup=float(mus[m].mean()), share_neg_markup=float((mus[m] < 0).mean()),
                        **neg_stats(d, mc)))
        neg = mc < 0
        for gname, gv in groups.items():
            for g, idx in pd.Series(np.arange(len(d))).groupby(np.asarray(gv)).groups.items():
                idx = np.asarray(idx)
                wh.append(dict(candidate=m, group_by=gname, group=str(g), fund_months=len(idx), share_neg=float(neg[idx].mean()),
                               share_of_all_neg=float(neg[idx].sum() / neg.sum()) if neg.sum() else np.nan))
    pd.DataFrame(mcs).to_csv(f'{a.out}_mc.csv', index=False)
    pd.DataFrame(wh).to_csv(f'{a.out}_where.csv', index=False)
    log('scale and marginal costs (MC at each candidate\'s own eta):')
    print(pd.DataFrame(mcs).round(4).to_string(index=False), flush=True)

    if a.no_conduct:
        return
    year = pd.Series(np.floor(d.month_t))
    capped = {m: winsor_by_year(mus[m], year) if CONDUCT[m] is not None else mus[m] for m in CONDUCT}
    runs = [('A: eta 0.024', mus, {m: 0.024 for m in CONDUCT}),
            ('B: own eta', mus, {m: scale[m]['eta'] for m in CONDUCT}),
            ('C: PC eta', mus, {m: scale['PC']['eta'] for m in CONDUCT}),
            ('A capped 1/99 by year', capped, {m: 0.024 for m in CONDUCT}),
            ('C capped 1/99 by year', capped, {m: scale['PC']['eta'] for m in CONDUCT})]
    out = []
    for name, mu, etas in runs:
        cd = conduct_test(d, mu, etas).assign(eta_scheme=name)
        out.append(cd)
        pd.concat(out).to_csv(f'{a.out}_conduct.csv', index=False)
        log(f'conduct [{name}] ' + ' | '.join(f'{iv.split(":")[0]}: {cd[(cd.iv_set == iv) & cd.selected].candidate.tolist()}'
                                              for iv in CONDUCT_IV))
    log('done')


if __name__ == '__main__':
    main()
