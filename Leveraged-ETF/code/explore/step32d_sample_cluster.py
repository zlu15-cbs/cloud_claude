"""Two new dimensions for the demand comparison (cheap = benchmark gene_idx unless noted; fund + month FE; SE by month).

Estimation sample (Danny vs us):
  S108  paper Hausman IV x gene_idx on all 108,300 rows
  S108f Z_flag with the family-less rows pooled into one pseudo-family (as Danny's IV3 does), x gene_idx, all rows
"Index" via market_m_cluster:
  CLX   Z_flag excluding same-family siblings in the same market_m_cluster (instead of the same asset class)
  ACC   Z_flag with the asset class assigned per market_m_cluster instead of per market_m_index
  IDX   Z_flag excluding same-family siblings tracking the same market_m_index (Danny's exclusion; ladder index -> cluster -> asset class)
Z_flag (asset class per index, other asset class) is re-run on its rows as the reference.

    python step32d_sample_cluster.py      # from a folder holding the index CSV and step31_cheap_by_fund.csv
Writes step32d.csv, step32d_funds.csv.
"""
import numpy as np
import pandas as pd

import common
from asset_class import classify
from new_iv import load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, H
from step32_demand_grid import cheap, run
from tiers import RAW
from tiers_crsp import CRSP
from new_iv import share_class

raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna()].copy()
# asset class as in the settled instrument (new_iv / classify_by_index): the per-index (or per-cluster) mode is taken over
# fund-months WITH a family id; family-less rows (pooled variant only) get the mapping of their index, else their own class
cls = classify(raw)
key_i = raw.market_m_index.fillna('_none_' + raw.product_j.astype(str))
fam_mask = raw.firm_f_old.notna()
t = pd.DataFrame({'i': key_i, 'c': raw.market_m_cluster, 'cls': cls, 'pj': raw.product_j})[fam_mask].drop_duplicates('pj')
raw['ac'] = key_i.map(t.groupby('i').cls.agg(lambda s: s.value_counts().index[0])).fillna(cls)
raw['ac_c'] = raw.market_m_cluster.map(t.groupby('c').cls.agg(lambda s: s.value_counts().index[0])).fillna(cls)
raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
fl = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund'], encoding='latin-1')
fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})
raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
mf = raw.ETF_ind == 0
raw['scf'] = np.select([~mf, raw.inst_fund == 'Y', raw.retail_fund == 'Y'], ['etf', 'inst', 'retail'], share_class(raw))
raw['fam_pool'] = raw.firm_f_old.fillna('__no_family__')


def leave_out(r, fam, excl, name):
    """median fee of same family / month / share class, excluding the focal row's `excl` group."""
    if r[excl].nunique() <= 10:  # few groups: complement by group
        tab = pd.concat([r[r[excl] != a].groupby([fam, 'month_t', 'scf']).product_exp_ratio.median().rename(name).reset_index().assign(**{excl: a})
                         for a in sorted(r[excl].dropna().unique())])
    else:  # many groups: drop the focal group's fees from the family pool
        keys = [fam, 'month_t', 'scf']
        own = r.groupby(keys + [excl]).product_exp_ratio.apply(list).rename('own').reset_index()
        own = own.merge(r.groupby(keys).product_exp_ratio.apply(list).rename('all').reset_index(), on=keys)

        def med(row):
            v = list(row['all'])
            for x in row['own']:
                v.remove(x)
            return np.median(v) if v else np.nan
        own[name] = own.apply(med, axis=1)
        tab = own[keys + [excl, name]]
    k = r[['product_j', 'month_t', fam, 'scf', excl]].merge(tab, on=[fam, 'month_t', 'scf', excl], how='left')
    return k[['product_j', 'month_t', name]].rename(columns={'product_j': 'product_ids'})


fam_rows = raw[raw.firm_f_old.notna()]
ivs = [leave_out(fam_rows, 'firm_f_old', 'ac', 'Z_flag'),
       leave_out(fam_rows, 'firm_f_old', 'market_m_cluster', 'Z_clx'),
       leave_out(fam_rows, 'firm_f_old', 'ac_c', 'Z_acc'),
       leave_out(fam_rows, 'firm_f_old', 'market_m_index', 'Z_idx'),
       leave_out(raw, 'fam_pool', 'ac', 'Z_flag_pool')]

d0 = add_variables(common.load('index'))
funds = top15(d0)
d0 = d0.join(cheap, on='product_ids')
d0['Z_paper'] = d0[H]
for iv in ivs:
    d0 = d0.merge(iv, on=['product_ids', 'month_t'], how='left')
print({c: int(d0[c].notna().sum()) for c in ('Z_flag', 'Z_clx', 'Z_acc', 'Z_idx', 'Z_flag_pool')}, flush=True)
grid_rows = load_new_iv_sample()[['product_ids', 'month_t']].assign(grid=1)
d0 = d0.merge(grid_rows, on=['product_ids', 'month_t'], how='left')
g = d0[d0.grid == 1]

out, fr_all = [], []
for label, dd, z in (('S108 paper IV, all 108,300', d0, 'Z_paper'),
                     ('paper IV, grid rows', g, 'Z_paper'),
                     ('S108f Z_flag pooled family-less, all rows', d0[d0.Z_flag_pool.notna()], 'Z_flag_pool'),
                     ('Z_flag (reference)', g[g.Z_flag.notna()], 'Z_flag'),
                     ('IDX Z_flag excl same index', g[g.Z_idx.notna()], 'Z_idx'),
                     ('CLX Z_flag excl same cluster', g[g.Z_clx.notna()], 'Z_clx'),
                     ('ACC Z_flag asset class per cluster', g[g.Z_acc.notna()], 'Z_acc')):
    o, fr = run(dd.reset_index(drop=True), z, 'gene_idx', label, funds)
    o['corr_with_Z_flag'] = float(dd[[z, 'Z_flag']].dropna().corr().iloc[0, 1])
    out.append(o); fr_all.append(fr)
pd.DataFrame(out).to_csv('step32d.csv', index=False)
pd.concat(fr_all).to_csv('step32d_funds.csv', index=False)
