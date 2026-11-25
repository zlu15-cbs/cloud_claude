"""How much of Danny's passive IV1 (and IV4) is the fund's own lagged fee?

    python -I step53b_own_lagged_fee.py PACKAGE_DIR NAMES_CSV PROCS

IV1 counts other-family rivals whose fee at t-1 is within 10 bp of the fund's own fee at t-1 (and tracking error
within 0.02). step53 shows that without these gates the passive fee slope is no longer robustly negative. Here:
  1  the fund's own lagged fee as the only instrument;
  2  IV1 with only the fee gate, and with only the tracking gate;
  3  his instruments with a cubic in the own lagged fee as a control, so that only rival-driven variation in the
     gated counts is used.
Static (Table 7) and lagged-share versions; fund and month FE; month-clustered SE.
Writes step53b_own_lagged_fee.csv (coefficients only).
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step51_one_menu as m
import step53_passive_iv_variants as s53
from step51_one_menu import Panel, IV, BASE


def main(P, names):
    d = m.prep(P, f'{P}/data/iv_inputs', names)
    f = s53.read(P, 'passive_focal')
    d['n1_fee'], d['n1_trk'], d['n1_3'] = s53.local_stock(f, 'fee', 3), s53.local_stock(f, 'tracking', 3), s53.local_stock(f, False, 3)
    x = d.sort_values(['product_ids', 'month'])
    pl = x.groupby('product_ids').prices.shift(1)
    pl[x.groupby('product_ids').month.diff() != 1] = np.nan
    d['p_lag'] = pl
    d['p_lag2'], d['p_lag3'] = d.p_lag ** 2, d.p_lag ** 3
    L = d.dropna(subset=['y_lag', 'p_lag'])
    print('correlation of IV1 with: fee-gate-only count %.3f; tracking-gate-only count %.3f; ungated count %.3f' % tuple(
        np.corrcoef(d[IV[1]], d[c])[0, 1] for c in ('n1_fee', 'n1_trk', 'n1_3')))
    print('share of months in which the fee equals last month\'s fee: %.3f' % (L.prices == L.p_lag).mean())
    cols = BASE + ['n1_fee', 'n1_trk', 'n1_3', 'p_lag', 'p_lag2', 'p_lag3', 'y_lag']
    PL = ('p_lag', 'p_lag2', 'p_lag3')
    for mode, con in (('static', ()), ('lag', ('y_lag',))):
        p = Panel(L, ['market_ids'], cols, mode)
        r2 = 1 - np.var(p.R[IV[1]] - np.column_stack([p.R[c] for c in PL]) @ np.linalg.lstsq(np.column_stack([p.R[c] for c in PL]), p.R[IV[1]], rcond=None)[0]) / np.var(p.R[IV[1]])
        print(f'\n=== {mode}. Within-fund, within-month R^2 of IV1 on a cubic in the own lagged fee: {r2:.3f}')
        p.est(['prices'], ['p_lag'], 'own lagged fee as the only instrument', con)
        p.est(['prices'], [IV[1]], 'IV1 alone', con)
        p.est(['prices'], ['n1_fee'], 'IV1 with the fee gate only', con)
        p.est(['prices'], ['n1_trk'], 'IV1 with the tracking gate only', con)
        p.est(['prices'], ['n1_3'], 'IV1 with no gate', con)
        p.est(['prices'], [IV[1]], 'IV1 alone, cubic in own lagged fee as control', con + PL)
        p.est(['prices'], [IV[4]], 'IV4 alone', con)
        p.est(['prices'], [IV[4]], 'IV4 alone, cubic in own lagged fee as control', con + PL)
        p.est(['prices'], [IV[0]], 'IV0 alone, cubic in own lagged fee as control', con + PL)
        p.est(['prices'], IV, 'his five, logit', con)
        p.est(['prices'], IV, 'his five, logit, cubic in own lagged fee as control', con + PL)
        p.est(['prices', 'K'], IV, 'his five, K', con)
        p.est(['prices', 'K'], IV, 'his five, K, cubic in own lagged fee as control', con + PL)
    pd.DataFrame(m.ROWS).to_csv('step53b_own_lagged_fee.csv', index=False)


if __name__ == '__main__':
    m.PROCS = int(sys.argv[3])
    main(sys.argv[1], sys.argv[2])
