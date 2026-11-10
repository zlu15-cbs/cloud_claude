"""Shared logit-IV helpers for the demand grid (step30+): one function fits pyblp logit IV with an optional price
interaction, returns coefficients, clustered SEs, Sanderson-Windmeijer F (clustered by month), elasticity summaries.
Same estimator, controls, FE and F statistic as step25_new_iv_main.model()."""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe

CONTROLS = ['product_tracking_err', 'product_past_1yr_ret', 'log_product_fund_age']
pyblp.options.verbose = False


def resid(dd, cols, tfe):
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd[tfe])[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    M = alg.residualize(dd[cols].to_numpy(float))
    return M - W @ np.linalg.lstsq(W, M, rcond=None)[0]


def cl_wald(y, X, g):
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    u = y - X @ b
    sc = pd.DataFrame(X * u[:, None]).groupby(g).sum().to_numpy()
    V = XtXi @ (sc.T @ sc) @ XtXi
    return float(b @ np.linalg.pinv(V) @ b)


def sw_f(dd, endog, excl, tfe):
    X = resid(dd, endog, tfe)
    Z = resid(dd, excl, tfe)
    g = dd.market_ids.to_numpy()
    k, L = len(endog), len(excl)
    out = {}
    for j, name in enumerate(endog):
        x = X[:, j]
        if k > 1:
            Xo = np.delete(X, j, axis=1)
            Pz = Z @ np.linalg.lstsq(Z, Xo, rcond=None)[0]
            x = x - Xo @ np.linalg.lstsq(Pz, x, rcond=None)[0]
        out[name] = cl_wald(x, Z, g) / (L - k + 1)
    return out


def fit(d, z, inter=None, tfe='market_ids'):
    """Logit IV: delta on prices (+ prices*inter) + CONTROLS, fund + tfe FE, instruments z (+ z*inter)."""
    dd = d.reset_index(drop=True).copy()
    dd = dd.drop(columns=[c for c in dd.columns if c.startswith('demand_instruments')])
    zz = dd[z].to_numpy(float)
    dd['demand_instruments0'] = zz
    terms, endog, excl = ['prices'], ['prices'], ['demand_instruments0']
    if inter:
        dd['px'] = dd.prices * dd[inter]
        dd['demand_instruments1'] = zz * dd[inter]
        terms.append(f'I(prices*{inter})'); endog.append('px'); excl.append('demand_instruments1')
    res = pyblp.Problem(pyblp.Formulation(' + '.join(terms + CONTROLS), absorb=f'C(product_ids) + C({tfe})'), dd).solve(se_type='clustered')
    f = sw_f(dd, endog, excl, tfe)
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    se = dict(zip(res.beta_labels, res.beta_se.flatten()))
    E = res.compute_elasticities()
    own = res.extract_diagonals(E).flatten()
    out = dict(N=len(dd), funds=dd.product_ids.nunique(), b_price=b['prices'], se_price=se['prices'],
               min_F=min(f.values()), F_price=f['prices'], share_pos_e=float((own > 0).mean()),
               avg_e=float(res.extract_diagonal_means(E).mean()))
    if inter:
        kx = next(k for k in b if inter in k)
        cov = res.parameter_covariances
        out.update(b_x=b[kx], se_x=se[kx], F_x=f['px'], cheap_total=b['prices'] + b[kx], share_inter=float(dd[inter].mean()))
    out.update({f'b_{c}': b[c] for c in CONTROLS})
    return out, res, dd
