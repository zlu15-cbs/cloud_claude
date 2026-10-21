"""Influence check: re-estimate the two-group fee specs (logit IV) without one fund (default: 43715, SPDR Portfolio
Intermediate Term Corporate Bond ETF, the switcher with the largest within-fund fee variation)."""
import sys

import pyblp

import common
from step2_logit_screen import add_variables, build, first_stage_f, spec_list

pyblp.options.verbose = False
drop = [int(x) for x in sys.argv[1:]] or [43715]
d = add_variables(common.load('index'))
specs = spec_list()
for name in ('A9_low_fee_tercile', 'A9b_low_fee12_tercile', 'A9_low_fee_40pct', 'A9b_low_fee12_40pct'):
    for label, dd in (('all funds', d), (f'without {drop}', d[~d.product_ids.isin(drop)].reset_index(drop=True))):
        dd, formula, endog, excl, exog = build(dd, specs[name])
        res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
            se_type='clustered')
        f = first_stage_f(dd, endog, excl, exog)
        b = {t: f'{v:.2f} ({s:.2f})' for t, v, s in zip(res.beta_labels, res.beta.flatten(), res.beta_se.flatten())
             if 'prices' in t}
        print(f'{name:24s} {label:22s} {b}  F: {[round(v, 1) for v in f.values()]}', flush=True)
