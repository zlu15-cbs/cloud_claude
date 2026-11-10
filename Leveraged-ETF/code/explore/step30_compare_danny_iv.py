"""Compare Danny's uploaded share-class Hausman IV (patch_hausman_share_class_exp_ratio_IV.csv, 31 Oct 2026) with our
instrument Z (new_iv.py: median fee of same family, same share class, other asset class, same month).

1. Row level, on every raw fund-month where either is defined: coverage, correlation, exact / near equality.
2. On the 97,429-row estimation sample: the same, plus the benchmark logit IV (price x raw20, fund + month FE)
   re-estimated with each of Danny's six columns in place of Z.

    python step30_compare_danny_iv.py <path to patch csv>     # from a folder holding the index CSV
Writes step30_iv_compare_rows.csv, step30_iv_compare_fits.csv, step30_iv_disagree_sample.csv.
"""
import sys

import numpy as np
import pandas as pd

import ivtools
from asset_class import classify_by_index
from new_iv import load_new_iv_sample, share_class
from tiers import RAW

PATCH = sys.argv[1]
pcols = ['IV3_exp_ratio_vw', 'IV3_exp_ratio_adj_vw', 'IV3_mgmt_fee_vw', 'IV3_exp_ratio_med', 'IV3_exp_ratio_adj_med', 'IV3_mgmt_fee_med']
patch = pd.read_csv(PATCH, float_precision='round_trip')
print('patch rows', len(patch), '| unique (product_j, month_t)', len(patch[['product_j', 'month_t']].drop_duplicates()),
      '| month_t range', patch.month_t.min(), patch.month_t.max(), flush=True)
print(patch[pcols].describe().T.round(4).to_string(), flush=True)
patch['month_key'] = np.round(patch.month_t * 12).astype(int)

# ---- 1. row level: our Z on every raw fund-month (same construction as new_iv.load_new_iv_sample)
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna() & raw.firm_f_old.notna()].copy()
raw['fam'] = raw.firm_f_old
raw['ac'] = classify_by_index(raw)
raw['sc'] = share_class(raw)
tab = pd.concat([raw[raw.ac != a].groupby(['fam', 'month_t', 'sc']).product_exp_ratio.agg(Z='median', Z_n='size').reset_index().assign(ac=a)
                 for a in sorted(raw.ac.unique())])
rz = raw.merge(tab, on=['fam', 'month_t', 'ac', 'sc'], how='left')
rz['month_key'] = np.round(rz.month_t * 12).astype(int)
m = rz[['product_j', 'month_key', 'Z', 'Z_n', 'ac', 'sc', 'fam', 'product_exp_ratio']].merge(
    patch[['product_j', 'month_key'] + pcols], on=['product_j', 'month_key'], how='outer', indicator=True)
print('\nraw-level merge:', m._merge.value_counts().to_dict(), flush=True)


def compare(df, a, b, tag):
    both = df[a].notna() & df[b].notna()
    x, y = df.loc[both, a], df.loc[both, b]
    dif = (x - y).abs()
    return dict(level=tag, ours=a, danny=b, n_ours=int(df[a].notna().sum()), n_danny=int(df[b].notna().sum()), n_both=int(both.sum()),
                only_ours=int((df[a].notna() & df[b].isna()).sum()), only_danny=int((df[a].isna() & df[b].notna()).sum()),
                corr=float(np.corrcoef(x, y)[0, 1]) if both.sum() > 2 else np.nan,
                share_exact=float((dif < 1e-9).mean()), share_within_0005=float((dif < 0.0005).mean()),
                share_within_005=float((dif < 0.005).mean()), median_absdiff=float(dif.median()), p99_absdiff=float(dif.quantile(0.99)),
                mean_ours=float(x.mean()), mean_danny=float(y.mean()))


rows = [compare(m, 'Z', c, 'raw fund-months') for c in pcols]

# ---- 2. estimation sample
d = load_new_iv_sample()
d = d.merge(patch[['product_j', 'month_key'] + pcols].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_key'], how='left')
print(f'\nestimation sample {len(d):,} rows; Danny IV3_exp_ratio_med defined on {d.IV3_exp_ratio_med.notna().sum():,}', flush=True)
rows += [compare(d, 'Z', c, 'estimation sample') for c in pcols]
R = pd.DataFrame(rows)
pd.set_option('display.width', 250)
print(R.round(4).to_string(index=False), flush=True)
R.to_csv('step30_iv_compare_rows.csv', index=False)

# where the median versions disagree: by share class / asset class
both = d.Z.notna() & d.IV3_exp_ratio_med.notna()
d['disagree'] = both & ((d.Z - d.IV3_exp_ratio_med).abs() >= 0.0005)
print('\nshare disagreeing (|diff| >= 0.0005 pp) by share class:', d[both].groupby('sc').disagree.mean().round(3).to_dict(), flush=True)
print('by asset class:', d[both].groupby('ac').disagree.mean().round(3).to_dict(), flush=True)
d.loc[d.disagree, ['product_ids', 'month_key', 'firm_ids', 'fam', 'sc', 'ac', 'prices', 'Z', 'Z_n', 'IV3_exp_ratio_med']].head(500).to_csv(
    'step30_iv_disagree_sample.csv', index=False)

# ---- 3. benchmark logit IV with each instrument, on the rows where the instrument is defined
fits = []
for z in ['Z'] + pcols:
    for rows_tag, dd in (('all 97,429', d), ('rows where Danny med IV defined', d[d.IV3_exp_ratio_med.notna()])):
        dd = dd[dd[z].notna()]
        if rows_tag != 'all 97,429' and z not in ('Z', 'IV3_exp_ratio_med'):
            continue
        out, _, _ = ivtools.fit(dd, z, 'raw20')
        out.update(instrument=z, rows=rows_tag)
        fits.append(out)
        print(f"{z:22s} {rows_tag:32s} N {out['N']:6,} | non-cheap {out['b_price']:7.3f} ({out['se_price']:.3f}) | x cheap {out['b_x']:7.3f} "
              f"({out['se_x']:.3f}) | total {out['cheap_total']:7.2f} | F {out['F_price']:.1f}/{out['F_x']:.1f} | avg e {out['avg_e']:.2f} | e>0 {out['share_pos_e']:.4f}", flush=True)
pd.DataFrame(fits).to_csv('step30_iv_compare_fits.csv', index=False)
