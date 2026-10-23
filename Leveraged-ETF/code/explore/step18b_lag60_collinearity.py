"""Follow-up to step18: (i) within-fund collinearity of z and p*z (lag-60 status, 20th pct) after FE and controls;
(ii) fees of switching funds by regime; (iii) Table 2 logit IV and the entry-tier interaction on the non-switcher
sample; (iv) the lag-60 model D on the switchers only (with z) and the implied net effect 'z*(b_z + b_pz*p)'.

    python step18b_lag60_collinearity.py      # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe

import common
from step2_logit_screen import add_variables, build, first_stage_f, CONTROLS
from tiers import RAW

pyblp.options.verbose = False
d = add_variables(common.load('index'))
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
d['e'] = d.raw20
d['z'] = np.where(m.c.notna(), m.c, d.e)
d['pz'] = d.prices * d.z
sw = d.groupby('product_ids').z.transform('nunique') > 1
print(f'switching funds: {d[sw].product_ids.nunique()} of {d.product_ids.nunique()}; {sw.mean():.3f} of fund-months')

ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]])
alg = pyhdfe.create(ids, drop_singletons=False)
W = alg.residualize(d[CONTROLS].to_numpy(float))
part = lambda c: (lambda M: M - W @ np.linalg.lstsq(W, M, rcond=None)[0])(alg.residualize(d[[c]].to_numpy(float))).ravel()
zt, pzt, pt, ht, hzt = part('z'), part('pz'), part('prices'), part('demand_instruments0'), None
d['hz'] = d.demand_instruments0 * d.z
hzt = part('hz')
cc = lambda a, b: float(np.corrcoef(a, b)[0, 1])
print(f'within-fund corr after FE+controls: corr(z, p*z) = {cc(zt, pzt):.3f}; corr(H*z, z) = {cc(hzt, zt):.3f}; '
      f'corr(p, p*z) = {cc(pt, pzt):.3f}; corr(H, H*z) = {cc(ht, hzt):.3f}')
r2 = lambda y, X: 1 - ((y - X @ np.linalg.lstsq(X, y, rcond=None)[0]) ** 2).sum() / (y ** 2).sum()
print(f'R2 of p*z on (z, p): {r2(pzt, np.column_stack([zt, pt])):.3f};  R2 of H*z on (z, H): {r2(hzt, np.column_stack([zt, ht])):.3f}')
g = d[sw]
print('switchers: mean fee by regime', g.groupby('z').prices.mean().round(3).to_dict(),
      '| non-switchers cheap / not:', d[~sw].groupby('z').prices.mean().round(3).to_dict())


def run(name, dd, zi, ctrl):
    dd, formula, endog, excl, exog = build(dd.reset_index(drop=True), dict(tier='-', z=zi, controls=ctrl))
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')
    f = first_stage_f(dd, endog, excl, exog)
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    s = dict(zip(res.beta_labels, res.beta_se.flatten()))
    avg = float(res.extract_diagonal_means(res.compute_elasticities()).flatten().mean())
    terms = ', '.join(f'{k} {b[k]:.2f} ({s[k]:.2f})' for k in b if 'prices' in k or k == 'z')
    print(f'{name:58s} N={len(dd):,} | {terms} | min F {min(f.values()):.1f} | avg e {avg:.2f}', flush=True)
    return b


ns = d[~sw]
run('non-switchers: Table 2 logit IV (p)', ns, [], [])
run('non-switchers: entry tier (p, p*e)', ns, ['e'], [])
run('non-switchers: lag-60 status, fixed (p, p*z)', ns, ['z'], [])
run('all funds: Table 2 logit IV (p)', d, [], [])
b = run('switchers only: D (p, p*z, z)', d[sw], ['z'], ['z'])
run('switchers only: Table 2 logit IV (p)', d[sw], [], [])
bD = run('all funds: D (p, p*z, z)', d, ['z'], ['z'])
bz, bpz = bD['z'], [v for k, v in bD.items() if 'prices*z' in k or 'z*prices' in k][0]
print(f'D: net effect of z at fee p is {bz:.2f} + ({bpz:.2f}) p, zero at p = {-bz / bpz:.3f}%; '
      f'at the switchers\' mean cheap-regime fee {g[g.z == 1].prices.mean():.3f}%: {bz + bpz * g[g.z == 1].prices.mean():.2f}; '
      f'at 0.03%: {bz + bpz * 0.03:.2f}')
