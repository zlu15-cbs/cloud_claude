"""Shared construction of the share-class-matched Hausman instrument and its estimation sample (as in step25):
Z_jt = median expense ratio of the same family's (firm_f_old) same-share-class funds outside fund j's asset class, month t.
Returns the Table 2 Panel A fund-months with a family id and Z defined (97,429), with add_variables() columns, Z, Z_n,
Z_paper (the paper's Hausman IV), ac (asset class), sc (share class), mkt_ac (month x asset class id), delta."""
import numpy as np
import pandas as pd

import common
from asset_class import classify_by_index
from step2_logit_screen import add_variables, H
from tiers import RAW


def share_class(raw):
    nm = raw.product_fund_name.fillna('').str.lower()
    mf = raw.ETF_ind == 0
    inst = mf & nm.str.contains(r'institutional|inst\b|class i\b|premier|select|class k\b|class z\b|class y\b|class r6|admiral')
    retail = mf & ~inst & nm.str.contains(r'investor|retail|class a\b|class c\b|class r\b|class t\b|service|advisor')
    return np.select([~mf, inst, retail], ['etf', 'inst', 'retail'], 'mf_other')


def add_z_flag(d):
    """Add Z_flag: Z with the share class from CRSP's inst_fund / retail_fund flags (ETF_ind first; flags-first with keyword
    fallback is identical in this sample, since 99.7% of mutual-fund rows carry exactly one Y). See step30d."""
    from tiers_crsp import CRSP
    raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                    'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
    raw = raw[raw.product_exp_ratio.notna() & raw.firm_f_old.notna()].copy()
    raw['ac'] = classify_by_index(raw)
    raw['quarter'] = np.floor(np.round(raw.month_t * 12) / 3) / 4
    fl = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'retail_fund', 'inst_fund'], encoding='latin-1')
    fl = fl.drop_duplicates(['crsp_fundno', 'quarter'], keep='last').rename(columns={'crsp_fundno': 'product_j'})
    raw = raw.merge(fl, on=['product_j', 'quarter'], how='left')
    mf = raw.ETF_ind == 0
    kw = share_class(raw)
    raw['scf'] = np.select([~mf, raw.inst_fund == 'Y', raw.retail_fund == 'Y'], ['etf', 'inst', 'retail'], kw)
    tab = pd.concat([raw[raw.ac != a].groupby(['firm_f_old', 'month_t', 'scf']).product_exp_ratio.median().rename('Z_flag').reset_index().assign(ac=a)
                     for a in sorted(raw.ac.unique())])
    k = raw[['product_j', 'month_t', 'ac', 'firm_f_old', 'scf']].merge(tab, on=['firm_f_old', 'month_t', 'ac', 'scf'], how='left')
    return d.merge(k[['product_j', 'month_t', 'Z_flag']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')


def load_new_iv_sample():
    raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                    'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
    raw = raw[raw.product_exp_ratio.notna() & raw.firm_f_old.notna()].copy()
    raw['fam'] = raw.firm_f_old
    raw['ac'] = classify_by_index(raw)
    raw['sc'] = share_class(raw)
    classes = sorted(raw.ac.unique())
    tab = pd.concat([raw[raw.ac != a].groupby(['fam', 'month_t', 'sc']).product_exp_ratio.agg(Z='median', Z_n='size').reset_index().assign(ac=a)
                     for a in classes])
    d = add_variables(common.load('index'))
    d = d.merge(raw[['product_j', 'month_t', 'fam', 'ac', 'sc']].rename(columns={'product_j': 'product_ids'}),
                on=['product_ids', 'month_t'], how='inner')
    d = d.merge(tab, on=['fam', 'month_t', 'ac', 'sc'], how='left')
    d = d[d.Z.notna()].reset_index(drop=True)
    d['Z_paper'] = d[H]
    d['mkt_ac'] = d.market_ids.astype(str) + '_' + d.ac
    d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))
    return d
