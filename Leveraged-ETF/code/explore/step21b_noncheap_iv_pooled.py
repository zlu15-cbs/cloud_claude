"""Pooled logit IV (main spec form: price + price x cheap, entry tier) with a different instrument for the non-cheap
funds. Instruments:
  main      H, H x cheap                                   (main spec, exactly identified)
  split     H x cheap, C x (1 - cheap)                     (each group its own instrument, exactly identified)
  over      H, H x cheap, C x (1 - cheap)                  (overidentified by 1; Hansen J)
C = BLP_IV_newproduct_1 (the coauthor's BLP instrument) or BLP_IV_newproduct_4 (strongest new-product count in step21).

    python step21b_noncheap_iv_pooled.py     # from a folder holding the index CSV; writes step21b_*.csv
"""
import numpy as np
import pandas as pd
import pyblp
from scipy import stats

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, build, first_stage_f, summarize, H

pyblp.options.verbose = False
d = add_variables(common.load('index'))
funds = top15(d)
rows, fund_rows = [], []
for q in (20, 15, 10):
    c = f'raw{q}'
    for C in ('BLP_IV_newproduct_1', 'BLP_IV_newproduct_4'):
        for name in ('main', 'split', 'over'):
            if name == 'main' and C != 'BLP_IV_newproduct_1':
                continue
            dd, formula, endog, excl, exog = build(d, dict(tier='A', z=[c]))
            h, ch, nc = dd[H].copy(), dd[c], 1 - dd[c]
            dd = dd.drop(columns=[x for x in dd.columns if x.startswith('demand_instruments')])
            ivs = {'main': [h, h * ch], 'split': [h * ch, dd[C] * nc], 'over': [h, h * ch, dd[C] * nc]}[name]
            for k, v in enumerate(ivs):
                dd[f'demand_instruments{k}'] = np.asarray(v, float)
            excl = [f'demand_instruments{k}' for k in range(len(ivs))]
            res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')
            f = first_stage_f(dd, endog, excl, exog)
            tag = f'q{q}:{name}' + ('' if name == 'main' else f':{C.replace("BLP_IV_", "")}')
            J = float(res.objective) if len(ivs) > 2 else np.nan
            row, fr = summarize(tag, dict(tier='A'), dd, res, funds, endog, f, dict(J=J, J_p=float(stats.chi2.sf(J, 1)) if len(ivs) > 2 else np.nan))
            e = res.extract_diagonals(res.compute_elasticities()).flatten()
            row['share_pos_e'] = float((e > 0).mean())
            row['n15_gt1'] = sum(abs(r['e_last']) > 1 for r in fr)
            b = dict(zip(res.beta_labels, res.beta.flatten()))
            s = dict(zip(res.beta_labels, res.beta_se.flatten()))
            kx = next(k for k in b if c in k)
            row.update(rest=b['prices'], rest_se=s['prices'], cheap_x=b[kx], cheap_x_se=s[kx], cheap_total=b['prices'] + b[kx],
                       min_F=min(f.values()))
            rows.append(row)
            fund_rows += fr
            print(f"{tag:32s} rest {b['prices']:7.2f} ({s['prices']:.2f}) | x cheap {b[kx]:7.2f} ({s[kx]:.2f}) | cheap total "
                  f"{row['cheap_total']:7.2f} | min F {row['min_F']:6.1f} | J p {row['J_p']:.3f} | avg e "
                  f"{row['avg_own_elasticity']:6.2f} | e>0 {row['share_pos_e']:.3f} | negMC {row['share_neg_mc_bertrand_firm']:.2f} | "
                  f"15>1 {row['n15_gt1']}", flush=True)
pd.DataFrame(rows).to_csv('step21b_noncheap_iv_pooled.csv', index=False)
fr = pd.DataFrame(fund_rows)
fr.to_csv('step21b_funds.csv', index=False)
fr['short'] = fr.name.str.split(': ').str[-1].str[:38]
pd.set_option('display.width', 300)
print(fr[fr.spec.str.startswith('q20')].pivot_table(index=['short', 'p_last'], columns='spec', values='e_last', sort=False).round(2).to_string())
