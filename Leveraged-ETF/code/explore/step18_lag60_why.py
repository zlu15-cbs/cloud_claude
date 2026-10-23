"""Why does the lag-60 cheap status (20th pct, step17) move both price coefficients from Table 2's -5.6 to -28 / -48?

Adds the lag-60 terms one at a time (logit IV, Table 2 Panel A, fund and month FE, clustered SE):
  A  p                            IV: H                     (Table 2 col 2)
  B  p + z                        IV: H                     (main effect of the lag-60 status only)
  C  p + p*z                      IV: H, H*z                (interaction only)
  D  p + p*z + z                  IV: H, H*z                (step17)
  E  p + p*e                      IV: H, H*e                (entry tier, main spec)
  F  p + p*e + z                  IV: H, H*e                (entry tier plus the lag-60 status main effect)
where z = lag-60 status (entry fallback), e = entry tier, H = Hausman fee IV.

For the single-endogenous specs A and B: alpha = reduced form / first stage (coefficients of H on delta and on p after
partialling out FE and the exogenous controls), and the IV omitted-variable formula
  alpha_A - alpha_B = gamma_B * cov(H~, z~) / cov(H~, p~)      (tilde: residual on FE and controls of A)
which splits the gap into the main effect of z (gamma_B) and how strongly the instrument co-moves with z.
Also: an event study of delta and p around the month a fund's lag-60 status switches from 0 to 1.

    python step18_lag60_why.py     # from a folder holding the index CSV; writes step18_*.csv
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe

import common
from step2_logit_screen import add_variables, build, first_stage_f, CONTROLS, H
from tiers import RAW

pyblp.options.verbose = False
L, Q = 60, 0.20

d = add_variables(common.load('index'))
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
cut = raw.groupby('month_key').product_exp_ratio.quantile(Q)
raw['c'] = (raw.product_exp_ratio <= raw.month_key.map(cut) + 1e-9).astype(float)
raw = raw.rename(columns={'product_j': 'product_ids'}).sort_values('month_key')
left = d[['product_ids', 'month_key']].copy()
left['target'] = left.month_key - L
left = left.sort_values('target')
m = pd.merge_asof(left, raw[['product_ids', 'month_key', 'c']].rename(columns={'month_key': 'target'}),
                  on='target', by='product_ids', direction='backward').set_index(left.index).sort_index()
d['e'] = d['raw20']
d['z'] = np.where(m.c.notna(), m.c, d.e)
outside = 1 - d.groupby('market_ids').shares.transform('sum')
d['delta'] = np.log(d.shares) - np.log(outside)
print(f'N = {len(d):,}; z = 1 in {d.z.mean():.3f} of fund-months; e = 1 in {d.e.mean():.3f}; '
      f'z != e in {(d.z != d.e).mean():.3f}', flush=True)


def solve(formula, dd):
    return pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')


rows = []
specs = {'A': ([], []), 'B': ([], ['z']), 'C': (['z'], []), 'D': (['z'], ['z']), 'E': (['e'], []), 'F': (['e'], ['z'])}
for name, (zi, ctrl) in specs.items():
    dd, formula, endog, excl, exog = build(d, dict(tier='-', z=zi, controls=ctrl))
    res = solve(formula, dd)
    f = first_stage_f(dd, endog, excl, exog)
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    se = dict(zip(res.beta_labels, res.beta_se.flatten()))
    em = res.compute_elasticities()
    row = dict(spec=name, formula=formula, avg_e=float(res.extract_diagonal_means(em).flatten().mean()),
               min_F=min(f.values()))
    for k in b:
        row[f'b[{k}]'], row[f'se[{k}]'] = b[k], se[k]
    rows.append(row)
    print(f'\n=== {name}: {formula}  excl={excl}')
    print({k: round(v, 3) if isinstance(v, float) else v for k, v in row.items() if k != 'formula'}, flush=True)
pd.DataFrame(rows).to_csv('step18_specs.csv', index=False)

# first stage / reduced form and the IV omitted-variable formula, single-endogenous specs
ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]])
alg = pyhdfe.create(ids, drop_singletons=False)
R = lambda cols: alg.residualize(d[cols].to_numpy(float))
g = d.market_ids.to_numpy()


def partial(M, W):
    return M - W @ np.linalg.lstsq(W, M, rcond=None)[0]


def ols(y, x):
    return float((x @ y) / (x @ x))


def cl_se(y, x):
    bb = ols(y, x)
    u = y - bb * x
    return float(np.sqrt(((pd.Series(x * u).groupby(g).sum()) ** 2).sum()) / (x @ x))


out = []
for name, ctrl in (('A', CONTROLS), ('B', CONTROLS + ['z'])):
    W = R(ctrl)
    y, p, h = (partial(R([c]).ravel()[:, None], W).ravel() for c in ('delta', 'prices', H))
    fs, rf = ols(p, h), ols(y, h)
    out.append(dict(spec=name, first_stage=fs, first_stage_se=cl_se(p, h), reduced_form=rf,
                    reduced_form_se=cl_se(y, h), alpha=rf / fs))
W = R(CONTROLS)
y, p, h, zz = (partial(R([c]).ravel()[:, None], W).ravel() for c in ('delta', 'prices', H, 'z'))
gamma_B = [r for r in rows if r['spec'] == 'B'][0]['b[z]']
ovb = gamma_B * float(h @ zz) / float(h @ p)
out.append(dict(spec='OVB: gamma_B * cov(H,z)/cov(H,p)', alpha=ovb,
                first_stage=float(h @ zz) / float(h @ h),  # coefficient of z on H (residualized)
                reduced_form=gamma_B))
# what z does to the instrument and to delta, within fund
out.append(dict(spec='OLS z~ on H~ (instrument co-moves with z)', first_stage=ols(zz, h), first_stage_se=cl_se(zz, h)))
out.append(dict(spec='OLS delta~ on z~ (no price)', reduced_form=ols(y, zz), reduced_form_se=cl_se(y, zz)))
out.append(dict(spec='OLS p~ on z~', first_stage=ols(p, zz), first_stage_se=cl_se(p, zz)))
pd.DataFrame(out).to_csv('step18_decomposition.csv', index=False)
print('\nFirst stage / reduced form / OVB:')
print(pd.DataFrame(out).round(4).to_string(index=False), flush=True)

# event study: funds whose lag-60 status switches 0 -> 1 once; delta and p (net of month FE) around the switch
d['res_delta'] = d.delta - d.groupby('market_ids').delta.transform('mean')
d['res_p'] = d.prices - d.groupby('market_ids').prices.transform('mean')
d['res_h'] = d[H] - d.groupby('market_ids')[H].transform('mean')
ev = []
for pid, gg in d.sort_values('month_key').groupby('product_ids'):
    s = gg.z.to_numpy()
    ch = np.flatnonzero(np.diff(s) != 0)
    if len(ch) == 1 and s[ch[0]] == 0 and s[ch[0] + 1] == 1:
        t0 = gg.month_key.iloc[ch[0] + 1]
        x = gg.assign(k=gg.month_key - t0)
        x = x[(x.k >= -36) & (x.k <= 36)]
        x = x.assign(res_delta=x.res_delta - x.res_delta[x.k < 0].mean() if (x.k < 0).any() else np.nan,
                     res_p=x.res_p - x.res_p[x.k < 0].mean() if (x.k < 0).any() else np.nan,
                     res_h=x.res_h - x.res_h[x.k < 0].mean() if (x.k < 0).any() else np.nan)
        ev.append(x[['product_ids', 'k', 'res_delta', 'res_p', 'res_h']])
ev = pd.concat(ev)
ev['bin'] = (np.floor(ev.k / 6) * 6).astype(int)
tab = ev.groupby('bin').agg(n=('product_ids', 'nunique'), delta=('res_delta', 'mean'), price=('res_p', 'mean'),
                            hausman=('res_h', 'mean'))
tab.to_csv('step18_event_study.csv')
print(f'\nEvent study around a single 0->1 switch ({ev.product_ids.nunique()} funds); values relative to the '
      f'fund\'s pre-switch mean, net of month means; bins of 6 months:')
print(tab.round(3).to_string(), flush=True)
