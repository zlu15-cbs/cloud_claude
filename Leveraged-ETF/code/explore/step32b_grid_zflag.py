"""Demand grid, third instrument: Z_flag (share class from CRSP inst/retail flags; new_iv.add_z_flag) x the 6 interactions.
Rows: the 97,429 grid rows where Z_flag is also defined (97,294; logs/step32b.log labels them "(97,279)" by mistake). Also re-runs Z x the 6 interactions on those rows,
so the keyword / flag comparison is on identical rows.
    python step32b_grid_zflag.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step32b_grid.csv, step32b_funds.csv.
"""
import pandas as pd

import common
from new_iv import add_z_flag, load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables
from step32_demand_grid import INTER, cheap, run

funds = top15(add_variables(common.load('index')))
d = add_z_flag(load_new_iv_sample().join(cheap, on='product_ids'))
d = d[d.Z_flag.notna()].reset_index(drop=True)
print(f'rows with Z_flag defined: {len(d):,}', flush=True)
grid, fr_all = [], []
for z in ('Z_flag', 'Z'):
    for inter in INTER:
        o, fr = run(d, z, inter, f'{z} x {inter or "none"} (Z_flag rows)', funds)
        grid.append(o); fr_all.append(fr)
pd.DataFrame(grid).to_csv('step32b_grid.csv', index=False)
pd.concat(fr_all).to_csv('step32b_funds.csv', index=False)
