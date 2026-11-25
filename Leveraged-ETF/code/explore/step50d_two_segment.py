"""Two-segment alternative to specification B (see step50*_retail_slope.py): mutual-fund classes vs ETFs.

    python -I step50d_two_segment.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV

Fee slope for mutual-fund classes (retail and institutional pooled) and for ETFs; fund FE and month x ETF FE.
Does not use the retail / institutional flag at all. Linear (Salanie-Wolak) screens, as step48.
Writes step50d_two_segment.csv (coefficients only).
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
    d['me'] = d.market_ids.astype(str) + '_' + d.etf.astype(int).astype(str)
    d['mf'] = 1 - d.etf
    for k in range(5):
        d[f'z{k}_mf'], d[f'z{k}_etf'] = d[IV[k]] * d.mf, d[IV[k]] * d.etf
    E2 = IV + ['iv0_etf', 'iv1_etf']
    full = lambda ks: [f'z{k}_{s}' for k in ks for s in ('mf', 'etf')]
    print('\nTwo segments, month x ETF FE')
    run(d, ['prices', 'p_etf'], E2, ['me'], 'S2 logit')
    run(d, ['prices', 'p_etf', 'K'], E2, ['me'], 'S2 with K')
    run(d, ['prices', 'p_etf', 'pp2', 'mpe'], E2, ['me'], 'S2 split (p^2/2, -p e_t)')
    run(d, ['prices', 'p_etf', 'K', 'Ka'], E2, ['me'], 'S2 + age K')
    run(d, ['prices', 'p_etf', 'K'], full(range(5)), ['me'], 'S2 with K, all five x segment (10 IVs)')
    run(d, ['prices', 'p_etf'], full(range(5)), ['me'], 'S2 logit, all five x segment (10 IVs)')
    for k in (1, 2, 3, 4):
        run(d, ['prices', 'p_etf', 'K'], full((0, k)), ['me'], f'S2 with K, IV0 and IV{k} x segment (just identified + 1)')
    print('\nETF rows only (K built from the whole market), fund + month FE, five IVs')
    e = d[d.etf == 1]
    run(e, ['prices'], IV, ['market_ids'], 'ETF only, logit')
    run(e, ['prices', 'K'], IV, ['market_ids'], 'ETF only, with K')
    run(e, ['prices', 'pp2', 'mpe'], IV, ['market_ids'], 'ETF only, split')
    run(e, ['prices', 'K', 'Ka'], IV, ['market_ids'], 'ETF only, + age K')
    for k in (1, 2, 3, 4):
        run(e, ['prices', 'K'], [IV[0], IV[k]], ['market_ids'], f'ETF only, with K, IV0 + IV{k}')
    print('\nMutual-fund rows only, fund + month FE, five IVs')
    m = d[d.etf == 0]
    run(m, ['prices'], IV, ['market_ids'], 'mutual-fund classes only, logit')
    run(m, ['prices', 'K'], IV, ['market_ids'], 'mutual-fund classes only, with K')
    b = pd.DataFrame(s50.ROWS)
    b.to_csv('step50d_two_segment.csv', index=False)
    # implied elasticities from S2 logit and (first order) S2 with K
    r = b[b.spec == 'S2 logit'].iloc[0]
    sl = r.prices + r.p_etf * d.etf
    el = sl * d.prices * (1 - d.shares)
    last = d.month_t == d.month_t.max()
    print('\nS2 logit: slope mutual fund %.2f, ETF %.2f; AUM-weighted elasticity, last month: mutual fund %.2f, ETF %.2f; all months %.2f' % (
        r.prices, r.prices + r.p_etf, np.average(el[last & (d.etf == 0)], weights=d.product_mtna[last & (d.etf == 0)]),
        np.average(el[last & (d.etf == 1)], weights=d.product_mtna[last & (d.etf == 1)]), np.average(el, weights=d.product_mtna)))


if __name__ == '__main__':
    main(*sys.argv[1:4])
