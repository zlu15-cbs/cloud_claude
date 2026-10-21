"""Why do first-month and 12-month-average 40% tiers give different slopes? Composition check (logit IV).

1. Ties: how many funds sit exactly at the cutoff fee (the rank-based split breaks ties by row order).
2. Re-estimate both rules (a) on all funds, (b) without the funds that switch group between the rules,
   (c) with a value cutoff (fee <= 0.20) instead of ranks.
3. For the switchers: fee path and log-share change around their largest fee change.
"""
import numpy as np
import pandas as pd
import pyblp

import common
from step2_logit_screen import add_variables, build, first_stage_f

pyblp.options.verbose = False
d = add_variables(common.load('index'))
srt = d.sort_values('month_t')
first = srt.groupby('product_ids').prices.first()
avg12 = srt.groupby('product_ids').head(12).groupby('product_ids').prices.mean()
print('funds with first-month fee exactly 0.20:', int((first.round(4) == 0.20).sum()),
      '| funds with 12-month average exactly 0.20:', int((avg12.round(4) == 0.20).sum()), 'of', len(first))
sw = d.groupby('product_ids')[['fee_b40', 'fee12_b40']].first()
switch = sw.index[sw.fee_b40 != sw.fee12_b40]
print('switchers:', len(switch), '| cheap under first month only:', int(((sw.fee_b40 == 1) & (sw.fee12_b40 == 0)).sum()),
      '| cheap under 12-month avg only:', int(((sw.fee_b40 == 0) & (sw.fee12_b40 == 1)).sum()))


def est(dd, col, label):
    dd = dd.assign(cheap=dd[col])
    dd, formula, endog, excl, exog = build(dd, dict(tier='A', z=['cheap']))
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
        se_type='clustered')
    b, s = res.beta.flatten(), res.beta_se.flatten()
    f = first_stage_f(dd, endog, excl, exog)
    print(f'{label:58s} rest {b[0]:7.2f} ({s[0]:5.2f})  cheap {b[0] + b[1]:7.2f}  F {min(f.values()):5.1f}', flush=True)


d['val_first'] = d.product_ids.map(first <= 0.20 + 1e-9).astype(float)
d['val_avg12'] = d.product_ids.map(avg12 <= 0.20 + 1e-9).astype(float)
keep = d[~d.product_ids.isin(switch)].reset_index(drop=True)
for col, lab in [('fee_b40', 'first month, rank 40%'), ('fee12_b40', '12-month avg, rank 40%')]:
    est(d, col, lab + ', all funds')
    est(keep, col, lab + f', without the {len(switch)} switchers')
for col, lab in [('val_first', 'first month, value cutoff fee <= 0.20'), ('val_avg12', '12-month avg, value cutoff fee <= 0.20')]:
    print(f'   ({lab}: {d.groupby("product_ids")[col].first().mean():.2f} of funds cheap)')
    est(d, col, lab)

d['lms'] = np.log(d.shares)
rows = []
for pid in switch:
    g = d[d.product_ids == pid].sort_values('month_key')
    dp = g.prices.diff()
    k = dp.abs().idxmax()
    i = g.index.get_loc(k)
    pre, post = g.iloc[max(0, i - 12):i], g.iloc[i:i + 12]
    rows.append(dict(name=str(g.product_fund_name.iloc[-1]).split(': ')[-1][:42], first_month=int(sw.loc[pid, 'fee_b40']),
                     avg12=int(sw.loc[pid, 'fee12_b40']), fee_first=first[pid], fee_avg12=round(avg12[pid], 3),
                     fee_before=pre.prices.mean(), fee_after=post.prices.mean(),
                     dlog_share_12m=post.lms.mean() - pre.lms.mean()))
r = pd.DataFrame(rows)
r['response_per_pp'] = r.dlog_share_12m / (r.fee_after - r.fee_before)
print(r.sort_values('fee_before', ascending=False).round(3).to_string(index=False))
