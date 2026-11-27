"""Final passive BLP estimates, resumable at every step (a session pause or restart loses at most one evaluation).

    python -I step58_final_blp.py lag PACKAGE_DIR NAMES_CSV PROCS     # (a) Table 7 + lagged log share ratio; fee RC
    python -I step58_final_blp.py age PACKAGE_DIR NAMES_CSV PROCS     # (b) static; log-age RC only, no fee RC

Both: fund and month FE; controls tracking error, past return, log age; Danny's five instruments and his 3,000
archived draws per month; SE clustered by month. Reads prepared arrays only; runs none of his code.
Stage 1  one-step GMM (2SLS weight). 'lag' evaluates at the sigma found by step49 (0.78274); 'age' optimizes from 1.5.
         The second-step weights are then saved to disk: heteroskedasticity-robust (his convention; checked against
         pyblp's own) and month-clustered.
Stage 2  two-step GMM for each weight, every evaluation checkpointed; its criterion is J.
Writes step58_<spec>_step1.csv, step58_<spec>_step2_<weight>.csv and the 15 Table 5 funds' elasticities.

Environment variables:
  ENTRY=<variant> ENTRY_NPZ=<file>  replace his IV1 and IV4 by the entry-fee-matched counts e1_<variant>, e4_<variant>
                                    built by step60_entry_fee_band.py (output files get the suffix _<variant>).
  WEIGHTS=clustered                 second-step weights to run (default "robust,clustered").
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step49_access_blp as s49
import step56_static_age_rc as s56
from step48_access_spec_linear import load

pyblp.options.verbose = False
CON = s49.CON
START = {'lag': 0.78274, 'age': 1.5}
# Search ranges. A wide range let L-BFGS-B's first trial step land at an extreme sigma where the share contraction
# takes tens of minutes per evaluation; a minimum at either end of these ranges would be reported as such.
BOUNDS = {'lag': (0.4, 1.2), 'age': (0.2, 2.2)}


def search(ckpt, history):
    """L-BFGS-B with every evaluation checkpointed; stops on a relative criterion change below 1e-9."""
    from pyblp.configurations.optimization import scipy_optimizer

    def optimizer(initial, bounds, objective_function, iteration_callback, **opts):
        def wrapped(values):
            out = objective_function(values)
            history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
            json.dump(history, open(ckpt + '.tmp', 'w'))
            os.replace(ckpt + '.tmp', ckpt)
            print(f'  eval {len(history)}: theta {np.round(history[-1]["theta"], 5).tolist()} obj {history[-1]["obj"]:.6g}', flush=True)
            return out
        return scipy_optimizer(initial, bounds, wrapped, iteration_callback, method='L-BFGS-B', compute_gradient=True, **opts)
    return pyblp.Optimization(optimizer, {'gtol': 1e-6, 'ftol': 1e-9, 'maxls': 6})


def weights(res, d):
    g = res.problem.products.ZD * res.xi
    g = g - g.mean(0)
    n = len(g)
    gc = pd.DataFrame(g).groupby(d.clustering_ids.to_numpy()).sum().to_numpy()
    return np.linalg.inv(g.T @ g / n), np.linalg.inv(gc.T @ gc / n)


def main(spec, P, names, procs):
    d = load(P, f'{P}/data/iv_inputs', names)
    z = np.load(f'{P}/data/prepared/passive.npz', allow_pickle=False)
    d['firm_ids'] = z['firm_ids']
    entry = os.environ.get('ENTRY', '')
    tag = spec + ('_' + entry if entry else '')
    if entry:
        nz = np.load(os.environ['ENTRY_NPZ'], allow_pickle=False)
        assert (nz['source_row'] == z['source_row']).all()
        d['demand_instruments1'], d['demand_instruments4'] = nz[f'e1_{entry}'], nz[f'e4_{entry}']
    a = np.load(f'{P}/data/draws/passive.npz', allow_pickle=False)
    if spec == 'lag':
        x = d.sort_values(['product_ids', 'month'])
        lag = x.groupby('product_ids').y.shift(1)
        lag[x.groupby('product_ids').month.diff() != 1] = np.nan
        d['y_lag'] = lag
        d = d.dropna(subset=['y_lag']).reset_index(drop=True)
        x1, x2, col, df = '0 + prices + y_lag + ' + ' + '.join(CON), '0 + prices', 0, 3
        summ = lambda res, lab, ex: s49.summarize(res, d, lab, ex)
    else:
        x1, x2, col, df = '0 + prices + ' + ' + '.join(CON), '0 + log_product_fund_age', 1, 3
        summ = lambda res, lab, ex: s56.summarize(res, d, lab, ex)
    live = np.isin(a['market_ids'], d.market_ids.unique())
    agents = {'market_ids': a['market_ids'][live], 'nodes': a['nodes'][live][:, [col]], 'weights': a['weights'][live]}
    lo, hi = (0.1, 1.4) if (spec == 'lag' and entry) else BOUNDS[spec]
    bnd = (np.array([[lo]]), np.array([[hi]]))
    print(f'{tag}: N={len(d):,}', flush=True)
    with pyblp.parallel(procs):
        pr = pyblp.Problem((pyblp.Formulation(x1, absorb='C(product_ids) + C(market_ids)'), pyblp.Formulation(x2)), d, agent_data=agents)
        wf = f'step58_{tag}_W.npz'
        if not os.path.exists(wf):
            t = time.time()
            ck = f'step58_{tag}_step1_ckpt.json'
            h = json.load(open(ck)) if os.path.exists(ck) else []
            s0 = min(h, key=lambda r: r['obj'])['theta'][0] if h else START[spec]
            opt = pyblp.Optimization('return') if spec == 'lag' and not entry else search(ck, h)
            res1 = pr.solve(np.array([[s0]]), sigma_bounds=bnd, optimization=opt, iteration=s49.ITERATION, method='1s', se_type='clustered')
            Wr, Wc = weights(res1, d)
            print('robust weight: max relative difference from pyblp %.2e' % float(np.abs(Wr / res1.updated_W - 1).max()), flush=True)
            row, fr = summ(res1, f'{tag}, one-step, 3000 draws', dict(minutes=round((time.time() - t) / 60, 1)))
            pd.DataFrame([row]).to_csv(f'step58_{tag}_step1.csv', index=False)
            fr.to_csv(f'step58_{tag}_step1_funds.csv', index=False)
            np.savez(wf + '.tmp.npz', robust=res1.updated_W, clustered=Wc, sigma=float(res1.sigma[0, 0]))
            os.replace(wf + '.tmp.npz', wf)
        W = np.load(wf)
        for wt in os.environ.get('WEIGHTS', 'robust,clustered').split(','):
            out = f'step58_{tag}_step2_{wt}.csv'
            if os.path.exists(out):
                continue
            t = time.time()
            ck = f'step58_{tag}_step2_{wt}_ckpt.json'
            h = json.load(open(ck)) if os.path.exists(ck) else []
            s1 = min(h, key=lambda r: r['obj'])['theta'][0] if h else float(W['sigma'])
            print(f'two-step, {wt} weight, from sigma {s1:.5f} ({len(h)} earlier evaluations)', flush=True)
            # converged already if the two best checkpointed evaluations agree: then one final evaluation, no search
            # (L-BFGS-B otherwise keeps re-evaluating the same point when the gradient is at numerical noise)
            best = sorted(h, key=lambda r: r['obj'])[:2]
            done = len(best) == 2 and abs(best[1]['obj'] - best[0]['obj']) < 1e-6 * best[0]['obj'] and abs(best[1]['theta'][0] - best[0]['theta'][0]) < 1e-3
            opt = pyblp.Optimization('return') if done else search(ck, h)
            res2 = pr.solve(np.array([[s1]]), sigma_bounds=bnd, W=W[wt], optimization=opt, iteration=s49.ITERATION,
                            method='1s', W_type=wt, se_type='clustered')
            row, fr = summ(res2, f'{tag}, two-step ({wt} weight), 3000 draws', dict(J=float(res2.objective), J_df=df, minutes=round((time.time() - t) / 60, 1)))
            pd.DataFrame([row]).to_csv(out, index=False)
            fr.to_csv(f'step58_{tag}_step2_{wt}_funds.csv', index=False)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
