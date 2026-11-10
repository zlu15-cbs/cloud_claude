"""Asset class from CRSP's own style code (crsp_obj_cd) instead of cluster map + name keywords, for model 1's instrument.

Mapping (CRSP MFDB Guide, Appendix A, "CRSP Style Code"):
  ED*  -> us_equity        EF* -> intl_equity
  EDSR/EFSR (real estate), EDSO/EFSO (gold), EDSC/EFSC (commodities) -> real_asset
  I*, OM (mortgage-backed) -> bond        M* (mixed, target) -> allocation        O, OC (alternatives, currency) -> other
Fund-level code = the fund's most common crsp_obj_cd over its CRSP records; asset class per market_m_index = the most
common fund class among family-id funds tracking it (as asset_class.classify_by_index).

Variants of Z_flag (CRSP share-class flags; same family, same share class, other asset class, same month; median):
  ours        cluster map, then keywords, then index code (asset_class.classify)  -> must reproduce -8.019
  crsp        CRSP style code only
  clus_crsp   cluster map first, CRSP style code for the rest (replaces only the keyword / index-code rules)
Each x gene_idx on the grid rows: demand (slopes, F, e>0, Table 5, leads); then downstream on all 108,300 rows as
step34 (markups PC/B0/B25/B50/B65, eta by candidate, negative MC, conduct scheme A) and step35 location.
    python step36_asset_class_crsp.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step36_agree.csv, step36_demand.csv, step36_mc.csv, step36_scale.csv, step36_conduct.csv, step36_where.csv.
"""
import numpy as np
import pandas as pd

import common
import downstream as ds
from asset_class import CLUSTER, classify
from ivbuild import _leave_out
from new_iv import load_new_iv_sample, share_class
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables
from step32_demand_grid import cheap, run
from tiers import RAW
from tiers_crsp import CRSP


def crsp_class(code):
    c = str(code)
    if c[:4] in ('EDSR', 'EFSR', 'EDSO', 'EFSO', 'EDSC', 'EFSC'):
        return 'real_asset'
    if c.startswith('ED'):
        return 'us_equity'
    if c.startswith('EF'):
        return 'intl_equity'
    if c.startswith('I') or c == 'OM':
        return 'bond'
    if c.startswith('M'):
        return 'allocation'
    if c.startswith('O'):
        return 'other'
    return np.nan


def per_index(raw, cls):
    key_i = raw.market_m_index.fillna('_none_' + raw.product_j.astype(str))
    t = pd.DataFrame({'i': key_i, 'cls': cls, 'pj': raw.product_j})[raw.firm_f_old.notna()].drop_duplicates('pj')
    return key_i.map(t.groupby('i').cls.agg(lambda s: s.value_counts().index[0])).fillna(cls)


raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna()].copy()
c = pd.read_csv(CRSP, usecols=['crsp_fundno', 'crsp_obj_cd'], encoding='latin-1', dtype={'crsp_obj_cd': str}).dropna()
fund_code = c.groupby('crsp_fundno').crsp_obj_cd.agg(lambda s: s.value_counts().index[0])
raw['obj'] = raw.product_j.map(fund_code)
print(f'raw rows {len(raw):,}; fund-level crsp_obj_cd present {raw.obj.notna().mean():.4f}', flush=True)
crsp_fund = raw.obj.map(crsp_class)
ours_fund = classify(raw)
raw['ac_ours'] = per_index(raw, ours_fund)
raw['ac_crsp'] = per_index(raw, crsp_fund.fillna(ours_fund))
raw['ac_clus_crsp'] = per_index(raw, raw.market_m_cluster.map(CLUSTER).fillna(crsp_fund).fillna(ours_fund))

raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
fl = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund'], encoding='latin-1')
fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})
raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
mf = raw.ETF_ind == 0
raw['scf'] = np.select([~mf, raw.inst_fund == 'Y', raw.retail_fund == 'Y'], ['etf', 'inst', 'retail'], share_class(raw))
r = raw[raw.firm_f_old.notna()]

# agreement, family-id rows of the raw file
fam = r.copy()
agree = []
for v in ('crsp', 'clus_crsp'):
    diff = fam.ac_ours != fam[f'ac_{v}']
    tab = pd.crosstab(fam.ac_ours, fam[f'ac_{v}'])
    print(f'\n[{v}] fund-months (family rows) with a different class from ours: {diff.mean():.3f}\n{tab}', flush=True)
    top = (fam[diff].groupby(['market_m_index', 'ac_ours', f'ac_{v}'])
           .agg(fund_months=('product_j', 'size'), funds=('product_j', 'nunique'),
                example=('product_fund_name', lambda s: s.value_counts().index[0][:60]))
           .reset_index().sort_values('fund_months', ascending=False))
    print(top.head(15).to_string(index=False), flush=True)
    agree.append(top.assign(variant=v, share_rows_differ=float(diff.mean())))
pd.concat(agree).to_csv('step36_agree.csv', index=False)

ivs = {'ours': _leave_out(r, 'ac_ours', 'Z_ours'), 'crsp': _leave_out(r, 'ac_crsp', 'Z_crsp'),
       'clus_crsp': _leave_out(r, 'ac_clus_crsp', 'Z_clus_crsp')}

d = add_variables(common.load('index'))
funds = top15(d)
d = d.join(cheap, on='product_ids')
for z in ivs.values():
    d = d.merge(z, on=['product_ids', 'month_t'], how='left')
grid = load_new_iv_sample()[['product_ids', 'month_t']].assign(grid=1)
d = d.merge(grid, on=['product_ids', 'month_t'], how='left').reset_index(drop=True)
d['grid'] = d.grid.fillna(0).astype(int)
print('\ncorr with Z_ours (grid rows):', d[d.grid == 1][['Z_ours', 'Z_crsp', 'Z_clus_crsp']].corr().iloc[0].round(4).to_dict(), flush=True)

# downstream helpers
p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
nm = d.product_fund_name.fillna('').str.lower()
d['size'] = np.select([nm.str.contains('small|micro'), nm.str.contains('mid')], ['small/micro', 'mid'], 'other')
d['grp_firm'] = np.where(d.firm_ids.isin(ds.BIG3), d.firm_ids, 'other firms')
d['spy'] = d.product_fund_name.fillna('').str.startswith('SPDR S&P 500 ETF Trust')

dem, mcs, scs, cds, wh = [], [], [], [], []
for v in ivs:
    z = f'Z_{v}'
    est = d[(d.grid == 1) & d[z].notna()].reset_index(drop=True)
    o, _ = run(est, z, 'gene_idx', f'{z} x gene_idx', funds)
    o['variant'] = v
    dem.append(o)
    if v == 'ours' and abs(o['b_price'] + 8.019) > 1e-3:
        raise SystemExit(f'reference does not reproduce -8.019: {o["b_price"]:.4f}')
    alpha = o['b_price'] + o['b_x'] * d.gene_idx.to_numpy()
    mus = {m: ds.markups(d, alpha, k) for m, k in ds.CONDUCT.items()}
    scale = {m: ds.scale_iv(d, p - mus[m]) for m in ds.CONDUCT}
    scs += [dict(variant=v, candidate=m, **scale[m]) for m in ds.CONDUCT]
    for m in ds.CONDUCT:
        mc = p + scale[m]['eta'] * logq - mus[m]
        mcs.append(dict(variant=v, candidate=m, eta=scale[m]['eta'], share_neg_markup=float((mus[m] < 0).mean()), **ds.neg_stats(d, mc)))
        if m in ('B0', 'B65'):
            neg = mc < 0
            tot = neg.sum()
            for gcol in ('grp_firm', 'size', 'spy', 'gene_idx'):
                for g, idx in d.groupby(gcol).indices.items():
                    wh.append(dict(variant=v, candidate=m, group_by=gcol, group=str(g), share_neg=float(neg[idx].mean()),
                                   share_of_all_neg=float(neg[idx].sum() / tot) if tot else np.nan))
    print(f'  [{v}] eta {[round(scale[m]["eta"], 4) for m in ds.CONDUCT]} | neg-MC share own eta '
          f'{[round(x["neg_share"], 3) for x in mcs[-5:]]} | min MC {min(x["mc_min"] for x in mcs[-5:]):.3f}', flush=True)
    cd = ds.conduct_test(d, mus, {m: 0.024 for m in ds.CONDUCT}).assign(variant=v, eta_scheme='A: 0.024')
    cds.append(cd)
    for iv in cd.iv_set.unique():
        s = cd[cd.iv_set == iv]
        print(f'  [{v}] conduct {iv:28s} selected {s[s.selected].candidate.tolist()}', flush=True)

pd.DataFrame(dem).drop(columns=['res', 'dd'], errors='ignore').to_csv('step36_demand.csv', index=False)
pd.DataFrame(mcs).to_csv('step36_mc.csv', index=False)
pd.DataFrame(scs).to_csv('step36_scale.csv', index=False)
pd.concat(cds).to_csv('step36_conduct.csv', index=False)
pd.DataFrame(wh).to_csv('step36_where.csv', index=False)
