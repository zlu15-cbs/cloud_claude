"""Two checks on V2 (step38: Lipper asset class, firm_f_old family, CRSP-flag share class, no grid, gene_idx).
  (1) Why V2 estimates on 96,142 of the 107,863 non-money-market Table 2 rows: break the rows without an instrument into
      (a) no family code (firm_f_old missing), (b) family has no fund in another asset class that month,
      (c) family has such funds but none in the same share class.
  (2) step38 dropped only the 4 money market funds that are in the Table 2 sample. The raw index file (the donor pool)
      holds more money market share classes (Lipper MM/ITM/IUS/UST/IMM, CRSP style IM*, or "money market" in the name).
      Re-estimate V2 with all of them dropped from the donor pool. Fidelity Series Treasury Bill Index Fund (94017) is a
      T-bill index fund, not a money market fund, and stays.
Before/after against step38's V2 (logs/step38_demand.csv). Downstream as step38, for V2 with the full donor drop.
    python step40_v2_rows_mmf_donors.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step40_{rows,demand,mc,scale,conduct,where}.csv.
"""
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'step38_best_model1.py'), encoding='utf-8').read()
exec(src[:src.index('# Money market funds in the Table 2 sample')])  # imports and helpers of step38, unchanged

MMF4 = (17490, 17491, 62651, 10509)
NOT_MMF = (94017,)

raw0 = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old', 'firm_f',
                                 'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw0 = raw0[raw0.product_exp_ratio.notna()].reset_index(drop=True)
lp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund', 'lipper_class', 'lipper_asset_cd',
                                'crsp_obj_cd', 'fund_name'], encoding='latin-1', dtype=str)
lp['crsp_fundno'] = lp.crsp_fundno.astype(float).astype(int)
lp = lp[lp.crsp_fundno.isin(raw0.product_j)]
# a money market fund: "money market" in a CRSP name AND (a money-market Lipper class or CRSP style code IM*) in some quarter.
# Requiring both avoids false hits such as 32066 (Wells Fargo Equity Index Fund, one stray IMM code in 1998) and 94017.
by_name = set(lp.loc[lp.fund_name.fillna('').str.contains('money market', case=False), 'crsp_fundno'])
by_code = set(lp.loc[lp.lipper_class.isin(['MM', 'ITM', 'IUS', 'UST', 'IMM']) | lp.crsp_obj_cd.fillna('').str.startswith('IM'), 'crsp_fundno'])
MMF_ALL = tuple(sorted((by_name & by_code) - set(NOT_MMF)))
nm = raw0[raw0.product_j.isin(MMF_ALL)].groupby('product_j').agg(fund_months=('month_t', 'size'),
                                                                 name=('product_fund_name', 'last'))
print(f'money market share classes in the raw index file: {len(MMF_ALL)} ({nm.fund_months.sum():,} fund-months, all years)')
print(nm.to_string(), flush=True)

lmode = lp.dropna(subset=['lipper_class']).groupby('crsp_fundno').lipper_class.agg(lambda s: s.value_counts().index[0])
acd = lp.dropna(subset=['lipper_class']).drop_duplicates('lipper_class').set_index('lipper_class').lipper_asset_cd
omode = lp.dropna(subset=['crsp_obj_cd']).groupby('crsp_fundno').crsp_obj_cd.agg(lambda s: s.value_counts().index[0])
fl = lp[['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund']].copy()
fl['quarter'] = fl.quarter.astype(float)
fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})


def build(drop):
    """step38's raw block with `drop` removed from the donor pool: returns raw (with ac_lip, scf) and Z_lip_old."""
    raw = raw0[~raw0.product_j.isin(drop)].reset_index(drop=True)
    ours_fund = classify(raw)
    lc = raw.product_j.map(lmode)
    lip_fund = pd.Series([lipper_class(c, acd.get(c)) for c in lc], index=raw.index)
    lip_fund = lip_fund.fillna(raw.product_j.map(omode).map(crsp_class)).fillna(ours_fund)
    raw['ac_lip'] = mode_per_index(raw, lip_fund, pd.Series(True, index=raw.index))
    raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
    raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
    mf = raw.ETF_ind == 0
    raw['scf'] = np.select([~mf, raw.inst_fund == 'Y', raw.retail_fund == 'Y'], ['etf', 'inst', 'retail'], share_class(raw))
    raw['Z'] = leave_out(raw, 'firm_f_old', 'ac_lip', 'scf', 'z')
    return raw


r4, rall = build(MMF4), build(MMF_ALL)

d = add_variables(common.load('index'))
funds = top15(d)
d = d.join(cheap[['gene_idx']], on='product_ids')
assert len(d) == 108300
d = d[~d.product_ids.isin(MMF4)].reset_index(drop=True)
key = ['product_ids', 'month_t']
for tag, r in (('4', r4), ('all', rall)):
    d = d.merge(r[['product_j', 'month_t', 'Z', 'ac_lip', 'scf', 'firm_f_old']]
                .rename(columns={'product_j': 'product_ids', 'Z': f'Z_{tag}', 'ac_lip': f'ac_{tag}', 'scf': f'scf_{tag}',
                                 'firm_f_old': f'fam_{tag}'}), on=key, how='left')
print(f'\nTable 2 rows without the 4 money market funds: {len(d):,}; V2 rows (Z defined, 4 dropped): {d.Z_4.notna().sum():,}')

# (1) why rows lack the instrument, with step38's donor pool (4 dropped)
r = r4
n_ft = r.groupby(['firm_f_old', 'month_t']).size()
n_fta = r.groupby(['firm_f_old', 'month_t', 'ac_lip']).size()
n_fts = r.groupby(['firm_f_old', 'month_t', 'scf']).size()
n_ftsa = r.groupby(['firm_f_old', 'month_t', 'scf', 'ac_lip']).size()
ix = pd.MultiIndex.from_frame
k = d[['fam_4', 'month_t']].rename(columns={'fam_4': 'firm_f_old'})
other_any = n_ft.reindex(ix(k)).to_numpy() - n_fta.reindex(ix(d[['fam_4', 'month_t', 'ac_4']].set_axis(['firm_f_old', 'month_t', 'ac_lip'], axis=1))).to_numpy()
other_sc = (n_fts.reindex(ix(d[['fam_4', 'month_t', 'scf_4']].set_axis(['firm_f_old', 'month_t', 'scf'], axis=1))).to_numpy()
            - n_ftsa.reindex(ix(d[['fam_4', 'month_t', 'scf_4', 'ac_4']].set_axis(['firm_f_old', 'month_t', 'scf', 'ac_lip'], axis=1))).fillna(0).to_numpy())
d['why'] = np.select([d.fam_4.isna(), np.nan_to_num(other_any) <= 0, np.nan_to_num(other_sc) <= 0],
                     ['a no family code', 'b no family fund in another asset class', 'c none in the same share class'], 'has Z')
chk = pd.crosstab(d.why, d.Z_4.notna())
print(chk, flush=True)
rows = (d.groupby('why').agg(fund_months=('product_ids', 'size'), funds=('product_ids', 'nunique'),
                             share_cheap=('gene_idx', 'mean'), mean_fee=('prices', 'mean'),
                             tna_share=('product_mtna', 'sum'))
        .assign(tna_share=lambda x: x.tna_share / x.tna_share.sum()))
print(rows.to_string(), flush=True)
top = (d[d.why != 'has Z'].groupby(['why', 'product_ids']).agg(fund_months=('month_t', 'size'), name=('product_fund_name', 'last'),
                                                             firm=('firm_ids', 'last'))
       .reset_index().sort_values('fund_months', ascending=False).groupby('why').head(8))
print(top.to_string(index=False), flush=True)
rows.to_csv('step40_rows.csv')

# (2) all money market funds out of the donor pool
both = d.Z_4.notna() & d.Z_all.notna()
chg = both & ~np.isclose(d.Z_4, d.Z_all)
print(f'\nZ defined: 4 dropped {d.Z_4.notna().sum():,}; all dropped {d.Z_all.notna().sum():,}; '
      f'rows whose Z changes {int(chg.sum()):,} ({d.loc[chg, "product_ids"].nunique()} funds); lost {int((d.Z_4.notna() & d.Z_all.isna()).sum()):,}', flush=True)
print(d.loc[chg].groupby('firm_ids').size().sort_values(ascending=False).head(10).to_string(), flush=True)

dem = []
for label, z in (('V2 (step38: 4 dropped from donors)', 'Z_4'), ('V2 (all money market funds dropped from donors)', 'Z_all')):
    est = d[d[z].notna()].reset_index(drop=True)
    o, _ = run(est, z, 'gene_idx', label, funds)
    dem.append(dict(o, variant=label, instrument=z))
pd.DataFrame(dem).to_csv('step40_demand.csv', index=False)
ref = pd.read_csv(os.path.join(HERE, '..', '..', 'logs', 'step38_demand.csv'))
ref = ref[ref.variant == 'V2 Lipper, old'].iloc[0]
if abs(dem[0]['b_price'] - ref.b_price) > 1e-6 or dem[0]['N'] != ref.N:
    print(f'WARNING: Z_4 does not reproduce step38 V2 ({dem[0]["b_price"]:.6f}, N {dem[0]["N"]} vs {ref.b_price:.6f}, N {ref.N})')
else:
    print('Z_4 reproduces step38 V2 exactly', flush=True)

o = dem[1]
if o['share_pos_e'] == 0 and o['min_F'] >= 10:
    p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
    nmf = d.product_fund_name.fillna('').str.lower()
    d['size'] = np.select([nmf.str.contains('small|micro'), nmf.str.contains('mid')], ['small/micro', 'mid'], 'other')
    d['grp_firm'] = np.where(d.firm_ids.isin(ds.BIG3), d.firm_ids, 'other firms')
    d['spy'] = d.product_fund_name.fillna('').str.startswith('SPDR S&P 500 ETF Trust')
    d['ac'] = d.ac_all
    alpha = o['b_price'] + o['b_x'] * d.gene_idx.to_numpy()
    mus = {m: ds.markups(d, alpha, k) for m, k in ds.CONDUCT.items()}
    scale = {m: ds.scale_iv(d, p - mus[m]) for m in ds.CONDUCT}
    mcs, wh = [], []
    for m in ds.CONDUCT:
        mc = p + scale[m]['eta'] * logq - mus[m]
        mcs.append(dict(candidate=m, eta=scale[m]['eta'], mean_markup=float(mus[m].mean()), **ds.neg_stats(d, mc)))
        if m in ('B0', 'B65'):
            neg = mc < 0
            for gcol in ('grp_firm', 'size', 'spy', 'gene_idx', 'ac'):
                for g, idx in d.groupby(gcol).indices.items():
                    wh.append(dict(candidate=m, group_by=gcol, group=str(g), fund_months=len(idx), share_neg=float(neg[idx].mean()),
                                   share_of_all_neg=float(neg[idx].sum() / neg.sum()) if neg.sum() else np.nan))
    pd.DataFrame([dict(candidate=m, **scale[m]) for m in ds.CONDUCT]).to_csv('step40_scale.csv', index=False)
    pd.DataFrame(mcs).to_csv('step40_mc.csv', index=False)
    pd.DataFrame(wh).to_csv('step40_where.csv', index=False)
    print(pd.DataFrame(mcs).to_string(index=False), flush=True)
    cd = ds.conduct_test(d, mus, {m: 0.024 for m in ds.CONDUCT})
    cd.to_csv('step40_conduct.csv', index=False)
    print(' | '.join(f'{iv.split(":")[0]}: {cd[(cd.iv_set == iv) & cd.selected].candidate.tolist()}' for iv in cd.iv_set.unique()), flush=True)
print('done', flush=True)
