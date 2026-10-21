"""Robustness of the two-group fee interaction to the cutoff and the tier rule (logit IV).

Cheap group = funds whose (a) fee in their first sample month or (b) average fee over their first 12 sample months
is at or below a cutoff. Mode 'rank' (default): cheapest share q of funds, ties broken by row order (this splits the
many funds that share a round fee such as 0.15 or 0.20 arbitrarily). Mode 'value': fee <= cutoff in percent.

    python step2e_cutoff_sweep.py [rank|value] For each q: coefficients, Sanderson-Windmeijer F, number of the 15 Table 5 funds with
|e| > 1 in their last month, share of fund-months with |e| > 1, and share with negative firm-Bertrand marginal cost.
"""
import sys

import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, build, first_stage_f

pyblp.options.verbose = False
d = add_variables(common.load('index'))
funds = top15(d)
srt = d.sort_values('month_t')
basis = {'first month': srt.groupby('product_ids').prices.first(),
         '12-month avg': srt.groupby('product_ids').head(12).groupby('product_ids').prices.mean()}
mode = sys.argv[1] if len(sys.argv) > 1 else 'rank'
rows = []
for rule, fee in basis.items():
    r = fee.rank(method='first') / len(fee)
    grid = (0.20, 0.25, 0.30, 0.333, 0.35, 0.40, 0.45, 0.50) if mode == 'rank' else \
        (0.05, 0.07, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25)
    for q in grid:
        cheap = (r <= q) if mode == 'rank' else (fee <= q + 1e-9)
        d['cheap'] = d.product_ids.map(cheap).astype(float)
        dd, formula, endog, excl, exog = build(d, dict(tier='A', z=['cheap']))
        res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
            se_type='clustered')
        f = first_stage_f(dd, endog, excl, exog)
        e = res.extract_diagonals(res.compute_elasticities()).flatten()
        mc = res.compute_costs().flatten()
        dd = dd.assign(e=e)
        last = dd.sort_values('month_t').groupby('product_ids').last().loc[funds.product_ids]
        b, s = res.beta.flatten(), res.beta_se.flatten()
        rows.append(dict(rule=rule, cutoff=q, share_funds_cheap=float(cheap.mean()), fee_cut=float(fee[cheap].max()), b_rest=b[0], se_rest=s[0],
                         b_cheap_total=b[0] + b[1], se_interaction=s[1], min_F=min(f.values()),
                         n15_gt1=int((last.e.abs() > 1).sum()), share_gt1=float((np.abs(e) > 1).mean()),
                         share_neg_mc=float((mc < 0).mean())))
        print(rows[-1], flush=True)
out = pd.DataFrame(rows)
print(out.round(3).to_string(index=False))
out.to_csv(f'step2e_cutoff_sweep_{mode}.csv', index=False)
