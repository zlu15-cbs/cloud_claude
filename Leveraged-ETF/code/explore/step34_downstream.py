"""Downstream analysis for the 9 demand models of RESULTS_demand_grid.md section 4a.

For each model: estimate demand on its estimation rows; then on the supply sample (all 108,300 fund-months; for models
1 and 5 also the estimation rows only):
  markups and MC under PC, B0, B25, B50, B65; negative-MC statistics at eta = 0, 0.024, the candidate's own estimated
  eta, and eta estimated under PC; the scale eta estimated under each candidate; the pyRVtest conduct test with
  (A) eta = 0.024 for all candidates, (B) each candidate's own estimated eta, (C) the PC-estimated eta for all (Danny).
    python step34_downstream.py [model numbers]     # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step34_{demand,mc,scale,conduct}_m<n>.csv, one set per model.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

import common
import downstream as ds
import ivbuild
import ivtools
from new_iv import load_new_iv_sample
from step2_logit_screen import add_variables, H
from step32_demand_grid import cheap

MODELS = {  # number: (label, instrument, interaction, estimation rows)
    1: ('Z_flag (excl. asset class) x gene_idx', 'Z_flag', 'gene_idx', 'grid'),
    2: ('Z_flag (excl. cluster) x gene_idx', 'Z_clx', 'gene_idx', 'grid'),
    3: ('Z_flag (excl. index) x gene_idx', 'Z_idx', 'gene_idx', 'grid'),
    4: ('Z_flag (excl. asset class), no interaction', 'Z_flag', None, 'grid'),
    5: ('paper IV x gene_idx, family-id rows', 'Z_paper', 'gene_idx', 'grid'),
    6: ('paper IV x gene_idx, all rows', 'Z_paper', 'gene_idx', 'all'),
    7: ("Danny's benchmark: paper IV x danny_crsp, all rows", 'Z_paper', 'danny_crsp', 'all'),
    8: ('paper IV x danny_crsp, family-id rows', 'Z_paper', 'danny_crsp', 'grid'),
    9: ('bridge: Z_flag (excl. asset class) x danny_crsp', 'Z_flag', 'danny_crsp', 'grid'),
}
SUPPLY_EST_ALSO = {1, 5}


def append(df, path):
    path = path.replace('.csv', f'_m{df.model.iloc[0]}.csv')  # one file per model, so models can run in parallel
    df.to_csv(path, mode='a', header=not os.path.exists(path), index=False)


def main(which):
    d = add_variables(common.load('index')).join(cheap, on='product_ids')
    d['Z_paper'] = d[H]
    d = d.merge(ivbuild.build(), on=['product_ids', 'month_t'], how='left')
    grid = load_new_iv_sample()[['product_ids', 'month_t']].assign(grid=1)
    d = d.merge(grid, on=['product_ids', 'month_t'], how='left').reset_index(drop=True)
    d['grid'] = d.grid.fillna(0).astype(int)
    print(f'supply rows {len(d):,}; grid rows {int(d.grid.sum()):,}', flush=True)
    for n in which:
        label, z, inter, rows = MODELS[n]
        t0 = time.time()
        est = d[d[z].notna() & ((d.grid == 1) if rows == 'grid' else True)]
        o, _, _ = ivtools.fit(est, z, inter)
        o.update(model=n, label=label, instrument=z, interaction=inter or 'none', est_rows=rows)
        append(pd.DataFrame([o]), 'step34_demand.csv')
        print(f"\n=== model {n}: {label} | N {o['N']:,} | a {o['b_price']:.3f}" + (f" a_x {o['b_x']:.3f}" if inter else '')
              + f" | e>0 {o['share_pos_e']:.3f}", flush=True)
        for supply in (['all', 'est'] if n in SUPPLY_EST_ALSO else ['all']):
            s = d if supply == 'all' else d.loc[est.index]
            s = s.reset_index(drop=True)
            alpha = (o['b_price'] + (o['b_x'] * s[inter].to_numpy() if inter else 0)) * np.ones(len(s))
            mus = {m: ds.markups(s, alpha, k) for m, k in ds.CONDUCT.items()}
            p, logq = s.prices.to_numpy(), np.log(s.product_mtna.to_numpy())
            scale = {m: ds.scale_iv(s, p - mus[m]) for m in ds.CONDUCT}
            append(pd.DataFrame([dict(model=n, supply=supply, candidate=m, **scale[m]) for m in ds.CONDUCT]), 'step34_scale.csv')
            mc_rows = []
            for m in ds.CONDUCT:
                for eta_name, eta in (('0', 0.0), ('0.024', 0.024), ('own', scale[m]['eta']), ('PC', scale['PC']['eta'])):
                    mc = p + eta * logq - mus[m]
                    mc_rows.append(dict(model=n, supply=supply, candidate=m, eta_rule=eta_name, eta=eta,
                                        mean_markup=float(mus[m].mean()), share_neg_markup=float((mus[m] < 0).mean()),
                                        **ds.neg_stats(s, mc)))
            append(pd.DataFrame(mc_rows), 'step34_mc.csv')
            for scheme, etas in (('A: 0.024', {m: 0.024 for m in ds.CONDUCT}),
                                 ('B: own estimated', {m: scale[m]['eta'] for m in ds.CONDUCT}),
                                 ('C: PC estimated', {m: scale['PC']['eta'] for m in ds.CONDUCT})):
                c = ds.conduct_test(s, mus, etas).assign(model=n, supply=supply, eta_scheme=scheme)
                append(c, 'step34_conduct.csv')
                sel = c[c.iv_set.str.startswith('main')]
                print(f"  [{supply}] {scheme:17s} main-IV selected: {sel[sel.selected].candidate.tolist()} | MCS p "
                      f"{dict(zip(sel.candidate, sel.mcs_p.round(3)))}", flush=True)
            sc = {m: round(scale[m]['eta'], 4) for m in ds.CONDUCT}
            neg = {r['candidate']: round(r['neg_share'], 3) for r in mc_rows if r['eta_rule'] == 'own'}
            print(f'  [{supply}] eta by candidate {sc} | neg-MC share at own eta {neg} | {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main([int(x) for x in sys.argv[1:]] or list(MODELS))
