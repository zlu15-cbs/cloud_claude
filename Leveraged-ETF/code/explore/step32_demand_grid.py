"""Demand grid (PLAN_demand_grid.md): 6 price interactions x 2 instruments = 12 logit-IV models, index market.

Rows: the common 97,429 fund-months where the share-class instrument Z is defined (new_iv.load_new_iv_sample).
Model: delta = a p + a_x (p x I) + controls + fund FE + month FE; instruments z and z x I; SE clustered by month.
Interactions I: none | gene_idx (benchmark raw20) | gene_crsp | danny_crsp | danny_idx (founded_1y_p20) | broad.
Instruments z: Z (share-class Hausman, ours) | Z_paper (BLP_IV_hausman_exp_ratio).
Validation (paper IV, all 108,300 rows): none, danny_crsp, danny_idx, broad vs Danny's / the paper's published numbers.

Per model: slopes, SEs, SW F, share e > 0, average own elasticity, Table 5 elasticities, lead tests (k = 12, 24, 36).
    python step32_demand_grid.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step32_grid.csv, step32_funds.csv, step32_validation.csv.
"""
import numpy as np
import pandas as pd

import common
import ivtools
from new_iv import load_new_iv_sample
from step1_table5_elasticity import own_last_market, top15
from step2_logit_screen import add_variables, H

INTER = [None, 'gene_idx', 'gene_crsp', 'danny_crsp', 'danny_idx', 'broad']
IVS = ['Z', 'Z_paper']
cheap = pd.read_csv('step31_cheap_by_fund.csv', index_col='product_ids')[['gene_idx', 'gene_crsp', 'danny_crsp', 'danny_idx']]


def leads(dd, res, z):
    dd = dd.assign(xi=res.xi.flatten())
    dd['zt'] = ivtools.resid(dd, [z], 'market_ids')[:, 0]
    out = {}
    for k in (12, 24, 36):
        lag = dd[['product_ids', 'month_key', 'xi']].assign(month_key=dd.month_key + k)
        m = dd[['product_ids', 'month_key', 'zt', 'market_ids']].merge(lag, on=['product_ids', 'month_key'])
        y = (m.xi - m.groupby('product_ids').xi.transform('mean')).to_numpy()
        x = (m.zt - m.groupby('product_ids').zt.transform('mean')).to_numpy()
        b = (x @ y) / (x @ x); u = y - b * x
        se = np.sqrt(((pd.Series(x * u).groupby(m.market_ids.to_numpy()).sum()) ** 2).sum()) / (x @ x)
        out[f'lead{k}_t'] = float(b / se)
    return out


def run(d, z, inter, label, funds, with_leads=True):
    o, res, dd = ivtools.fit(d, z, inter)
    o.update(model=label, instrument=z, interaction=inter or 'none')
    if with_leads:
        o.update(leads(dd, res, z))
    fr = own_last_market(res, dd, funds[funds.product_ids.isin(dd.product_ids)]).assign(model=label, instrument=z, interaction=inter or 'none')
    o['n15_abs_e_gt1'] = int((fr.e.abs() > 1).sum())
    o['n15_pos_e'] = int((fr.e > 0).sum())
    print(f"{label:28s} N {o['N']:7,} | a {o['b_price']:8.3f} ({o['se_price']:.3f})"
          + (f" | a_x {o['b_x']:8.3f} ({o['se_x']:.3f}) total {o['cheap_total']:8.2f} | share I {o['share_inter']:.3f}" if inter else '')
          + f" | min F {o['min_F']:7.1f} | avg e {o['avg_e']:6.2f} | e>0 {o['share_pos_e']:.4f} | T5 |e|>1 {o['n15_abs_e_gt1']}/{len(fr)}"
          + (f" | leads t {o['lead12_t']:.1f}/{o['lead24_t']:.1f}/{o['lead36_t']:.1f}" if with_leads else ''), flush=True)
    return o, fr


def main():
    d0 = add_variables(common.load('index'))
    funds = top15(d0)
    d0 = d0.join(cheap, on='product_ids')
    d0['Z_paper'] = d0[H]

    # validation: paper IV, all 108,300 rows
    val = []
    for inter, target in ((None, 'Table 2.0: -5.606 (1.310), F 33.61'), ('danny_crsp', 'CRSP Table 2.2: 5.846 / -20.786, F 28.08 / 1128.15'),
                          ('danny_idx', 'index Table 2.2: -0.613 / -13.739, F 31.80 / 241.67'), ('broad', 'A7 col 2: -7.503 / -5.278')):
        o, _ = run(d0, 'Z_paper', inter, f'VALIDATION {inter or "none"}', funds, with_leads=False)
        o['target'] = target
        val.append(o)
    pd.DataFrame(val).to_csv('step32_validation.csv', index=False)

    d = load_new_iv_sample().join(cheap, on='product_ids')
    assert (d.gene_idx == d.raw20).all(), 'gene_idx must equal the benchmark raw20'
    grid, fund_rows = [], []
    for z in IVS:
        for inter in INTER:
            o, fr = run(d, z, inter, f'{z} x {inter or "none"}', funds)
            grid.append(o); fund_rows.append(fr)
    pd.DataFrame(grid).to_csv('step32_grid.csv', index=False)
    pd.concat(fund_rows).to_csv('step32_funds.csv', index=False)


if __name__ == '__main__':
    main()
