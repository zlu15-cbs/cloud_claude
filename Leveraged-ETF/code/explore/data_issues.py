"""List the data issues found during the replication, as CSV files for the data owner.

  data_issues_spy_fee.csv              SPY's recorded expense ratio by month (0.04% Oct 2022 - Sep 2023; actual 0.0945%)
  data_issues_broad_label_spx.csv      funds tracking the S&P 500 (market_m_index == 'SPX') with their broad_specialized label
  data_issues_broad_label_mixed.csv    tracked indices whose funds carry BOTH labels (broad-based and specialized)
  data_issues_no_family_id.csv         estimation-sample funds without firm_f_old (the Hausman IV's family id); fund-months
  data_issues_mgmt_fee_units.csv       product_mgmt_fee vs product_exp_ratio for the 15 Table 5 funds (mgmt fee is in bp)
The temporary fee episodes (fee changes >= 0.02 pp that revert to the exact prior fee within 12 months) are listed by
step8_raw20_robustness.py in step8_fee_reversals.csv.

    python data_issues.py        # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd

import common
from step1_table5_elasticity import top15
from tiers import RAW

raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'product_ticker', 'product_fund_name', 'market_m_index', 'broad_specialized',
                                'firm_f_old', 'firm_f', 'product_exp_ratio', 'product_mgmt_fee'])
spy = raw[raw.product_ticker == 'SPY'].sort_values('month_t')[['month_t', 'product_exp_ratio']]
spy.to_csv('data_issues_spy_fee.csv', index=False)
print('SPY months recorded at 0.04%:', spy[spy.product_exp_ratio.round(4) == 0.04].month_t.agg(['min', 'max', 'count']).to_dict())

d = common.load('index')
spx = d[d.market_m_index == 'SPX'].sort_values('month_t').groupby(['product_ids', 'broad_specialized']).agg(product_fund_name=('product_fund_name', 'last'), fund_months=('month_t', 'size')).reset_index()
spx.sort_values(['broad_specialized', 'fund_months'], ascending=[True, False]).to_csv('data_issues_broad_label_spx.csv', index=False)
print('S&P 500 fund-months labelled specialized:', round(float((d[d.market_m_index == 'SPX'].broad_specialized == 'specialized').mean()), 3))
lab = d.groupby('market_m_index').broad_specialized.agg(lambda s: s.nunique())
mixed = d[d.market_m_index.isin(lab[lab > 1].index)].groupby(['market_m_index', 'broad_specialized']).product_ids.nunique().unstack(fill_value=0)
mixed.to_csv('data_issues_broad_label_mixed.csv')
print('tracked indices whose funds carry both labels:', len(mixed))

nf = d[d.firm_f_old.isna()].sort_values('month_t').groupby('product_ids').agg(product_fund_name=('product_fund_name', 'last'), firm_ids=('firm_ids', 'last'), fund_months=('month_t', 'size')).reset_index()
nf.sort_values('fund_months', ascending=False).to_csv('data_issues_no_family_id.csv', index=False)
print(f'estimation-sample funds without firm_f_old: {len(nf)}; fund-months {int(nf.fund_months.sum()):,} ({nf.fund_months.sum() / len(d):.3f})')

f15 = top15(d)
m = d[d.product_ids.isin(f15.product_ids)].sort_values('month_t').groupby('product_ids').last()[['product_fund_name', 'prices', 'product_mgmt_fee']]
m['mgmt_fee_if_bp_in_pct'] = m.product_mgmt_fee / 100
m.to_csv('data_issues_mgmt_fee_units.csv')
print(m.round(3).to_string())
