"""Percentile of SPY's and VTI's expense ratio in each month's cross-section of index-fund expense ratios
(Table 2 Panel A estimation sample). Fees are rounded to 0.01 percent, so many funds tie: report the share of
funds with a strictly lower fee and the share with a fee at or below.

    python fee_percentiles_spy_vti.py      # writes fee_percentiles_spy_vti.csv
"""
import pandas as pd

import common

FUNDS = {'SPY': 27635, 'VTI': 31466}  # SPDR S&P 500 ETF Trust; Vanguard Total Stock Market Index Fund, ETF shares
d = common.load('index')
rows = []
for m, g in d.groupby('month_t'):
    row = {'month_t': m, 'n_funds': len(g), 'median_fee': g.prices.median()}
    for tk, pid in FUNDS.items():
        f = g[g.product_ids == pid]
        if f.empty:
            continue
        p = f.prices.iloc[0]
        row[f'{tk}_fee'] = p
        row[f'{tk}_pct_lower'] = (g.prices < p - 1e-12).mean() * 100
        row[f'{tk}_pct_at_or_below'] = (g.prices <= p + 1e-12).mean() * 100
    rows.append(row)
out = pd.DataFrame(rows)
out.to_csv('fee_percentiles_spy_vti.csv', index=False)
out['year'] = out.month_t.astype(int)
cols = [c for c in out.columns if c.startswith(('SPY', 'VTI'))] + ['median_fee', 'n_funds']
print(out.groupby('year')[cols].agg(['min', 'max']).round(2).to_string())
print('\nfirst and last month:')
print(out.iloc[[0, -1]].drop(columns='year').round(3).to_string(index=False))
