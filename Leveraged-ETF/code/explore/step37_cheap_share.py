"""Is it the rule, the reference universe, or the size of the cheap group? Re-tune each cheap definition's percentile so
that the cheap share matches gene_idx (0.473 of the grid fund-months), then re-estimate Z_flag x I on the grid rows.
  danny_crsp / danny_idx: Danny's founded_1y rule, all-CRSP / index-universe reference, q in QD
  gene_crsp:              the benchmark rule with the all-CRSP reference, q in QG
Picks, per definition, the q whose grid cheap share is closest to gene_idx's; also reports every q (demand at each).
    python step37_cheap_share.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step37_share.csv, step37_demand.csv.
"""
import pandas as pd

import common
import ivbuild
import tiers_crsp as tc
from new_iv import load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables
from step32_demand_grid import cheap, run
from tiers import raw_entry_tiers

QD = [3, 5, 7, 10, 12, 15, 20]
QG = [1, 2, 3, 4, 5, 7, 10, 20]

d = add_variables(common.load('index'))
funds = top15(d)
d = d.join(cheap[['gene_idx']], on='product_ids')
d = d.merge(ivbuild.build()[['product_ids', 'month_t', 'Z_flag']], on=['product_ids', 'month_t'], how='left')
grid = load_new_iv_sample()[['product_ids', 'month_t']].assign(grid=1)
d = d.merge(grid, on=['product_ids', 'month_t'], how='left')
g = d[(d.grid == 1) & d.Z_flag.notna()].reset_index(drop=True)
target = g.gene_idx.mean()
print(f'grid rows {len(g):,}; gene_idx cheap share {target:.3f}', flush=True)

uni = tc.index_universe()
ent = raw_entry_tiers((0.20,))
cols = {}
for q in QD:
    cols[f'danny_crsp_q{q}'] = tc.danny_founded(1, q, None).cheap
    cols[f'danny_idx_q{q}'] = tc.danny_founded(1, q, uni).cheap
for q in QG:
    cols[f'gene_crsp_q{q}'] = tc.gene_crsp(ent[['month_t', 'product_exp_ratio']], q / 100).cheap
f = pd.DataFrame(cols)
g = g.join(f, on='product_ids')
for c in cols:
    g[c] = g[c].fillna(0)

share = pd.DataFrame([dict(indicator=c, family=c.rsplit('_q', 1)[0], q=int(c.rsplit('_q', 1)[1]), share=g[c].mean()) for c in cols])
share['gap'] = (share.share - target).abs()
share.to_csv('step37_share.csv', index=False)
print(share.round(3).to_string(index=False), flush=True)

out = []
for c in cols:
    o, _ = run(g, 'Z_flag', c, f'Z_flag x {c}', funds)
    o.update(indicator=c, share=float(g[c].mean()))
    out.append(o)
pd.DataFrame(out).drop(columns=['res', 'dd'], errors='ignore').to_csv('step37_demand.csv', index=False)
