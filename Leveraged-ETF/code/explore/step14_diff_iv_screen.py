"""Candidate instruments for sigma that rest on the Hausman exogeneity assumption only: differentiation instruments
(Gandhi-Houde style) built from the Hausman fee instrument H instead of from price. For fund j in market t:
  diffH_quad  = sum_k (H_k - H_j)^2 over rivals k in t
  diffH_local = number of rivals with |H_k - H_j| < sd_t(H)
plus the characteristic-based differentiation instruments (tracking error, past return, log age) for comparison.
Screen in logit IV with the cheap interaction: IVs H, H x cheap, D (uninteracted) -> Hansen J, slopes, weakest F.

    python step14_diff_iv_screen.py          # writes step14_diff_iv_screen.csv
"""
import numpy as np
import pandas as pd
import pyblp
from scipy import stats

import common
from step2_logit_screen import add_variables, first_stage_f
from tiers import raw_entry_tiers

pyblp.options.verbose = False
CONTROLS = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
d0 = add_variables(common.load('index'))
H = d0['demand_instruments0'].copy()
g = d0.groupby('market_ids')['demand_instruments0']
n = g.transform('size')
d0['diffH_quad'] = (g.transform(lambda x: (x ** 2).sum()) - H ** 2) - 2 * H * (g.transform('sum') - H) + (n - 1) * H ** 2
sd = g.transform('std')
d0['diffH_local'] = d0.groupby('market_ids', group_keys=False).apply(
    lambda m: pd.Series(((np.abs(m['demand_instruments0'].to_numpy()[:, None] - m['demand_instruments0'].to_numpy()[None, :])
                          < m['demand_instruments0'].std()).sum(1) - 1).astype(float), index=m.index))
chars = pyblp.Formulation('0 + ' + ' + '.join(CONTROLS))
loc = pyblp.build_differentiation_instruments(chars, d0, version='local')
quad = pyblp.build_differentiation_instruments(chars, d0, version='quadratic')
for k in range(loc.shape[1]):
    d0[f'diffX_local{k}'] = loc[:, k]
    d0[f'diffX_quad{k}'] = quad[:, k]
cands = {'diffH_quad': ['diffH_quad'], 'diffH_local': ['diffH_local'], 'diffH_both': ['diffH_quad', 'diffH_local'],
         'diffX_local': [f'diffX_local{k}' for k in range(loc.shape[1])],
         'diffX_quad': [f'diffX_quad{k}' for k in range(loc.shape[1])],
         'newproduct_3': ['BLP_IV_newproduct_3']}
rows = []
for q in (10, 15, 20):
    tier = f'raw{q}'
    d0['cheap'] = d0.product_ids.map(raw_entry_tiers((q / 100,))[tier]).astype(float)
    d0['_px'] = d0.prices * d0.cheap
    for name, cols in cands.items():
        d = d0.drop(columns=[c for c in d0.columns if c.startswith('demand_instruments')])
        ivs = [H, H * d0.cheap] + [d0[c] for c in cols]
        for k, v in enumerate(ivs):
            d[f'demand_instruments{k}'] = np.asarray(v, dtype=float)
        res = pyblp.Problem(pyblp.Formulation('prices + I(prices*cheap) + ' + ' + '.join(CONTROLS),
                                              absorb='C(product_ids) + C(market_ids)'), d).solve(se_type='clustered')
        f = first_stage_f(d, ['prices', '_px'], [f'demand_instruments{k}' for k in range(len(ivs))], CONTROLS)
        b = res.beta.flatten()
        df = len(ivs) - 2
        J = float(res.objective)
        rows.append(dict(cutoff=q, instrument=name, n_excl=len(ivs), b_rest=b[0], b_cheap_total=b[0] + b[1],
                         min_F=min(f.values()), J=J, J_df=df, J_p=float(stats.chi2.sf(J, df))))
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rows[-1].items()}, flush=True)
out = pd.DataFrame(rows)
pd.set_option('display.width', 200)
print(out.round(3).to_string(index=False))
out.to_csv('step14_diff_iv_screen.csv', index=False)
d0[['product_ids', 'market_ids', 'diffH_quad', 'diffH_local'] + [c for c in d0.columns if c.startswith('diffX_')]].to_csv(
    'step14_diff_ivs.csv', index=False)
