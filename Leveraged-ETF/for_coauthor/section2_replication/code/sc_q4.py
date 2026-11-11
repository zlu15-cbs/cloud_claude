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
    if mode == 'refined':        # the rule-based refined ID (sc_family_refined.py) in place of firm_f
        from sc_family_refined import refined_family
        fam, _ = refined_family()
        fam['mk'] = np.round(fam.month_t * 12).astype(int)
        s = s.drop(columns='firm_f').merge(fam[['product_j', 'mk', 'family']].rename(columns={'family': 'firm_f'}), on=['product_j', 'mk'], how='left').sort_values(['product_j', 'mk'])
    if mode in ('parent', 'refined'):
        par = s.groupby('product_j').firm_f.transform(lambda x: x.ffill().bfill())
    else:
        last = cf.sort_values('mk').groupby('product_j').firm_f.last()
        par = s.product_j.map(last)
        code_last = s.dropna(subset=['firm_f_old']).groupby('product_j').firm_f_old.last()   # funds outside the CSV: their last code
        par = par.fillna(s.product_j.map(code_last).map(code_map)).fillna(s.product_j.map(code_last))
    par = par.fillna(s.firm_f_old.map(code_map)).fillna(s.firm_f_old)
    par = par.where(s.firm_f_old.notna())
    return par.sort_index().reindex(s.sort_values('ord').index).to_numpy()


LIPPER_GROUPS = {   # groups of Lipper classes (matched on lipper_class_name, per quarter; a fund is in a group if most of its quarters match)
    'target_date': r'Mixed-Asset Target',
    'extension': r'Extension|Extended U\.S\.',
    'long_short_alt': r'Long/Short|Market Neutral|Absolute Return|Event Driven|Multi-Strat|Managed Futures|Currency Strateg|Currency Funds|Alternative (?!Act|Energy)',
    'leveraged': r'Leverage|Short Bias',
    'money_market': r'Money Market',
}
RULES = {'bd': [], 'all': [], 'full': ['target_date', 'extension', 'long_short_alt', 'leveraged', 'money_market'], 'narrow': ['long_short_alt', 'leveraged', 'money_market'],
         'no_target': ['extension', 'long_short_alt', 'leveraged', 'money_market'], 'no_extension': ['target_date', 'long_short_alt', 'leveraged', 'money_market']}


def lipper_groups(ids):
    """fund -> group name (or NaN) from the Lipper class name held in most quarters."""
    from sc_build import CRSP
    cr = pd.read_csv(CRSP, usecols=['crsp_fundno', 'lipper_class_name'], encoding='latin-1', dtype=str)
    cr['crsp_fundno'] = cr.crsp_fundno.astype(float).astype(int)
    cr = cr[cr.crsp_fundno.isin(set(ids)) & cr.lipper_class_name.notna()]
    out = pd.Series(np.nan, index=sorted(set(ids)), dtype=object)
    for g, pat in LIPPER_GROUPS.items():
        sh = cr.lipper_class_name.str.contains(pat, case=False, regex=True).groupby(cr.crsp_fundno).mean()
        out[sh[sh > 0.5].index] = g
    return out


def pure_index_funds(ids):
    """Index-fund restriction. Funds that CRSP flags as an index fund, pure ('D') or index-based ('B'), in most of their quarters
    (enhanced 'E' and unflagged funds are left out), minus the Lipper groups of the rule named in SC_RULE (default 'bd': none)."""
    import os
    from sc_build import CRSP
    cr = pd.read_csv(CRSP, usecols=['crsp_fundno', 'index_fund_flag'], encoding='latin-1', dtype=str)
    cr['crsp_fundno'] = cr.crsp_fundno.astype(float).astype(int)
    cr = cr[cr.crsp_fundno.isin(set(ids))]
    share = cr.index_fund_flag.isin(['B', 'D']).groupby(cr.crsp_fundno).mean()
    keep = set(share[share > 0.5].index)
    rule = os.environ.get('SC_RULE', 'bd')
    if rule == 'all':            # no index-fund flag requirement
        keep = set(ids)
    if os.environ.get('SC_NOSWITCH') == '1':   # drop funds whose family (Danny's ownership ID, firm_f) changes at any time in the index CSV
        keep -= family_switchers()
    if RULES[rule]:
        g = lipper_groups(ids)
        keep -= set(g[g.isin(RULES[rule])].index)
    return keep


def family_switchers():
    """Funds to exclude for a change of family. With SC_FAMILY=refined: funds with a real acquisition or transfer in 2010-2024 under
    the refined ID. Otherwise: funds with more than one value of firm_f anywhere in the index CSV."""
    import os
    if os.environ.get('SC_FAMILY') == 'refined':
        from sc_family_refined import refined_family
        _, sw = refined_family(2010, 2024 + 8 / 12)
        return set(sw.product_j)
    cf = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'firm_f']).dropna()
    n = cf.groupby('product_j').firm_f.nunique()
    return set(n[n > 1].index)
