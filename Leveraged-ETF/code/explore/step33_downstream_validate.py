"""Validate downstream.py before using it.
  1. Markups: ours vs pyblp (compute_markups, firm ownership) and vs pyRVtest's own build_markups (B0, B25, B65),
     for the Table 2 col 2 logit and for Danny's benchmark (heterogeneous alpha).
  2. Negative-MC share, B0, Table 2 logit IV, scale 0: target 0.5156 (Danny, Table 2.0).
  3. Scale under PC: target 0.0205 (0.0051) (Danny, Table 2.0; demand-independent).
  4. Conduct test with supplied markups == pyRVtest computing markups itself (eta = 0.024 through prices).
    python step33_downstream_validate.py     # from a folder holding the index CSV and step31_cheap_by_fund.csv
"""
import contextlib
import io

import numpy as np
import pandas as pd
import pyRVtest

import common
import downstream as ds
import ivtools
from step2_logit_screen import add_variables, H
from step32_demand_grid import cheap

d = add_variables(common.load('index')).join(cheap, on='product_ids').reset_index(drop=True)
d['Z_paper'] = d[H]
print(f'supply rows {len(d):,}', flush=True)

for label, inter in (('Table 2 col 2 logit IV', None), ("Danny's benchmark", 'danny_crsp')):
    o, res, dd = ivtools.fit(d, 'Z_paper', inter)
    assert (dd.product_ids.to_numpy() == d.product_ids.to_numpy()).all()
    alpha = o['b_price'] + (o['b_x'] * d[inter].to_numpy() if inter else 0)
    alpha = np.broadcast_to(alpha, (len(d),)).astype(float)
    mine = ds.markups(d, alpha, 0.0)
    with contextlib.redirect_stdout(io.StringIO()):
        pyb = res.compute_markups().flatten()
    lerner = mine / d.prices.to_numpy()  # pyblp's compute_markups returns the Lerner index (p - c) / p
    print(f'[1] {label}: max |ours/p - pyblp Lerner| B0 = {np.abs(lerner - pyb).max():.2e} (mean markup level {mine.mean():.4f})', flush=True)
    if inter is None:
        # [2] negative MC, B0, scale 0
        st = ds.neg_stats(d, d.prices.to_numpy() - mine)
        print(f"[2] negative MC B0 scale 0: monthly-mean share {st['neg_share']:.4f} (target 0.5156); pooled {st['neg_share_pooled']:.4f}", flush=True)
        # [3] PC scale
        sc = ds.scale_iv(d, d.prices.to_numpy())
        print(f"[3] PC scale eta {sc['eta']:.4f} ({sc['eta_se']:.4f}), p {sc['eta_p']:.4f}  (target 0.0205 (0.0051))", flush=True)
        # [1c + 4] pyRVtest native markups vs ours, and identical test statistics
        mus = {m: ds.markups(d, alpha, k) for m, k in ds.CONDUCT.items()}
        etas = {m: 0.024 for m in ds.CONDUCT}
        iv1 = {'main': ds.CONDUCT_IV['main: rival2 x csent_index']}
        ours = ds.conduct_test(d, mus, etas, iv1)
        dn = d.copy()
        dn['prices'] = dn.prices + 0.024 * np.log(dn.product_mtna)
        forms = [pyRVtest.ModelFormulation(model_downstream='perfect_competition', ownership_downstream='firm_ids')] + \
                [pyRVtest.ModelFormulation(model_downstream='bertrand', ownership_downstream='firm_ids',
                                           kappa_specification_downstream=ds.kappa_fn(ds.CONDUCT[m])) for m in list(ds.CONDUCT)[1:]]
        with contextlib.redirect_stdout(io.StringIO()):
            prob = pyRVtest.Problem(
                cost_formulation=pyRVtest.Formulation('0 + log_product_fund_age + product_tracking_err + product_past_1yr_ret',
                                                      absorb='C(product_ids) + C(market_ids)'),
                instrument_formulation=pyRVtest.Formulation(iv1['main']), model_formulations=tuple(forms),
                product_data=dn, demand_results=res)
            nat = prob.solve(demand_adjustment=False, clustering_adjustment=True)
        for i, m in enumerate(ds.CONDUCT):
            print(f'[1c] {m}: max |ours - pyRVtest native| markup = {np.abs(mus[m] - np.asarray(nat.markups[i]).flatten()).max():.2e}', flush=True)
        print('[4] MCS p-values  ours  :', ours.mcs_p.round(4).tolist(), flush=True)
        print('[4] MCS p-values native :', np.asarray(nat.MCS_pvalues[0]).flatten().round(4).tolist(), flush=True)
        print('[4] TRV ours row PC     :', ours.filter(like='TRV_vs').iloc[0].round(3).tolist(), flush=True)
        print('[4] TRV native row PC   :', np.asarray(nat.TRV[0])[0].round(3).tolist(), flush=True)
