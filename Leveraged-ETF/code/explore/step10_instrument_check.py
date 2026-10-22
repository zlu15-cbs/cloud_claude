"""Is the non-cheap price slope driven by the instrument set? Logit IV (2-step GMM, clustered) with the cheap-tier
interaction under different excluded-instrument sets:
  H      : Hausman IV, Hausman x cheap                       (Table2_alt logit IV, exactly identified)
  N      : newproduct_1, newproduct_1 x cheap               (the extra BLP instrument alone)
  H+N    : all four (the BLP instrument set; overidentified by 2, Hansen J reported)
Index panel; cheap = raw-entry 10th/15th/20th percentile tiers.
"""
import numpy as np
import pandas as pd
import pyblp
from scipy import stats

import common
from step2_logit_screen import add_variables, first_stage_f

pyblp.options.verbose = False
d0 = add_variables(common.load('index'))
H = d0['demand_instruments0'].copy()
rows = []
for q in (10, 15, 20):
    c = d0[f'raw{q}']
    d0['cheap'] = c
    d0['px'] = d0.prices * c
    sets = {'H': [H, H * c], 'N': [d0.BLP_IV_newproduct_1, d0.BLP_IV_newproduct_1 * c],
            'H+N': [H, H * c, d0.BLP_IV_newproduct_1, d0.BLP_IV_newproduct_1 * c]}
    for name, ivs in sets.items():
        d = d0.drop(columns=[x for x in d0.columns if x.startswith('demand_instruments')])
        for k, z in enumerate(ivs):
            d[f'demand_instruments{k}'] = z.to_numpy()
        res = pyblp.Problem(pyblp.Formulation('prices + I(prices*cheap) + product_tracking_err + product_past_1yr_ret'
                                              ' + log_product_fund_age', absorb='C(product_ids) + C(market_ids)'),
                            d).solve(se_type='clustered')
        excl = [f'demand_instruments{k}' for k in range(len(ivs))]
        f = first_stage_f(d, ['prices', 'px'], excl, ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age'])
        df = len(ivs) - 2
        J = float(res.objective) if df else np.nan
        b, s = res.beta.flatten(), res.beta_se.flatten()
        rows.append(dict(cutoff=q, instruments=name, b_rest=b[0], se_rest=s[0], b_cheap_total=b[0] + b[1],
                         se_interaction=s[1], min_F=min(f.values()), hansen_J=J, J_df=df,
                         J_pvalue=float(stats.chi2.sf(J, df)) if df else np.nan))
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rows[-1].items()}, flush=True)
out = pd.DataFrame(rows)
print(out.round(3).to_string(index=False))
out.to_csv('step10_instrument_check.csv', index=False)
