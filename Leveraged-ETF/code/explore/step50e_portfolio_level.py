"""Does aggregating mutual-fund share classes to the fund (portfolio) level restore a negative fee slope?

    python -I step50e_portfolio_level.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV

Share-class restructuring (Investor -> Admiral conversions, class mergers, changed minimums) moves assets between
classes of one portfolio. Here the mutual-fund classes of a portfolio (name before the last ';') are one product:
share and AUM summed; fee, controls and Danny's instruments AUM-weighted across its classes. ETFs are unchanged.
A crude test: the instruments are averaged, not rebuilt. Linear screens as step48 (fund FE = aggregated product).
Writes step50e_portfolio_level.csv (coefficients only).
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step48_access_spec_linear as s48
import step50_retail_slope as s50
from step48_access_spec_linear import IV, CON
from step50_retail_slope import run


def aggregate(d, key):
    wcols = ['prices'] + CON + IV
    x = d.copy()
    for c in wcols:
        x[c] = x[c] * x.product_mtna
    g = x.groupby([key, 'market_ids'], as_index=False).agg(
        **{c: (c, 'sum') for c in wcols}, shares=('shares', 'sum'), product_mtna=('product_mtna', 'sum'),
        s0=('s0', 'first'), e_t=('e_t', 'first'), etf=('etf', 'first'), month=('month', 'first'), month_t=('month_t', 'first'),
        n_classes=('product_ids', 'nunique'))
    for c in wcols:
        g[c] = g[c] / g.product_mtna
    g['product_ids'] = g[key]
    g['y'] = np.log(g.shares) - np.log(g.s0)
    g['K'] = g.prices * (g.prices / 2 - g.e_t)
    g['p_etf'] = g.prices * g.etf
    for k in (0, 1):
        g[f'iv{k}_etf'] = g[IV[k]] * g.etf
    g['me'] = g.market_ids.astype(str) + '_' + g.etf.astype(int).astype(str)
    g['post'] = (g.month >= 2019 * 12).astype(int)
    return g


def main(P, D, names):
    d = s48.load(P, D, names)
    nm = pd.read_csv(names).set_index('product_ids').product_fund_name
    name = d.product_ids.map(nm).astype(str)
    port = name.where(~name.str.contains(';'), name.str.rsplit(';', n=1).str[0]).str.strip()
    d['pf'] = np.where(d.etf == 1, 'E' + d.product_ids.astype(str), 'M' + port)
    d['pf_access'] = np.where(d.etf == 1, d.pf, d.pf + '|' + d.access.astype(int).astype(str))
    E2 = IV + ['iv0_etf', 'iv1_etf']
    for key, lab in (('pf', 'portfolio'), ('pf_access', 'portfolio x access')):
        g = aggregate(d, key)
        m = g[g.etf == 0]
        print(f'\nMutual-fund product = {lab}: {m.product_ids.nunique()} products from {d.product_ids[d.etf == 0].nunique()} classes; '
              f'fund-months {len(m):,}; with more than one class {float((m.n_classes > 1).mean()):.3f}; '
              f'months with a fee change {float((m.sort_values("month").groupby("product_ids").prices.diff().abs() > 1e-9).mean()):.3f}')
        run(m, ['prices'], IV, ['market_ids'], f'{lab}: mutual funds only, logit, five IVs')
        run(m, ['prices'], [IV[0]], ['market_ids'], f'{lab}: mutual funds only, logit, IV0 alone')
        run(m[m.post == 0], ['prices'], IV, ['market_ids'], f'{lab}: mutual funds only, before 2019, five IVs')
        run(m[m.post == 1], ['prices'], IV, ['market_ids'], f'{lab}: mutual funds only, 2019 on, five IVs')
        run(m, ['prices', 'K'], IV, ['market_ids'], f'{lab}: mutual funds only, with K')
        run(g, ['prices', 'p_etf'], E2, ['me'], f'{lab}: S2 logit')
        run(g, ['prices', 'p_etf', 'K'], E2, ['me'], f'{lab}: S2 with K')
    pd.DataFrame(s50.ROWS).to_csv('step50e_portfolio_level.csv', index=False)


if __name__ == '__main__':
    main(*sys.argv[1:4])
