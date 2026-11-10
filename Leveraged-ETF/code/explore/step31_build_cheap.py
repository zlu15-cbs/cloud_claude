"""Build the four cheap indicators of the demand grid (PLAN_demand_grid.md models 1-4) and check them against Danny's
page-3 counts on the 108,300-row Table 2 Panel A sample:
    model 3, CRSP founded_1y_p20: 80,799 cheap observations;  model 4, index founded_1y_p20: 59,094.
Writes step31_cheap_by_fund.csv (product_ids, gene_idx, gene_crsp, danny_crsp, danny_idx and flags).

    python step31_build_cheap.py      # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd

import common
import tiers_crsp as tc
from tiers import raw_entry_tiers

d = common.load('index')
print(f'Table 2 sample {len(d):,} rows, {d.product_ids.nunique():,} funds', flush=True)

# model 1: benchmark (raw index file)
ent = raw_entry_tiers((0.20,))
# model 2: benchmark rule, all-CRSP reference
g2 = tc.gene_crsp(ent[['month_t', 'product_exp_ratio']], 0.20)
# models 3-4: Danny founded_1y_p20
d3 = tc.danny_founded(1, 20, None)
uni = tc.index_universe()
d4 = tc.danny_founded(1, 20, uni)

f = pd.DataFrame(index=pd.Index(sorted(d.product_ids.unique()), name='product_ids'))
f['gene_idx'] = ent.raw20.reindex(f.index)
f['gene_crsp'] = g2.cheap.reindex(f.index)
f['gene_crsp_nref'] = g2.n_ref.reindex(f.index)
for tag, o in (('danny_crsp', d3), ('danny_idx', d4)):
    f[tag] = o.cheap.reindex(f.index)
    f[f'{tag}_nofee'] = o.flag_missing_fee.reindex(f.index)
    f[f'{tag}_noref'] = o.flag_empty_ref.reindex(f.index)
    f[f'{tag}_nref'] = o.n_ref.reindex(f.index)
print('funds without a CRSP founding date (not in class table):', int(f.danny_crsp.isna().sum()), flush=True)
f.to_csv('step31_cheap_by_fund.csv')

obs = d[['product_ids']].join(f, on='product_ids')
target = {'danny_crsp': 80799, 'danny_idx': 59094}
for c in ('gene_idx', 'gene_crsp', 'danny_crsp', 'danny_idx'):
    n = int((obs[c] == 1).sum())
    print(f'{c:11s} cheap obs {n:7,} ({n / len(obs):.3f}) | cheap funds {int((f[c] == 1).sum()):5,} of {len(f):,} | missing {int(obs[c].isna().sum()):,}'
          + (f' | Danny target {target[c]:,} -> diff {n - target[c]:+,}' if c in target else ''), flush=True)
for c in ('danny_crsp', 'danny_idx'):
    print(f'{c}: obs coded not cheap for missing fee {int((obs[c + "_nofee"] == 1).sum()):,}, for empty reference {int((obs[c + "_noref"] == 1).sum()):,}', flush=True)
print('agreement (fund level):')
print(f[['gene_idx', 'gene_crsp', 'danny_crsp', 'danny_idx']].corr().round(3).to_string(), flush=True)
