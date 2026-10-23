"""Lead tests for the fee instruments, written to be replicated.

Question: do a fund's PAST demand shocks predict TODAY's instrument? If the instrument reflects family cost conditions
unrelated to this fund's demand, they should not.

Procedure, for an instrument Z, a demand model M and a fixed-effect set FE (fund + month, or fund + month x asset class):
  1. Estimate M by logit IV with pyblp (absorb fund FE and the time FE; controls: tracking error, past 1-yr return,
     log age; instruments Z [and Z x cheap]). Take the residual xi_hat = res.xi, which equals (delta - X beta_hat) with
     the absorbed fixed effects removed (delta = log share - log outside share).
  2. Residualize the instrument: Z~ = residual of Z on fund FE, the time FE and the three controls (Frisch-Waugh).
  3. Index months by month_key = round(12 * month_t). For each lag k in {12, 24, 36}, pair every fund-month (j, t)
     with the same fund's residual k months earlier: (Z~_{j,t}, xi_hat_{j,t-k}). Keep pairs where both exist.
  4. Demean both variables within fund over the paired sample.
  5. OLS without constant: xi_hat_{j,t-k} = b * Z~_{j,t} + u. Standard error clustered by the calendar month t of the
     instrument observation (no small-sample correction). Report t = b / SE.
A significant b means past demand shocks of the fund predict its family's later fees in the instrument's markets.

Rows computed: the paper's Hausman IV on the full Table 2 sample; and, on the 97,429 fund-months where the
share-class-matched instrument is defined, both instruments x {one-slope model (Table 2 col 2), main model with
price x cheap (20th pct)} x {fund + month FE, fund + month x asset class FE}.

    python step27_lead_tests.py      # from a folder holding the index CSV; writes step27_lead_tests.csv
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe

import common
from new_iv import load_new_iv_sample
from step2_logit_screen import add_variables, CONTROLS, H

pyblp.options.verbose = False


def fit(d, z, tfe, cheap=None):
    d = d.reset_index(drop=True).copy()
    zz = d[z].to_numpy(float)
    d = d.drop(columns=[c for c in d.columns if c.startswith('demand_instruments')])
    d['demand_instruments0'] = zz
    terms = ['prices']
    if cheap:
        d['demand_instruments1'] = zz * d[cheap]
        terms.append(f'I(prices*{cheap})')
    res = pyblp.Problem(pyblp.Formulation(' + '.join(terms + CONTROLS), absorb=f'C(product_ids) + C({tfe})'), d).solve(se_type='clustered')
    return d, res


def lead_test(d, xi, z, tfe):
    ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d[tfe])[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(d[CONTROLS].to_numpy(float))
    zt = alg.residualize(d[[z]].to_numpy(float))
    zt = (zt - W @ np.linalg.lstsq(W, zt, rcond=None)[0]).ravel()
    p = pd.DataFrame({'product_ids': d.product_ids, 'month_key': np.round(d.month_t * 12).astype(int), 'month': d.market_ids,
                      'zt': zt, 'xi': xi})
    out = {}
    for k in (12, 24, 36):
        lag = p[['product_ids', 'month_key', 'xi']].assign(month_key=p.month_key + k)  # xi from t-k, aligned to t
        m = p[['product_ids', 'month_key', 'month', 'zt']].merge(lag, on=['product_ids', 'month_key'])
        y = (m.xi - m.groupby('product_ids').xi.transform('mean')).to_numpy()
        x = (m.zt - m.groupby('product_ids').zt.transform('mean')).to_numpy()
        b = (x @ y) / (x @ x)
        u = y - b * x
        se = np.sqrt(((pd.Series(x * u).groupby(m.month.to_numpy()).sum()) ** 2).sum()) / (x @ x)
        out[f'b_{k}'], out[f'se_{k}'], out[f't_{k}'], out[f'pairs_{k}'] = b, se, b / se, len(m)
    return out


rows = []
full = add_variables(common.load('index'))
full['Z_paper'] = full[H]
for cheap in (None, 'raw20'):
    d, res = fit(full, 'Z_paper', 'market_ids', cheap)
    r = dict(sample='Table 2 sample (108,300)', instrument='paper Hausman IV', model='one slope' if not cheap else 'main (x cheap)',
             fe='fund + month', N=len(d), price=float(res.beta[0, 0]))
    r.update(lead_test(d, res.xi.flatten(), 'Z_paper', 'market_ids'))
    rows.append(r)
    print(r, flush=True)
s = load_new_iv_sample()
for fe, tfe in (('fund + month', 'market_ids'), ('fund + month x asset class', 'mkt_ac')):
    for z, zname in (('Z_paper', 'paper Hausman IV'), ('Z', 'share-class Hausman IV')):
        for cheap in (None, 'raw20'):
            d, res = fit(s, z, tfe, cheap)
            r = dict(sample='family id, new IV defined (97,429)', instrument=zname, model='one slope' if not cheap else 'main (x cheap)',
                     fe=fe, N=len(d), price=float(res.beta[0, 0]))
            r.update(lead_test(d, res.xi.flatten(), z, tfe))
            rows.append(r)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
out = pd.DataFrame(rows)
out.to_csv('step27_lead_tests.csv', index=False)
pd.set_option('display.width', 250)
print(out[['sample', 'instrument', 'model', 'fe', 'N', 'price', 't_12', 't_24', 't_36', 'pairs_12', 'pairs_36']].round(2).to_string(index=False))
