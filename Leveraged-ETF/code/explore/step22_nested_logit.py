"""Nested logit IV, nests = tracked index (market_m_index), linear in the fee (Berry 1994):
    ln s_j - ln s_0 = alpha p_j [+ alpha_c p_j cheap_j] + controls + rho ln s_{j|g} + fund FE + month FE + xi_j
estimated in pyblp (nesting_ids = tracked index, rho estimated by GMM; elasticities and costs account for the nests).
Endogenous: p (and p x cheap) and ln s_{j|g}. Price instruments: Hausman IV (and x cheap). Nest instruments, built
from the FULL raw file (all funds tracking the index, before the sample's share filter):
  nest_lrivals    log(1 + number of other funds tracking the same index that month)
  nest_lrivals12  the same, 12 months earlier
  nest_entrants   funds whose first raw month is in the last 12 months, same index
  nest_rival_age  mean log age of the other funds tracking the index
  coauthor        BLP_IV_rival_funds1 and BLP_IV_newproduct_1 (coauthor's constructions)
Runs: (A) one slope, (B) main spec with cheap (entry tier), each with several nest-instrument sets, plus the
split-sample version (cheap / non-cheap separately, group-specific FE). Reports rho, slopes, Sanderson-Windmeijer F,
Hansen J, average own elasticity, share e > 0, negative MC, the 15 Table 5 funds.

    python step22_nested_logit.py      # from a folder holding the index CSV; writes step22_*.csv
"""
import numpy as np
import pandas as pd
import pyblp
from scipy import stats

import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, first_stage_f, summarize, CONTROLS, H
from tiers import RAW

pyblp.options.verbose = False
d = add_variables(common.load('index'))
funds = top15(d)

# nest instruments from the raw file
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'product_fund_age'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
raw = raw.dropna(subset=['market_m_index'])
first = raw.groupby('product_j').month_key.min()
raw['entrant'] = (raw.month_key - raw.product_j.map(first) < 12).astype(float)
raw['lage'] = np.log(raw.product_fund_age.clip(lower=1 / 12)) if raw.product_fund_age.notna().any() else np.nan
nest = raw.groupby(['market_m_index', 'month_key']).agg(n=('product_j', 'nunique'), ent=('entrant', 'sum'),
                                                         age_sum=('lage', 'sum'), age_n=('lage', 'count')).reset_index()
d = d.merge(nest, on=['market_m_index', 'month_key'], how='left')
d['n'] = d.n.fillna(1)
d['nest_lrivals'] = np.log(d.n)  # log(1 + rivals) = log(n)
lag = nest[['market_m_index', 'month_key', 'n']].rename(columns={'n': 'n12'})
lag['month_key'] += 12
d = d.merge(lag, on=['market_m_index', 'month_key'], how='left')
d['nest_lrivals12'] = np.log(d.n12.fillna(0) + 1)
d['nest_entrants'] = d.ent.fillna(0) - d.groupby('product_ids').month_key.transform(lambda s: 0)  # count in nest
own_age = np.log(d.product_fund_age.clip(lower=1 / 12)) if 'product_fund_age' in d else 0
d['nest_rival_age'] = ((d.age_sum - own_age) / (d.age_n - 1)).where(d.age_n > 1, 0).fillna(0)
d['nesting_ids'] = d.market_m_index
d['lnsjg'] = np.log(d.shares / d.groupby(['market_ids', 'nesting_ids']).shares.transform('sum'))
print(f'N={len(d):,}; nests {d.nesting_ids.nunique()}; alone in nest {float((d.lnsjg == 0).mean()):.3f}; '
      f'within-fund SD of log rivals {float((d.nest_lrivals - d.groupby("product_ids").nest_lrivals.transform("mean")).std()):.3f}',
      flush=True)

NEST_SETS = {
    'rivals': ['nest_lrivals'],
    'rivals12': ['nest_lrivals12'],
    'rivals+entrants+age': ['nest_lrivals', 'nest_entrants', 'nest_rival_age'],
    'coauthor': ['BLP_IV_rival_funds1', 'BLP_IV_newproduct_1'],
}


def run(tag, dd, cheap, nest_ivs, rho0=0.5):
    dd = dd.reset_index(drop=True).copy()
    h = dd[H].to_numpy(float)
    dd = dd.drop(columns=[c for c in dd.columns if c.startswith('demand_instruments')])
    ivs = [h] + ([h * dd[cheap]] if cheap else []) + [dd[c] for c in nest_ivs]
    for k, v in enumerate(ivs):
        dd[f'demand_instruments{k}'] = np.asarray(v, float)
    excl = [f'demand_instruments{k}' for k in range(len(ivs))]
    terms = ['prices'] + ([f'I(prices*{cheap})'] if cheap else [])
    if cheap:
        dd['px'] = dd.prices * dd[cheap]
    endog = ['prices'] + (['px'] if cheap else []) + ['lnsjg']
    formula = ' + '.join(terms + CONTROLS)
    problem = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd)
    res = problem.solve(rho=rho0, rho_bounds=(0, 0.99), se_type='clustered',
                        optimization=pyblp.Optimization('l-bfgs-b', {'gtol': 1e-10}))
    f = first_stage_f(dd, endog, excl, CONTROLS)
    L, K = len(excl), len(endog)
    J = float(res.objective) if L > K else np.nan
    row, fr = summarize(tag, dict(tier='A'), dd, res, funds[funds.product_ids.isin(dd.product_ids)], [], f,
                        dict(J=J, J_df=L - K, J_p=float(stats.chi2.sf(J, L - K)) if L > K else np.nan))
    e = res.extract_diagonals(res.compute_elasticities()).flatten()
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    s = dict(zip(res.beta_labels, res.beta_se.flatten()))
    row.update(rho=float(res.rho[0, 0]), rho_se=float(res.rho_se[0, 0]), share_pos_e=float((e > 0).mean()),
               rest=b['prices'], rest_se=s['prices'], min_F=min(f.values()), F_lnsjg=f['lnsjg'], F_p=f['prices'],
               n15_gt1=sum(abs(r['e_last']) > 1 for r in fr), converged=bool(res.converged))
    if cheap:
        kx = next(k for k in b if cheap in k)
        row.update(cheap_x=b[kx], cheap_x_se=s[kx], cheap_total=b['prices'] + b[kx], F_px=f['px'])
    print(f"{tag:46s} rho {row['rho']:.3f} ({row['rho_se']:.3f}) | price {row['rest']:7.2f} ({row['rest_se']:.2f})"
          + (f" | x cheap {row['cheap_x']:7.2f} ({row['cheap_x_se']:.2f}) total {row['cheap_total']:7.2f}" if cheap else '')
          + f" | F p/lnsjg {row['F_p']:.1f}/{row['F_lnsjg']:.1f} | J p {row['J_p']:.3f} | avg e {row['avg_own_elasticity']:.2f} | "
          f"e>0 {row['share_pos_e']:.3f} | negMC {row['share_neg_mc_bertrand_firm']:.2f} | 15>1 {row['n15_gt1']} | conv {row['converged']}",
          flush=True)
    return row, fr


rows, fund_rows = [], []
for name, ivs in NEST_SETS.items():
    r, fr = run(f'one slope | {name}', d, None, ivs)
    rows.append(r); fund_rows += fr
for q in (20, 15, 10):
    for name, ivs in NEST_SETS.items():
        r, fr = run(f'cheap {q} | {name}', d, f'raw{q}', ivs)
        rows.append(r); fund_rows += fr
# split sample, 20th pct: each group with its own FE
for grp, mask in (('not cheap', d.raw20 == 0), ('cheap', d.raw20 == 1)):
    for name, ivs in NEST_SETS.items():
        r, fr = run(f'split 20 {grp} | {name}', d[mask], None, ivs)
        rows.append(r); fund_rows += fr
pd.DataFrame(rows).to_csv('step22_nested_logit.csv', index=False)
fr = pd.DataFrame(fund_rows)
fr.to_csv('step22_funds.csv', index=False)
fr['short'] = fr.name.str.split(': ').str[-1].str[:38]
pd.set_option('display.width', 300)
sel = fr[fr.spec.str.startswith(('one slope', 'cheap 20'))]
print(sel.pivot_table(index=['short', 'p_last'], columns='spec', values='e_last', sort=False).round(2).to_string())
