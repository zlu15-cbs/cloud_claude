"""Screen candidate extra instruments entered WITHOUT the z interaction (logit IV, index panel): IVs H, H x z, E.
In logit this is overidentified by 1 (Hansen J, 1 df). In a 1-RC BLP the same three instruments exactly identify
(price, price x z, sigma), the structure Table A7 col 3 has with two RCs.

    python step12b_iv_screen_uninteracted.py     # writes step12b_iv_screen_uninteracted.csv
"""
import numpy as np
import pandas as pd
import pyblp
from scipy import stats

import common
from step2_logit_screen import add_variables, first_stage_f

pyblp.options.verbose = False
CONTROLS = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
d0 = add_variables(common.load('index'))
H = d0['demand_instruments0'].copy()
cands = [c for c in d0.columns if c.startswith('BLP_IV_') and c not in ('BLP_IV_hausman_exp_ratio', 'BLP_IV_hausman_exp_ratio_x_broad')
         and d0[c].notna().all() and d0[c].std() > 0]
rows = []
for z in ('broad', 'raw10', 'raw15', 'raw20'):
    for c in cands:
        d = d0.drop(columns=[x for x in d0.columns if x.startswith('demand_instruments')])
        for k, v in enumerate([H, H * d0[z], d0[c]]):
            d[f'demand_instruments{k}'] = np.asarray(v, dtype=float)
        d['_px'] = d.prices * d[z]
        try:
            res = pyblp.Problem(pyblp.Formulation(f'prices + I(prices*{z}) + ' + ' + '.join(CONTROLS),
                                                  absorb='C(product_ids) + C(market_ids)'), d).solve(se_type='clustered')
            f = first_stage_f(d, ['prices', '_px'], ['demand_instruments0', 'demand_instruments1', 'demand_instruments2'],
                              CONTROLS)
        except Exception as ex:
            print('skip', z, c, ex, flush=True)
            continue
        b = res.beta.flatten()
        J = float(res.objective)
        rows.append(dict(z=z, candidate=c.replace('BLP_IV_', ''), b_base=b[0], b_z_total=b[0] + b[1], min_F=min(f.values()),
                         J=J, J_p=float(stats.chi2.sf(J, 1))))
out = pd.DataFrame(rows)
out.to_csv('step12b_iv_screen_uninteracted.csv', index=False)
pd.set_option('display.width', 200, 'display.max_rows', 300)
for z in ('broad', 'raw10', 'raw15', 'raw20'):
    print(f'\n== {z}'); print(out[out.z == z].sort_values('J_p', ascending=False).round(3).head(10).to_string(index=False))
