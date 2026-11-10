"""Danny's benchmark (his clarification, 3 Nov 2026): cheap = founded_1y_p20, all-CRSP reference (danny_crsp); all 108,300
Table 2 Panel A fund-months; IV logit. Instruments: the paper's Hausman IV (his two PDFs) and his newer IV3_exp_ratio_med /
IV3_exp_ratio_vw (patch file; the 284 cases he is running). Also the no-interaction model with each instrument.
Also reports how the restriction to the 97,429 grid rows changes the outside share (Danny's concern).
    python step32c_danny_benchmark.py <patch csv>     # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step32c_danny_benchmark.csv, step32c_funds.csv.
"""
import sys

import numpy as np
import pandas as pd

import common
from new_iv import load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, H
from step32_demand_grid import cheap, run

patch = pd.read_csv(sys.argv[1])
patch['month_key'] = np.round(patch.month_t * 12).astype(int)
d0 = add_variables(common.load('index'))
funds = top15(d0)
d0 = d0.join(cheap, on='product_ids')
d0['Z_paper'] = d0[H]
d0 = d0.merge(patch[['product_j', 'month_key', 'IV3_exp_ratio_med', 'IV3_exp_ratio_vw']].rename(columns={'product_j': 'product_ids'}),
              on=['product_ids', 'month_key'], how='left')
print(f'rows {len(d0):,}; IV3_med defined {d0.IV3_exp_ratio_med.notna().sum():,}; no family id (firm_f_old) {d0.firm_f_old.isna().sum():,}', flush=True)

# outside share: full sample vs the 97,429 grid rows
g = load_new_iv_sample()
s0_full = 1 - d0.groupby('market_ids').shares.sum()
s0_grid = 1 - g.groupby('market_ids').shares.sum()
print(f'outside share, mean over months: all 108,300 rows {s0_full.mean():.4f}; grid rows {s0_grid.mean():.4f}; '
      f'max difference {(s0_grid - s0_full).max():.4f} (a month-level shift, absorbed by month FE in logit)', flush=True)

out, fr_all = [], []
for z in ('Z_paper', 'IV3_exp_ratio_med', 'IV3_exp_ratio_vw'):
    dd = d0[d0[z].notna()]
    for inter in (None, 'danny_crsp'):
        o, fr = run(dd, z, inter, f'DANNY {z} x {inter or "none"}', funds)
        out.append(o); fr_all.append(fr)
pd.DataFrame(out).to_csv('step32c_danny_benchmark.csv', index=False)
pd.concat(fr_all).to_csv('step32c_funds.csv', index=False)
