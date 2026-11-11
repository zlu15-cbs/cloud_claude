"""High-entry-fee funds (entry-fee quartiles 3 and 4): does another instrument remove the upward-sloping demand?

One fee slope, fund and month effects, month-clustered SE, estimated on the high-fee funds alone (and subgroups).
Instruments tried:
  family fee instruments (same family, same month), varying the donors
    v2            other broad asset class, same share type, median (V2's Z)
    noncheap      as v2, donors restricted to funds that are not cheap (entry-fee quartile 2-4)
    highfee       as v2, donors restricted to entry-fee quartiles 3-4
    specialized   as v2, donors restricted to specialized funds
    highfee_pool  as highfee, share types pooled
    niche_idx     other index (any asset class), same share type, donors in quartiles 3-4, lag-AUM-weighted mean
    v2_lag12      v2 lagged 12 months
    paper         the paper's IV0;  hausman1 / mgmt_fee / op_cost: the build's other Hausman variants
  rival instruments (other families), from the build
    rivals_index / rivals_cluster   number of other-family funds on the same index / index cluster
    newprod_index / newprod_cluster number of other-family funds launched in the last year on the same index / cluster
  v2 with extra fixed effects: asset class x month, share type x month, specialized x month, family x year
"""
import os, sys
import numpy as np, pandas as pd, pyblp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2
from sc_build import CRSP, DATA, PANEL
pyblp.options.verbose = False
C = v2.CONTROLS
CSVP = f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv'
d = pd.read_pickle(PANEL)
d['mk'] = np.round(d.month_t * 12).astype(int)
cf = pd.read_csv(CSVP, usecols=['product_j', 'month_t', 'product_exp_ratio', 'product_L1_mtna', 'broad_specialized']).dropna(subset=['product_exp_ratio'])
x = cf[cf.month_t >= 2005 - 1e-9]
x = x.assign(r=x.groupby('month_t').product_exp_ratio.rank(pct=True))
rank = x.sort_values('month_t').groupby('product_j').r.first()
rank_all = cf.assign(r=cf.groupby('month_t').product_exp_ratio.rank(pct=True)).sort_values('month_t').groupby('product_j').r.first()
qf = np.clip(np.ceil(rank.reindex(rank_all.index).fillna(rank_all) * 4), 1, 4)       # entry-fee quartile per fund, all CSV funds
specf = (cf.groupby('product_j').broad_specialized.agg(lambda s: (s != 'broad-based').mean()) > 0.5)

mmf_ids = set(d.loc[d.mmf == 1, 'product_ids'])
crsp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
mmf = v2.money_market_funds(crsp, set(cf.product_j)); del crsp
raw = v2.build_instrument(CSVP, CRSP, mmf)
raw['mk'] = np.round(raw.month_t * 12).astype(int)
raw = raw.merge(cf[['product_j', 'month_t', 'product_L1_mtna']], on=['product_j', 'month_t'], how='left')
raw['q'] = raw.product_j.map(qf); raw['spec'] = raw.product_j.map(specf)

def fam_med(mask, same_type=True):
    don = raw[mask & raw.asset_class.notna() & raw.share_class.notna() & raw.firm_f_old.notna()]
    keys = ['firm_f_old', 'month_t'] + (['share_class'] if same_type else [])
    tab = pd.concat([don[don.asset_class != a].groupby(keys).product_exp_ratio.median().rename('z').reset_index().assign(asset_class=a)
                     for a in sorted(don.asset_class.unique())])
    return raw[['product_j', 'mk', 'firm_f_old', 'month_t', 'share_class', 'asset_class']].merge(tab, on=keys + ['asset_class'], how='left').z.to_numpy()

raw['z_v2'] = fam_med(pd.Series(True, index=raw.index))
raw['z_noncheap'] = fam_med(raw.q >= 2)
raw['z_highfee'] = fam_med(raw.q >= 3)
raw['z_specialized'] = fam_med(raw.spec == True)
raw['z_highfee_pool'] = fam_med(raw.q >= 3, same_type=False)
don = raw[(raw.q >= 3) & (raw.product_L1_mtna > 0) & raw.firm_f_old.notna() & raw.market_m_index.notna()].assign(wp=lambda z: z.product_exp_ratio * z.product_L1_mtna)
k1, k2 = ['firm_f_old', 'month_t', 'share_class'], ['firm_f_old', 'month_t', 'share_class', 'market_m_index']
a1 = don.groupby(k1)[['wp', 'product_L1_mtna']].sum().rename(columns={'wp': 'W', 'product_L1_mtna': 'M'}).reset_index()
a2 = don.groupby(k2)[['wp', 'product_L1_mtna']].sum().rename(columns={'wp': 'w', 'product_L1_mtna': 'm'}).reset_index()
t = raw[['product_j', 'mk'] + k2].merge(a1, on=k1, how='left').merge(a2, on=k2, how='left').fillna({'w': 0, 'm': 0})
raw['z_niche_idx'] = np.where(t.M - t.m > 0, (t.W - t.w) / (t.M - t.m).replace(0, np.nan), np.nan)
lag = raw[['product_j', 'mk', 'z_v2']].assign(mk=lambda z: z.mk + 12).rename(columns={'z_v2': 'z_v2_lag12'})
raw = raw.merge(lag, on=['product_j', 'mk'], how='left')
zc = [c for c in raw.columns if c.startswith('z_')]
d = d.merge(raw[['product_j', 'mk'] + zc].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'mk'], how='left')
assert np.allclose(d.z_v2.fillna(-9), d.Z.fillna(-9)), 'rebuilt Z differs from V2'
d['z_paper'] = d.demand_instruments0
for nm, c in (('hausman1', 'BLP_IV_hausman1_exp_ratio'), ('mgmt_fee', 'BLP_IV_hausman_mgmt_fee'), ('op_cost', 'BLP_IV_hausman_op_cost'),
              ('rivals_cluster', 'BLP_IV_rival_funds2'), ('rivals_index', 'BLP_IV_rival_funds3'), ('newprod_cluster', 'BLP_IV_newproduct_2'), ('newprod_index', 'BLP_IV_newproduct_3')):
    d[f'z_{nm}'] = pd.to_numeric(d[c], errors='coerce')
d['q'] = d.product_ids.map(qf); d['spec'] = d.product_ids.map(specf).astype(float)
d['acm'] = d.asset_class.astype(str) + '_' + d.market_ids.astype(str); d['tym'] = d.share_class.astype(str) + '_' + d.market_ids.astype(str)
d['spm'] = d.spec.astype(str) + '_' + d.market_ids.astype(str); d['fy'] = d.firm_ids.astype(str) + '_' + np.floor(d.month_t).astype(int).astype(str)
base = d[(d.mmf == 0) & (d.q >= 3)].reset_index(drop=True)
print(f'high-fee funds (entry-fee quartiles 3-4), Table 2 sample: {len(base):,} fund-months, {base.product_ids.nunique()} funds; with V2 Z {int(base.Z.notna().sum()):,}')
print('correlation of the family instruments with V2 Z (after fund and month effects are not removed):')
print(base[[c for c in base.columns if c.startswith('z_')]].corr().z_v2.round(2).to_string())

def fit1(est, iv, extra=None):
    dd = est[est[iv].notna() & np.isfinite(est[iv])].drop(columns=[c for c in est.columns if c.startswith('demand_instruments')]).reset_index(drop=True)
    dd['demand_instruments0'] = dd[iv].to_numpy(float)
    ab = 'C(product_ids) + C(market_ids)' + (f' + C({extra})' if extra else '')
    res = pyblp.Problem(pyblp.Formulation(' + '.join(['prices'] + C), absorb=ab), dd).solve(se_type='clustered')
    b = dict(zip(res.beta_labels, res.beta.flatten())); se = dict(zip(res.beta_labels, res.beta_se.flatten()))
    f = v2.sw_f(dd, ['prices'], ['demand_instruments0'])['prices'] if not extra else np.nan
    return len(dd), dd.product_ids.nunique(), b['prices'], se['prices'], f

SAMPLES = {'all high-fee': base.index >= 0, 'specialized': base.spec == 1, 'broad-based': base.spec == 0, 'ETFs': base.share_class == 'etf',
           'quartile 3 only': base.q == 3, 'Big 3 families': base.firm_ids.isin(v2.BIG3) if hasattr(v2, 'BIG3') else base.index < 0, 'other families': ~base.firm_ids.isin(getattr(v2, 'BIG3', []))}
IVS = [(c[2:], c, None) for c in ('z_v2', 'z_noncheap', 'z_highfee', 'z_specialized', 'z_highfee_pool', 'z_niche_idx', 'z_v2_lag12', 'z_paper', 'z_hausman1', 'z_mgmt_fee', 'z_op_cost',
                                   'z_rivals_index', 'z_rivals_cluster', 'z_newprod_index', 'z_newprod_cluster')]
IVS += [('v2 + asset class x month FE', 'z_v2', 'acm'), ('v2 + share type x month FE', 'z_v2', 'tym'), ('v2 + specialized x month FE', 'z_v2', 'spm'), ('v2 + family x year FE', 'z_v2', 'fy')]
rows = []
for sname, sm in SAMPLES.items():
    est = base[np.asarray(sm)].reset_index(drop=True)
    print(f'\n=== {sname}: {len(est):,} fund-months', flush=True)
    for nm, col, extra in IVS:
        try:
            n, nf, b, se, f = fit1(est, col, extra)
            rows.append(dict(sample=sname, iv=nm, N=n, funds=nf, slope=b, se=se, F=f))
            print(f'  {nm:30s} N {n:>6,} funds {nf:>4} | fee slope {b:9.3f} ({se:.3f}) | F {f:6.1f}', flush=True)
        except Exception as ex:
            print(f'  {nm:30s} failed: {str(ex)[:90]}', flush=True)
    pd.DataFrame(rows).to_csv('sc_highfee_iv.csv', index=False)
