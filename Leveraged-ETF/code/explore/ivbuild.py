"""Share-class Hausman instruments with CRSP share-class flags (DECISIONS.md), at three exclusion levels:
  Z_flag  exclude same-family, same-share-class siblings in the same ASSET CLASS (asset class per market_m_index)
  Z_clx   ... in the same market_m_cluster
  Z_idx   ... tracking the same market_m_index (Danny's exclusion)
Median fee of the remaining same-family (firm_f_old), same-share-class funds in the same month; raw index file donors.
Identical to step32d_sample_cluster.py (Z_flag reproduces step32b's -8.019).
"""
import numpy as np
import pandas as pd

from asset_class import classify
from new_iv import share_class
from tiers import RAW
from tiers_crsp import CRSP


def _leave_out(r, excl, name):
    keys = ['firm_f_old', 'month_t', 'scf']
    if r[excl].nunique() <= 10:
        tab = pd.concat([r[r[excl] != a].groupby(keys).product_exp_ratio.median().rename(name).reset_index().assign(**{excl: a})
                         for a in sorted(r[excl].dropna().unique())])
    else:
        own = r.groupby(keys + [excl]).product_exp_ratio.apply(list).rename('own').reset_index()
        own = own.merge(r.groupby(keys).product_exp_ratio.apply(list).rename('all').reset_index(), on=keys)

        def med(row):
            v = list(row['all'])
            for x in row['own']:
                v.remove(x)
            return np.median(v) if v else np.nan
        own[name] = own.apply(med, axis=1)
        tab = own[keys + [excl, name]]
    k = r[['product_j', 'month_t'] + keys[:1] + ['scf', excl]].merge(tab, on=keys + [excl], how='left')
    return k[['product_j', 'month_t', name]].rename(columns={'product_j': 'product_ids'})


def build():
    raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                    'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
    raw = raw[raw.product_exp_ratio.notna()].copy()
    cls = classify(raw)
    key_i = raw.market_m_index.fillna('_none_' + raw.product_j.astype(str))
    t = pd.DataFrame({'i': key_i, 'cls': cls, 'pj': raw.product_j})[raw.firm_f_old.notna()].drop_duplicates('pj')
    raw['ac'] = key_i.map(t.groupby('i').cls.agg(lambda s: s.value_counts().index[0])).fillna(cls)
    raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
    fl = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund'], encoding='latin-1')
    fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})
    raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
    mf = raw.ETF_ind == 0
    raw['scf'] = np.select([~mf, raw.inst_fund == 'Y', raw.retail_fund == 'Y'], ['etf', 'inst', 'retail'], share_class(raw))
    r = raw[raw.firm_f_old.notna()]
    out = None
    for excl, name in (('ac', 'Z_flag'), ('market_m_cluster', 'Z_clx'), ('market_m_index', 'Z_idx')):
        z = _leave_out(r, excl, name)
        out = z if out is None else out.merge(z, on=['product_ids', 'month_t'], how='outer')
    return out
