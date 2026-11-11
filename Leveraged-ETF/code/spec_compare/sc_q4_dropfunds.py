"""Exact re-estimation after dropping the most influential funds found by sc_q4_influence.py."""
import os, sys
import numpy as np, pandas as pd, pyblp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sc_build import CACHE, PANEL
from sc_demand import fit
pyblp.options.verbose = False
d = pd.read_pickle(PANEL)
d['cheap'] = np.load(f'{CACHE}/cheap_V2n.npy'); d['gene_idx'] = d.cheap
d['broad'] = ((d.broad_specialized == 'broad-based').groupby(d.product_ids).transform('mean') > 0.5).astype(float)
d['paper'] = d.demand_instruments0
DB, PHY, DBA = 24698, 52699, 24773   # Invesco DB Commodity Index Tracking; PIMCO 0-5 Year High Yield ETF; Invesco DB Agriculture
nova = d.firm_f_old.notna()
for lab, drop in (('nothing dropped', []), ('Invesco DB Commodity Index Tracking Fund dropped', [DB]), ('that fund, PIMCO 0-5 Year High Yield ETF and Invesco DB Agriculture dropped', [DB, PHY, DBA])):
    k = ~d.product_ids.isin(drop)
    print(f'\n{lab}')
    for nm, mask, iv, zs in (('T2, all rows (paper)', k, 'paper', []), ('T2, no VA', k & nova, 'paper', []), ('A5, all rows (paper)', k, 'paper', ['broad']), ('A5, no VA', k & nova, 'paper', ['broad']),
                             ('V2', k & (d.mmf == 0) & d.Z.notna(), 'Z', ['cheap'])):
        o, res, dd, b = fit(d[mask].reset_index(drop=True), iv, zs)
        print(f"  {nm:22s} N {o['N']:>7,} | price {o['b_prices']:8.3f} ({o['se_prices']:.3f})" + ''.join(f" | x {z} {o['b_'+z]:.3f} ({o['se_'+z]:.3f})" for z in zs) + f" | F {o['min_F']:.0f} | e>0 {o['share_pos_e']:.3f}", flush=True)
x = d[d.product_ids.isin([DB, PHY, DBA])]
print('\nfee, instrument and assets of the three funds, by year (means):')
print(x.assign(year=np.floor(x.month_t).astype(int)).groupby(['product_fund_name', 'year'])[['prices', 'demand_instruments0', 'product_mtna']].mean().round(3).to_string())
print(x.groupby('product_fund_name')[['firm_f_old', 'firm_ids', 'market_m_index', 'asset_class']].first().to_string())
