"""Map the lognormal-RC GMM criterion on a grid instead of searching it (the step44/step45 L-BFGS-B searches stalled
at extreme points, where the share contraction barely converges).

    python step47_lognormal_profile.py ours PROCS DRAWS      # from the folder holding the index CSV, as step44
    python -I step47_lognormal_profile.py danny PKG PROCS    # PKG = extracted tables7_10_replication/, as step45

ours  Same problem as step44 lognormal: fee coefficient -exp(pi + sigma nu) < 0 for every investor; X1 = controls,
      X2 = -fee, agent constant; excluded IVs Z and Z x cheap; fund + month FE; one-step GMM, W = (Z'Z/N)^-1.
      (1) sigma = 0 exactly. The model is a logit with a fixed fee coefficient a = -exp(pi). With beta concentrated
          out, the criterion is the 2SLS quadratic q(a) = N gbar(a)' W gbar(a). Evaluated on a grid of a <= 0 and at
          the unconstrained minimum (which must match step44's normal profile at sigma = 0.001: a = +14.85, 354.8).
      (2) sigma > 0. pyblp objective and gradient (no optimization) at eleven (sigma, pi) points with DRAWS Monte Carlo
          draws, all with exp(pi + 3 sigma) <= 150, including step44's last good point (0.28373, 1.31343; 667.5 at
          3,000 draws) as a check on simulation noise. Resumes from the CSV.
danny Lognormal at the point that matches the mean and SD of his Table 7 step-1 normal fee coefficient
      N(-18.53, 2.239^2): sigma = sqrt(ln(1 + (sd/mean)^2)), pi = ln(mean) - sigma^2/2. One evaluation with his
      3,000 archived draws: objective (his normal RC: 100.87) and gradient.
Writes step47_*.csv.
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
pyblp.options.verbose = False
ITERATION = pyblp.Iteration('squarem', {'atol': 1e-14, 'max_evaluations': 1000})


def linear_profile(d, resid, controls):
    """sigma = 0: q(a) for the logit with fee coefficient a, beta on the controls concentrated out."""
    R = resid(d, ['delta', 'prices'] + controls + ['demand_instruments0', 'demand_instruments1'])
    y, p = R[:, 0], R[:, 1]
    X = R[:, 2:2 + len(controls)]
    Z = np.column_stack([X, R[:, 2 + len(controls):]])
    N = len(y)
    W = np.linalg.inv(Z.T @ Z / N)

    def q(a):
        dl = y - a * p
        A = X.T @ Z @ W @ Z.T
        b = np.linalg.solve(A @ X, A @ dl)
        g = Z.T @ (dl - X @ b) / N
        return float(N * g @ W @ g)
    Xf = np.column_stack([p, X])
    A = Xf.T @ Z @ W @ Z.T
    a_hat = float(np.linalg.solve(A @ Xf, A @ y)[0])
    rows = [dict(a=a_hat, pi=np.nan, objective=q(a_hat), note='unconstrained minimum (positive fee coefficient)')]
    for a in (0.0, -0.1, -0.5, -1, -2, -3.7, -5, -7.4, -10, -15, -20, -30):
        rows.append(dict(a=a, pi=np.log(-a) if a < 0 else -np.inf, objective=q(a), note='sigma = 0, sign-constrained'))
    return pd.DataFrame(rows)


def ours(procs, draws):
    import step44_rc1_zcheap as s44
    d = s44.data()
    lp = linear_profile(d, s44.resid, s44.CONTROLS)
    print(lp.round(3).to_string(index=False), flush=True)
    lp.to_csv('step47_sigma0_profile.csv', index=False)

    integ = pyblp.Integration('monte_carlo', size=draws, specification_options={'seed': 623543})
    # pi = 0 exactly would be read by pyblp as a fixed parameter, so the grid avoids it. Small sigma first, then a
    # sparse set spanning larger dispersion (where a second basin would have to be).
    grid = [(0.28372927543112303, 1.3134266506262935), (0.25, -2.0), (0.25, -1.0),
            (0.5, -1.0), (0.5, 1.5), (1.0, -1.0), (1.0, 1.5), (1.5, -1.0), (1.5, 0.5),
            (2.0, -1.0), (2.5, -2.5)]
    out = f'step47_lognormal_grid_d{draws}.csv'
    rows = pd.read_csv(out).to_dict('records') if os.path.exists(out) else []
    done = {(round(r['sigma'], 6), round(r['pi'], 6)) for r in rows}
    grid = [g for g in grid if (round(g[0], 6), round(g[1], 6)) not in done]
    with pyblp.parallel(procs):
        ids, nodes, weights = integ._build_many(1, np.unique(d.market_ids))
        pr = pyblp.Problem((pyblp.Formulation('0 + ' + s44.X1C, absorb='C(product_ids) + C(market_ids)'),
                            pyblp.Formulation('0 + I(-prices)')), d, agent_formulation=pyblp.Formulation('1'),
                           agent_data={'market_ids': ids, 'nodes': nodes, 'weights': weights}, rc_types=['log'])
        for s, p in grid:
            t = time.time()
            res = pr.solve(sigma=np.array([[s]]), pi=np.array([[p]]), optimization=pyblp.Optimization('return'),
                           iteration=ITERATION, method='1s', se_type='unadjusted')
            e = res.extract_diagonals(res.compute_elasticities()).flatten()
            slope = e / d.prices.to_numpy()
            row = dict(sigma=s, pi=p, median_fee_coef=-np.exp(p), mean_fee_coef=-np.exp(p + s * s / 2),
                       objective=float(res.objective), grad_sigma=float(res.gradient.flat[0]), grad_pi=float(res.gradient.flat[1]),
                       contraction_converged=float(np.mean(res.fp_converged)), mean_e=float(e.mean()),
                       share_abs_e_gt1=float((np.abs(e) > 1).mean()), slope_cheap=float(slope[d.cheap == 1].mean()),
                       slope_noncheap=float(slope[d.cheap == 0].mean()), draws=draws, secs=round(time.time() - t))
            rows.append(row)
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
            pd.DataFrame(rows).to_csv(out, index=False)


def danny(pkg, procs):
    import step45_lognormal_danny as s45
    d, agents = s45.load(pkg)
    m, sd = 18.5285, 2.238688664247958        # his step-1 fee coefficient: mean (b[prices]) and normal sigma
    s = float(np.sqrt(np.log(1 + (sd / m) ** 2)))
    p = float(np.log(m) - s * s / 2)
    print(f'moment-matched lognormal: sigma {s:.5f}, pi {p:.5f} (mean {np.exp(p + s * s / 2):.4f}, '
          f'sd {np.exp(p + s * s / 2) * np.sqrt(np.exp(s * s) - 1):.4f})', flush=True)
    t = time.time()
    with pyblp.parallel(procs):
        pr = pyblp.Problem((pyblp.Formulation('0 + ' + s45.X1C, absorb=s45.ABSORB), pyblp.Formulation('0 + I(-prices)')), d,
                           agent_formulation=pyblp.Formulation('1'), agent_data=agents, rc_types=['log'])
        res = pr.solve(sigma=np.array([[s]]), pi=np.array([[p]]), optimization=pyblp.Optimization('return'),
                       iteration=s45.ITERATION, method='1s', se_type='clustered')
        row, fr = s45.summarize(res, d, 'lognormal RC matched to Table 7 step-1 normal (his objective 100.87)',
                                dict(sigma=s, pi=p, grad_sigma=float(res.gradient[0, 0]), grad_pi=float(res.gradient[1, 0]),
                                     share_contraction_converged=float(np.mean(res.fp_converged)),
                                     minutes=round((time.time() - t) / 60, 1)))
    pd.DataFrame([row]).to_csv('step47_danny_matched.csv', index=False)
    fr.to_csv('step47_danny_matched_funds.csv', index=False)


if __name__ == '__main__':
    if sys.argv[1] == 'ours':
        ours(int(sys.argv[2]), int(sys.argv[3]))
    else:
        danny(sys.argv[2], int(sys.argv[3]))
