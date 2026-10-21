"""Step 1: reproduce Table 5 Panel A's "Elasticity" column.

Port of code/R_table5/Get_passive_index_elasticities.txt: funds are the top 5 by product_mtna in the last month for
BlackRock, Vanguard and State Street Global Advisors; the elasticity is the own elasticity in the last market in which
the fund appears (R: tail(.SD, 1) after sorting by month). Bertrand markups (levels, as pyRVtest reports them and the R
averages) are computed for single-firm Bertrand ownership.

    python step1_table5_elasticity.py logit|blp1|blp3 [PROCESSES]

logit: notebook cells 6-8 (logit IV). blp1 / blp3: notebook formulations (cells 12 / 23-24) evaluated at the paper's
published sigma with pyblp's 'return' optimization (no re-optimization).
"""
import sys
import time

import numpy as np
import pandas as pd
import pyblp

import common

PAPER = {  # Table 5 Panel A, from EXPECTED_RESULTS.md
    'Vanguard Total Stock Market Index Fund': -0.160, 'Vanguard 500 Index Fund (MF)': -0.323,
    'Vanguard 500 Index Fund (ETF)': -0.243, 'Vanguard Total Stock Market (MF)': -0.244,
    'Vanguard Total Stock Market (ETF)': -0.326, 'SPDR S&P 500 ETF Trust': -0.725, 'SPDR Gold Shares': -3.325,
    'Technology Select Sector SPDR': -0.665, 'Financial Select Sector SPDR': -0.666,
    'SPDR Portfolio S&P 500 ETF': -0.167, 'iShares Core S&P 500 ETF': -0.242, 'iShares Core MSCI EAFE ETF': -0.580,
    'iShares Core US Aggregate Bond ETF': -0.249, 'iShares Russell 1000 Growth ETF': -1.494,
    'iShares Core S&P Mid-Cap ETF': -0.415,
}
BIG3 = ['BlackRock', 'Vanguard', 'State Street Global Advisors']
X1 = '0 + prices + product_tracking_err + product_past_1yr_ret + log_product_fund_age'
ABSORB = 'C(product_ids) + C(market_ids)'


def top15(d):
    last = d[d.month_t == d.month_t.max()]
    top = last[last.firm_ids.isin(BIG3)].sort_values(['firm_ids', 'product_mtna'], ascending=[True, False])
    return top.groupby('firm_ids').head(5)[['firm_ids', 'product_ids', 'product_fund_name', 'product_mtna']]


def own_last_market(results, d, funds):
    """Own elasticity of each fund in the last market in which it appears, plus p, s and the implied loading."""
    rows = []
    for _, f in funds.iterrows():
        obs = d[d.product_ids == f.product_ids].sort_values('month_t').iloc[-1]
        mid = obs.market_ids
        in_mkt = d[d.market_ids == mid].reset_index(drop=True)
        pos = int(np.flatnonzero(in_mkt.product_ids.to_numpy() == f.product_ids)[0])
        e = results.compute_elasticities(market_id=mid)[pos, pos]
        p, s = obs.prices, obs.shares
        rows.append(dict(firm=f.firm_ids, product_ids=f.product_ids, name=f.product_fund_name, aum=f.product_mtna,
                         month_t=obs.month_t, p=p, s=s, e=e, loading=e / (p * (1 - s)), loading_for_e1=-1 / (p * (1 - s))))
    return pd.DataFrame(rows)


def main(model, procs):
    cells = {'logit': [2, 3, 4], 'blp1': [2, 3, 4, 12], 'blp3': [2, 3, 4, 12, 23]}[model]
    d = common.run_cells('index', cells)['product_data'].reset_index(drop=True)
    funds = top15(d)
    t = time.time()
    if model == 'logit':
        res = pyblp.Problem(pyblp.Formulation(X1.replace('0 + ', ''), absorb=ABSORB), d).solve(se_type='clustered')
    else:
        x2 = '0 + prices' if model == 'blp1' else '0 + prices + log_product_fund_age + product_past_1yr_ret'
        # paper's published sigma (Table 2 Panel A cols 3 and 4); X2 order: prices, age, past return
        sigma = np.array([[0.027]]) if model == 'blp1' else np.diag([-0.008, 0.001, -0.009])
        integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
        with pyblp.parallel(procs):
            problem = pyblp.Problem((pyblp.Formulation(X1, absorb=ABSORB), pyblp.Formulation(x2)), d, integration=integ)
            res = problem.solve(sigma, optimization=pyblp.Optimization('return'), se_type='clustered')
    print(res)
    print(f'solve time {time.time() - t:.0f}s')
    out = own_last_market(res, d, funds)
    # Bertrand (single-firm ownership) markups in levels and Lerner, sample mean per fund (as the R averages margins)
    costs = res.compute_costs()
    d['bt_markup_level'] = d.prices.to_numpy() - costs.flatten()
    d['bt_lerner'] = d['bt_markup_level'] / d.prices
    m = d.groupby('product_ids')[['bt_markup_level', 'bt_lerner']].mean()
    out = out.join(m, on='product_ids')
    pd.set_option('display.width', 250, 'display.max_columns', 30, 'display.max_colwidth', 45)
    print(out.round(4).to_string(index=False))
    print('share of all fund-months with negative implied marginal cost (Bertrand):', round(float((costs < 0).mean()), 4))
    out.to_csv(f'step1_{model}.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
