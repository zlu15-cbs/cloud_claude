"""Decompose the lag-60 cheap tier (step17): how much comes from status levels that differ from the entry tier but are
constant within the sample, and how much from the 199 funds whose status switches inside the sample.

  frozen   cheap fixed per fund at its lag-60 status in the fund's first sample month (predetermined: uses the fee 60
           months before the fund enters the sample, or the entry fee for young funds). No main effect needed (fund FE).
  noswitch the time-varying lag-60 tier, dropping funds whose status changes inside the sample.
  full     the time-varying lag-60 tier (step17), for reference.
Also: within-fund autocorrelation of the baseline xi_hat at 12/36/60/72 months, and lead tests of xi_hat(t-k) on
cheap_t for k = 60, 72 (does demand before the classification date predict the status?).

    python step17b_lag60_decompose.py      # from a folder holding the index CSV; writes step17b_summary.csv, step17b_funds.csv
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, build, first_stage_f, summarize, tier_c_diagnostics, dm_by
from tiers import RAW, raw_entry_tiers

pyblp.options.verbose = False
QS = (0.10, 0.15, 0.20)
L = 60

d = add_variables(common.load('index'))
funds = top15(d)
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
cut = raw.groupby('month_key').product_exp_ratio.quantile(list(QS)).unstack()
for q in QS:
    raw[f'c{round(q * 100)}'] = (raw.product_exp_ratio <= raw.month_key.map(cut[q]) + 1e-9).astype(float)
raw = raw.rename(columns={'product_j': 'product_ids'}).sort_values('month_key')
entry = raw_entry_tiers(QS)
left = d[['product_ids', 'month_key']].copy()
left['target'] = left.month_key - L
left = left.sort_values('target')
m = pd.merge_asof(left, raw[['product_ids', 'month_key'] + [f'c{round(q * 100)}' for q in QS]].rename(
    columns={'month_key': 'target'}), on='target', by='product_ids', direction='backward').set_index(left.index).sort_index()
first_idx = d.sort_values('month_t').groupby('product_ids').head(1).index
for q in QS:
    qq = round(q * 100)
    d[f'entry{qq}'] = d.product_ids.map(entry[f'raw{qq}']).astype(float)
    d[f'full{qq}'] = np.where(m[f'c{qq}'].notna(), m[f'c{qq}'], d[f'entry{qq}'])
    frozen = d.loc[first_idx].set_index('product_ids')[f'full{qq}']
    d[f'frozen{qq}'] = d.product_ids.map(frozen).astype(float)
    d[f'switch{qq}'] = d.product_ids.map(d.groupby('product_ids')[f'full{qq}'].nunique() > 1)

bd, bform, *_ = build(d, dict(tier='-', z=[]))
base = pyblp.Problem(pyblp.Formulation(bform, absorb='C(product_ids) + C(market_ids)'), bd).solve(se_type='clustered')
d['xi_base'] = base.xi.flatten()

# within-fund autocorrelation of xi_hat at long lags
panel = d[['product_ids', 'month_key', 'xi_base']]
for k in (1, 12, 36, 60, 72):
    lag = panel.rename(columns={'xi_base': 'xi_lag'}).assign(month_key=lambda x: x.month_key + k)
    mm = panel.merge(lag, on=['product_ids', 'month_key'])
    a, b = dm_by(mm, 'xi_base'), dm_by(mm, 'xi_lag')
    print(f'within-fund corr(xi_t, xi_t-{k}) = {np.corrcoef(a, b)[0, 1]:.3f}   (n pairs {len(mm):,})', flush=True)

rows, fund_rows = [], []
for q in QS:
    qq = round(q * 100)
    variants = {f'frozen{qq}': ('A', d, f'frozen{qq}'),
                f'noswitch{qq}': ('A', d[~d[f'switch{qq}']].reset_index(drop=True), f'full{qq}'),  # constant within fund
                f'full{qq}': ('C', d, f'full{qq}')}
    for name, (tier, dd0, z) in variants.items():
        if tier == 'A':
            sp = dict(tier='A', z=[z])
        else:
            sp = dict(tier='C', z=[z], controls=[z])
        dd, formula, endog, excl, exog = build(dd0, sp)
        res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')
        f = first_stage_f(dd, endog, excl, exog)
        info = dict(share_funds_cheap=float(dd.groupby('product_ids')[z].last().mean()),
                    share_months_differ_from_entry=float((dd[z] != dd[f'entry{qq}']).mean()),
                    n_funds=int(dd.product_ids.nunique()))
        if tier == 'C':
            info.update(tier_c_diagnostics(dd, [z]))
            # lead tests at the classification horizon and beyond
            pz = dd[['product_ids', 'month_key', 'xi_base', z]]
            for k in (60, 72):
                lead = pz[['product_ids', 'month_key', 'xi_base']].rename(columns={'xi_base': 'xi_lag'})
                lead = lead.assign(month_key=lead.month_key + k)
                mm = pz.merge(lead, on=['product_ids', 'month_key'])
                y, x = dm_by(mm, 'xi_lag'), dm_by(mm, z)
                if (x @ x) > 0:
                    bb = (x @ y) / (x @ x)
                    u = y - bb * x
                    se = np.sqrt(((pd.Series(x * u).groupby(mm.month_key.to_numpy()).sum()) ** 2).sum()) / (x @ x)
                    info[f'lead{k}_t'] = float(bb / se)
                    info[f'lead{k}_n'] = len(mm)
        row, fr = summarize(name, sp, dd, res, funds[funds.product_ids.isin(dd.product_ids)], endog, f, info)
        b = dict(zip(res.beta_labels, res.beta.flatten()))
        bz = b[next(k for k in b if z in k and 'prices' in k)]
        row['slope_rest'], row['slope_cheap_total'] = b['prices'], b['prices'] + bz
        rows.append(row)
        fund_rows += fr
        print(f'\n=== {name}  N={len(dd):,}  formula: {formula}')
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()
               if k.startswith(('b[prices', 'se[prices', f'b[{z}', f'se[{z}', 'F[', 'slope', 'avg', 'share', 'n_funds',
                                'corr', 'lead', 'xi_AR', 'N'))}, flush=True)
pd.DataFrame(rows).to_csv('step17b_summary.csv', index=False)
fr = pd.DataFrame(fund_rows)
fr.to_csv('step17b_funds.csv', index=False)
fr['short'] = fr.name.str.split(': ').str[-1].str[:40]
pd.set_option('display.width', 250)
print(fr.pivot_table(index=['short', 'p_last'], columns='spec', values='e_last', sort=False).round(2).to_string())
