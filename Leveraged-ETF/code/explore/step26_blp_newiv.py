"""BLP with one random coefficient on the expense ratio (Table 2 col 3 analogue) for the recommended spec:
X1 = prices + prices x cheap (entry tier, 20th pct) + controls, fund and month FE absorbed; X2 = prices.
Instruments: Z (share-class-matched Hausman IV, new_iv.py), Z x cheap, and one extra instrument E for sigma
(exactly identified: price, price x cheap, sigma):
  newproduct_1   BLP_IV_newproduct_1, the paper's Table 2 col 3 extra instrument (uninteracted)
  zsq            Z squared
  diffz          differentiation IV (Gandhi-Houde): sum over the other funds in the same month and asset class of (Z_j - Z_k)^2
Monte Carlo 3000 draws, seed 623543; SE clustered by month.

    python step26_blp_newiv.py profile PROCS EXTRA [grid]      # one-step GMM objective at fixed sigma, beta concentrated
    python step26_blp_newiv.py estimate PROCS EXTRA [sigma0]   # BFGS (gtol 1e-7), checkpointed per evaluation; FINALIZE=1
                                                               # evaluates at the best checkpointed sigma
Options (environment variables): CUTOFF=10|15|20 (cheap tier, default 20); METHOD=1s|2s (two-step GMM re-optimizes with
the clustered efficient weighting matrix, W_type='clustered'); FE=month|ac (fund + month, or fund + month x asset class).
Every estimate also writes step26_cov_<tag>.csv: the parameter covariance matrix, its eigenvalues and the correlation
matrix of the estimates, to diagnose the large covariance condition number pyblp reports.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp
from pyblp.configurations.optimization import scipy_optimizer

from new_iv import load_new_iv_sample
from step1_table5_elasticity import top15
from step2_logit_screen import summarize, CONTROLS

pyblp.options.verbose = False


CUTOFF = int(os.environ.get('CUTOFF', '20'))
METHOD = os.environ.get('METHOD', '1s')
FE = os.environ.get('FE', 'month')
TAG_SUFFIX = ('' if CUTOFF == 20 else f'_q{CUTOFF}') + ('' if METHOD == '1s' else f'_{METHOD}') + ('' if FE == 'month' else f'_fe{FE}')


def data(extra):
    d = load_new_iv_sample()
    d['cheap'] = d[f'raw{CUTOFF}']
    d = d.drop(columns=[c for c in d.columns if c.startswith('demand_instruments')])
    d['demand_instruments0'] = d.Z
    d['demand_instruments1'] = d.Z * d.cheap
    if extra == 'newproduct_1':
        d['demand_instruments2'] = d.BLP_IV_newproduct_1
    elif extra == 'zsq':
        d['demand_instruments2'] = d.Z ** 2
    elif extra == 'diffz':
        g = d.groupby(['market_ids', 'ac']).Z
        n, s1, s2 = g.transform('size'), g.transform('sum'), d.Z.pow(2).groupby([d.market_ids, d.ac]).transform('sum')
        d['demand_instruments2'] = n * d.Z ** 2 - 2 * d.Z * s1 + s2
    else:
        raise ValueError(extra)
    return d


def problem(d):
    absorb = 'C(product_ids) + C(market_ids)' if FE == 'month' else 'C(product_ids) + C(mkt_ac)'
    X1 = pyblp.Formulation('0 + prices + I(prices*cheap) + ' + ' + '.join(CONTROLS), absorb=absorb)
    X2 = pyblp.Formulation('0 + prices')
    integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
    return pyblp.Problem((X1, X2), d, integration=integ)


def describe(res, d, funds, label, extra_fields):
    em = res.compute_elasticities()
    e = res.extract_diagonals(em).flatten()
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    bc = b[next(k for k in b if 'cheap' in k)]
    row, fr = summarize(label, dict(tier='A'), d, res, funds, [], {}, extra_fields)
    row.update(sigma=float(res.sigma[0, 0]), sigma_se=float(res.sigma_se[0, 0]), b_rest=b['prices'], b_x_cheap=bc,
               b_cheap_total=b['prices'] + bc, share_pos_e=float((e > 0).mean()), n15_gt1=sum(abs(q['e_last']) > 1 for q in fr),
               n15_pos=sum(q['e_last'] > 0 for q in fr))
    return row, fr


def profile(procs, extra, grid):
    d = data(extra)
    funds = top15(d)
    rows = []
    with pyblp.parallel(procs):
        pr = problem(d)
        for s in grid:
            t = time.time()
            res = pr.solve(np.array([[s]]), optimization=pyblp.Optimization('return'), method='1s', se_type='clustered')
            row, _ = describe(res, d, funds, f'{extra}_sigma{s}', {})  # summarize() already records the objective
            row['secs'] = round(time.time() - t)
            rows.append(row)
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()
                   if k in ('sigma', 'objective', 'b_rest', 'b_cheap_total', 'avg_own_elasticity', 'share_pos_e',
                            'share_neg_mc_bertrand_firm', 'n15_gt1', 'n15_pos', 'secs')}, flush=True)
    pd.DataFrame(rows).to_csv(f'step26_profile_{extra}.csv', index=False)


def estimate(procs, extra, sigma0):
    d = data(extra)
    funds = top15(d)
    tag = f'{extra}{TAG_SUFFIX}'
    ckpt = f'step26_{tag}_ckpt.json'
    history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
    if history:
        sigma0 = min(history, key=lambda r: r['obj'])['theta'][0]
    print(f'{tag}: N={len(d):,}; cutoff {CUTOFF}, method {METHOD}, FE {FE}; start sigma {sigma0:.4f} ({len(history)} checkpointed evaluations)', flush=True)

    def bfgs(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            print(f'  eval {len(history)}: sigma {history[-1]["theta"][0]:.5f} obj {history[-1]["obj"]:.6g}', flush=True)
            return out
        return scipy_optimizer(initial, None, wrapped, iteration_callback, method='BFGS', compute_gradient=True, **opts)

    t = time.time()
    with pyblp.parallel(procs):
        pr = problem(d)
        opt = pyblp.Optimization(bfgs, {'gtol': 1e-7})
        if os.environ.get('FINALIZE') == '1':
            opt = pyblp.Optimization('return')
        kw = dict(W_type='clustered') if METHOD == '2s' else {}
        res = pr.solve(np.array([[sigma0]]), optimization=opt, method=METHOD, se_type='clustered', **kw)
        print(res, flush=True)
        row, fr = describe(res, d, funds, f'BLP1RC_newiv_{tag}', dict(converged=bool(res.converged), cutoff=CUTOFF, method=METHOD, fe=FE,
                                                                       minutes=round((time.time() - t) / 60, 1)))
        # covariance diagnostics
        V = np.asarray(res.parameter_covariances, float)
        labels = ['sigma[prices]'] + [f'beta[{b}]' for b in res.beta_labels]
        labels = labels[:V.shape[0]] + [f'p{i}' for i in range(len(labels), V.shape[0])]
        se = np.sqrt(np.clip(np.diag(V), 0, None))
        C = V / np.outer(se, se)
        ev, evec = np.linalg.eigh(V)
        evc = np.linalg.eigvalsh(C)
        row.update(cov_cond=float(ev.max() / max(ev.min(), 1e-300)), corr_cond=float(evc.max() / max(evc.min(), 1e-300)),
                   max_abs_offdiag_corr=float(np.max(np.abs(C - np.eye(len(C))))))
        out = pd.DataFrame(C, index=labels, columns=labels)
        out['se'] = se
        out.to_csv(f'step26_cov_{tag}.csv')
        pd.DataFrame({'eigenvalue': ev, **{f'v[{l}]': evec[i] for i, l in enumerate(labels)}}).to_csv(f'step26_coveig_{tag}.csv', index=False)
        print('covariance condition number', f"{row['cov_cond']:.3e}", '| correlation-matrix condition number', f"{row['corr_cond']:.3e}",
              '| largest |correlation| between estimates', round(row['max_abs_offdiag_corr'], 4), flush=True)
        print(out.round(3).to_string(), flush=True)
        print('eigenvalues of the covariance matrix:', np.array2string(ev, precision=3), flush=True)
    pd.DataFrame([row]).to_csv(f'step26_estimate_{tag}.csv', index=False)
    pd.DataFrame(fr).to_csv(f'step26_estimate_{tag}_funds.csv', index=False)
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()
           if k in ('sigma', 'sigma_se', 'b_rest', 'se[prices]', 'b_x_cheap', 'se_x_cheap', 'b_cheap_total', 'avg_own_elasticity', 'share_abs_e_gt1',
                    'share_pos_e', 'share_neg_mc_bertrand_firm', 'n15_gt1', 'n15_pos', 'objective', 'converged', 'minutes', 'cov_cond',
                    'corr_cond', 'max_abs_offdiag_corr')}, flush=True)
    print(pd.DataFrame(fr)[['name', 'p_last', 'e_last']].round(2).to_string(index=False))


if __name__ == '__main__':
    mode, procs, extra = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    if mode == 'profile':
        grid = [float(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else [0.001, 0.25, 0.5, 1, 2, 3, 4, 6]
        profile(procs, extra, grid)
    else:
        estimate(procs, extra, float(sys.argv[4]) if len(sys.argv) > 4 else 0.5)
