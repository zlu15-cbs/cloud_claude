"""Which construction difference moves the benchmark slope from Z to Danny's IV3_exp_ratio_med?
Danny's construction (5_fund_market_data_for_Matteo_v6_nonlev_etf.R, lines 208-310): donors in the CRSP index-fund file,
same fund_family, same share class (CRSP inst/retail flags + name regex), different TRACKED INDEX, lagged TNA present.
Ours (new_iv.py): donors in the raw index file, same firm_f_old, same share class (name regex), different ASSET CLASS.
Variants of ours, one change at a time; each enters the benchmark (price x raw20, fund + month FE) on the same rows.

    python step30b_iv_decompose.py <patch csv>     # from a folder holding the index CSV
"""
import sys

import numpy as np
import pandas as pd

import ivtools
from asset_class import classify_by_index
from new_iv import load_new_iv_sample, share_class
from tiers import RAW

patch = pd.read_csv(sys.argv[1])
patch['month_key'] = np.round(patch.month_t * 12).astype(int)
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna() & raw.firm_f_old.notna()].copy()
raw['ac'] = classify_by_index(raw)
raw['sc'] = share_class(raw)


def leave_group_out(r, keys, excl):
    """median fee over same `keys`, excluding rows whose `excl` equals the focal row's."""
    s = r.groupby(keys + [excl]).product_exp_ratio.apply(list).rename('own').reset_index()
    a = r.groupby(keys).product_exp_ratio.apply(list).rename('all').reset_index()
    s = s.merge(a, on=keys)

    def med(row):
        v = list(row['all'])
        for x in row['own']:
            v.remove(x)
        return np.median(v) if v else np.nan
    s['V'] = s.apply(med, axis=1)
    return s[keys + [excl, 'V']]


d = load_new_iv_sample()
d = d.merge(patch[['product_j', 'month_key', 'IV3_exp_ratio_med']].rename(columns={'product_j': 'product_ids'}),
            on=['product_ids', 'month_key'], how='left')
mi = raw[['product_j', 'month_t', 'market_m_index']].rename(columns={'product_j': 'product_ids'})
d = d.drop(columns=[c for c in ('market_m_index',) if c in d.columns]).merge(mi, on=['product_ids', 'month_t'], how='left')
variants = {'Z_other_index': (['firm_f_old', 'month_t', 'sc'], 'market_m_index'),
            'Z_other_ac_no_sc': (['firm_f_old', 'month_t'], 'ac'),
            'Z_other_index_no_sc': (['firm_f_old', 'month_t'], 'market_m_index')}
for name, (keys, excl) in variants.items():
    t = leave_group_out(raw, keys, excl).rename(columns={'V': name})
    lk = {'firm_f_old': 'fam'}
    t = t.rename(columns=lk)
    d = d.merge(t, on=[lk.get(k, k) for k in keys] + [excl], how='left')
rows = d[d.IV3_exp_ratio_med.notna() & d[list(variants)].notna().all(axis=1)]
print(f'common rows {len(rows):,} of {len(d):,}', flush=True)
out = []
for z in ['Z', 'Z_other_index', 'Z_other_ac_no_sc', 'Z_other_index_no_sc', 'IV3_exp_ratio_med']:
    o, _, _ = ivtools.fit(rows, z, 'raw20')
    o.update(instrument=z, corr_with_Z=float(np.corrcoef(rows.Z, rows[z])[0, 1]))
    out.append(o)
    print(f"{z:22s} corr(Z) {o['corr_with_Z']:.3f} | non-cheap {o['b_price']:7.3f} ({o['se_price']:.3f}) | x cheap {o['b_x']:7.3f} ({o['se_x']:.3f}) "
          f"| total {o['cheap_total']:7.2f} | F {o['F_price']:.1f}/{o['F_x']:.1f} | avg e {o['avg_e']:.2f} | e>0 {o['share_pos_e']:.4f}", flush=True)
pd.DataFrame(out).to_csv('step30b_iv_decompose.csv', index=False)
