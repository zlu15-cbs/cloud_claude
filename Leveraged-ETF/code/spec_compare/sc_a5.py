"""The broad-based interaction (paper Table A7 in our copy; "A5" in Gene's message of 10 Nov) and a more defensible version.

  A5       paper's spec: price + price x broad, paper IV0 and IV0 x broad, all 108,300 rows   (reference -7.503 / -5.278)
  A5d      same interaction; rows with a family code and a defined instrument, money market funds dropped (96,069);
           instrument = lag-AUM-weighted mean fee of same-family, same-share-type funds in another Lipper-6 asset class
Sample-sensitivity rows (demand only): T2, A5 and the fee-tercile interaction on the paper sample with and without the
7,771 fund-months that have no family code; A5d with the label made consistent within an index; V2 + broad.
    python sc_a5.py            # demand fits -> sc_a5_demand.csv, sc_a5_table5.csv, alpha/rows for the downstream step
then, in the same folder:  python sc_a5.py downstream ;  python sc_a5.py conduct A5 ;  python sc_a5.py conduct A5d
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
import sc_downstream  # noqa: E402
from sc_broad_ladder import leave_out  # noqa: E402
from sc_build import CACHE, CRSP, INDEX, PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402

pyblp.options.verbose = False


def demand():
    d = pd.read_pickle(PANEL)
    d['gene_idx'] = d.cheap
    d['IV0'] = d.demand_instruments0
    d['broad'] = ((d.broad_specialized == 'broad-based').groupby(d.product_ids).transform('mean') > 0.5).astype(float)
    d['broad_tv'] = (d.broad_specialized == 'broad-based').astype(float)      # the paper's own (row-level) label
    key_i = d.market_m_index.fillna('_none_' + d.product_ids.astype(str))
    fl = pd.DataFrame({'i': key_i, 'b': d.broad, 'pj': d.product_ids}).drop_duplicates('pj')
    d['broadfix'] = key_i.map((fl.groupby('i').b.mean() > 0.5).astype(float))
    print('fund-months where the row-level label differs from the fund-level one:', int((d.broad != d.broad_tv).sum()), flush=True)

    crsp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    mmf = v2.money_market_funds(crsp, set(pd.read_csv(INDEX, usecols=['product_j']).product_j))
    del crsp
    raw = v2.build_instrument(INDEX, CRSP, mmf)
    raw = raw.merge(pd.read_csv(INDEX, usecols=['product_j', 'month_t', 'product_L1_mtna']), on=['product_j', 'month_t'], how='left')
    raw['W'] = leave_out(raw, 'asset_class', True, 'wavg')
    d = d.merge(raw[['product_j', 'month_t', 'W']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
    del raw
    allr, fam, nomm = d.index >= 0, d.firm_f_old.notna().to_numpy(), (d.mmf == 0).to_numpy()
    v2rows = nomm & d.Z.notna().to_numpy()
    assert (d.W.notna() & nomm).sum() == v2rows.sum()
    SPECS = {  # name: (label, iv, interactions, estimation rows, supply rows)
        'A5': ('broad, paper IV0, all rows', 'IV0', ['broad'], allr, allr),
        'A5d': ('broad, asset-class / same-type / weighted IV, V2 rows', 'W', ['broad'], v2rows, nomm),
        'x_A5_rowlabel': ('broad (row-level label, as the paper), paper IV0, all rows', 'IV0', ['broad_tv'], allr, None),
        'x_A5_fam': ('broad, paper IV0, rows with a family code', 'IV0', ['broad'], fam, None),
        'x_A5_nofam': ('broad, paper IV0, rows without a family code', 'IV0', ['broad'], ~fam, None),
        'x_T2_all': ('one slope, paper IV0, all rows', 'IV0', [], allr, None),
        'x_T2_fam': ('one slope, paper IV0, rows with a family code', 'IV0', [], fam, None),
        'x_T2_nofam': ('one slope, paper IV0, rows without a family code', 'IV0', [], ~fam, None),
        'x_terc_all': ('fee tercile, paper IV0, all rows', 'IV0', ['fee_t1', 'fee_t2'], allr, None),
        'x_terc_fam': ('fee tercile, paper IV0, rows with a family code', 'IV0', ['fee_t1', 'fee_t2'], fam, None),
        'x_cheap_all': ('cheap, paper IV0, all rows', 'IV0', ['cheap'], allr, None),
        'x_cheap_fam': ('cheap, paper IV0, rows with a family code', 'IV0', ['cheap'], fam, None),
        'x_A5d_fix': ('broad made consistent within an index, same IV as A5d', 'W', ['broadfix'], v2rows, None),
        'x_A5d_Z': ('broad, V2 instrument Z', 'Z', ['broad'], v2rows, None),
        'x_V2_broad': ('cheap + broad, V2 instrument Z', 'Z', ['cheap', 'broad'], v2rows, nomm),
        'x_V2w': ('cheap, weighted IV W', 'W', ['cheap'], v2rows, None),
    }
    rows, t5s = [], []
    for name, (label, iv, zs, erows, srows) in SPECS.items():
        o, res, dd, b = fit(d[erows].reset_index(drop=True), iv, zs)
        o = dict(spec=name, label=label, iv=iv, interactions='+'.join(zs), **o)
        t5 = v2.table5(res, dd, d)
        o['t5_gt1'], o['t5_n'] = (int((t5.own_elasticity.abs() > 1).sum()) if len(t5) else 0), len(t5)
        if len(t5):
            t5s.append(t5.assign(spec=name))
        if srows is not None:
            sup = d[srows]
            alpha = np.full(len(sup), b['prices']) + sum(b[f'px_{z}'] * sup[z].to_numpy() for z in zs)
            np.save(f'{CACHE}/alpha_{name}.npy', alpha)
            np.save(f'{CACHE}/rows_{name}.npy', np.flatnonzero(np.asarray(srows)))
            o['share_pos_alpha_supply'] = float((alpha > 0).mean())
        rows.append(o)
        coefs = ' | '.join([f"p {o['b_prices']:.3f} ({o['se_prices']:.3f})"] + [f"x{z} {o[f'b_{z}']:.3f} ({o[f'se_{z}']:.3f})" for z in zs])
        print(f"{name:14s} N {o['N']:,} funds {o['funds']} | {coefs} | minF {o['min_F']:.1f} | e>0 {o['share_pos_e']:.3f} | avg e {o['avg_e']:.2f} "
              f"(AUM-w {o['e_aum_weighted']:.2f}) | T5 {o['t5_gt1']}/{o['t5_n']} | leads {o['lead12_t']:.1f}/{o['lead24_t']:.1f}/{o['lead36_t']:.1f}", flush=True)
        pd.DataFrame(rows).to_csv('sc_a5_demand.csv', index=False)
    pd.concat(t5s).to_csv('sc_a5_table5.csv', index=False)


if __name__ == '__main__':
    pd.set_option('display.width', 250, 'display.max_columns', 40)
    sc_downstream.SPECS = ['A5', 'A5d', 'x_V2_broad']
    if len(sys.argv) > 1 and sys.argv[1] == 'downstream':
        sc_downstream.downstream()
    elif len(sys.argv) > 1 and sys.argv[1] == 'conduct':
        sc_downstream.conduct(sys.argv[2])
    else:
        demand()
