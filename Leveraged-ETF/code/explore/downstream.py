"""Downstream analysis for a logit demand model (index market): markups by conduct, marginal costs, the scale parameter
estimated under each conduct candidate, and the pyRVtest conduct test.

Conventions (Danny's note of 2 Nov 2026, section 4, and the Oct 2026 index notebook, cells 4, 40, 41, 43):
  * conduct candidates: PC (zero markup), B0 (Bertrand, firm ownership), B25 / B50 / B65 (Bertrand with profit weight
    kappa among the Big 3: BlackRock, Vanguard, State Street Global Advisors) = notebook kappa_specification 2 / 3 / 6.
  * markups: logit FOC, s + (Omega o J') mu = 0 with J[j,k] = ds_j/dp_k = alpha_k s_j (1{j=k} - s_k) and
    alpha_k = alpha + alpha_x * I_k; computed on the supply sample (default: all 108,300 fund-months).
  * MC(eta) = price + eta * log(TNA) - markup; eta = 0, 0.024, or estimated.
  * negative-MC share: equal-weight mean over months of the within-month share (pooled share reported too).
  * scale: raw MC = price - markup under the candidate; winsorized 1/99 within calendar year (linear quantiles);
    2SLS of MC on log AUM (instrument: rotator) + |tracking error| + log age, fund and month FE, SE clustered by month
    (CR1 with fixest-style small-sample factor, t(G-1)); eta = -coefficient on log AUM.
  * conduct test: pyRVtest 0.3.2, cost formulation 0 + log age + tracking error + past 1-yr return with fund and month
    FE; markups supplied directly (problem.markups) so each candidate can carry its own eta:
    MC_m = p - (mu_m - eta_m log TNA); demand_adjustment=False, clustering_adjustment=True.
"""
import contextlib
import io

import numpy as np
import pandas as pd
import pyhdfe
from scipy import stats

BIG3 = ('BlackRock', 'Vanguard', 'State Street Global Advisors')
CONDUCT = {'PC': None, 'B0': 0.0, 'B25': 0.25, 'B50': 0.50, 'B65': 0.65}
CONDUCT_IV = {  # pre-specified main set first; the rest are the notebook's listed alternatives (cell 41 comments)
    'main: rival2 x csent_index': '0 + BLP_IV_rival_funds2*Conduct_IV_csent_index_resid',
    'rival2 x bab_usa': '0 + BLP_IV_rival_funds2*Conduct_IV_bab_usa_resid',
    'rival2 x fmax': '0 + BLP_IV_rival_funds2*Conduct_IV_fmax_resid',
    'rival2 x rotator': '0 + BLP_IV_rival_funds2*rotator',
    'rival2 x csent_income3': '0 + BLP_IV_rival_funds2*Conduct_IV_csent_income3_resid',
    'rival3 x csent_index': '0 + BLP_IV_rival_funds3*Conduct_IV_csent_index_resid',
}


def kappa_fn(k):
    return lambda f, g: 1.0 if f == g else (k if (f in BIG3 and g in BIG3) else 0.0)


def markups(d, alpha, kappa):
    """d: supply rows (market_ids, firm_ids, shares); alpha: array of own-price coefficients per row; kappa: None (PC) or
    profit weight among the Big 3. Returns markups in d's row order."""
    mu = np.zeros(len(d))
    if kappa is None:
        return mu
    for _, idx in d.groupby('market_ids').indices.items():
        s = d.shares.to_numpy()[idx]
        a = alpha[idx]
        f = d.firm_ids.to_numpy()[idx]
        J = -np.outer(s, s) * a[None, :]          # J[j,k] = -alpha_k s_j s_k
        J[np.diag_indices_from(J)] = a * s * (1 - s)
        same = f[:, None] == f[None, :]
        big = np.isin(f, BIG3)
        Om = np.where(same, 1.0, np.where(big[:, None] & big[None, :], kappa, 0.0))
        mu[idx] = -np.linalg.solve(Om * J.T, s)
    return mu


def neg_stats(d, mc):
    neg = pd.Series(mc < 0, index=d.index)
    by_m = neg.groupby(d.market_ids).mean()
    return dict(neg_share=float(by_m.mean()), neg_share_pooled=float(neg.mean()),
                share_below_m020=float((mc < -0.20).mean()), share_below_m060=float((mc < -0.60).mean()),
                share_below_m010=float((mc < -0.10).mean()), share_below_m030=float((mc < -0.30).mean()),
                mc_p1=float(np.percentile(mc, 1)), mc_min=float(mc.min()), mc_mean=float(mc.mean()))


def winsor_by_year(x, year, lo=0.01, hi=0.99):
    x = pd.Series(x)
    q = x.groupby(year).quantile([lo, hi]).unstack()
    return x.clip(year.map(q[lo]).to_numpy(), year.map(q[hi]).to_numpy()).to_numpy()


def scale_iv(d, mc):
    """2SLS: winsorized MC on log AUM (instr. rotator), |tracking error|, log age; fund + month FE; cluster month."""
    y = winsor_by_year(mc, np.floor(d.month_t).reset_index(drop=True))
    X = np.column_stack([np.log(d.product_mtna.to_numpy()), d.product_tracking_err.to_numpy(), d.log_product_fund_age.to_numpy()])
    Z = np.column_stack([d.rotator.to_numpy(), X[:, 1:]])
    ids = np.column_stack([pd.factorize(d.product_ids)[0], pd.factorize(d.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    yt, Xt, Zt = alg.residualize(y[:, None])[:, 0], alg.residualize(X), alg.residualize(Z)
    Pz = Zt @ np.linalg.lstsq(Zt, Xt, rcond=None)[0]
    b = np.linalg.lstsq(Pz, yt, rcond=None)[0]
    u = yt - Xt @ b
    A = np.linalg.inv(Pz.T @ Pz)
    g = d.market_ids.to_numpy()
    sc = pd.DataFrame(Pz * u[:, None]).groupby(g).sum().to_numpy()
    G, n = len(np.unique(g)), len(y)
    k = X.shape[1] + d.product_ids.nunique()  # month FE nested in the month cluster are not counted (fixest)
    V = A @ (sc.T @ sc) @ A * (G / (G - 1)) * ((n - 1) / (n - k))
    se = float(np.sqrt(V[0, 0]))
    t = b[0] / se
    return dict(eta=float(-b[0]), eta_se=se, eta_p=float(2 * stats.t.sf(abs(t), G - 1)))


def conduct_test(d, mus, etas, iv_sets=CONDUCT_IV):
    """pyRVtest with supplied markups. mus/etas: dicts by candidate. Returns long DataFrame of MCS p-values and TRV."""
    import pyRVtest
    dd = d.copy()
    names = list(CONDUCT)
    forms = [pyRVtest.ModelFormulation(model_downstream='perfect_competition', ownership_downstream='firm_ids')] + \
            [pyRVtest.ModelFormulation(model_downstream='bertrand', ownership_downstream='firm_ids',
                                       kappa_specification_downstream=kappa_fn(CONDUCT[m])) for m in names[1:]]
    with contextlib.redirect_stdout(io.StringIO()):
        prob = pyRVtest.Problem(
            cost_formulation=pyRVtest.Formulation('0 + log_product_fund_age + product_tracking_err + product_past_1yr_ret',
                                                  absorb='C(product_ids) + C(market_ids)'),
            instrument_formulation=(tuple(pyRVtest.Formulation(f) for f in iv_sets.values()) if len(iv_sets) > 1
                                    else pyRVtest.Formulation(next(iter(iv_sets.values())))),
            model_formulations=tuple(forms), product_data=dd, demand_results=None)
        logq = np.log(dd.product_mtna.to_numpy())
        prob.markups = [(mus[m] - etas[m] * logq).reshape(-1, 1) for m in names]
        res = prob.solve(demand_adjustment=False, clustering_adjustment=True)
    rows = []
    for l, ivname in enumerate(iv_sets):
        p = np.asarray(res.MCS_pvalues[l]).flatten()
        T = np.asarray(res.TRV[l])
        F = np.asarray(res.F[l])
        for i, m in enumerate(names):
            rows.append(dict(iv_set=ivname, candidate=m, mcs_p=float(p[i]), selected=bool(p[i] >= 0.05),
                             **{f'TRV_vs_{n}': float(T[i, j]) for j, n in enumerate(names)},
                             **{f'F_vs_{n}': float(F[i, j]) for j, n in enumerate(names)}))
    return pd.DataFrame(rows)
