"""Logit IV with price x cheap, where cheap is set from the fund's fee L months earlier (default 60), falling back to the
fund's first raw month when its raw history is shorter than L months at t.

cheap_jt = 1[fee_{j, s} <= q-th percentile of fees across all raw index funds in month s], with
  s = the fund's latest raw observation at or before t - L   (if one exists),
  s = the fund's first raw month                              (otherwise; this is the entry tier of the main spec).
Time-varying for funds with a long history, so the main effect of cheap enters as a control and the time-varying
diagnostics are run (within-fund corr with xi_hat, lead tests of xi_hat(t-k) on cheap_t, AR(1) of xi_hat), both with the
baseline (Table 2 col 2) xi_hat and with the interacted model's own xi_hat (keys with suffix _own).
Instruments: Hausman IV and Hausman IV x cheap; SE clustered by month; Table 2 Panel A sample.

    python step17_lag60_tier.py        # from a folder holding the index CSV; writes step17_summary.csv, step17_funds.csv
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, build, first_stage_f, summarize, tier_c_diagnostics
from tiers import RAW, raw_entry_tiers

pyblp.options.verbose = False
QS = (0.10, 0.15, 0.20)
RUNS = [(60, q) for q in QS] + [(36, 0.20), (48, 0.20), (84, 0.20)]

d = add_variables(common.load('index'))
funds = top15(d)
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
cut = raw.groupby('month_key').product_exp_ratio.quantile(list(QS)).unstack()
for q in QS:
    raw[f'c{round(q * 100)}'] = (raw.product_exp_ratio <= raw.month_key.map(cut[q]) + 1e-9).astype(float)
raw = raw.rename(columns={'product_j': 'product_ids'}).sort_values('month_key')
entry = raw_entry_tiers(QS)
for q in QS:
    d[f'entry{round(q * 100)}'] = d.product_ids.map(entry[f'raw{round(q * 100)}']).astype(float)


def lagged_status(d, L):
    """Status from the latest raw observation at or before t - L; NaN where none exists."""
    left = d[['product_ids', 'month_key']].copy()
    left['target'] = left.month_key - L
    left = left.sort_values('target')
    m = pd.merge_asof(left, raw[['product_ids', 'month_key'] + [f'c{round(q * 100)}' for q in QS]].rename(
        columns={'month_key': 'target'}), on='target', by='product_ids', direction='backward')
    return m.set_index(left.index).sort_index()


# baseline xi for the diagnostics (Table 2 col 2)
bd, bform, *_ = build(d, dict(tier='-', z=[]))
base = pyblp.Problem(pyblp.Formulation(bform, absorb='C(product_ids) + C(market_ids)'), bd).solve(se_type='clustered')
d['xi_base'] = base.xi.flatten()

rows, fund_rows = [], []
for L, q in RUNS:
    qq = round(q * 100)
    lag = lagged_status(d, L)
    z = f'lag{L}_{qq}'
    from_lag = lag[f'c{qq}'].notna()
    d[z] = np.where(from_lag, lag[f'c{qq}'], d[f'entry{qq}'])
    g = d.groupby('product_ids')[z]
    info = dict(share_months_from_lag=float(from_lag.mean()), share_cheap_months=float(d[z].mean()),
                share_funds_cheap_last=float(g.last().mean()),
                share_months_differ_from_entry=float((d[z] != d[f'entry{qq}']).mean()),
                share_funds_ever_switch=float((g.nunique() > 1).mean()), n_funds_switch=int((g.nunique() > 1).sum()))
    dd, formula, endog, excl, exog = build(d, dict(tier='C', z=[z], controls=[z]))
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')
    f = first_stage_f(dd, endog, excl, exog)
    diag = tier_c_diagnostics(dd, [z])
    dd['xi_own'] = res.xi.flatten()  # same diagnostics with the interacted model's own xi_hat
    diag.update({k + '_own': v for k, v in tier_c_diagnostics(dd, [z], xi_col='xi_own').items()})
    row, fr = summarize(f'L{L}_q{qq}', dict(tier='C'), dd, res, funds, endog, f, {**info, **diag})
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    bz = b[next(k for k in b if z in k and 'prices' in k)]
    row['slope_rest'], row['slope_cheap_total'] = b['prices'], b['prices'] + bz
    rows.append(row)
    last = dd.sort_values('month_t').groupby('product_ids')[z].last()
    ever = dd.groupby('product_ids')[z].nunique() > 1
    for r in fr:
        r['cheap_last'], r['ever_switch'] = int(last[r['product_ids']]), bool(ever[r['product_ids']])
        r['cheap_entry'] = int(dd[dd.product_ids == r['product_ids']][f'entry{qq}'].iloc[0])
    fund_rows += fr
    print(f'\n=== lag {L}, {qq}th pct   formula: {formula}')
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()
           if k.startswith(('b[prices', 'se[prices', f'b[{z}', f'se[{z}', 'F[', 'slope', 'avg', 'share', 'n_funds', 'corr',
                            'lead', 'xi_AR', 'N'))}, flush=True)
pd.DataFrame(rows).to_csv('step17_summary.csv', index=False)
fr = pd.DataFrame(fund_rows)
fr.to_csv('step17_funds.csv', index=False)
fr['short'] = fr.name.str.split(': ').str[-1].str[:40]
pd.set_option('display.width', 250)
print(fr.pivot_table(index=['short', 'p_last'], columns='spec', values='e_last', sort=False).round(2).to_string())
print(fr[fr.spec.str.startswith('L60')].pivot_table(index='short', columns='spec', values='cheap_last', sort=False).to_string())
print(fr[fr.spec.str.startswith('L60')].pivot_table(index='short', columns='spec', values='cheap_entry', sort=False).to_string())
