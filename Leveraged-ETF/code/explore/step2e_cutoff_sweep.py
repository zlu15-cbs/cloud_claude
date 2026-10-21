"""Robustness of the two-group fee interaction to the cutoff and the tier rule (logit IV).

Cheap group = cheapest share q of funds by (a) fee in the fund's first sample month or (b) average fee over its
first 12 sample months. For each q: coefficients, Sanderson-Windmeijer F, number of the 15 Table 5 funds with
|e| > 1 in their last month, share of fund-months with |e| > 1, and share with negative firm-Bertrand marginal cost.
"""
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
rows = []
for rule, fee in basis.items():
    r = fee.rank(method='first') / len(fee)
    for q in (0.20, 0.25, 0.30, 0.333, 0.35, 0.40, 0.45, 0.50):
        d['cheap'] = d.product_ids.map(r <= q).astype(float)
        dd, formula, endog, excl, exog = build(d, dict(tier='A', z=['cheap']))
        res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
            se_type='clustered')
        f = first_stage_f(dd, endog, excl, exog)
        e = res.extract_diagonals(res.compute_elasticities()).flatten()
        mc = res.compute_costs().flatten()
        dd = dd.assign(e=e)
        last = dd.sort_values('month_t').groupby('product_ids').last().loc[funds.product_ids]
        b, s = res.beta.flatten(), res.beta_se.flatten()
        rows.append(dict(rule=rule, cutoff=q, fee_cut=float(fee[r <= q].max()), b_rest=b[0], se_rest=s[0],
                         b_cheap_total=b[0] + b[1], se_interaction=s[1], min_F=min(f.values()),
                         n15_gt1=int((last.e.abs() > 1).sum()), share_gt1=float((np.abs(e) > 1).mean()),
                         share_neg_mc=float((mc < 0).mean())))
        print(rows[-1], flush=True)
out = pd.DataFrame(rows)
print(out.round(3).to_string(index=False))
out.to_csv('step2e_cutoff_sweep.csv', index=False)
