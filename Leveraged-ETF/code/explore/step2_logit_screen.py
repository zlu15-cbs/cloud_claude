"""Steps 2-3: logit IV screen of heterogeneous price loadings (index market, Table 2 Panel A sample).

Each spec is estimated with pyblp's logit (same X1 controls, fund and month FE, clustered by month, 2-step GMM as in
notebook cell 8), with the price terms extended. On top of pyblp: Sanderson-Windmeijer first-stage F (cluster-robust),
Hansen J when overidentified, elasticity summaries, Bertrand costs, and exogeneity diagnostics for tier C.

    python step2_logit_screen.py [SPEC ...]      # default: all specs; run from a folder holding the index CSV

Writes step2_summary.csv and step2_funds.csv in the working folder.
"""
import sys
import time

import numpy as np
import pandas as pd
import pyblp
import pyhdfe

import common
from step1_table5_elasticity import top15

pyblp.options.verbose = False
CONTROLS = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
H = 'demand_instruments0'  # BLP_IV_hausman_exp_ratio, renamed in notebook cell 4

# market_m_cluster is an index cluster (313 codes). Collapsed to asset classes by the indices and funds in each code
# (largest codes only; checked by listing their indices and largest funds):
ASSET_CLASS = {1: 'us_large_blend',                                  # SPX, MXWO, RIY: S&P 500 / total market
               5: 'us_other_equity', 6: 'us_other_equity', 7: 'us_other_equity', 10: 'us_other_equity',
               11: 'us_other_equity', 12: 'us_other_equity', 23: 'us_other_equity',  # small, growth, NDX, value, mid, dividend
               3: 'intl_equity', 9: 'intl_equity', 46: 'intl_equity',  # MXEA developed, MXEF emerging, Eurozone
               2: 'bond', 16: 'bond', 25: 'bond', 26: 'bond', 52: 'bond'}  # US agg, TIPS, short, intermediate, long
# everything else (target date 17, REIT 21, 296 small codes) -> 'other' (the base group)


def add_variables(d):
    d['broad'] = (d.broad_specialized == 'broad-based').astype(float)
    d['etf'] = d.ETF_ind.astype(float)
    d['big3'] = d.Big3.astype(float)
    for f, c in [('Vanguard', 'vanguard'), ('BlackRock', 'blackrock'), ('State Street Global Advisors', 'ssga')]:
        d[c] = (d.firm_ids == f).astype(float)
    ac = d.market_m_cluster.map(ASSET_CLASS).fillna('other')
    for c in ['us_large_blend', 'us_other_equity', 'intl_equity', 'bond']:
        d['ac_' + c] = (ac == c).astype(float)
    first = d.sort_values('month_t').groupby('product_ids').first()
    for var, name in [('prices', 'fee'), ('product_mtna', 'aum')]:
        x = first[var] if var == 'prices' else np.log(first[var])
        terc = pd.qcut(x.rank(method='first'), 3, labels=False)  # fund-level terciles at the fund's first month
        d[name + '_t1'] = d.product_ids.map(terc == 0).astype(float)  # lowest tercile
        d[name + '_t2'] = d.product_ids.map(terc == 1).astype(float)
    # C2: log-AUM tercile 12 months earlier, within that month's cross-section of sample funds
    d['month_key'] = np.round(d.month_t * 12).astype(int)
    lag = d[['product_ids', 'month_key', 'product_mtna']].copy()
    lag['lag_t'] = lag.groupby('month_key').product_mtna.transform(
        lambda x: pd.qcut(np.log(x).rank(method='first'), 3, labels=False))
    lag['month_key'] += 12
    d = d.merge(lag[['product_ids', 'month_key', 'lag_t']], on=['product_ids', 'month_key'], how='left')
    d['laum_t1'] = (d.lag_t == 0).astype(float)
    d['laum_t2'] = (d.lag_t == 1).astype(float)
    return d


def spec_list():
    """name -> dict(tier, z (interaction vars), form ('lin'|'log'|'sq'), c, controls (extra exog), sample)"""
    s = {'baseline': dict(tier='-', z=[])}
    s['A1_broad'] = dict(tier='A', z=['broad'])
    s['A2_etf'] = dict(tier='A', z=['etf'])
    s['A3_big3'] = dict(tier='A', z=['big3'])
    s['A3_firms'] = dict(tier='A', z=['vanguard', 'blackrock', 'ssga'])
    s['A4_asset_class'] = dict(tier='A', z=['ac_us_large_blend', 'ac_us_other_equity', 'ac_intl_equity', 'ac_bond'])
    s['A5_fee_tercile'] = dict(tier='A', z=['fee_t1', 'fee_t2'])
    s['A6_aum_tercile'] = dict(tier='A', z=['aum_t1', 'aum_t2'])
    s['A7_broad_fee'] = dict(tier='A', z=['broad', 'fee_t1', 'fee_t2'])
    s['A7_firms_fee'] = dict(tier='A', z=['vanguard', 'blackrock', 'ssga', 'fee_t1', 'fee_t2'])
    s['A7_broad_firms_fee'] = dict(tier='A', z=['broad', 'vanguard', 'blackrock', 'ssga', 'fee_t1', 'fee_t2'])
    for c in (0.01, 0.005, 0.02):
        s[f'B1_logp_c{c}'] = dict(tier='B', z=[], form='log', c=c)
    s['B2_p_sq'] = dict(tier='B', z=[], form='sq')
    s['C1_csent'] = dict(tier='C', z=['csent_index_resid'], controls=['csent_index_resid'])
    s['C1_vix'] = dict(tier='C', z=['chg_VIX_resid'], controls=['chg_VIX_resid'])
    s['C2_lag12_aum'] = dict(tier='C', z=['laum_t1', 'laum_t2'], controls=['laum_t1', 'laum_t2'], sample='lag12')
    s['C2_baseline_same_sample'] = dict(tier='C', z=[], sample='lag12')
    return s


def build(d, sp):
    """Return (data, X1 formula, endogenous columns, excluded instrument columns, exogenous columns)."""
    d = d.copy()
    form, z, c = sp.get('form', 'lin'), sp['z'], sp.get('c')
    exog = CONTROLS + sp.get('controls', [])
    if form == 'log':
        d['lp'] = np.log(d.prices + c)
        price_terms, endog, d[H] = [f'log(prices + {c})'], ['lp'], np.log(d[H] + c)
    elif form == 'sq':
        d['p2'] = d.prices ** 2
        d['demand_instruments1'] = d[H] ** 2
        price_terms, endog = ['prices', 'I(prices**2)'], ['prices', 'p2']
    else:
        price_terms, endog = ['prices'], ['prices']
    for k, v in enumerate(z, start=1):
        d['px_' + v] = d.prices * d[v]
        d[f'demand_instruments{k}'] = d[H] * d[v]
        price_terms.append(f'I(prices*{v})')
        endog.append('px_' + v)
    excl = [c for c in d.columns if c.startswith('demand_instruments')]
    formula = ' + '.join(price_terms + exog)
    return d, formula, endog, sorted(excl), exog


def cluster_wald(y, X, groups):
    """OLS of y on X (already residualized), cluster-robust Wald for all coefficients = 0."""
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    scores = pd.DataFrame(X * u[:, None]).groupby(groups).sum().to_numpy()
    V = XtX_inv @ (scores.T @ scores) @ XtX_inv
    return float(b @ np.linalg.solve(V, b))


def first_stage_f(d, endog, excl, exog):
    """Sanderson-Windmeijer F per endogenous term (equals the usual cluster-robust first-stage F with one)."""
    ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(d[exog].to_numpy(float))
    part = lambda M: M - W @ np.linalg.lstsq(W, M, rcond=None)[0]
    X = part(alg.residualize(d[endog].to_numpy(float)))
    Z = part(alg.residualize(d[excl].to_numpy(float)))
    g = d.market_ids.to_numpy()
    k, L = len(endog), len(excl)
    out = {}
    for j, name in enumerate(endog):
        x = X[:, j]
        if k > 1:
            Xo = np.delete(X, j, axis=1)
            Pz = Z @ np.linalg.lstsq(Z, Xo, rcond=None)[0]  # first-stage fitted other endogenous
            delta = np.linalg.lstsq(Pz, x, rcond=None)[0]   # 2SLS of x_j on the others
            x = x - Xo @ delta
        out[name] = cluster_wald(x, Z, g) / (L - k + 1)
    return out


def summarize(name, sp, d, res, funds, endog, f_stats, extra):
    e_mat = res.compute_elasticities()
    e = res.extract_diagonals(e_mat).flatten()
    avg = res.extract_diagonal_means(e_mat).flatten().mean()
    costs = res.compute_costs().flatten()  # Bertrand, ownership by firm_ids (multi-product firms)
    d = d.assign(e=e, mc=costs, mu=d.prices.to_numpy() - costs)
    row = dict(spec=name, tier=sp['tier'], N=len(d), avg_own_elasticity=avg,
               share_abs_e_gt1=(np.abs(e) > 1).mean(),
               share_abs_e_gt1_broad=(np.abs(d.e[d.broad == 1]) > 1).mean(),
               share_abs_e_gt1_big3=(np.abs(d.e[d.big3 == 1]) > 1).mean(),
               share_neg_mc_single_product=(d.prices - d.prices / np.abs(d.e) < 0).mean(),
               share_neg_mc_bertrand_firm=(d.mc < 0).mean(),
               objective=float(res.objective), **extra)
    for t, b, se in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
        row[f'b[{t}]'], row[f'se[{t}]'] = b, se
    for k, v in f_stats.items():
        row[f'F[{k}]'] = v
    fund_rows = []
    for _, f in funds.iterrows():
        g = d[d.product_ids == f.product_ids].sort_values('month_t')
        last = g.iloc[-1]
        fund_rows.append(dict(spec=name, product_ids=f.product_ids, name=f.product_fund_name, firm=f.firm_ids,
                              p_last=last.prices, e_last=last.e, e_mean=g.e.mean(),
                              lerner_single_last=1 / abs(last.e), mu_bertrand_firm_mean=g.mu.mean(),
                              mc_bertrand_firm_mean=g.mc.mean()))
    return row, fund_rows


def tier_c_diagnostics(d, z_cols, xi_col='xi_base'):
    """(i) within-fund corr(z, xi); (ii) lead test xi_{t-k} on z_t; (iv) within-fund AR(1) of xi."""
    out = {}
    dm = lambda s: s - s.groupby(d.product_ids).transform('mean')
    xi = d[xi_col]
    for z in z_cols:
        out[f'corr_within[{z}]'] = np.corrcoef(dm(d[z]), dm(xi))[0, 1]
    panel = d[['product_ids', 'month_key', xi_col] + z_cols].copy()
    for k in (1, 3, 12):
        lead = panel[['product_ids', 'month_key', xi_col]].rename(columns={xi_col: 'xi_lag'})
        lead['month_key'] += k  # xi from t-k, aligned to t
        m = panel.merge(lead, on=['product_ids', 'month_key'])
        y = (m.xi_lag - m.xi_lag.groupby(m.product_ids).transform('mean')).to_numpy()
        for z in z_cols:
            x = (m[z] - m[z].groupby(m.product_ids).transform('mean')).to_numpy()
            b = (x @ y) / (x @ x)
            u = y - b * x
            se = np.sqrt(((pd.Series(x * u).groupby(m.month_key.to_numpy()).sum()) ** 2).sum()) / (x @ x)
            out[f'lead{k}_t[{z}]'] = b / se
    m = panel.merge(panel[['product_ids', 'month_key', xi_col]].assign(month_key=lambda q: q.month_key + 1)
                    .rename(columns={xi_col: 'xi_l1'}), on=['product_ids', 'month_key'])
    a, b = dm_by(m, xi_col), dm_by(m, 'xi_l1')
    out['xi_AR1_within'] = float((a @ b) / (b @ b))
    return out


def dm_by(m, c):
    return (m[c] - m[c].groupby(m.product_ids).transform('mean')).to_numpy()


def main(names):
    t0 = time.time()
    d = add_variables(common.load('index'))
    funds = top15(d)
    specs = spec_list()
    names = names or list(specs)
    # baseline residual xi for tier C diagnostics (Table 2 col 2)
    bd, bform, *_ = build(d, specs['baseline'])
    base = pyblp.Problem(pyblp.Formulation(bform, absorb='C(product_ids) + C(market_ids)'), bd).solve(se_type='clustered')
    d['xi_base'] = base.xi.flatten()
    print(f'data ready, N={len(d)}, {time.time() - t0:.0f}s', flush=True)
    rows, fund_rows = [], []
    for name in names:
        sp = specs[name]
        t = time.time()
        dd = d[d.lag_t.notna()].reset_index(drop=True) if sp.get('sample') == 'lag12' else d
        dd, formula, endog, excl, exog = build(dd, sp)
        res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
            se_type='clustered')
        f_stats = first_stage_f(dd, endog, excl, exog)
        extra = {'L_excl': len(excl), 'K_endog': len(endog),
                 'hansen_J': float(res.objective) if len(excl) > len(endog) else np.nan}
        if sp['tier'] == 'C' and sp['z']:
            extra.update(tier_c_diagnostics(dd, sp['z']))
        row, fr = summarize(name, sp, dd, res, funds, endog, f_stats, extra)
        rows.append(row)
        fund_rows += fr
        print(f'\n=== {name}  ({time.time() - t:.0f}s)  formula: {formula}  excluded IVs: {excl}')
        print(res)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    pd.DataFrame(rows).to_csv('step2_summary.csv', index=False)
    pd.DataFrame(fund_rows).to_csv('step2_funds.csv', index=False)
    print(f'\ntotal {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main(sys.argv[1:])
