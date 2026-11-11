"""Variable-annuity (VA) funds in the Table 2 sample: who they are, what Table 2 col 2 gives under each treatment of
them, and their fee data. Reproduces sections 1 and 6 of RESULTS_spec_summary.md. Run after sc_build.py.
Writes sc_va_funds.csv and sc_va_checks.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sc_build import CRSP, INDEX, PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402

pyblp.options.verbose = False


def main():
    d = pd.read_pickle(PANEL)
    d['gene_idx'] = d.cheap
    d['IV0'] = d.demand_instruments0
    blank = d.firm_f_old.isna()

    # 1. the rows without a family code are the CRSP variable-annuity funds
    c = pd.read_csv(CRSP, usecols=['crsp_fundno', 'vau_fund', 'mgmt_cd', 'mgmt_name'], encoding='latin-1', dtype=str)
    c['crsp_fundno'] = c.crsp_fundno.astype(float).astype(int)
    c = c[c.crsp_fundno.isin(set(d.product_ids))]
    f = c.groupby('crsp_fundno').agg(vau_any=('vau_fund', lambda x: (x == 'Y').any()), vau_all=('vau_fund', lambda x: (x == 'Y').all()),
                                     has_mgmt_cd=('mgmt_cd', lambda x: x.notna().any()), mgmt_name=('mgmt_name', 'last'))
    fund = d.groupby('product_ids').agg(blank_family=('firm_f_old', lambda x: x.isna().all()), fund_months=('month_t', 'size'),
                                        name=('product_fund_name', 'last'), parent_firm=('firm_ids', 'last'), mean_fee=('prices', 'mean')).join(f)
    print('funds: blank family code x CRSP variable-annuity flag (any quarter)')
    print(pd.crosstab(fund.blank_family, fund.vau_any, margins=True))
    print('funds with the flag in every quarter / in some quarters:', int(fund.vau_all.sum()), '/', int((fund.vau_any & ~fund.vau_all).sum()))
    print('funds with a blank family code that have a CRSP mgmt_cd:', int((fund.blank_family & fund.has_mgmt_cd).sum()))
    va = d.product_ids.map(fund.vau_any)
    print(f'fund-months: blank & VA {int((blank & va).sum()):,}; blank & not VA {int((blank & ~va).sum()):,}; not blank & VA {int((~blank & va).sum()):,}')
    s = d.assign(va=blank).groupby(['month_t', 'va']).shares.sum().unstack().fillna(0)
    sh = s[True] / (s[True] + s[False])
    print(f'VA share of inside-market assets: mean {sh.mean():.4f}, first month {sh.iloc[0]:.4f}, last month {sh.iloc[-1]:.4f}')
    fund[fund.blank_family].sort_values('fund_months', ascending=False).to_csv('sc_va_funds.csv')

    # 2. Table 2 col 2 under each treatment of the VA funds
    r = pd.read_csv(INDEX, usecols=['product_j', 'month_t', 'market_m_index', 'firm_f_old', 'firm_f', 'product_exp_ratio', 'product_L1_mtna'])
    r['market_m_index'] = r.market_m_index.fillna('_none_' + r.product_j.astype(str))

    def rebuilt(fam):  # lag-AUM-weighted mean fee of same-family funds tracking another index (the paper's IV0 design)
        w = r.product_L1_mtna.fillna(0)
        x = r.product_exp_ratio.fillna(0) * w
        g1, g2 = [fam, r.month_t], [fam, r.month_t, r.market_m_index]
        den = w.groupby(g1).transform('sum') - w.groupby(g2).transform('sum')
        return ((x.groupby(g1).transform('sum') - x.groupby(g2).transform('sum')) / den).where(den > 1e-9)
    r['R_va'] = rebuilt(r.firm_f_old.fillna('VA:' + r.firm_f.astype(str)))   # donors: the parent firm's other VA funds
    r['R_firm'] = rebuilt(r.firm_f.astype(str))                               # donors: all funds of the parent firm
    d = d.merge(r[['product_j', 'month_t', 'R_va', 'R_firm']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
    blank = d.firm_f_old.isna()
    d['iv_va'] = np.where(blank, d.R_va, d.IV0)
    d['iv_firm'] = np.where(blank, d.R_firm, d.IV0)
    rows = []
    for label, iv, mask in (('as in the paper: blank families pooled, all rows', 'IV0', d.IV0.notna()),
                            ('true families: the parent firm\'s other VA funds as donors', 'iv_va', d.iv_va.notna()),
                            ('true families: all funds of the parent firm as donors', 'iv_firm', d.iv_firm.notna()),
                            ('VA funds excluded from the sample', 'IV0', ~blank),
                            ('VA funds only', 'IV0', blank)):
        o = fit(d[np.asarray(mask)].reset_index(drop=True), iv, [])[0]
        rows.append(dict(treatment=label, N=o['N'], price=o['b_prices'], se=o['se_prices'], F=o['min_F'], share_pos_e=o['share_pos_e']))
        print(f"{label:62s} N {o['N']:>7,} | price {o['b_prices']:7.3f} ({o['se_prices']:.3f}) | F {o['min_F']:.1f}", flush=True)
    pd.DataFrame(rows).to_csv('sc_va_checks.csv', index=False)

    # 3. fee data of the VA funds in the index CSV
    b = r[r.firm_f_old.isna() & (r.month_t >= 2010)]
    g = b.groupby(['firm_f', 'month_t']).product_exp_ratio
    multi = g.size() > 1
    print(f'VA rows in the index CSV since 2010: {len(b):,}; funds {b.product_j.nunique()}; parent firms {b.firm_f.nunique()}')
    print(f'firm-months with more than one VA fund: {int(multi.sum()):,}; share where all of them have the same expense ratio: {(g.nunique() == 1)[multi].mean():.3f}')
    for firm in ('Allianz', 'Mutual of America'):
        x = b[b.firm_f == firm].groupby(np.floor(b.month_t)).product_exp_ratio.agg(['min', 'max', 'nunique', 'size'])
        print(firm, '(fee by calendar year: min, max, distinct values, fund-months)')
        print(x.iloc[::2].round(3).to_string())


if __name__ == '__main__':
    pd.set_option('display.width', 200)
    main()
