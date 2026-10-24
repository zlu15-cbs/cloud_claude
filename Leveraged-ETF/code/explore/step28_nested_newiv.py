"""Nested logit IV with tracked-index nests (as step22), re-estimated with the share-class-matched Hausman IV (new_iv):
    ln s_j - ln s_0 = alpha p_j [+ alpha_c p_j cheap_j] + controls + rho ln s_{j|g} + fund FE + time FE + xi_j
Sample: the 97,429 fund-months where Z is defined. Price instruments: Z (and Z x cheap); for comparison the paper's
Hausman IV on the same rows. Nest instruments (built from the full raw file, as in step22):
  rivals    log number of funds tracking the same index that month
  rivals12  the same, 12 months earlier
  rivals+entrants+age  rivals, entrants in the last 12 months, rivals' mean log age (overidentified)
  coauthor  BLP_IV_rival_funds1 and BLP_IV_newproduct_1
Time FE: month, or month x asset class. 20th pct cheap tier (raw20); 10th and 15th for the main nest set.
Reports rho, slopes, Sanderson-Windmeijer F (with the same FE), Hansen J, elasticities, share e > 0, negative MC,
the 15 Table 5 funds.

    python step28_nested_newiv.py      # from a folder holding the index CSV; writes step28_*.csv
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe
from scipy import stats

from new_iv import load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import cluster_wald, summarize, CONTROLS
from tiers import RAW

pyblp.options.verbose = False
d = load_new_iv_sample()
funds = top15(d)

raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'product_fund_age'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
raw = raw.dropna(subset=['market_m_index'])
first = raw.groupby('product_j').month_key.min()
raw['entrant'] = (raw.month_key - raw.product_j.map(first) < 12).astype(float)
raw['lage'] = np.log(raw.product_fund_age.clip(lower=1 / 12))
nest = raw.groupby(['market_m_index', 'month_key']).agg(n=('product_j', 'nunique'), ent=('entrant', 'sum'),
                                                         age_sum=('lage', 'sum'), age_n=('lage', 'count')).reset_index()
d = d.merge(nest, on=['market_m_index', 'month_key'], how='left')
d['n'] = d.n.fillna(1)
d['nest_lrivals'] = np.log(d.n)
lag = nest[['market_m_index', 'month_key', 'n']].rename(columns={'n': 'n12'})
lag['month_key'] += 12
d = d.merge(lag, on=['market_m_index', 'month_key'], how='left')
d['nest_lrivals12'] = np.log(d.n12.fillna(0) + 1)
d['nest_entrants'] = d.ent.fillna(0)
own_age = np.log(d.product_fund_age.clip(lower=1 / 12))
d['nest_rival_age'] = ((d.age_sum - own_age) / (d.age_n - 1)).where(d.age_n > 1, 0).fillna(0)
d['nesting_ids'] = d.market_m_index
# within-nest share among the estimation sample's funds (pyblp computes it the same way from nesting_ids)
d['lnsjg'] = np.log(d.shares / d.groupby(['market_ids', 'nesting_ids']).shares.transform('sum'))
print(f'N={len(d):,}; nests {d.nesting_ids.nunique()}; alone in nest {float((d.lnsjg == 0).mean()):.3f}', flush=True)

NEST_SETS = {
    'rivals': ['nest_lrivals'],
    'rivals12': ['nest_lrivals12'],
    'rivals+entrants+age': ['nest_lrivals', 'nest_entrants', 'nest_rival_age'],
    'coauthor': ['BLP_IV_rival_funds1', 'BLP_IV_newproduct_1'],
}


def first_stage_f(d, endog, excl, exog, tfe):
    """Sanderson-Windmeijer F per endogenous term, with fund FE and the given time FE partialled out."""
    ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d[tfe])[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(d[exog].to_numpy(float))
    part = lambda M: M - W @ np.linalg.lstsq(W, M, rcond=None)[0]
    X = part(alg.residualize(d[endog].to_numpy(float)))
    Z = part(alg.residualize(d[excl].to_numpy(float)))
    g = d.market_ids.to_numpy()
    k, L = len(endog), len(excl)
    out = {}
    for j, name in enumerate(endog):
        x = X[:, j]
        if k > 1:
            Xo = np.delete(X, j, axis=1)
            Pz = Z @ np.linalg.lstsq(Z, Xo, rcond=None)[0]
            x = x - Xo @ np.linalg.lstsq(Pz, x, rcond=None)[0]
        out[name] = cluster_wald(x, Z, g) / (L - k + 1)
    return out


def run(tag, dd, z, cheap, nest_ivs, tfe, rho0=0.5):
    dd = dd.reset_index(drop=True).copy()
    h = dd[z].to_numpy(float)
    dd = dd.drop(columns=[c for c in dd.columns if c.startswith('demand_instruments')])
    ivs = [h] + ([h * dd[cheap]] if cheap else []) + [dd[c] for c in nest_ivs]
    for k, v in enumerate(ivs):
        dd[f'demand_instruments{k}'] = np.asarray(v, float)
    excl = [f'demand_instruments{k}' for k in range(len(ivs))]
    terms = ['prices'] + ([f'I(prices*{cheap})'] if cheap else [])
    if cheap:
        dd['px'] = dd.prices * dd[cheap]
    endog = ['prices'] + (['px'] if cheap else []) + ['lnsjg']
    problem = pyblp.Problem(pyblp.Formulation(' + '.join(terms + CONTROLS), absorb=f'C(product_ids) + C({tfe})'), dd)
    res = problem.solve(rho=rho0, rho_bounds=(0, 0.99), se_type='clustered',
                        optimization=pyblp.Optimization('l-bfgs-b', {'gtol': 1e-10}))
    f = first_stage_f(dd, endog, excl, CONTROLS, tfe)
    L, K = len(excl), len(endog)
    J = float(res.objective) if L > K else np.nan
    row, fr = summarize(tag, dict(tier='A'), dd, res, funds[funds.product_ids.isin(dd.product_ids)], [], f,
                        dict(J=J, J_df=L - K, J_p=float(stats.chi2.sf(J, L - K)) if L > K else np.nan))
    e = res.extract_diagonals(res.compute_elasticities()).flatten()
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    s = dict(zip(res.beta_labels, res.beta_se.flatten()))
    row.update(rho=float(res.rho[0, 0]), rho_se=float(res.rho_se[0, 0]), share_pos_e=float((e > 0).mean()),
               rest=b['prices'], rest_se=s['prices'], F_p=f['prices'], F_lnsjg=f['lnsjg'],
               n15_gt1=sum(abs(r['e_last']) > 1 for r in fr), converged=bool(res.converged))
    if cheap:
        kx = next(k for k in b if cheap in k)
        row.update(cheap_x=b[kx], cheap_x_se=s[kx], cheap_total=b['prices'] + b[kx], F_px=f['px'])
    print(f"{tag:62s} rho {row['rho']:.3f} ({row['rho_se']:.3f}) | price {row['rest']:7.2f} ({row['rest_se']:.2f})"
          + (f" | x cheap {row['cheap_x']:7.2f} ({row['cheap_x_se']:.2f}) total {row['cheap_total']:7.2f}" if cheap else '')
          + f" | F p/lnsjg {row['F_p']:.1f}/{row['F_lnsjg']:.1f} | J p {row['J_p']:.3f} | avg e {row['avg_own_elasticity']:.2f} | "
          f"e>0 {row['share_pos_e']:.3f} | negMC {row['share_neg_mc_bertrand_firm']:.2f} | 15>1 {row['n15_gt1']} | conv {row['converged']}",
          flush=True)
    return row, fr


rows, fund_rows = [], []


def add(*a):
    r, fr = run(*a)
    rows.append(r)
    fund_rows.extend(fr)


for fe, tfe in (('month', 'market_ids'), ('month x ac', 'mkt_ac')):
    for z, zname in (('Z', 'new IV'), ('Z_paper', 'paper IV')):
        for name, ivs in NEST_SETS.items():
            add(f'{zname} | {fe} | cheap 20 | {name}', d, z, 'raw20', ivs, tfe)
    for name in ('rivals', 'rivals12'):
        add(f'new IV | {fe} | one slope | {name}', d, 'Z', None, NEST_SETS[name], tfe)
        for q in (15, 10):
            add(f'new IV | {fe} | cheap {q} | {name}', d, 'Z', f'raw{q}', NEST_SETS[name], tfe)
# split sample, 20th pct, new IV, each group with its own FE
for grp, mask in (('not cheap', d.raw20 == 0), ('cheap', d.raw20 == 1)):
    for name in ('rivals', 'rivals12'):
        add(f'new IV | month | split 20 {grp} | {name}', d[mask], 'Z', None, NEST_SETS[name], 'market_ids')
pd.DataFrame(rows).to_csv('step28_nested_newiv.csv', index=False)
fr = pd.DataFrame(fund_rows)
fr.to_csv('step28_funds.csv', index=False)
fr['short'] = fr.name.str.split(': ').str[-1].str[:38]
pd.set_option('display.width', 300)
sel = fr[fr.spec.str.contains(r'new IV \| month \| cheap 20 \| rivals')]
print(sel.pivot_table(index=['short', 'p_last'], columns='spec', values='e_last', sort=False).round(2).to_string())
