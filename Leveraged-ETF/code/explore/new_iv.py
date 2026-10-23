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
