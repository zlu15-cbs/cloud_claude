"""Checks for the final passive specifications: width of the fee band in IV1 / IV4, and the lag coefficient.

    python -I step54_band_and_rho.py PACKAGE_DIR NAMES_CSV PROCS

1  Fee band. Danny's IV1 and IV4 count rivals whose lagged fee is within 10 bp of the fund's own. Rebuilt from his
   panels for bands of 6 to 20 bp (tracking band unchanged). For each band, with his other three instruments:
   static (Table 7) and lagged-share versions; logit fee slope, sigma^2 (coefficient on K), J; IV1 alone.
2  Lag coefficient. With fund effects the estimate of rho is biased toward zero by about (1 + rho) / T.
   (a) half-panel jackknife (Dhaene and Jochmans 2015): each fund's months split in two halves, the model estimated on
       each set of halves with its own fund effects, corrected estimate = 2 x full - mean of the two halves;
   (b) the same regression on funds with long histories only.
3  Feasibility of estimating the partial-adjustment model directly: implied target log share ratios
   y* = (y_t - rho y_{t-1}) / (1 - rho) and the outside share they imply.
Writes step54_band_and_rho.csv (coefficients only).
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step51_one_menu as m
import step53_passive_iv_variants as s53
from step51_one_menu import Panel, IV, BASE

BANDS = (0.06, 0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.15, 0.20)


def main(P, names):
    d = m.prep(P, f'{P}/data/iv_inputs', names)
    f = s53.read(P, 'passive_focal')
    hist, ev = s53.read(P, 'passive_exit_history'), s53.read(P, 'passive_certified_exits')
    for w in BANDS:
        d[f'iv1_{w}'], d[f'iv4_{w}'] = s53.local_stock(f, True, 3, w), s53.exits(f, hist, ev, True, 3, w)
    assert np.abs(d['iv1_0.1'] - d[IV[1]]).max() == 0 and np.abs(d['iv4_0.1'] - d[IV[4]]).max() == 0
    print('distinct fee values: %d; share of fees on a whole basis point: %.3f' % (d.prices.nunique(), np.isclose(d.prices * 100, np.round(d.prices * 100)).mean()))
    new = [f'iv{k}_{w}' for w in BANDS for k in (1, 4)]
    L = d.dropna(subset=['y_lag'])

    print('\n1. Fee band in IV1 and IV4')
    for mode, data, con in (('static', d, ()), ('lag', L, ('y_lag',))):
        p = Panel(data, ['market_ids'], BASE + new + (['y_lag'] if mode == 'lag' else []), mode)
        for w in BANDS:
            Z = [IV[0], f'iv1_{w}', IV[2], IV[3], f'iv4_{w}']
            p.tag = f'{mode}; band {round(w * 100)} bp'
            print(f'   band {round(w * 100)} bp: mean IV1 {d[f"iv1_{w}"].mean():.2f}, mean IV4 {d[f"iv4_{w}"].mean():.3f}')
            p.est(['prices'], [f'iv1_{w}'], 'IV1 alone, logit', con)
            p.est(['prices'], Z, 'five IVs, logit', con)
            p.est(['prices', 'K'], Z, 'five IVs, K', con)
            p.est(['prices', 'K'], [z for z in Z if z != IV[2]], 'K, without IV2', con)

    print('\n2. Lag coefficient')
    T = L.groupby('product_ids').size()
    print('   funds %d; months per fund: mean %.0f, median %.0f; mean of 1/T %.4f; (1 + 0.983) x mean(1/T) = %.4f' % (
        len(T), T.mean(), T.median(), (1 / T).mean(), 1.983 * (1 / T).mean()))
    x = L.sort_values(['product_ids', 'month']).copy()
    rank = x.groupby('product_ids').cumcount()
    n = x.groupby('product_ids').product_ids.transform('size')
    x['half'] = (rank >= n / 2).astype(int)
    x = x[n >= 8]
    res = {}
    for lab, sub in (('full', x), ('first halves', x[x.half == 0]), ('second halves', x[x.half == 1])):
        q = Panel(sub, ['market_ids'], BASE + ['y_lag'], f'jackknife; {lab}')
        res[lab] = (q.est(['prices'], IV, 'logit', ('y_lag',)), q.est(['prices', 'K'], IV, 'K', ('y_lag',)))
    for i, spec in enumerate(('logit', 'K')):
        for c in ('y_lag', 'prices') + (('K',) if i else ()):
            full, a, b = (res[k][i][c] for k in ('full', 'first halves', 'second halves'))
            print(f'   {spec}: {c}: full {full:+.4f}; halves {a:+.4f}, {b:+.4f}; jackknife {2 * full - (a + b) / 2:+.4f}')
    for tmin in (60, 120, 170):
        sub = L[L.groupby('product_ids').product_ids.transform('size') >= tmin]
        q = Panel(sub, ['market_ids'], BASE + ['y_lag'], f'funds with at least {tmin} months ({sub.product_ids.nunique()} funds)')
        q.est(['prices'], IV, 'logit', ('y_lag',))
        q.est(['prices', 'K'], IV, 'K', ('y_lag',))

    print('\n3. Target log share ratios y* = (y_t - rho y_{t-1}) / (1 - rho)')
    for rho in (0.95, 0.983):
        ys = (L.y - rho * L.y_lag) / (1 - rho)
        big = ys.groupby(L.market_ids).max()
        s0 = 1 / (1 + np.exp(ys).groupby(L.market_ids).sum())
        print(f'   rho {rho}: y in [{L.y.min():.1f}, {L.y.max():.1f}]; y* quantiles 1/50/99%: {ys.quantile(.01):.1f} / {ys.median():.1f} / {ys.quantile(.99):.1f}; '
              f'max {ys.max():.1f}; months with implied outside share below 1e-6: {int((s0 < 1e-6).sum())} of {len(s0)}; '
              f'months where one fund has target share above 0.5: {int((np.exp(big) * s0 > 0.5).sum())}')
    pd.DataFrame(m.ROWS).to_csv('step54_band_and_rho.csv', index=False)


if __name__ == '__main__':
    m.PROCS = int(sys.argv[3])
    main(sys.argv[1], sys.argv[2])
