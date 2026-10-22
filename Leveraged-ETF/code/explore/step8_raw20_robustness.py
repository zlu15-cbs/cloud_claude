"""Robustness of the raw-entry fee-tier interaction (logit IV, Table 2 Panel A sample).

Baseline: cheap = fee at the fund's first raw month <= that month's 20th percentile across all raw index funds.
Tests:
  1. cutoff grid 10/15/20/25/30;
  2. cutoffs computed among funds that ever enter the estimation sample only;
  3. leave one firm out (Vanguard, BlackRock, State Street Global Advisors);
  4. tier interaction together with the broad-based interaction (Table A7);
  5. SPY's fee recorded as 0.04 in Oct 2022 - Sep 2023 (actual 0.0945) corrected to 0.0945;
  6. scan: fee changes that reverse within 12 months (possible recording errors like SPY's).

    python step8_raw20_robustness.py      # writes step8_robustness.csv, step8_fee_reversals.csv
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import build, first_stage_f
from tiers import raw_entry_tiers

pyblp.options.verbose = False
SPY = 27635
d0 = common.load('index')
d0['broad'] = (d0.broad_specialized == 'broad-based').astype(float)
funds = top15(d0)
tiers_all = raw_entry_tiers((0.10, 0.15, 0.20, 0.25, 0.30))
tiers_pop = raw_entry_tiers((0.20,), population=set(d0.product_ids))
rows = []


def est(label, d, tier, extra_z=()):
    d = d.assign(cheap=d.product_ids.map(tier).astype(float)).reset_index(drop=True)
    z = ['cheap', *extra_z]
    dd, formula, endog, excl, exog = build(d, dict(tier='A', z=z))
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
        se_type='clustered')
    f = first_stage_f(dd, endog, excl, exog)
    em = res.compute_elasticities()
    e = res.extract_diagonals(em).flatten()
    mc = res.compute_costs().flatten()
    lab = res.beta_labels
    b = dict(zip(lab, res.beta.flatten()))
    s = dict(zip(lab, res.beta_se.flatten()))
    ci = next(k for k in lab if 'cheap' in k)
    f15 = funds[funds.product_ids.isin(dd.product_ids)]
    last = dd.assign(e=e).sort_values('month_t').groupby('product_ids').last().loc[f15.product_ids]
    row = dict(test=label, N=len(dd), share_funds_cheap=float(dd.groupby('product_ids').cheap.first().mean()),
               b_rest=b['prices'], se_rest=s['prices'], b_interaction=b[ci], se_interaction=s[ci],
               b_cheap_total=b['prices'] + b[ci], min_F=min(f.values()),
               n15=len(f15), n15_gt1=int((last.e.abs() > 1).sum()),
               avg_own_e=float(res.extract_diagonal_means(em).flatten().mean()),
               share_gt1=float((np.abs(e) > 1).mean()), share_pos_e=float((e > 0).mean()),
               share_neg_mc=float((mc < 0).mean()))
    for k in extra_z:
        kk = next(x for x in lab if k in x)
        row[f'b[{kk}]'], row[f'se[{kk}]'] = b[kk], s[kk]
    rows.append(row)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)


# 1. cutoff grid
for q in (10, 15, 20, 25, 30):
    est(f'1. raw-entry {q}th pct (all raw funds)', d0, tiers_all[f'raw{q}'])
# 2. cutoffs from sample funds only
est('2. raw-entry 20th pct, cutoffs from sample funds only', d0, tiers_pop['raw20'])
# 3. leave one firm out
for firm in ('Vanguard', 'BlackRock', 'State Street Global Advisors'):
    est(f'3. raw-entry 20th pct, without {firm}', d0[d0.firm_ids != firm], tiers_all['raw20'])
# 4. with the broad-based interaction
d0['broad_x'] = d0.broad
est('4. raw-entry 20th pct + broad-based interaction', d0, tiers_all['raw20'], extra_z=('broad',))
# 5. SPY fee correction
spy_bad = (d0.product_ids == SPY) & (d0.month_t >= 2022 + 9 / 12 - 1e-9) & (d0.month_t <= 2023 + 8 / 12 + 1e-9)
print('SPY rows corrected:', int(spy_bad.sum()), 'fees there:', sorted(d0.loc[spy_bad, 'prices'].unique()))
d5 = d0.copy()
d5.loc[spy_bad, 'prices'] = 0.0945
est('5. raw-entry 20th pct, SPY fee corrected to 0.0945', d5, tiers_all['raw20'])
d5b = d0[~spy_bad]
est('5b. raw-entry 20th pct, SPY anomaly months dropped', d5b, tiers_all['raw20'])

out = pd.DataFrame(rows)
pd.set_option('display.width', 250, 'display.max_columns', 30)
print(out.round(3).to_string(index=False))
out.to_csv('step8_robustness.csv', index=False)

# 6. scan for fee changes that reverse within 12 months (sample funds, consecutive sample months)
d0['mk'] = np.round(d0.month_t * 12).astype(int)
rev = []
for pid, g in d0.sort_values('mk').groupby('product_ids'):
    p, m = g.prices.to_numpy(), g.mk.to_numpy()
    ch = np.flatnonzero(np.abs(np.diff(p)) > 1e-9) + 1  # index of the first month at the new fee
    for i in ch:
        for j in ch[ch > i]:
            if m[j] - m[i] <= 12 and abs(p[j] - p[i - 1]) < 1e-9 and abs(p[i] - p[i - 1]) >= 0.02:
                rev.append(dict(product_ids=pid, name=str(g.product_fund_name.iloc[-1]).split(': ')[-1][:45],
                                firm=g.firm_ids.iloc[-1], start=float(g.month_t.iloc[i]), months=int(m[j] - m[i]),
                                fee_before=p[i - 1], fee_during=p[i], aum_bn=float(g.product_mtna.iloc[i] / 1000)))
                break
rev = pd.DataFrame(rev)
print(f'\n6. temporary fee changes (>= 0.02 pp, reversed to the exact prior fee within 12 months): {len(rev)} episodes, '
      f'{rev.product_ids.nunique() if len(rev) else 0} funds; '
      f'share of sample fund-months inside an episode: {rev.months.sum() / len(d0):.4f}' if len(rev) else '\n6. none found')
if len(rev):
    print(rev.sort_values('aum_bn', ascending=False).head(25).round(3).to_string(index=False))
    rev.to_csv('step8_fee_reversals.csv', index=False)
