"""Screen candidate extra instruments for the 1-RC BLP with an expense-ratio interaction (index panel, logit IV).

For each interaction z (broad-based as in Table A7; raw-entry cheap tiers 10/15/20) and each candidate extra
instrument E (every BLP_IV_* column except the Hausman expense-ratio IV itself):
  - 'alone': IVs E, E x z (exactly identified) -> implied base and interaction slopes;
  - 'with Hausman': IVs H, H x z, E, E x z (overidentified by 2) -> slopes, Hansen J and p-value, weakest
    Sanderson-Windmeijer F.
A candidate is usable as the extra BLP instrument if J does not reject and its own implied slopes agree in sign
with the Hausman ones. Also the no-interaction (paper) spec: H vs H + E.

    python step12_iv_screen.py      # writes step12_iv_screen.csv
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
cands = [c for c in d0.columns if c.startswith('BLP_IV_') and c not in ('BLP_IV_hausman_exp_ratio_x_broad',)
         and d0[c].notna().all() and d0[c].std() > 0]
print('candidates:', len(cands), cands, flush=True)


def fit(d, z, ivs):
    d = d.drop(columns=[c for c in d.columns if c.startswith('demand_instruments')])
    for k, v in enumerate(ivs):
        d[f'demand_instruments{k}'] = np.asarray(v, dtype=float)
    terms = 'prices' + (f' + I(prices*{z})' if z else '')
    res = pyblp.Problem(pyblp.Formulation(terms + ' + ' + ' + '.join(CONTROLS), absorb='C(product_ids) + C(market_ids)'),
                        d).solve(se_type='clustered')
    endog = ['prices'] + (['_px'] if z else [])
    if z:
        d['_px'] = d.prices * d[z]
    f = first_stage_f(d, endog, [f'demand_instruments{k}' for k in range(len(ivs))], CONTROLS)
    b = res.beta.flatten()
    df = len(ivs) - len(endog)
    J = float(res.objective) if df else np.nan
    return dict(b_base=b[0], b_cheap_total=(b[0] + b[1]) if z else np.nan, min_F=min(f.values()),
                J=J, J_p=float(stats.chi2.sf(J, df)) if df else np.nan)


rows = []
for z in (None, 'broad', 'raw10', 'raw15', 'raw20'):
    d = d0.copy()
    if z == 'broad':
        d['broad'] = (d.broad_specialized == 'broad-based').astype(float)
    zz = d[z] if z else None
    h = fit(d, z, [H] + ([H * zz] if z else []))
    rows.append(dict(z=z or 'none', candidate='(Hausman only)', mode='Hausman', **h))
    for c in cands:
        if c == 'BLP_IV_hausman_exp_ratio':
            continue
        E = d[c]
        try:
            a = fit(d, z, [E] + ([E * zz] if z else []))
            w = fit(d, z, [H] + ([H * zz] if z else []) + [E] + ([E * zz] if z else []))
        except Exception as ex:  # collinear or degenerate instrument
            print('skip', z, c, ex, flush=True)
            continue
        rows.append(dict(z=z or 'none', candidate=c, alone_b_base=a['b_base'], alone_b_cheap_total=a['b_cheap_total'],
                         alone_min_F=a['min_F'], **{f'with_H_{k}': v for k, v in w.items()}))
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in rows[-1].items()}, flush=True)
out = pd.DataFrame(rows)
out.to_csv('step12_iv_screen.csv', index=False)
pd.set_option('display.width', 250, 'display.max_columns', 20, 'display.max_rows', 500)
print(out.round(3).to_string(index=False))
