"""Last linear checks before recommending the passive specifications.

    python -I step55_final_checks.py PACKAGE_DIR NAMES_CSV PROCS

1  Inertia version over calendar time: before / from 2019, and the two halves of the sample period.
2  Static alternative without a fee random coefficient: random coefficients on log age and past return only
   (K_age, K_ret), Danny's five instruments. Leave-one-instrument-out, fee band of 8 / 12 / 15 bp, ETF trend.
   Also the plain static IV logit under the same variations.
Writes step55_final_checks.csv (coefficients only).
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
    hist, ev = s53.read(P, 'passive_exit_history'), s53.read(P, 'passive_certified_exits')
    for w in (0.08, 0.12, 0.15):
        d[f'iv1_{w}'], d[f'iv4_{w}'] = s53.local_stock(f, True, 3, w), s53.exits(f, hist, ev, True, 3, w)
    r = d.product_past_1yr_ret
    d['Kr'] = r * (r / 2 - (d.shares * r).groupby(d.market_ids).transform('sum'))
    L = d.dropna(subset=['y_lag'])
    mid = d.month.min() + (d.month.max() - d.month.min()) // 2

    print('\n1. Inertia version by period (fund + month FE, five IVs)')
    for lab, msk in (('before 2019', L.month < 2019 * 12), ('2019 on', L.month >= 2019 * 12), ('first half of sample', L.month <= mid), ('second half of sample', L.month > mid)):
        q = Panel(L[msk], ['market_ids'], BASE + ['y_lag'], lab)
        q.est(['prices'], IV, 'logit', ('y_lag',))
        q.est(['prices', 'K'], IV, 'K', ('y_lag',))
        q.est(['prices'], [IV[0]], 'logit, IV0 alone', ('y_lag',))
    for lab, msk in (('before 2019', d.month < 2019 * 12), ('2019 on', d.month >= 2019 * 12)):
        q = Panel(d[msk], ['market_ids'], BASE, f'static; {lab}')
        q.est(['prices'], IV, 'logit')
        q.est(['prices', 'K'], IV, 'K')

    print('\n2. Static, no fee random coefficient: age and return random coefficients')
    new = [f'iv{k}_{w}' for w in (0.08, 0.12, 0.15) for k in (1, 4)]
    p = Panel(d, ['market_ids'], BASE + ['Kr', 'etf_t'] + new, 'static')
    p.est(['prices'], IV, 'logit')
    p.est(['prices', 'Ka', 'Kr'], IV, 'age K + return K')
    p.est(['prices', 'Ka'], IV, 'age K only')
    p.est(['prices', 'Kr'], IV, 'return K only')
    p.est(['prices', 'K', 'Ka', 'Kr'], IV, 'fee K + age K + return K')
    p.est(['prices'], IV, 'logit, ETF x trend', ('etf_t',))
    p.est(['prices', 'Ka', 'Kr'], IV, 'age K + return K, ETF x trend', ('etf_t',))
    p.est(['prices', 'Ka'], IV, 'age K only, ETF x trend', ('etf_t',))
    p.est(['prices', 'K', 'Ka'], IV, 'fee K + age K')
    for k in range(5):
        Z = [v for j, v in enumerate(IV) if j != k]
        p.est(['prices'], Z, f'logit, without IV{k}')
        p.est(['prices', 'Ka'], Z, f'age K only, without IV{k}')
        p.est(['prices', 'Ka', 'Kr'], Z, f'age K + return K, without IV{k}')
    for w in (0.08, 0.12, 0.15):
        Z = [IV[0], f'iv1_{w}', IV[2], IV[3], f'iv4_{w}']
        p.est(['prices'], Z, f'logit, band {round(w * 100)} bp')
        p.est(['prices', 'Ka'], Z, f'age K only, band {round(w * 100)} bp')
        p.est(['prices', 'Ka', 'Kr'], Z, f'age K + return K, band {round(w * 100)} bp')
    for lab, msk in (('before 2019', d.month < 2019 * 12), ('2019 on', d.month >= 2019 * 12), ('mutual-fund rows', d.etf == 0), ('ETF rows', d.etf == 1)):
        q = Panel(d[msk], ['market_ids'], BASE, f'static; {lab}')
        q.est(['prices', 'Ka'], IV, 'age K only')
    pd.DataFrame(m.ROWS).to_csv('step55_final_checks.csv', index=False)


if __name__ == '__main__':
    m.PROCS = int(sys.argv[3])
    main(sys.argv[1], sys.argv[2])
