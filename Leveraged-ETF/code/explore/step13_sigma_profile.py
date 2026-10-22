"""Profile the one-step GMM objective over a grid of sigma (one RC on the expense ratio), beta concentrated out.

Model: X1 = prices + prices x cheap + controls (fund, month FE absorbed); X2 = prices. Instruments: Hausman IV,
Hausman IV x cheap, and an extra instrument E (default BLP_IV_newproduct_3, uninteracted; exactly identified).
At each sigma on the grid pyblp recovers beta by IV regression (optimization='return', method='1s', fixed W = (Z'Z)^-1),
so the profile shows whether the objective has a sensible root near sigma = 0 or genuinely falls toward large sigma.

    python step13_sigma_profile.py PROCESSES raw20 [EXTRA_IV] [sigma grid, comma separated]
"""
import sys
import time

import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables
from tiers import raw_entry_tiers

pyblp.options.verbose = False


def main(procs, tier, extra='BLP_IV_newproduct_3', grid=None):
    grid = grid or [0.001, 0.027, 0.25, 0.5, 1, 2, 3, 4, 5, 6.5, 8]
    d = add_variables(common.load('index'))
    q = int(tier[3:]) / 100
    d['cheap'] = d.product_ids.map(raw_entry_tiers((q,))[tier]).astype(float)
    funds = top15(d)
    h = d['demand_instruments0'].copy()
    d['demand_instruments1'] = h * d.cheap
    if extra != 'none':
        d['demand_instruments2'] = d[extra]
    X1 = pyblp.Formulation('0 + prices + I(prices*cheap) + product_tracking_err + product_past_1yr_ret + log_product_fund_age',
                           absorb='C(product_ids) + C(market_ids)')
    X2 = pyblp.Formulation('0 + prices')
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    rows = []
    with pyblp.parallel(procs):
        problem = pyblp.Problem((X1, X2), d, integration=integ)
        for s in grid:
            t = time.time()
            res = problem.solve(np.array([[s]]), optimization=pyblp.Optimization('return'), method='1s', se_type='clustered')
            em = res.compute_elasticities()
            e = res.extract_diagonals(em).flatten()
            last = d.assign(e=e).sort_values('month_t').groupby('product_ids').last().loc[funds.product_ids]
            b = dict(zip(res.beta_labels, res.beta.flatten()))
            bc = b[next(k for k in b if 'cheap' in k)]
            rows.append(dict(sigma=s, objective=float(res.objective), b_rest=b['prices'], b_interaction=bc,
                             b_cheap_total=b['prices'] + bc,
                             avg_own_e=float(res.extract_diagonal_means(em).flatten().mean()),
                             share_pos_e=float((e > 0).mean()), share_abs_e_gt1=float((np.abs(e) > 1).mean()),
                             n15_gt1=int((last.e.abs() > 1).sum()), n15_pos=int((last.e > 0).sum()),
                             spdr_gold_e=float(last.loc[29218, 'e']), secs=round(time.time() - t)))
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in rows[-1].items()}, flush=True)
    out = pd.DataFrame(rows)
    pd.set_option('display.width', 220)
    print(out.round(4).to_string(index=False))
    out.to_csv(f'step13_sigma_profile_{tier}_{extra.replace("BLP_IV_", "")}.csv', index=False)
    if extra == 'none':  # calibrated-sigma run: also save the 15 funds at each grid point
        pass


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2], *(sys.argv[3:4]), grid=[float(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else None)
