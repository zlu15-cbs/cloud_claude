"""Does it matter that V2's donor pool is the whole index CSV rather than the Table 2 sample?
Same as final V2 (replicate_V2.py, --donor-mmf all) except that Z is recomputed with donors restricted to Table 2 Panel A
fund-months (share >= 0.0001, prefer 1-5, price > 0, 2010-2024m8), money market funds out. Asset and share classes are
unchanged (built from the whole CSV as in V2). Demand and negative MC; no conduct.
Writes step42_demand.csv, step42_mc.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'for_coauthor', 'V2_replication'))
import replicate_V2 as rv


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--index-csv', required=True)
    ap.add_argument('--crsp', required=True)
    a = ap.parse_args()
    d_all = rv.load_sample(a.index_csv)
    raw_all = pd.read_csv(a.index_csv, usecols=['product_j', 'month_t', 'product_exp_ratio', 'product_fund_name']).dropna(subset=['product_exp_ratio'])
    crsp = pd.read_csv(a.crsp, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    mmf = rv.money_market_funds(crsp, set(raw_all.product_j))
    mmf_sample = sorted(set(mmf) & set(d_all.product_ids))
    raw = rv.build_instrument(a.index_csv, a.crsp, mmf)
    t2 = d_all[['product_ids', 'month_t']].rename(columns={'product_ids': 'product_j'}).assign(in_t2=1)
    raw = raw.merge(t2, on=['product_j', 'month_t'], how='left')
    est_months = raw.month_t >= 2010
    m = raw[est_months]
    print(f'donor-pool rows 2010+: {len(m):,}; in Table 2: {int(m.in_t2.eq(1).sum()):,}; outside Table 2: {int(m.in_t2.isna().sum()):,}', flush=True)
    r2 = raw[raw.in_t2.eq(1)].reset_index(drop=True)
    r2['Z_t2'] = rv.leave_out(r2, 'firm_f_old', 'asset_class', 'share_class', 'Z_t2')
    d = d_all[~d_all.product_ids.isin(mmf_sample)].reset_index(drop=True).join(rv.gene_idx(raw_all), on='product_ids')
    d = d.merge(raw[['product_j', 'month_t', 'Z']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
    d = d.merge(r2[['product_j', 'month_t', 'Z_t2']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
    both = d.Z.notna() & d.Z_t2.notna()
    print(f'Z defined: whole CSV {d.Z.notna().sum():,}; Table 2 donors {d.Z_t2.notna().sum():,}; '
          f'rows where Z differs {int((both & ~np.isclose(d.Z, d.Z_t2)).sum()):,}; corr {d.loc[both, ["Z", "Z_t2"]].corr().iloc[0, 1]:.3f}', flush=True)
    out = []
    for z in ('Z', 'Z_t2'):
        est = d[d[z].notna()].drop(columns=[c for c in ('Z', 'Z_t2') if c != z]).rename(columns={z: 'Z'}).reset_index(drop=True)
        o, res, dd = rv.fit_demand(est)
        o.update(rv.lead_tests(dd, res))
        t5 = rv.table5(res, dd, d_all)
        o.update(donors='whole CSV' if z == 'Z' else 'Table 2 only', table5_abs_e_gt1=f'{int((t5.own_elasticity.abs() > 1).sum())}/{len(t5)}')
        out.append(o)
        print(f"{o['donors']:12s} N {o['N']:,} | alpha {o['alpha']:.3f} ({o['se_alpha']:.3f}) | alpha_x {o['alpha_x']:.3f} | min F {o['min_F']:.1f} "
              f"| e>0 {o['share_pos_e']:.4f} | T5 {o['table5_abs_e_gt1']} | leads {o['lead12_t']:.2f} / {o['lead24_t']:.2f} / {o['lead36_t']:.2f}", flush=True)
    pd.DataFrame(out).to_csv('step42_demand.csv', index=False)
    o = out[1]
    p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
    alpha = o['alpha'] + o['alpha_x'] * d.gene_idx.to_numpy()
    rows = []
    for m_, k in rv.CONDUCT.items():
        mu = rv.markups(d, alpha, k)
        s = rv.scale_iv(d, p - mu)
        rows.append(dict(candidate=m_, eta=s['eta'], **rv.neg_stats(d, p + s['eta'] * logq - mu)))
    pd.DataFrame(rows).to_csv('step42_mc.csv', index=False)
    print(pd.DataFrame(rows)[['candidate', 'eta', 'neg_share', 'share_below_m010', 'share_below_m020', 'mc_min']].round(4).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
