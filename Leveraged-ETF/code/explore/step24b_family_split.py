"""Table 2 col 2 (logit IV, Hausman IV) on the fund-months WITH and WITHOUT a family id (firm_f_old), and what the
Hausman IV looks like on the rows without one.

    python step24b_family_split.py      # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step2_logit_screen import first_stage_f, CONTROLS, H
from tiers import RAW

pyblp.options.verbose = False
d = common.load('index')
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'firm_f_old', 'firm_f', 'market_m_index', 'product_exp_ratio'])
d['has_fam'] = d.firm_f_old.notna()
formula = 'prices + ' + ' + '.join(CONTROLS)
for lab, dd in (('all (Table 2 col 2)', d), ('with family id', d[d.has_fam]), ('without family id', d[~d.has_fam])):
    dd = dd.reset_index(drop=True)
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')
    f = first_stage_f(dd, ['prices'], ['demand_instruments0'], CONTROLS)
    avg = float(res.extract_diagonal_means(res.compute_elasticities()).flatten().mean())
    print(f'{lab:22s} N {len(dd):7,d} funds {dd.product_ids.nunique():5d} | price {res.beta[0, 0]:7.2f} ({res.beta_se[0, 0]:.2f}) | '
          f'first-stage F {f["prices"]:6.1f} | avg e {avg:6.2f}', flush=True)
# pooled, but with group-specific month FE (family / no family): removes cross-group identification
d['mkt_grp'] = d.market_ids.astype(str) + '_' + d.has_fam.astype(str)
for lab, absorb in (('pooled, common month FE', 'C(product_ids) + C(market_ids)'),
                    ('pooled, month FE x family-id group', 'C(product_ids) + C(mkt_grp)')):
    res = pyblp.Problem(pyblp.Formulation(formula, absorb=absorb), d).solve(se_type='clustered')
    print(f'{lab:36s} price {res.beta[0, 0]:7.2f} ({res.beta_se[0, 0]:.2f})', flush=True)
# trends of the two groups: month means of H, fee and delta
d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))
yr = d.assign(year=d.month_t.astype(int)).groupby(['year', 'has_fam'])[[H, 'prices', 'delta']].mean().unstack().round(3)
print(yr.iloc[::2].to_string())
n = d[~d.has_fam]
dm = lambda s, g: s - s.groupby(g).transform('mean')
print('\nrows without a family id:')
print(f'  funds {n.product_ids.nunique()}, fund-months {len(n):,}, share of fund-months by year: {n.month_t.astype(int).value_counts(normalize=True).sort_index().round(3).to_dict()}')
print(f'  corr(H, own fee) levels {np.corrcoef(n[H], n.prices)[0, 1]:.3f}; within fund {np.corrcoef(dm(n[H], n.product_ids), dm(n.prices, n.product_ids))[0, 1]:.3f}')
print(f'  share of rows with H == own fee: {float((n[H] - n.prices).abs().lt(1e-6).mean()):.3f}')
w = d[d.has_fam]
print(f'rows with a family id: corr(H, own fee) levels {np.corrcoef(w[H], w.prices)[0, 1]:.3f}; within fund '
      f'{np.corrcoef(dm(w[H], w.product_ids), dm(w.prices, w.product_ids))[0, 1]:.3f}; H == own fee {float((w[H] - w.prices).abs().lt(1e-6).mean()):.3f}')
# is H on the no-family rows equal to the AUM-weighted mean fee of OTHER funds tracking the same index (a 'rival' average)?
raw = raw[raw.product_exp_ratio.notna()]
g = raw.groupby(['market_m_index', 'month_t']).product_exp_ratio
tot, cnt = g.transform('sum'), g.transform('count')
raw['idx_loo_mean'] = (tot - raw.product_exp_ratio) / (cnt - 1)
m = n.merge(raw[['product_j', 'month_t', 'idx_loo_mean']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
ok = m.idx_loo_mean.notna()
print(f'  corr(H, mean fee of other funds tracking the same index) on these rows: {np.corrcoef(m[H][ok], m.idx_loo_mean[ok])[0, 1]:.3f}')
