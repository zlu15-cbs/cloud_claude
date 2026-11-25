"""Third round of retail-slope diagnostics (see step50_retail_slope.py): what happens to retail classes from 2019.

    python -I step50c_retail_slope.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV

11  Retail AUM by group and period; fee changes by group. Groups: Vanguard Admiral; Vanguard other retail
    (Investor classes, closed to new investors from Nov 2018 and converted to Admiral); other families.
12  Retail slope by group and period (logit; fund + month FE; five IVs and IV0 alone).
13  Fixes for the wind-down of Vanguard Investor classes: (a) drop those class-months from 2019 (shares unchanged);
    (b) give them their own month effects from 2019. Then the pooled specifications (logit B, B with K, two-segment).
14  Institutional slope by period and family, for comparison.
Writes step50c_retail_slope.csv (coefficients only).
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step48_access_spec_linear as s48
import step50_retail_slope as s50
from step48_access_spec_linear import IV
from step50_retail_slope import run


def main(P, D, names):
    d = s48.load(P, D, names)
    nm = pd.read_csv(names).set_index('product_ids').product_fund_name
    d['name'] = d.product_ids.map(nm).astype(str)
    van = d.family.astype(str).str.contains('anguard') | d.name.str.contains('Vanguard')
    adm = d.name.str.contains('Admiral')
    d['grp'] = np.select([(d.access == 0) & adm, (d.access == 0) & van & ~adm, d.access == 0], ['V-Admiral', 'V-Investor', 'other retail'], '')
    d['post'] = (d.month >= 2019 * 12).astype(int)
    d['year'] = d.month // 12
    d['ma'] = d.market_ids.astype(str) + '_' + d.access.astype(int).astype(str)
    d['me'] = d.market_ids.astype(str) + '_' + d.etf.astype(int).astype(str)
    r = d[d.access == 0]

    print('\n11. Retail groups: classes, AUM share of retail by period, AUM-weighted fee by period, fee changes')
    for g, x in r.groupby('grp'):
        sh = [x.product_mtna[x.post == q].sum() / r.product_mtna[r.post == q].sum() for q in (0, 1)]
        fee = [np.average(x.prices[x.post == q], weights=x.product_mtna[x.post == q]) for q in (0, 1)]
        dp = x.sort_values('month').groupby('product_ids').prices.diff()
        print(f'  {g:13s} classes {x.product_ids.nunique():3d}; share of retail AUM before/from 2019 {sh[0]:.3f}/{sh[1]:.3f}; '
              f'AUM-weighted fee {fee[0]:.4f}/{fee[1]:.4f}; fee cuts {int((dp < -1e-9).sum())}, increases {int((dp > 1e-9).sum())}')
    print('  V-Investor examples:', '; '.join(r[r.grp == 'V-Investor'].drop_duplicates('product_ids').sort_values('product_mtna', ascending=False).name.head(6).str.slice(0, 70)))
    y = r[r.grp == 'V-Investor'].groupby('year').agg(n=('product_ids', 'nunique'), aum=('product_mtna', lambda s: s.sum() / 12), fee=('prices', 'mean'))
    y['share_of_retail_aum'] = r[r.grp == 'V-Investor'].groupby('year').product_mtna.sum() / r.groupby('year').product_mtna.sum()
    print('  V-Investor by year (classes, mean fee, share of retail AUM):')
    print(y[['n', 'fee', 'share_of_retail_aum']].round(4).to_string())

    print('\n12. Retail slope by group and period (logit, fund + month FE)')
    for g in ('V-Admiral', 'V-Investor', 'other retail'):
        for q, lab in ((0, 'before 2019'), (1, '2019 on')):
            x = r[(r.grp == g) & (r.post == q)]
            if x.product_ids.nunique() > 8:
                run(x, ['prices'], IV, ['market_ids'], f'{g}, {lab}, five IVs')
                run(x, ['prices'], [IV[0]], ['market_ids'], f'{g}, {lab}, IV0 alone')
    for q, lab in ((0, 'before 2019'), (1, '2019 on')):
        x = r[(r.grp != 'V-Investor') & (r.post == q)]
        run(x, ['prices'], IV, ['market_ids'], f'retail without V-Investor, {lab}, five IVs')
        run(x, ['prices'], [IV[0]], ['market_ids'], f'retail without V-Investor, {lab}, IV0 alone')

    print('\n13. Fixes for the Vanguard Investor wind-down')
    wd = (d.grp == 'V-Investor') & (d.post == 1)
    print(f'   wind-down class-months: {int(wd.sum()):,} ({d.product_ids[wd].nunique()} classes)')
    da = d[~wd]
    db = d.copy()
    db['ma'] = np.where(wd, db.market_ids.astype(str) + '_w', db.ma)
    db['me'] = np.where(wd, db.market_ids.astype(str) + '_w', db.me)
    for dd, lab in ((d, 'as is'), (da, '(a) wind-down months dropped'), (db, '(b) own month effects')):
        run(dd[dd.access == 0], ['prices'], IV, ['ma'], f'retail only, {lab}, five IVs')
        run(dd[dd.access == 0], ['prices'], [IV[0]], ['ma'], f'retail only, {lab}, IV0 alone')
        run(dd, ['prices', 'p_inst', 'p_etf'], IV + s48.IVX, ['ma'], f'logit B, {lab}')
        run(dd, ['prices', 'p_inst', 'p_etf', 'K'], IV + s48.IVX, ['ma'], f'B with K, {lab}')
        run(dd, ['prices', 'p_etf'], IV + ['iv0_etf', 'iv1_etf'], ['me'], f'two-segment logit, {lab}')
        run(dd, ['prices', 'p_etf', 'K'], IV + ['iv0_etf', 'iv1_etf'], ['me'], f'two-segment with K, {lab}')

    print('\n14. Institutional slope by period and family (logit, fund + month FE, five IVs)')
    i = d[d.access == 1]
    vi = i.family.astype(str).str.contains('anguard') | i.name.str.contains('Vanguard')
    print('   Vanguard share of institutional AUM %.3f' % (i.product_mtna[vi].sum() / i.product_mtna.sum()))
    for m, lab in ((i.post == 0, 'before 2019'), (i.post == 1, '2019 on'), (vi, 'Vanguard'), (~vi, 'non-Vanguard')):
        run(i[m], ['prices'], IV, ['market_ids'], f'institutional {lab}')
    m = d.access < 2
    vm = d.family.astype(str).str.contains('anguard') | d.name.str.contains('Vanguard')
    for mm, lab in ((m, 'all mutual-fund classes'), (m & ~vm, 'mutual-fund classes, non-Vanguard'), (m & vm, 'mutual-fund classes, Vanguard'),
                    (m & (d.post == 0), 'mutual-fund classes, before 2019'), (m & (d.post == 1), 'mutual-fund classes, 2019 on')):
        run(d[mm], ['prices'], IV, ['market_ids'], f'{lab}, five IVs')
        run(d[mm], ['prices'], [IV[0]], ['market_ids'], f'{lab}, IV0 alone')
    pd.DataFrame(s50.ROWS).to_csv('step50c_retail_slope.csv', index=False)


if __name__ == '__main__':
    main(*sys.argv[1:4])
