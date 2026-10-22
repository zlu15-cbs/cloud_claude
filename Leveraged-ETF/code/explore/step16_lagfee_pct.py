"""Logit IV with price x (percentile of the fund's expense ratio 12 months earlier), index panel.

pct12_jt = percentile rank (0-1) of fund j's expense ratio in month t-12 among all funds with a recorded fee in the
raw file that month (same population as the raw-entry tiers). Time-varying, so its main effect is included as a
control (fund FE do not absorb it). Specs:
  L1  price + price x pct12           (continuous; slope at pct = 0 is b_p, at pct = 1 is b_p + b_px)
  L2-4 price + price x 1[pct12 <= 0.10 / 0.15 / 0.20]
Instruments: Hausman IV and Hausman IV x z. Clustered by month. Also the time-varying diagnostics used for the
other C-tier specs: within-fund corr(z, xi_hat), lead tests of xi_hat(t-k) on z_t, within-fund AR(1) of xi_hat.
Sample: Table 2 Panel A rows with a fee observed 12 months earlier.

    python step16_lagfee_pct.py      # run from a folder holding the index CSV; writes step16_summary.csv, step16_funds.csv
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, build, first_stage_f, summarize, tier_c_diagnostics
from tiers import RAW

pyblp.options.verbose = False

d = add_variables(common.load('index'))
funds = top15(d)
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
raw['pct'] = raw.groupby('month_key').product_exp_ratio.rank(method='average', pct=True)
lag = raw[['product_j', 'month_key', 'pct']].rename(columns={'product_j': 'product_ids', 'pct': 'pct12'})
lag['month_key'] += 12
d = d.merge(lag, on=['product_ids', 'month_key'], how='left')
print(f'rows with a fee 12 months earlier: {d.pct12.notna().sum():,} of {len(d):,}', flush=True)
d = d[d.pct12.notna()].reset_index(drop=True)
for q in (10, 15, 20):
    d[f'lp{q}'] = (d.pct12 <= q / 100).astype(float)
print('share of fund-months with lagged-fee percentile <= 10/15/20:',
      [round(float(d[f'lp{q}'].mean()), 3) for q in (10, 15, 20)], flush=True)

# baseline xi on this sample for the diagnostics
bd, bform, *_ = build(d, dict(tier='-', z=[]))
base = pyblp.Problem(pyblp.Formulation(bform, absorb='C(product_ids) + C(market_ids)'), bd).solve(se_type='clustered')
d['xi_base'] = base.xi.flatten()
print('baseline on this sample: price', round(float(base.beta[0, 0]), 3), 'avg e',
      round(float(base.extract_diagonal_means(base.compute_elasticities()).flatten().mean()), 3), flush=True)

specs = {'L1_pct12_continuous': ['pct12'], 'L2_lagfee_le10': ['lp10'], 'L3_lagfee_le15': ['lp15'], 'L4_lagfee_le20': ['lp20']}
rows, fund_rows = [], []
for name, z in specs.items():
    dd, formula, endog, excl, exog = build(d, dict(tier='C', z=z, controls=z))
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')
    f = first_stage_f(dd, endog, excl, exog)
    diag = tier_c_diagnostics(dd, z)
    row, fr = summarize(name, dict(tier='C'), dd, res, funds, endog, f, diag)
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    bz = b[next(k for k in b if z[0] in k and 'prices' in k)]
    row['slope_at_z0'] = b['prices']
    row['slope_at_z1'] = b['prices'] + bz
    rows.append(row)
    # attach the fund's z in its last month
    last_z = dd.sort_values('month_t').groupby('product_ids')[z[0]].last()
    for r in fr:
        r['z_last'] = float(last_z.get(r['product_ids'], np.nan))
    fund_rows += fr
    print(f'\n=== {name}  N={len(dd):,}  formula: {formula}')
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()
           if k.startswith(('b[', 'se[', 'F[', 'slope', 'avg', 'share', 'corr', 'lead', 'xi_AR', 'N'))}, flush=True)
pd.DataFrame(rows).to_csv('step16_summary.csv', index=False)
pd.DataFrame(fund_rows).to_csv('step16_funds.csv', index=False)
fr = pd.DataFrame(fund_rows)
fr['short'] = fr.name.str.split(': ').str[-1].str[:38]
pd.set_option('display.width', 250)
print(fr.pivot_table(index=['short', 'p_last'], columns='spec', values='e_last', sort=False).round(2).to_string())
print(fr[fr.spec == 'L1_pct12_continuous'][['short', 'z_last']].round(3).to_string(index=False))
