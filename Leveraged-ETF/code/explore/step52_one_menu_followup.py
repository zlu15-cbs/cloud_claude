"""Follow-up to step51_one_menu.py: robustness of the two pooled specifications that gave sigma^2 > 0.

    python -I step52_one_menu_followup.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV PROCS

G1  Inertia. y_t = rho y_{t-1} + fee terms + ...: one instrument at a time, leave one instrument out, IV0 + one
    other; K split, age K, ETF trend; rho imposed at 0.95, 0.98, 0.99, 1 (dependent variable y_t - rho y_{t-1});
    y_{t-1} instrumented with y_{t-2}; mutual-fund and ETF rows as diagnostics.
G2  Fee x trend: leave one instrument (and its trend interaction) out; with the lag; diagnostics by vehicle.
G3  Fund-specific linear trends instead of the lag (static model).
Writes step52_one_menu_followup.csv (coefficients only).
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step51_one_menu as m
from step51_one_menu import Panel, IV, CON, BASE, ZT

RHOS = (0.95, 0.98, 0.99, 1.0)


def main(P, D, names):
    d = m.prep(P, D, names)
    x = d.sort_values(['product_ids', 'month'])
    lag2 = x.groupby('product_ids').y.shift(2)
    lag2[x.groupby('product_ids').month.diff(2) != 2] = np.nan
    d['y_lag2'] = lag2
    for r in RHOS:
        d[f'y_r{r}'] = d.y - r * d.y_lag
    L = d.dropna(subset=['y_lag']).copy()
    cols = BASE + ['y_lag', 'etf_t', 'p_t'] + ZT + [f'y_r{r}' for r in RHOS]
    lr = lambda row, c: row[c] / (1 - row['y_lag'])

    print('\nG1. Inertia')
    for lab, fe in (('month', ['market_ids']), ('month x asset class', ['mp8'])):
        p = Panel(L, fe, cols, f'{lab}; lag')
        r = p.est(['prices'], IV, 'logit', ('y_lag',))
        print(f'      long-run fee slope {lr(r, "prices"):+.2f}')
        r = p.est(['prices', 'K'], IV, 'K', ('y_lag',))
        print(f'      long-run fee slope {lr(r, "prices"):+.2f}, long-run sigma^2 {lr(r, "K"):+.1f}')
        p.est(['prices', 'pp2', 'mpe'], IV, 'split', ('y_lag',))
        p.est(['prices', 'K', 'Ka'], IV, 'K + age K', ('y_lag',))
        p.est(['prices', 'K'], IV, 'K + ETF x trend', ('y_lag', 'etf_t'))
        p.est(['prices', 'p_t', 'K'], IV + ZT, 'K + fee x trend', ('y_lag',))
        for k in range(5):
            p.est(['prices'], [IV[k]], f'logit, IV{k} alone', ('y_lag',))
        for k in range(1, 5):
            p.est(['prices', 'K'], [IV[0], IV[k]], f'K, IV0 + IV{k}', ('y_lag',))
        for k in range(5):
            p.est(['prices', 'K'], [v for j, v in enumerate(IV) if j != k], f'K, all but IV{k}', ('y_lag',))
        for r in RHOS:
            p.est(['prices'], IV, f'logit, rho imposed {r}', dep=f'y_r{r}')
            p.est(['prices', 'K'], IV, f'K, rho imposed {r}', dep=f'y_r{r}')
        L2 = L.dropna(subset=['y_lag2'])
        q = Panel(L2, fe, BASE + ['y_lag', 'y_lag2'], f'{lab}; lag instrumented with second lag')
        q.est(['prices', 'y_lag'], IV + ['y_lag2'], 'logit')
        q.est(['prices', 'K', 'y_lag'], IV + ['y_lag2'], 'K')
        for v, vl in ((0, 'mutual-fund rows'), (1, 'ETF rows')):
            q = Panel(L[L.etf == v], fe, cols, f'{lab}; lag; diagnostic, {vl}')
            q.est(['prices'], IV, 'logit', ('y_lag',))
            for k in (0, 1, 2, 4):
                q.est(['prices'], [IV[k]], f'logit, IV{k} alone', ('y_lag',))
            q.est(['prices'], IV, 'logit, rho imposed 0.98', dep='y_r0.98')
            q.est(['prices'], IV, 'logit, rho imposed 1.0', dep='y_r1.0')

    print('\nG2. Fee x trend')
    for lab, fe in (('month', ['market_ids']), ('month x asset class', ['mp8'])):
        p = Panel(d, fe, BASE + ['p_t'] + ZT, lab)
        p.est(['prices', 'p_t', 'K'], IV + ZT, 'K + fee x trend')
        p.est(['prices', 'p_t', 'pp2', 'mpe'], IV + ZT, 'split + fee x trend')
        for k in range(5):
            keep = [j for j in range(5) if j != k]
            p.est(['prices', 'p_t', 'K'], [IV[j] for j in keep] + [ZT[j] for j in keep], f'K + fee x trend, all but IV{k}')
        for v, vl in ((0, 'mutual-fund rows'), (1, 'ETF rows')):
            q = Panel(d[d.etf == v], fe, BASE + ['p_t'] + ZT, f'{lab}; diagnostic, {vl}')
            q.est(['prices', 'p_t'], IV + ZT, 'logit + fee x trend')
            q.est(['prices', 'p_t', 'K'], IV + ZT, 'K + fee x trend')

    print('\nG3. Fund-specific linear trends (static)')
    for lab, fe in (('month', ['market_ids']), ('month x asset class', ['mp8'])):
        p = Panel(d, fe, BASE, f'{lab}; fund trends', fund_trend=True)
        p.est(['prices'], IV, 'logit')
        p.est(['prices', 'K'], IV, 'K')
        p.est(['prices', 'pp2', 'mpe'], IV, 'split')
        for k in range(5):
            p.est(['prices'], [IV[k]], f'logit, IV{k} alone')
        for k in range(5):
            p.est(['prices', 'K'], [v for j, v in enumerate(IV) if j != k], f'K, all but IV{k}')
        for v, vl in ((0, 'mutual-fund rows'), (1, 'ETF rows')):
            q = Panel(d[d.etf == v], fe, BASE, f'{lab}; fund trends; diagnostic, {vl}', fund_trend=True)
            q.est(['prices'], IV, 'logit')
    pd.DataFrame(m.ROWS).to_csv('step52_one_menu_followup.csv', index=False)


if __name__ == '__main__':
    m.PROCS = int(sys.argv[4])
    main(*sys.argv[1:4])
