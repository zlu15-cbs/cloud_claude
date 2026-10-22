"""Same instrument check for the paper's own specification (no interaction): logit IV with Hausman IV only (Table 2
col 2), BLP_IV_newproduct_1 only, and both (Hansen J). Index panel; for LETF the extra BLP instrument is
BLP_IV_rival_funds1 (notebook cell 12)."""
import numpy as np
import pandas as pd
import pyblp
from scipy import stats

import common

pyblp.options.verbose = False
rows = []
for panel, extra in (('index', 'BLP_IV_newproduct_1'), ('lev', 'BLP_IV_rival_funds1')):
    d0 = common.load(panel)
    H = d0['demand_instruments0'].copy()
    for name, ivs in {'Hausman': [H], 'extra': [d0[extra]], 'both': [H, d0[extra]]}.items():
        d = d0.drop(columns=[x for x in d0.columns if x.startswith('demand_instruments')])
        for k, z in enumerate(ivs):
            d[f'demand_instruments{k}'] = z.to_numpy()
        res = pyblp.Problem(pyblp.Formulation('prices + product_tracking_err + product_past_1yr_ret + log_product_fund_age',
                                              absorb='C(product_ids) + C(market_ids)'), d).solve(se_type='clustered')
        df = len(ivs) - 1
        J = float(res.objective) if df else np.nan
        rows.append(dict(panel=panel, instruments=name if name != 'extra' else extra, b_price=float(res.beta[0, 0]),
                         se=float(res.beta_se[0, 0]), hansen_J=J, J_pvalue=float(stats.chi2.sf(J, df)) if df else np.nan,
                         avg_own_e=float(res.extract_diagonal_means(res.compute_elasticities()).flatten().mean())))
        print(rows[-1], flush=True)
out = pd.DataFrame(rows)
print(out.round(3).to_string(index=False))
out.to_csv('step10b_instrument_check_baseline.csv', index=False)
