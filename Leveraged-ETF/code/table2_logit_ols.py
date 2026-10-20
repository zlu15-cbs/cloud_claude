"""Table 2, column (1): logit OLS, for both panels.

Same sample, variables and fixed effects as column (2) (logit IV) in
main_Danny_Oct2026_{leveraged,index}_market.ipynb (cells 3, 4, 6-9), with OLS
instead of IV. Run from a folder holding the panel's CSV:

    python table2_logit_ols.py lev     # LETF_product_month_level_v4_patched.csv
    python table2_logit_ols.py index   # nonLev_funds_product_month_level_v2_patched.csv

Two routes, which should agree to numerical precision:
  A. pyblp logit with the price as its own instrument (exactly identified 2SLS = OLS),
     clustered SE; elasticities from pyblp.
  B. by hand: logit delta = log(s_jt) - log(1 - sum_j s_jt), absorb product and market
     FE with pyhdfe, OLS with statsmodels, SE clustered by market.
"""
import sys

import numpy as np
import pandas as pd
import pyblp
import pyhdfe
import statsmodels.api as sm

pyblp.options.digits = 5
pyblp.options.verbose = False

X_COLS = ['prices', 'product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']


def load_lev(path='LETF_product_month_level_v4_patched.csv'):
    # notebook cells 3-4
    d = pd.read_csv(path)
    d = d[d['market_m_bull_bear'] == 'Bull']
    d['market_ids'] = d.groupby(['month_t', 'market_m_bull_bear']).ngroup() + 1
    d['log_product_fund_age'] = np.log(d['product_fund_age'])
    d['product_tracking_err'] = abs(d['product_tracking_err'])
    d = d.dropna(subset=['BLP_IV_hausman_mgmt_fee'])
    d['clustering_ids'] = d.market_ids
    d = d.rename(columns={'product_exp_ratio': 'prices', 'market_share_m_bull_bear': 'shares_old',
                          'BLP_IV_hausman_exp_ratio': 'demand_instruments0',
                          'firm_f': 'firm_ids', 'product_ticker': 'product_ids'})
    d['shares'] = d['product_mtna'] / d['market_share_m_bull_bear_denom']
    d = d.loc[d['shares'] >= 0.0001]
    d = d.loc[d['month_t'] >= 2010]
    d = d[d['firm_ids'].isin(['ProShares', 'Direxion', 'ProFunds'])]
    return d


def load_index(path='nonLev_funds_product_month_level_v2_patched.csv'):
    # notebook cells 3-4
    d = pd.read_csv(path)
    d['market_ids'] = d.groupby(['month_t']).ngroup() + 1
    d['log_product_fund_age'] = np.log(d['product_fund_age'])
    d['product_tracking_err'] = abs(d['product_tracking_err'])
    d = d.dropna(subset=['Conduct_IV_csent_index_resid'])
    d['clustering_ids'] = d.market_ids
    d = d.rename(columns={'product_exp_ratio': 'prices', 'market_share': 'shares_old',
                          'BLP_IV_hausman_exp_ratio': 'demand_instruments0',
                          'firm_f': 'firm_ids', 'product_j': 'product_ids'})
    d['shares'] = d['product_mtna'] / d['market_share_m_denom_alt1']
    d = d.loc[d['shares'] >= 0.0001]
    d = d.loc[d['month_t'] >= 2010]
    d = d.loc[d['month_t'] <= (2024 + 8 / 12)]
    d = d[d['prefer'].isin([1, 2, 3, 4, 5])]
    d = d.loc[d['prices'] > 0]
    return d


def route_a(d):
    """pyblp, price instrumented by itself."""
    d = d.copy()
    d['demand_instruments0'] = d['prices']
    form = pyblp.Formulation(' + '.join(X_COLS), absorb='C(product_ids) + C(market_ids)')
    res = pyblp.Problem(form, d).solve(se_type='clustered')
    own = res.extract_diagonal_means(res.compute_elasticities()).flatten().mean()
    return res, own


def route_b(d):
    """pyhdfe + statsmodels, clustered by market."""
    d = d.reset_index(drop=True)
    inside = d.groupby('market_ids')['shares'].transform('sum')
    delta = np.log(d['shares']) - np.log(1 - inside)
    ids = np.column_stack([pd.factorize(d['product_ids'])[0], pd.factorize(d['market_ids'])[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)  # pyblp's absorb keeps singletons
    y = alg.residualize(delta.to_numpy()[:, None])
    X = alg.residualize(d[X_COLS].to_numpy())
    fit = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': d['market_ids'].to_numpy()})
    alpha = fit.params[0]
    own = (alpha * d['prices'] * (1 - d['shares'])).mean()
    return fit, own, len(d)


if __name__ == '__main__':
    panel = sys.argv[1]
    d = {'lev': load_lev, 'index': load_index}[panel]()
    print(f'panel={panel}  N={len(d)}  markets={d.market_ids.nunique()}  products={d.product_ids.nunique()}')
    res, own_a = route_a(d)
    print('\n--- Route A: pyblp, price as its own instrument ---')
    print(res)
    print('beta:', dict(zip(X_COLS, res.beta.flatten().round(4))))
    print('se  :', dict(zip(X_COLS, res.beta_se.flatten().round(4))))
    print('mean own-price elasticity (pyblp):', own_a)
    fit, own_b, n = route_b(d)
    print('\n--- Route B: pyhdfe + statsmodels OLS ---')
    print('beta:', dict(zip(X_COLS, fit.params.round(4))))
    print('se  :', dict(zip(X_COLS, fit.bse.round(4))))
    print('mean own-price elasticity (alpha*p*(1-s)):', own_b, ' N =', n)
