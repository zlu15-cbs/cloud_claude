"""Demand for downstream models 1-9 (step34 MODELS) with and without the 4 money market funds (step38 MMF) in the
estimation rows. Instruments as in step34 (built with all donors). Demand only (slopes, F, e>0, Table 5, leads).
    python step39_models_no_mmf.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step39_demand.csv.
"""
import pandas as pd

import common
import ivbuild
from new_iv import load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, H
from step32_demand_grid import cheap, run
from step34_downstream import MODELS

MMF = (17490, 17491, 62651, 10509)
d = add_variables(common.load('index')).join(cheap, on='product_ids')
funds = top15(d)
d['Z_paper'] = d[H]
d = d.merge(ivbuild.build(), on=['product_ids', 'month_t'], how='left')
grid = load_new_iv_sample()[['product_ids', 'month_t']].assign(grid=1)
d = d.merge(grid, on=['product_ids', 'month_t'], how='left').reset_index(drop=True)
d['grid'] = d.grid.fillna(0).astype(int)
out = []
for n, (label, z, inter, rows) in MODELS.items():
    est = d[d[z].notna() & ((d.grid == 1) if rows == 'grid' else True)]
    for tag, e in (('with MMF', est), ('no MMF', est[~est.product_ids.isin(MMF)])):
        o, _ = run(e.reset_index(drop=True), z, inter, f'm{n} {tag}', funds)
        o.update(model=n, label=label, mmf=tag)
        out.append(o)
pd.DataFrame(out).to_csv('step39_demand.csv', index=False)
