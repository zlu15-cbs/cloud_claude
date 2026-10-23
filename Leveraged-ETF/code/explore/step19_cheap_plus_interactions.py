"""Logit IV with price x cheap (entry tier) plus one more price interaction at a time: ETF vs mutual fund, institutional
share class, full share class, broad-based, Big 3, firm dummies. Each p*z is instrumented by Hausman IV x z. Every z is
fixed per fund (absorbed by fund FE), so no main effects are needed. Table 2 Panel A sample; SE clustered by month.

Share class is parsed from fund names for mutual funds (code in step2_logit_screen.add_variables):
  sc_inst   institutional / Admiral / Institutional Plus / class I, K, Y, Z, R6, Premier, Select
  sc_retail Investor / retail / class A, C, R, T / service / advisor
  sc_mf_other other mutual-fund classes; ETFs are the base group in the full share-class spec.

    python step19_cheap_plus_interactions.py [10 15 20]   # cheap cutoff(s), default 20
"""
import sys

import numpy as np
import pandas as pd
import pyblp

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, build, first_stage_f, summarize

pyblp.options.verbose = False

d = add_variables(common.load('index'))
funds = top15(d)
d['mf'] = 1 - d.etf
d['mf_noninst'] = d.mf * (1 - d.sc_inst)
fm = d.groupby('product_ids')[['etf', 'sc_inst', 'sc_retail', 'sc_mf_other', 'broad', 'big3']].first()
print('share of funds:', fm.mean().round(3).to_dict(), flush=True)
print('share of fund-months:', d[['etf', 'sc_inst', 'sc_retail', 'sc_mf_other', 'broad', 'big3']].mean().round(3).to_dict())

cutoffs = [int(a) for a in sys.argv[1:]] or [20]
rows, fund_rows = [], []
for q in cutoffs:
    c = f'raw{q}'
    print(f'\ncheap = {c}: share of funds {d.groupby("product_ids")[c].first().mean():.3f}; '
          f'cheap x ETF {d.groupby("product_ids").apply(lambda g: (g[c].iloc[0] * g.etf.iloc[0])).mean():.3f}; '
          f'cheap x inst {d.groupby("product_ids").apply(lambda g: (g[c].iloc[0] * g.sc_inst.iloc[0])).mean():.3f}',
          flush=True)
    specs = {
        'cheap': [c],
        'etf': ['etf'],
        'inst': ['sc_inst'],
        'cheap+etf': [c, 'etf'],
        'cheap+inst': [c, 'sc_inst'],
        'cheap+etf+inst': [c, 'etf', 'sc_inst'],                  # base: non-institutional mutual funds
        'cheap+shareclass': [c, 'sc_inst', 'sc_retail', 'sc_mf_other'],  # base: ETFs
        'cheap+broad': [c, 'broad'],
        'cheap+big3': [c, 'big3'],
        'cheap+firms': [c, 'vanguard', 'blackrock', 'ssga'],
        'cheap+etf+inst+broad+big3': [c, 'etf', 'sc_inst', 'broad', 'big3'],
    }
    for name, z in specs.items():
        if q != 20 and not name.startswith('cheap'):
            continue
        dd, formula, endog, excl, exog = build(d, dict(tier='A', z=z))
        res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(
            se_type='clustered')
        f = first_stage_f(dd, endog, excl, exog)
        tag = f'q{q}:{name}'
        row, fr = summarize(tag, dict(tier='A'), dd, res, funds, endog, f, {})
        e = res.extract_diagonals(res.compute_elasticities()).flatten()
        row['share_pos_e'] = float((e > 0).mean())
        row['avg_e_market_mean'] = row.pop('avg_own_elasticity')
        row['min_F'] = min(f.values())
        row['n15_gt1'] = sum(abs(r['e_last']) > 1 for r in fr)
        rows.append(row)
        fund_rows += fr
        b = dict(zip(res.beta_labels, res.beta.flatten()))
        s = dict(zip(res.beta_labels, res.beta_se.flatten()))
        terms = ', '.join(f'{k}: {b[k]:.2f} ({s[k]:.2f}, t={b[k] / s[k]:.1f})' for k in b if 'prices' in k)
        print(f'{tag:34s} | {terms} | min F {row["min_F"]:.1f} | avg e {row["avg_e_market_mean"]:.2f} | '
              f'e>0 {row["share_pos_e"]:.3f} | negMC {row["share_neg_mc_bertrand_firm"]:.2f} | 15>1 {row["n15_gt1"]}',
              flush=True)
suffix = '_'.join(map(str, cutoffs))
pd.DataFrame(rows).to_csv(f'step19_summary_{suffix}.csv', index=False)
fr = pd.DataFrame(fund_rows)
fr.to_csv(f'step19_funds_{suffix}.csv', index=False)
fr['short'] = fr.name.str.split(': ').str[-1].str[:40]
pd.set_option('display.width', 300)
print(fr.pivot_table(index=['short', 'p_last'], columns='spec', values='e_last', sort=False).round(2).to_string())
