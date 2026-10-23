"""Split-sample diagnostic: Table 2 col 2 (logit IV) estimated separately on cheap and non-cheap funds.

For each group (entry tier at the 10th/15th/20th pct; plus the 20th-pct split of the 1,103 non-switching funds, where
the status is the lag-60 status): fund FE, month FE and the three controls estimated within the group, SE clustered by
month. Reported per group:
  OLS          delta on fee (FE, controls)
  first stage  fee on Hausman IV (FE, controls): coefficient, clustered SE, F = t^2
  reduced form delta on Hausman IV (FE, controls): coefficient, clustered SE
  IV           pyblp logit IV on the group = reduced form / first stage; clustered SE; per-market mean own elasticity
plus variation that identifies it: within-fund SD of fee and of the Hausman IV (after month FE), share of funds whose
fee ever changes in the sample.
delta = log share - log outside share; within a group the outside-share term is absorbed by the month FE.

    python step20_split_sample_iv.py     # from a folder holding the index CSV; writes step20_split_sample_iv.csv
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe

import common
from step2_logit_screen import add_variables, CONTROLS, H
from tiers import RAW

pyblp.options.verbose = False
d = add_variables(common.load('index'))
d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))

# lag-60 status (20th pct, entry fallback) to identify the non-switching funds
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
cut = raw.groupby('month_key').product_exp_ratio.quantile(0.20)
raw['c'] = (raw.product_exp_ratio <= raw.month_key.map(cut) + 1e-9).astype(float)
raw = raw.rename(columns={'product_j': 'product_ids'}).sort_values('month_key')
left = d[['product_ids', 'month_key']].copy()
left['target'] = left.month_key - 60
left = left.sort_values('target')
m = pd.merge_asof(left, raw[['product_ids', 'month_key', 'c']].rename(columns={'month_key': 'target'}),
                  on='target', by='product_ids', direction='backward').set_index(left.index).sort_index()
d['z60'] = np.where(m.c.notna(), m.c, d.raw20)
d['switcher'] = d.groupby('product_ids').z60.transform('nunique') > 1


def coef(y, x, g):
    b = float((x @ y) / (x @ x))
    u = y - b * x
    se = float(np.sqrt(((pd.Series(x * u).groupby(g).sum()) ** 2).sum()) / (x @ x))
    return b, se


def run(label, group, dd):
    dd = dd.reset_index(drop=True)
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    part = lambda c: (lambda M: M - W @ np.linalg.lstsq(W, M, rcond=None)[0])(alg.residualize(dd[[c]].to_numpy(float))).ravel()
    y, p, h = part('delta'), part('prices'), part(H)
    g = dd.market_ids.to_numpy()
    ols, ols_se = coef(y, p, g)
    fs, fs_se = coef(p, h, g)
    rf, rf_se = coef(y, h, g)
    res = pyblp.Problem(pyblp.Formulation('prices + ' + ' + '.join(CONTROLS), absorb='C(product_ids) + C(market_ids)'),
                        dd).solve(se_type='clustered')
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    s = dict(zip(res.beta_labels, res.beta_se.flatten()))
    e = res.extract_diagonals(res.compute_elasticities()).flatten()
    mm = lambda c: dd[c] - dd.groupby('market_ids')[c].transform('mean')
    within = lambda c: float((mm(c) - mm(c).groupby(dd.product_ids).transform('mean')).std())
    row = dict(split=label, group=group, funds=dd.product_ids.nunique(), fund_months=len(dd),
               mean_fee=float(dd.prices.mean()), median_fee=float(dd.prices.median()),
               share_funds_fee_changes=float((dd.groupby('product_ids').prices.nunique() > 1).mean()),
               sd_fee_within=within('prices'), sd_H_within=within(H),
               ols=ols, ols_se=ols_se, fs=fs, fs_se=fs_se, fs_F=(fs / fs_se) ** 2, rf=rf, rf_se=rf_se,
               iv=b['prices'], iv_se=s['prices'], iv_check=rf / fs,
               avg_e=float(res.extract_diagonal_means(res.compute_elasticities()).flatten().mean()),
               share_e_pos=float((e > 0).mean()),
               b_track=b['product_tracking_err'], b_ret=b['product_past_1yr_ret'], b_age=b['log_product_fund_age'])
    print(f"{label:34s} {group:10s} funds {row['funds']:5d} N {row['fund_months']:7,d} | OLS {ols:7.2f} ({ols_se:.2f}) | "
          f"FS {fs:6.3f} ({fs_se:.3f}) F {row['fs_F']:7.1f} | RF {rf:7.3f} ({rf_se:.3f}) | IV {row['iv']:7.2f} "
          f"({row['iv_se']:.2f}) | avg e {row['avg_e']:6.2f} | mean fee {row['mean_fee']:.3f} | "
          f"funds w/ fee change {row['share_funds_fee_changes']:.2f} | sd fee/H within {row['sd_fee_within']:.4f}/"
          f"{row['sd_H_within']:.4f}", flush=True)
    return row


rows = [run('Table 2 sample', 'all', d)]
for q in (10, 15, 20):
    c = f'raw{q}'
    rows += [run(f'entry tier {q}th pct', 'cheap', d[d[c] == 1]), run(f'entry tier {q}th pct', 'not cheap', d[d[c] == 0])]
ns = d[~d.switcher]
rows += [run('non-switchers, lag-60 20th', 'all', ns), run('non-switchers, lag-60 20th', 'cheap', ns[ns.z60 == 1]),
         run('non-switchers, lag-60 20th', 'not cheap', ns[ns.z60 == 0]), run('switchers, lag-60 20th', 'all', d[d.switcher])]
pd.DataFrame(rows).to_csv('step20_split_sample_iv.csv', index=False)
