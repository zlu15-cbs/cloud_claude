"""Table2_alt, logit columns: Table 2 cols (1) logit OLS and (2) logit IV with price x cheap added.

cheap = raw-entry fee tier: the fund's expense ratio in its first month with a recorded fee in the full raw CSV is at
or below that month's q-th percentile across all funds in the same raw file (index CSV for Panel A, LETF CSV for
Panel B). Same samples, controls, fund and month FE and clustering as Table 2. IV: Hausman IV and Hausman IV x cheap;
OLS: each price term instrumented by itself.

    python table2_alt_logit.py      # run from a folder holding both CSVs; writes table2_alt_logit.csv, table2_alt_funds.csv
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import build, first_stage_f
from tiers import LETF, raw_entry_tiers

pyblp.options.verbose = False
QS = (10, 15, 20)
rows, fund_rows = [], []
for panel in ('index', 'lev'):
    d0 = common.load(panel)
    rt = raw_entry_tiers(tuple(q / 100 for q in QS), **({} if panel == 'index' else dict(path=LETF, id_col='product_ticker')))
    funds = top15(d0) if panel == 'index' else None
    for q in (None,) + QS:
        d = d0.assign(cheap=0.0 if q is None else d0.product_ids.map(rt[f'raw{q}']).astype(float))
        z = [] if q is None else ['cheap']
        for est in ('OLS', 'IV'):
            dd, formula, endog, excl, exog = build(d, dict(tier='A', z=z))
            if est == 'OLS':
                for k, c in enumerate(endog):
                    dd[f'demand_instruments{k}'] = dd[c]
            res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
                se_type='clustered')
            em = res.compute_elasticities()
            e = res.extract_diagonals(em).flatten()
            mc = res.compute_costs().flatten()
            row = dict(panel=panel, cutoff='none (Table 2)' if q is None else f'{q}th pct', column=est, N=len(dd),
                       share_funds_cheap=float(dd.groupby('product_ids').cheap.first().mean()),
                       avg_own_e_market_mean=float(res.extract_diagonal_means(em).flatten().mean()),
                       avg_own_e_obs_mean=float(e.mean()), share_abs_e_gt1=float((np.abs(e) > 1).mean()),
                       share_pos_e=float((e > 0).mean()), share_neg_mc=float((mc < 0).mean()),
                       min_F=min(first_stage_f(dd, endog, excl, exog).values()) if est == 'IV' else np.nan)
            for t, b, s in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten()):
                row[f'b[{t}]'], row[f'se[{t}]'] = b, s
            rows.append(row)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
            if panel == 'index':
                last = dd.assign(e=e).sort_values('month_t').groupby('product_ids').last().loc[funds.product_ids]
                for pid, r in last.iterrows():
                    fund_rows.append(dict(cutoff=row['cutoff'], column=est, product_ids=pid,
                                          name=str(r.product_fund_name).split(': ')[-1][:45], p=r.prices,
                                          cheap=r.cheap, e_last=r.e))
pd.DataFrame(rows).to_csv('table2_alt_logit.csv', index=False)
pd.DataFrame(fund_rows).to_csv('table2_alt_funds.csv', index=False)
print('done')
