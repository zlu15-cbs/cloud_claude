"""Second round of retail-slope diagnostics (see step50_retail_slope.py).

    python -I step50b_retail_slope.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV

 7  One instrument at a time, by access segment: logit fee slope, first stage and reduced form.
 8  Logit B with instruments restricted to subsets, each fully interacted with access (so segment slopes do not
    depend on first stages restricted across segments).
 9  Retail sub-samples: Vanguard / other families; before / from 2019; classes with and without a fee change.
10  Specification with K under alternative FE and instrument sets.
Writes step50b_retail_slope.csv (coefficients only).
"""
import os
import sys
import numpy as np
import pandas as pd
import pyhdfe

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step48_access_spec_linear as s48
import step50_retail_slope as s50
from step48_access_spec_linear import IV, CON
from step50_retail_slope import run


def fs_rf(d, k):
    """First stage and reduced form of instrument k (fund + month FE, controls), month-clustered t."""
    d = d.reset_index(drop=True)
    alg = pyhdfe.create(np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]]), drop_singletons=False)
    R = alg.residualize(d[['prices', 'y', IV[k]] + CON].to_numpy(float))
    X = R[:, 2:]
    clu = pd.factorize(d.market_ids)[0]
    out = []
    for j in (0, 1):
        b = np.linalg.lstsq(X, R[:, j], rcond=None)[0]
        u = R[:, j] - X @ b
        sc = pd.DataFrame(X * u[:, None]).groupby(clu).sum().to_numpy()
        Vi = np.linalg.inv(X.T @ X)
        out += [b[0], b[0] / np.sqrt((Vi @ sc.T @ sc @ Vi)[0, 0])]
    return out


def main(P, D, names):
    d = s48.load(P, D, names)
    d['ma'] = d.market_ids.astype(str) + '_' + d.access.astype(int).astype(str)
    d['me'] = d.market_ids.astype(str) + '_' + d.etf.astype(int).astype(str)
    d['ret'] = (d.access == 0).astype(float)
    for k in range(5):
        for s in ('ret', 'inst', 'etf'):
            d[f'z{k}_{s}'] = d[IV[k]] * d[s]
    full = lambda ks: [f'z{k}_{s}' for k in ks for s in ('ret', 'inst', 'etf')]

    print('\n7. One instrument at a time by segment: slope (2SLS); first stage on fee [t]; reduced form on log share ratio [t]')
    for a, lab in ((0, 'retail'), (1, 'institutional'), (2, 'ETF')):
        g = d[d.access == a]
        for k in range(5):
            row, b = run(g, ['prices'], [IV[k]], ['market_ids'], f'{lab}, IV{k} alone')
            f1, t1, r1, t2 = fs_rf(g, k)
            print(f'      first stage {f1:+.5f} [{t1:+.1f}]   reduced form {r1:+.5f} [{t2:+.1f}]   SD of instrument {g[IV[k]].std():.3f}')

    print('\n8. Logit B, instrument subsets fully interacted with access (month x access FE)')
    for ks, lab in (((0,), 'IV0'), ((0, 2), 'IV0, IV2'), ((0, 2, 4), 'IV0, IV2, IV4'), ((1,), 'IV1'), ((0, 1), 'IV0, IV1'), ((0, 1, 2, 3, 4), 'all five')):
        run(d, ['prices', 'p_inst', 'p_etf'], full(ks), ['ma'], f'logit B, {lab} x access')

    print('\n9. Retail sub-samples (logit, fund + month FE, five IVs; then IV0 alone)')
    r = d[d.access == 0].copy()
    van = r.family.astype(str).str.contains('anguard')
    print('   Vanguard share of retail fund-months %.3f, of retail AUM %.3f' % (van.mean(), r.product_mtna[van].sum() / r.product_mtna.sum()))
    ever = r.groupby('product_ids').prices.transform('nunique') > 1
    for m, lab in ((van, 'Vanguard'), (~van, 'non-Vanguard'), (r.month < 2019 * 12, 'before 2019'), (r.month >= 2019 * 12, '2019 on')):
        if r[m].product_ids.nunique() > 10:
            run(r[m], ['prices'], IV, ['market_ids'], f'retail {lab}, five IVs')
            run(r[m], ['prices'], [IV[0]], ['market_ids'], f'retail {lab}, IV0 alone')
    print('   retail classes whose fee ever changes: %d of %d' % (r.product_ids[ever].nunique(), r.product_ids.nunique()))

    print('\n10. With the random-coefficient term K')
    run(d, ['prices', 'p_inst', 'p_etf', 'K'], IV + s48.IVX, ['market_ids'], 'month FE; fee x access; K; B instruments')
    run(d, ['prices', 'p_inst', 'p_etf', 'K'], full((0, 1, 2, 3, 4)), ['ma'], 'B, all five x access (15 IVs)')
    run(d, ['prices', 'p_inst', 'p_etf', 'K'], full((0, 2)), ['ma'], 'B, IV0 and IV2 x access (6 IVs)')
    run(d, ['prices', 'p_inst', 'p_etf', 'K'], full((0, 2, 4)), ['ma'], 'B, IV0, IV2, IV4 x access (9 IVs)')
    run(d, ['prices', 'p_etf', 'K'], IV + ['iv0_etf', 'iv1_etf'], ['me'], 'two segments (mutual fund, ETF): slopes, month x ETF FE; K')
    run(d, ['prices', 'p_etf'], IV + ['iv0_etf', 'iv1_etf'], ['me'], 'two segments, logit')
    pd.DataFrame(s50.ROWS).to_csv('step50b_retail_slope.csv', index=False)


if __name__ == '__main__':
    main(*sys.argv[1:4])
