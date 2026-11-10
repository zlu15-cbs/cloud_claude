"""Two follow-up checks on the downstream results (RESULTS_downstream.md section 6).
  (a) Where are the negative MCs? Rule 3 of NOTE_seclending_MC_bounds.md: they should sit in high-lending categories
      (small cap, EM, international), not in Vanguard funds (lending at cost) or SPY (a UIT that cannot lend).
      Shares of fund-months with MC < 0 at the candidate's own estimated eta, B0 and B65, by group.
  (b) Danny's conduct convention: markups capped 1/99 within calendar year (equal weights, linear quantiles) before the
      test; eta = 0.024 (A) and the PC-estimated eta (C). pyRVtest stands in for his own RV/MCS code.
    python step35_checks.py [model numbers]     # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step35_where_m<n>.csv, step35_conduct_capped_m<n>.csv.
"""
import sys

import numpy as np
import pandas as pd

import common
import downstream as ds
import ivbuild
import ivtools
from asset_class import classify_by_index
from new_iv import load_new_iv_sample
from step2_logit_screen import add_variables, H
from step32_demand_grid import cheap
from step34_downstream import MODELS


def main(which):
    d = add_variables(common.load('index')).join(cheap, on='product_ids')
    d['Z_paper'] = d[H]
    d = d.merge(ivbuild.build(), on=['product_ids', 'month_t'], how='left')
    grid = load_new_iv_sample()[['product_ids', 'month_t']].assign(grid=1)
    d = d.merge(grid, on=['product_ids', 'month_t'], how='left').reset_index(drop=True)
    d['grid'] = d.grid.fillna(0).astype(int)
    d['ac5'] = classify_by_index(d.assign(product_j=d.product_ids))
    nm = d.product_fund_name.fillna('').str.lower()
    d['size'] = np.select([nm.str.contains('small|micro'), nm.str.contains('mid')], ['small/micro', 'mid'], 'other')
    d['grp_firm'] = np.where(d.firm_ids.isin(ds.BIG3), d.firm_ids, 'other firms')
    d['spy'] = d.product_fund_name.fillna('').str.startswith('SPDR S&P 500 ETF Trust')
    p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
    for n in which:
        label, z, inter, rows = MODELS[n]
        est = d[d[z].notna() & ((d.grid == 1) if rows == 'grid' else True)]
        o, _, _ = ivtools.fit(est, z, inter)
        alpha = (o['b_price'] + (o['b_x'] * d[inter].to_numpy() if inter else 0)) * np.ones(len(d))
        mus = {m: ds.markups(d, alpha, k) for m, k in ds.CONDUCT.items()}
        eta = {m: ds.scale_iv(d, p - mus[m])['eta'] for m in ds.CONDUCT}
        # (a) where
        out = []
        for m in ('B0', 'B65'):
            neg = (p + eta[m] * logq - mus[m]) < 0
            tot = neg.sum()
            for gcol in ('ac5', 'grp_firm', 'size', 'etf', 'spy') + ((inter,) if inter else ()):
                for g, idx in d.groupby(gcol).indices.items():
                    out.append(dict(model=n, candidate=m, group_by=gcol, group=str(g), fund_months=len(idx),
                                    share_neg=float(neg[idx].mean()), share_of_all_neg=float(neg[idx].sum() / tot) if tot else np.nan))
        W = pd.DataFrame(out)
        W.to_csv(f'step35_where_m{n}.csv', index=False)
        print(f'\n=== model {n}: {label} | a {o["b_price"]:.3f}' + (f' a_x {o["b_x"]:.3f}' if inter else ''), flush=True)
        for m in ('B0', 'B65'):
            w = W[W.candidate == m]
            print(f'  {m} share negative by group: ' + ' | '.join(f'{r.group}: {r.share_neg:.2f} ({r.share_of_all_neg:.2f} of neg)'
                                                             for r in w.itertuples()), flush=True)
        # (b) capped markups, Danny's convention
        yr = pd.Series(np.floor(d.month_t.to_numpy()))
        capped = {m: (mus[m] if m == 'PC' else ds.winsor_by_year(mus[m], yr)) for m in ds.CONDUCT}
        res = []
        for scheme, etas in (('A: 0.024', {m: 0.024 for m in ds.CONDUCT}), ('C: PC estimated', {m: eta['PC'] for m in ds.CONDUCT})):
            c = ds.conduct_test(d, capped, etas).assign(model=n, eta_scheme=scheme, markups='capped 1/99 by year')
            res.append(c)
            for iv in c.iv_set.unique():
                s = c[c.iv_set == iv]
                print(f'  capped {scheme:16s} {iv:28s} selected {s[s.selected].candidate.tolist()}', flush=True)
        pd.concat(res).to_csv(f'step35_conduct_capped_m{n}.csv', index=False)


if __name__ == '__main__':
    main([int(x) for x in sys.argv[1:]] or [1, 2, 3, 5, 6, 7, 9])
