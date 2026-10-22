"""Two-group fee interaction with tiers set at each fund's first month in the FULL raw data (logit IV).

For every month of the raw index CSV (1994-2025), compute the q-th percentile of expense ratios across all index
funds with a recorded fee that month. A fund is 'cheap' if its expense ratio in its first raw month with a recorded fee
is at or below that month's cutoff (ties count as cheap). Then estimate the Table 2 col (2) logit IV with
price + price x cheap on the Table 2 Panel A sample, instruments Hausman IV and Hausman IV x cheap.

    python step2g_raw_entry_tiers.py     # run from a folder holding the index CSV; writes step2g_raw_entry_tiers.csv
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import build, first_stage_f

pyblp.options.verbose = False
QS = (0.10, 0.20, 0.30, 0.40, 0.50)

raw = pd.read_csv('nonLev_funds_product_month_level_v2_patched.csv',
                  usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
cut = raw.groupby('month_t').product_exp_ratio.quantile(list(QS)).unstack()  # month x q
entry = raw.sort_values('month_t').groupby('product_j').first()             # first raw month with a fee
for q in QS:
    entry[f'cheap{int(q * 100)}'] = (entry.product_exp_ratio <= entry.month_t.map(cut[q]) + 1e-9).astype(float)

d = common.load('index')
funds = top15(d)
e_in = entry.reindex(d.product_ids.unique())
print(f'sample funds: {len(e_in)}; first raw month before 2010: {(e_in.month_t < 2010).mean():.0%}; '
      f'median first raw month {e_in.month_t.median():.1f}')
print('cutoffs in Jan 2000 / Jan 2010 / Aug 2024:',
      {q: [round(cut.loc[m, q], 3) for m in (2000.0, 2010.0, 2024 + 7 / 12) if m in cut.index] for q in QS})

rows = []
for q in QS:
    col = f'cheap{int(q * 100)}'
    d['cheap'] = d.product_ids.map(entry[col]).astype(float)
    dd, formula, endog, excl, exog = build(d, dict(tier='A', z=['cheap']))
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
        se_type='clustered')
    f = first_stage_f(dd, endog, excl, exog)
    e = res.extract_diagonals(res.compute_elasticities()).flatten()
    mc = res.compute_costs().flatten()
    last = dd.assign(e=e).sort_values('month_t').groupby('product_ids').last().loc[funds.product_ids]
    b, s = res.beta.flatten(), res.beta_se.flatten()
    rows.append(dict(percentile=int(q * 100), share_funds_cheap=float(d.groupby('product_ids').cheap.first().mean()),
                     share_obs_cheap=float(d.cheap.mean()), b_rest=b[0], se_rest=s[0], b_cheap_total=b[0] + b[1],
                     b_interaction=b[1], se_interaction=s[1], min_F=min(f.values()),
                     n15_cheap=int(last.cheap.sum()), n15_gt1=int((last.e.abs() > 1).sum()),
                     avg_own_e=float(res.extract_diagonal_means(res.compute_elasticities()).flatten().mean()),
                     share_gt1=float((np.abs(e) > 1).mean()), share_neg_mc=float((mc < 0).mean())))
    print(rows[-1], flush=True)
    print('   15 funds, last-market e:', dict(zip(last.product_fund_name.str.split(': ').str[-1].str[:22],
                                                 last.e.round(2))), flush=True)
out = pd.DataFrame(rows)
print(out.round(3).to_string(index=False))
out.to_csv('step2g_raw_entry_tiers.csv', index=False)
