"""V2 with a finer exclusion: about 14 Lipper-based groups instead of 6 asset classes. Everything else as final V2
(for_coauthor/V2_replication/replicate_V2.py, --donor-mmf all): only the fund-level Lipper mapping changes; the CRSP style
code and name fallbacks (0.04% of rows) keep the 6-class labels. Demand, scale and negative MC; no conduct test.
    python step41_finer_asset_class.py --index-csv ... --crsp ...
Writes step41_demand.csv, step41_mc.csv, step41_classes.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'for_coauthor', 'V2_replication'))
import replicate_V2 as rv

FINE = {
    'us_large': ('LCCE', 'LCGE', 'LCVE', 'SPSP', 'MLCE', 'MLGE', 'MLVE', 'EIEI', 'ELCC'),
    'us_mid': ('MCCE', 'MCGE', 'MCVE', 'SPMC'),
    'us_small': ('SCCE', 'SCGE', 'SCVE'),
    'us_sector': ('TK', 'H', 'FS', 'UT', 'NR', 'BM', 'CG', 'CS', 'ID', 'TL', 'S', 'SESE', 'AE'),
    'intl_developed': ('IF', 'IEI', 'IFCE', 'IFGE', 'IFVE', 'INI', 'IS', 'CN'),
    'global_equity': ('GL', 'GEI', 'GSME', 'GTK', 'GNR', 'GFS', 'GH', 'GIF', 'GLI'),
    'emerging': ('EM', 'FM'),
    'region_country': ('EU', 'JA', 'CH', 'LT', 'PC', 'XJ', 'INR'),
    'bond_government': ('GUT', 'GUS', 'IUG', 'SUT', 'SUS', 'SIU', 'IUT', 'USO', 'GNM', 'USM', 'ITM', 'IUS', 'UST', 'MM'),
    'bond_muni': ('GM', 'IMD', 'SMD', 'SIM', 'HM', 'CAG', 'CAI', 'NY', 'MN', 'MDI', 'SSIM'),
}
FINE_PREFIX = {'intl_developed': ('IML', 'ILC', 'ISM'), 'global_equity': ('GML', 'GLC', 'GLV', 'GLG')}


def lipper_fine(code, asset_cd):
    c = str(code)
    base = coarse(code, asset_cd)
    if base in ('allocation', 'real_asset', 'other') or c == 'nan':
        return base
    for g, codes in FINE.items():
        if c in codes or c.startswith(FINE_PREFIX.get(g, ('\0',))):
            return g
    if base == 'bond':
        return 'bond_core_credit'          # IID, CPB, GB, SID, SII, A, BBB, HY, SHY, LP, EMD, MSI, FLX, ...
    if base == 'intl_equity':
        return 'intl_developed'
    return 'us_large' if base == 'us_equity' else base


coarse = rv.lipper_class
rv.lipper_class = lipper_fine


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
    cls = raw.drop_duplicates('product_j').asset_class.value_counts()
    cls.to_csv('step41_classes.csv')
    print('fine groups (funds per group):\n', cls.to_string(), flush=True)
    d = d_all[~d_all.product_ids.isin(mmf_sample)].reset_index(drop=True).join(rv.gene_idx(raw_all), on='product_ids')
    d = d.merge(raw[['product_j', 'month_t', 'Z', 'asset_class']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
    est = d[d.Z.notna()].reset_index(drop=True)
    o, res, dd = rv.fit_demand(est)
    o.update(rv.lead_tests(dd, res))
    t5 = rv.table5(res, dd, d_all)
    o['table5_abs_e_gt1'] = f'{int((t5.own_elasticity.abs() > 1).sum())}/{len(t5)}'
    pd.DataFrame([o]).to_csv('step41_demand.csv', index=False)
    print(f"demand: N {o['N']:,} | alpha {o['alpha']:.3f} ({o['se_alpha']:.3f}) | alpha_x {o['alpha_x']:.3f} ({o['se_alpha_x']:.3f}) "
          f"| min F {o['min_F']:.1f} | share e>0 {o['share_pos_e']:.4f} | avg e {o['avg_e']:.2f} | T5 {o['table5_abs_e_gt1']} "
          f"| leads {o['lead12_t']:.2f} / {o['lead24_t']:.2f} / {o['lead36_t']:.2f}", flush=True)
    if o['share_pos_e'] > 0:
        return
    p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
    alpha = o['alpha'] + o['alpha_x'] * d.gene_idx.to_numpy()
    rows = []
    for m, k in rv.CONDUCT.items():
        mu = rv.markups(d, alpha, k)
        s = rv.scale_iv(d, p - mu)
        mc = p + s['eta'] * logq - mu
        neg = mc < 0
        rows.append(dict(candidate=m, eta=s['eta'], **rv.neg_stats(d, mc),
                         vanguard_share_of_neg=float(neg[d.firm_ids.to_numpy() == 'Vanguard'].sum() / neg.sum()) if neg.sum() else np.nan))
    pd.DataFrame(rows).to_csv('step41_mc.csv', index=False)
    print(pd.DataFrame(rows).round(4).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
