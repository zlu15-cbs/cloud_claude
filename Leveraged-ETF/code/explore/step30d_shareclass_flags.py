"""Does using CRSP's retail_fund / inst_fund flags instead of name keywords change Z and the benchmark?
(Danny, 3 Nov 2026: "classification of retail vs. institutional using only keywords is undesirable since CRSP has the flag".)

Share-class rules compared (ETF_ind == 1 -> etf in all of them):
  kw     ours (new_iv.share_class): name keywords with word boundaries
  flag   CRSP flags only: inst_fund == Y -> inst; else retail_fund == Y -> retail; else other
  flagkw CRSP flags first; where neither flag is Y, our keywords
  danny  Danny's R rule: inst if inst_fund == Y or loose keyword; else retail if retail_fund == Y or loose keyword; else other
Z is rebuilt with each rule (same family firm_f_old, same share class, other asset class, same month; raw index file),
then the benchmark (price x raw20, fund + month FE) is re-estimated on the rows where every version is defined.

    python step30d_shareclass_flags.py      # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd

import ivtools
from asset_class import classify_by_index
from new_iv import load_new_iv_sample, share_class
from tiers import RAW
from tiers_crsp import CRSP

raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna() & raw.firm_f_old.notna()].copy()
raw['ac'] = classify_by_index(raw)
raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
fl = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund'], encoding='latin-1')
fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})
n0 = len(raw)
raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
assert len(raw) == n0
mf = raw.ETF_ind == 0
print(f'raw fund-months {len(raw):,}; mutual-fund rows {mf.sum():,}; CRSP flag row found for {raw.inst_fund.notna()[mf].mean():.3f} of MF rows', flush=True)
print('MF rows: inst_fund x retail_fund\n', pd.crosstab(raw.inst_fund[mf].fillna('NA'), raw.retail_fund[mf].fillna('NA')), flush=True)
yrs = raw[mf].assign(y=np.floor(raw.month_t[mf])).groupby('y').apply(lambda g: ((g.inst_fund == 'Y') | (g.retail_fund == 'Y')).mean())
print('MF rows with a Y flag, by year:', yrs.round(2).to_dict(), flush=True)

raw['sc_kw'] = share_class(raw)
I, R = raw.inst_fund == 'Y', raw.retail_fund == 'Y'
raw['sc_flag'] = np.select([~mf, I, R], ['etf', 'inst', 'retail'], 'mf_other')
raw['sc_flagkw'] = np.select([~mf, I, R], ['etf', 'inst', 'retail'], raw.sc_kw)
nm = raw.product_fund_name.fillna('').str.lower()
li = I | nm.str.contains('institutional|inst|class i|class k|class y|class z|class r6|premier|select|admiral')
lr = R | nm.str.contains('investor|retail|class a|class c|class r|class t|service|advisor')
raw['sc_danny'] = np.select([~mf, li, lr], ['etf', 'inst', 'retail'], 'mf_other')
print('\nkeywords (rows) vs CRSP flags (cols), MF rows:\n', pd.crosstab(raw.sc_kw[mf], raw.sc_flag[mf], margins=True), flush=True)

d = load_new_iv_sample()
for v in ('kw', 'flag', 'flagkw', 'danny'):
    sc = f'sc_{v}'
    tab = pd.concat([raw[raw.ac != a].groupby(['firm_f_old', 'month_t', sc]).product_exp_ratio.median().rename(f'Z_{v}').reset_index().assign(ac=a)
                     for a in sorted(raw.ac.unique())])
    k = raw[['product_j', 'month_t', 'ac', 'firm_f_old', sc]].merge(tab, on=['firm_f_old', 'month_t', 'ac', sc], how='left')
    d = d.merge(k[['product_j', 'month_t', f'Z_{v}']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
assert np.allclose(d.Z, d.Z_kw), 'Z_kw must reproduce Z'
rows = d.dropna(subset=['Z_flag', 'Z_flagkw', 'Z_danny'])
print(f'\nrows with every version defined: {len(rows):,} of {len(d):,}', flush=True)
out = []
for v in ('kw', 'flag', 'flagkw', 'danny'):
    z = f'Z_{v}'
    o, _, _ = ivtools.fit(rows, z, 'raw20')
    o.update(rule=v, corr_with_Z=float(np.corrcoef(rows.Z, rows[z])[0, 1]), share_equal_Z=float((np.abs(rows.Z - rows[z]) < 1e-9).mean()))
    out.append(o)
    print(f"{v:7s} corr(Z) {o['corr_with_Z']:.3f} equal {o['share_equal_Z']:.3f} | non-cheap {o['b_price']:7.3f} ({o['se_price']:.3f}) | x cheap {o['b_x']:7.3f} "
          f"({o['se_x']:.3f}) | total {o['cheap_total']:7.2f} | F {o['F_price']:.1f}/{o['F_x']:.1f} | avg e {o['avg_e']:.2f} | e>0 {o['share_pos_e']:.4f}", flush=True)
pd.DataFrame(out).to_csv('step30d_shareclass_flags.csv', index=False)
