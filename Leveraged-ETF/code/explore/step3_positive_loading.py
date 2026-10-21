"""Step 3 add-on: share of fund-months with a positive own-price loading (upward-sloping demand) in each logit spec.

In logit the loading on price is d(delta)/dp: b_p + sum_k b_k z_k (linear), b_p + 2 b_p2 p (squared), b / (p + c) (log).
Reads step2_summary.csv files given as arguments; run from a folder holding the index CSV.
"""
import sys

import numpy as np
import pandas as pd

import common
from step2_logit_screen import add_variables, spec_list

d = add_variables(common.load('index'))
specs = spec_list()
rows = []
for path in sys.argv[1:]:
    for _, r in pd.read_csv(path).iterrows():
        sp = specs[r.spec]
        dd = d[d.lag_t.notna()] if sp.get('sample') == 'lag12' else d
        form = sp.get('form', 'lin')
        if form == 'log':
            loading = pd.Series(r[f'b[log(prices + {sp["c"]})]'] / (dd.prices + sp['c']))
        elif form == 'sq':
            loading = r['b[prices]'] + 2 * r['b[prices**2]'] * dd.prices
        else:
            loading = pd.Series(r['b[prices]'], index=dd.index)
            for z in sp['z']:
                col = next(c for c in r.index if c.startswith('b[') and z in c and 'prices' in c)
                loading = loading + r[col] * dd[z]
        rows.append(dict(spec=r.spec, share_positive_loading=float((loading > 0).mean()),
                         loading_p5=float(loading.quantile(.05)), loading_median=float(loading.median()),
                         loading_p95=float(loading.quantile(.95))))
print(pd.DataFrame(rows).round(3).to_string(index=False))
pd.DataFrame(rows).to_csv('step3_positive_loading.csv', index=False)
