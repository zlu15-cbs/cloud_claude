"""Specifications 1-4 with the variable-annuity (VA) funds excluded from the sample.

VA funds = the 112 funds (7,771 fund-months) with a blank firm_f_old; all carry CRSP vau_fund = Y and no other Table 2
fund does. "Excluded" = their rows are dropped, so they leave the demand estimation and the supply side and their
assets count in the outside good. Everything else is as in sc_demand.py / sc_a5.py:
  T2x   paper IV0, one slope                       (paper sample minus VA: 100,529)
  4px   Danny proxy 4p instrument, one slope       (100,529)
  V2x   Z x cheap                                  (estimation 96,069 as before; supply 100,092 = V2's supply minus VA)
  A5x   paper IV0 x broad-based                    (100,529)
    python sc_exva.py ; python sc_exva.py downstream ; python sc_exva.py conduct SPEC
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
import sc_downstream  # noqa: E402
from sc_build import CACHE, PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402

pyblp.options.verbose = False
NAMES = ['T2x', '4px', 'V2x', 'A5x']


def demand():
    d = pd.read_pickle(PANEL)
    d['gene_idx'] = d.cheap
    d['IV0'] = d.demand_instruments0
    fam = d.firm_f_old.notna().to_numpy()
    d['iv4p'] = d.R_ac.where(fam).fillna(d.IV0)
    d['broad'] = ((d.broad_specialized == 'broad-based').groupby(d.product_ids).transform('mean') > 0.5).astype(float)
    nomm = (d.mmf == 0).to_numpy()
    v2rows = nomm & d.Z.notna().to_numpy()
    assert (v2rows & ~fam).sum() == 0
    SPECS = {'T2x': ('IV0', [], fam, fam), '4px': ('iv4p', [], fam, fam),
             'V2x': ('Z', ['cheap'], v2rows, nomm & fam), 'A5x': ('IV0', ['broad'], fam, fam)}
    rows, t5s = [], []
    for name, (iv, zs, erows, srows) in SPECS.items():
        o, res, dd, b = fit(d[erows].reset_index(drop=True), iv, zs)
        o = dict(spec=name, iv=iv, interactions='+'.join(zs), **o)
        t5 = v2.table5(res, dd, d)
        o['t5_gt1'], o['t5_n'] = int((t5.own_elasticity.abs() > 1).sum()), len(t5)
        t5s.append(t5.assign(spec=name))
        sup = d[srows]
        alpha = np.full(len(sup), b['prices']) + sum(b[f'px_{z}'] * sup[z].to_numpy() for z in zs)
        np.save(f'{CACHE}/alpha_{name}.npy', alpha)
        np.save(f'{CACHE}/rows_{name}.npy', np.flatnonzero(np.asarray(srows)))
        o['supply_rows'], o['share_pos_alpha_supply'] = len(sup), float((alpha > 0).mean())
        rows.append(o)
        coefs = ' | '.join([f"p {o['b_prices']:.3f} ({o['se_prices']:.3f})"] + [f"x{z} {o[f'b_{z}']:.3f} ({o[f'se_{z}']:.3f})" for z in zs])
        print(f"{name:5s} N {o['N']:,} supply {len(sup):,} | {coefs} | minF {o['min_F']:.1f} | e>0 {o['share_pos_e']:.3f} | avg e {o['avg_e']:.2f} "
              f"(AUM-w {o['e_aum_weighted']:.2f}) | T5 {o['t5_gt1']}/{o['t5_n']} | leads {o['lead12_t']:.1f}/{o['lead24_t']:.1f}/{o['lead36_t']:.1f}", flush=True)
    pd.DataFrame(rows).to_csv('sc_exva_demand.csv', index=False)
    pd.concat(t5s).to_csv('sc_exva_table5.csv', index=False)


if __name__ == '__main__':
    pd.set_option('display.width', 250, 'display.max_columns', 40)
    sc_downstream.SPECS = NAMES
    if len(sys.argv) > 1 and sys.argv[1] == 'downstream':
        sc_downstream.downstream()
    elif len(sys.argv) > 1 and sys.argv[1] == 'conduct':
        sc_downstream.conduct(sys.argv[2])
    else:
        demand()
