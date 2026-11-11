"""Entry-fee quartile per fund: percentile rank of the fund's fee in its entry-month cross-section (index CSV; entry month =
first month on or after January 2005, or the fund's first month if it has none), cut at 0.25 / 0.50 / 0.75."""
import numpy as np
import pandas as pd
from sc_build import DATA


def entry_quartile():
    cf = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna()
    def er(x):
        return x.assign(r=x.groupby('month_t').product_exp_ratio.rank(pct=True)).sort_values('month_t').groupby('product_j').r.first()
    r_all = er(cf)
    r = er(cf[cf.month_t >= 2005 - 1e-9]).reindex(r_all.index).fillna(r_all)
    return np.clip(np.ceil(r * 4), 1, 4)


def remap_family(src, mode):
    """Coarser family for the instrument's donors and targets. src has product_j, month_t, firm_f_old (= CRSP mgmt_cd).
    mode 'parent': the parent firm (the index CSV's firm_f) in that month; for fund-months outside the CSV, the fund's nearest
                   CSV month, else the parent that the management code most often maps to, else the code itself.
    mode 'fixed':  one family per fund for all months: the fund's last parent firm.
    Fund-months with a blank management code (the variable-annuity funds) stay blank."""
    cf = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'month_t', 'firm_f', 'firm_f_old']).dropna(subset=['firm_f'])
    cf['mk'] = np.round(cf.month_t * 12).astype(int)
    s = src[['product_j', 'month_t', 'firm_f_old']].copy()
    s['mk'] = np.round(s.month_t * 12).astype(int)
    s['ord'] = np.arange(len(s))
    s = s.merge(cf[['product_j', 'mk', 'firm_f']], on=['product_j', 'mk'], how='left').sort_values(['product_j', 'mk'])
    code_map = cf.dropna(subset=['firm_f_old']).groupby('firm_f_old').firm_f.agg(lambda x: x.value_counts().index[0])
    if mode == 'parent':
        par = s.groupby('product_j').firm_f.transform(lambda x: x.ffill().bfill())
    else:
        last = cf.sort_values('mk').groupby('product_j').firm_f.last()
        par = s.product_j.map(last)
        code_last = s.dropna(subset=['firm_f_old']).groupby('product_j').firm_f_old.last()   # funds outside the CSV: their last code
        par = par.fillna(s.product_j.map(code_last).map(code_map)).fillna(s.product_j.map(code_last))
    par = par.fillna(s.firm_f_old.map(code_map)).fillna(s.firm_f_old)
    par = par.where(s.firm_f_old.notna())
    return par.sort_index().reindex(s.sort_values('ord').index).to_numpy()


def pure_index_funds(ids):
    """Funds that CRSP flags as an index fund, pure (index_fund_flag 'D') or index-based ('B'), in most of their quarters.
    Enhanced index funds ('E') and funds with no flag are left out. B and D are pooled because 458 funds switch between them."""
    from sc_build import CRSP
    cr = pd.read_csv(CRSP, usecols=['crsp_fundno', 'index_fund_flag'], encoding='latin-1', dtype=str)
    cr['crsp_fundno'] = cr.crsp_fundno.astype(float).astype(int)
    cr = cr[cr.crsp_fundno.isin(set(ids))]
    share = cr.index_fund_flag.isin(['B', 'D']).groupby(cr.crsp_fundno).mean()
    return set(share[share > 0.5].index)
