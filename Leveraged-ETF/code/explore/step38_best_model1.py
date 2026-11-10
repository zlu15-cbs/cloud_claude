"""Candidate "best model 1": Z x gene_idx, logit IV, index market. One change at a time from model 1:
  asset class   ours  = cluster map -> name keywords -> index code (asset_class.classify), mode per index on family rows
                lip   = Lipper class (CRSP lipper_class, fund's most common) mapped below; mode per market_m_index over all
                        funds; CRSP style code, then ours, where Lipper is missing (0.04% of rows)
  family        old   = firm_f_old (CRSP management code)
                fill  = firm_f_old; for rows without it, the parent firm firm_f (= firm_ids) with ALL that firm's funds as donors
                firm  = firm_f for every row
  fallback      none  = instrument missing when no same-family, same-share-class fund in another asset class that month
                fb    = then the same-family median across all share classes in other asset classes (flagged)
  sample        grid  = also restrict to the old keyword-Z rows (model 1 as run so far); all = every Table 2 row with Z defined
Instrument: median expense ratio of the donor funds k in the raw index file in month t (k != j's asset class, same family,
same CRSP-flag share class). Demand: delta = a p + a_x p*gene_idx + |TE| + past 1y return + log age + fund FE + month FE;
instruments Z, Z*gene_idx; SE clustered by month.
The 4 money market funds (437 fund-months) are dropped from estimation, supply and donors in every variant but R0.
Downstream (the remaining 107,863 rows): markups PC/B0/B25/B50/B65, eta by candidate, negative MC at own eta, location,
pyRVtest conduct (eta 0.024), for variants with no upward-sloping demand and min F >= 10.
    python step38_best_model1.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step38_{demand,mc,scale,conduct,where,classes}.csv.
"""
import numpy as np
import pandas as pd

import common
import downstream as ds
from asset_class import classify
from new_iv import load_new_iv_sample, share_class
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables
from step32_demand_grid import cheap, run
from tiers import RAW
from tiers_crsp import CRSP


def crsp_class(code):  # as step36 (CRSP style code -> class); copied because step36 runs on import
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

LIP_ALLOC = ('FX', 'B', 'BT', 'GX', 'CV')
LIP_REAL = ('RE', 'GRE', 'IRE', 'AU', 'CMG', 'CMP', 'CME', 'CMM', 'CMA', 'CMD', 'RR')
LIP_OTHER = ('LSE', 'OS', 'AED', 'AGM', 'ABR', 'AMS', 'MFF', 'EMN', 'DSB', 'DL', 'ALT', 'CRX', 'EMP')
LIP_INTL = ('EM', 'EU', 'CH', 'LT', 'JA', 'XJ', 'PC', 'INR', 'FM', 'IF', 'GL', 'GEI', 'GSME', 'GTK', 'GNR', 'GFS', 'GH', 'GIF')


def lipper_class(code, asset_cd):
    c = str(code)
    if c in LIP_OTHER:
        return 'other'
    if c.startswith(('MAT', 'MTA')) or c in LIP_ALLOC:
        return 'allocation'
    if c in LIP_REAL:
        return 'real_asset'
    if asset_cd in ('TX', 'MB'):
        return 'bond'
    if c in LIP_INTL or c.startswith(('IML', 'ILC', 'ISM', 'IEI', 'IFCE', 'IFGE', 'GML', 'GLC', 'GLV', 'GLG')):
        return 'intl_equity'
    if c == 'nan':
        return np.nan
    return 'us_equity'


def mode_per_index(raw, cls, rows):
    key_i = raw.market_m_index.fillna('_none_' + raw.product_j.astype(str))
    t = pd.DataFrame({'i': key_i, 'cls': cls, 'pj': raw.product_j})[rows & cls.notna()].drop_duplicates('pj')
    return key_i.map(t.groupby('i').cls.agg(lambda s: s.value_counts().index[0])).fillna(cls)


def leave_out(r, fam, ac, sc, name):
    """median fee of same family / month / share class (sc=None: any share class), asset class != own."""
    keys = [fam, 'month_t'] + ([sc] if sc else [])
    rr = r[r[fam].notna()]
    tab = pd.concat([rr[rr[ac] != a].groupby(keys).product_exp_ratio.median().rename(name).reset_index().assign(**{ac: a})
                     for a in sorted(rr[ac].dropna().unique())])
    k = r[['product_j', 'month_t', ac] + keys[:1] + keys[2:]].merge(tab, on=keys + [ac], how='left')
    return k[name].to_numpy()


# Money market funds in the Table 2 sample: flagged by Lipper class (ITM/UST/IUS/MM), CRSP style code IM* and the fund
# name alike. Not index funds: dropped from estimation, the supply side and the donor pool of every variant except R0.
MMF = (17490, 17491, 62651, 10509)

# ---------------- raw file: classes, families, share classes ----------------
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old', 'firm_f',
                                'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna() & ~raw.product_j.isin(MMF)].reset_index(drop=True)
lp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'lipper_class', 'lipper_asset_cd', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
lp['crsp_fundno'] = lp.crsp_fundno.astype(float).astype(int)
lp = lp[lp.crsp_fundno.isin(raw.product_j)]
lmode = lp.dropna(subset=['lipper_class']).groupby('crsp_fundno').lipper_class.agg(lambda s: s.value_counts().index[0])
acd = lp.dropna(subset=['lipper_class']).drop_duplicates('lipper_class').set_index('lipper_class').lipper_asset_cd
omode = lp.dropna(subset=['crsp_obj_cd']).groupby('crsp_fundno').crsp_obj_cd.agg(lambda s: s.value_counts().index[0])
ours_fund = classify(raw)
lc = raw.product_j.map(lmode)
lip_fund = pd.Series([lipper_class(c, acd.get(c)) for c in lc], index=raw.index)
lip_fund = lip_fund.fillna(raw.product_j.map(omode).map(crsp_class)).fillna(ours_fund)
raw['ac_ours'] = mode_per_index(raw, ours_fund, raw.firm_f_old.notna())
raw['ac_lip'] = mode_per_index(raw, lip_fund, pd.Series(True, index=raw.index))
print(f'raw rows {len(raw):,}; Lipper class present {lc.notna().mean():.4f}; fund-months classed differently (lip vs ours) '
      f'{(raw.ac_lip != raw.ac_ours).mean():.3f}', flush=True)
print(pd.crosstab(raw.ac_ours, raw.ac_lip), flush=True)
dis = (raw[raw.ac_lip != raw.ac_ours].groupby(['market_m_index', 'ac_ours', 'ac_lip'])
       .agg(fund_months=('product_j', 'size'), example=('product_fund_name', lambda s: s.value_counts().index[0][:60]))
       .reset_index().sort_values('fund_months', ascending=False))
dis.to_csv('step38_classes.csv', index=False)
print(dis.head(25).to_string(index=False), flush=True)

raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
fl = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund'], encoding='latin-1')
fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})
raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
mf = raw.ETF_ind == 0
raw['scf'] = np.select([~mf, raw.inst_fund == 'Y', raw.retail_fund == 'Y'], ['etf', 'inst', 'retail'], share_class(raw))

Z = raw[['product_j', 'month_t']].rename(columns={'product_j': 'product_ids'}).copy()
for ac in ('ours', 'lip'):
    a = f'ac_{ac}'
    z_old = leave_out(raw, 'firm_f_old', a, 'scf', 'z')
    z_firm = leave_out(raw, 'firm_f', a, 'scf', 'z')
    fb_old = leave_out(raw, 'firm_f_old', a, None, 'z')
    fb_firm = leave_out(raw, 'firm_f', a, None, 'z')
    has_old = raw.firm_f_old.notna().to_numpy()
    z_fill = np.where(has_old, z_old, z_firm)
    fb_fill = np.where(has_old, fb_old, fb_firm)
    Z[f'Z_{ac}_old'] = z_old
    Z[f'Z_{ac}_fill'] = z_fill
    Z[f'Z_{ac}_firm'] = z_firm
    Z[f'Z_{ac}_fill_fb'] = np.where(np.isnan(z_fill), fb_fill, z_fill)
    Z[f'Z_{ac}_firm_fb'] = np.where(np.isnan(z_firm), fb_firm, z_firm)

# ---------------- estimation ----------------
import ivbuild
d = add_variables(common.load('index'))
funds = top15(d)
d = d.join(cheap[['gene_idx']], on='product_ids').merge(Z, on=['product_ids', 'month_t'], how='left')
d = d.merge(ivbuild.build()[['product_ids', 'month_t', 'Z_flag']].rename(columns={'Z_flag': 'Z_R0'}), on=['product_ids', 'month_t'], how='left')
grid = load_new_iv_sample()[['product_ids', 'month_t']].assign(grid=1)
d = d.merge(grid, on=['product_ids', 'month_t'], how='left').reset_index(drop=True)
d['grid'] = d.grid.fillna(0).astype(int)
assert len(d) == 108300
# R0 (model 1 exactly as run, money market funds included): demand only, reproduces -8.019
r0 = d[d.Z_R0.notna() & (d.grid == 1)].reset_index(drop=True)
o, _ = run(r0, 'Z_R0', 'gene_idx', 'R0 model 1 as run, with MMFs', funds)
if abs(o['b_price'] + 8.019) > 1e-3:
    raise SystemExit(f'R0 does not reproduce -8.019: {o["b_price"]:.4f}')
dem = [dict(o, variant='R0 model 1 as run, with MMFs', instrument='Z_R0', grid=True)]
d = d[~d.product_ids.isin(MMF)].reset_index(drop=True)
print(f'supply / estimation universe without money market funds: {len(d):,} fund-months', flush=True)

VARIANTS = [  # label, instrument column, grid restriction (all without money market funds)
    ('V0 ours, old, grid', 'Z_ours_old', True),
    ('V1 ours, old, no grid', 'Z_ours_old', False),
    ('V2 Lipper, old', 'Z_lip_old', False),
    ('V3 Lipper, fill', 'Z_lip_fill', False),
    ('V4 Lipper, firm', 'Z_lip_firm', False),
    ('V5 Lipper, fill + fallback', 'Z_lip_fill_fb', False),
    ('V6 Lipper, firm + fallback', 'Z_lip_firm_fb', False),
    ('V7 ours, fill + fallback', 'Z_ours_fill_fb', False),
]
p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
nm = d.product_fund_name.fillna('').str.lower()
d['size'] = np.select([nm.str.contains('small|micro'), nm.str.contains('mid')], ['small/micro', 'mid'], 'other')
d['grp_firm'] = np.where(d.firm_ids.isin(ds.BIG3), d.firm_ids, 'other firms')
d['spy'] = d.product_fund_name.fillna('').str.startswith('SPDR S&P 500 ETF Trust')
d['ac'] = d[['product_ids', 'month_t']].merge(raw[['product_j', 'month_t', 'ac_lip']].rename(columns={'product_j': 'product_ids'}),
                                             on=['product_ids', 'month_t'], how='left').ac_lip.to_numpy()

mcs, scs, cds, wh = [], [], [], []
fits = {}
for label, z, use_grid in VARIANTS:  # stage 1: demand for every variant
    est = d[d[z].notna() & ((d.grid == 1) if use_grid else True)].reset_index(drop=True)
    o, _ = run(est, z, 'gene_idx', label, funds)
    o.update(variant=label, instrument=z, grid=use_grid, corr_with_V0=float(d[[z, 'Z_ours_old']].dropna().corr().iloc[0, 1]))
    dem.append(o)
    fits[label] = o
pd.DataFrame(dem).to_csv('step38_demand.csv', index=False)
for label, z, use_grid in VARIANTS:  # stage 2: downstream for variants passing the demand screens
    o = fits[label]
    if o['share_pos_e'] > 0 or o['min_F'] < 10:
        continue
    print(f'\n--- downstream: {label}', flush=True)
    alpha = o['b_price'] + o['b_x'] * d.gene_idx.to_numpy()
    mus = {m: ds.markups(d, alpha, k) for m, k in ds.CONDUCT.items()}
    scale = {m: ds.scale_iv(d, p - mus[m]) for m in ds.CONDUCT}
    scs += [dict(variant=label, candidate=m, **scale[m]) for m in ds.CONDUCT]
    for m in ds.CONDUCT:
        mc = p + scale[m]['eta'] * logq - mus[m]
        mcs.append(dict(variant=label, candidate=m, eta=scale[m]['eta'], mean_markup=float(mus[m].mean()),
                        share_neg_markup=float((mus[m] < 0).mean()), **ds.neg_stats(d, mc)))
        if m in ('B0', 'B65'):
            neg = mc < 0
            tot = neg.sum()
            for gcol in ('grp_firm', 'size', 'spy', 'gene_idx', 'ac'):
                for g, idx in d.groupby(gcol).indices.items():
                    wh.append(dict(variant=label, candidate=m, group_by=gcol, group=str(g), fund_months=len(idx),
                                   share_neg=float(neg[idx].mean()), share_of_all_neg=float(neg[idx].sum() / tot) if tot else np.nan))
    print(f'  eta {[round(scale[m]["eta"], 4) for m in ds.CONDUCT]} | neg-MC share {[round(x["neg_share"], 4) for x in mcs[-5:]]} '
          f'| min MC {min(x["mc_min"] for x in mcs[-5:]):.3f}', flush=True)
    for scheme, etas in (('A: 0.024', {m: 0.024 for m in ds.CONDUCT}),):  # scheme C matched A in every earlier run
        cd = ds.conduct_test(d, mus, etas).assign(variant=label, eta_scheme=scheme)
        cds.append(cd)
        print(f'  [{scheme}] ' + ' | '.join(f'{iv.split(":")[0]}: {cd[(cd.iv_set == iv) & cd.selected].candidate.tolist()}'
                                           for iv in cd.iv_set.unique()), flush=True)
    pd.concat(cds).to_csv('step38_conduct.csv', index=False)

pd.DataFrame(mcs).to_csv('step38_mc.csv', index=False)
pd.DataFrame(scs).to_csv('step38_scale.csv', index=False)
pd.concat(cds).to_csv('step38_conduct.csv', index=False)
pd.DataFrame(wh).to_csv('step38_where.csv', index=False)
