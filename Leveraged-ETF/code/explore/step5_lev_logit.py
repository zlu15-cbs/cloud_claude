"""Step 5 (logit part): log-price spec B1 on the leveraged market, compared with Table 2 Panel B col 2.

Same sample, controls, FE and clustering as notebook cells 3-8 of the leveraged notebook. Run from a folder holding
the LETF CSV.
"""
import numpy as np
import pyblp

import common

pyblp.options.verbose = False
CONTROLS = ' + product_tracking_err + product_past_1yr_ret + log_product_fund_age'
ABSORB = 'C(product_ids) + C(market_ids)'

d = common.load('lev')
print('N', len(d), 'price: median %.3f min %.3f max %.3f' % (d.prices.median(), d.prices.min(), d.prices.max()))
for label, term, iv in [('Table 2 Panel B col 2 (linear)', 'prices', None)] + \
        [(f'B1 log(p + {c})', f'log(prices + {c})', c) for c in (0.01, 0.005, 0.02)]:
    dd = d.copy()
    if iv is not None:
        dd['demand_instruments0'] = np.log(dd['demand_instruments0'] + iv)
    res = pyblp.Problem(pyblp.Formulation(term + CONTROLS, absorb=ABSORB), dd).solve(se_type='clustered')
    e = res.compute_elasticities()
    own = res.extract_diagonals(e).flatten()
    print(f'\n=== {label}')
    print('beta', dict(zip(res.beta_labels, res.beta.flatten().round(4))))
    print('se  ', dict(zip(res.beta_labels, res.beta_se.flatten().round(4))))
    print('avg own elasticity (per-market mean): %.4f   share |e|>1: %.3f   share e>0: %.3f'
          % (res.extract_diagonal_means(e).flatten().mean(), (np.abs(own) > 1).mean(), (own > 0).mean()))
