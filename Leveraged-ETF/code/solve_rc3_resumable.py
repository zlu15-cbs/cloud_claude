"""BLP with 3 random coefficients, as in the Oct2026 notebooks, but parallel over markets and resumable.

usage: solve_rc3_resumable.py NOTEBOOK PREP_CELLS PROCESSES CKPT_JSON

PREP_CELLS (comma list) are executed unmodified from the notebook (data prep and instrument renames). The solve
then mirrors the notebook's 'BLP with additional RCs V2' cell: same X1/X2, Monte Carlo size 3000 seed 623543,
BFGS gtol 1e-7, clustered SE. Differences: pyblp.parallel(PROCESSES) and a custom (but equivalent) SciPy BFGS call
that records every objective evaluation to CKPT_JSON; if CKPT_JSON exists, the lowest-objective point recorded is
used as the starting sigma instead of the identity. With env FINALIZE=1 no optimization is done: the results are computed
at that best point (used for Panel A column 4 when BFGS stalled; see RESULTS_table2.md).
"""
import json, os, sys, time
import matplotlib; matplotlib.use('Agg')

nb = json.load(open(sys.argv[1]))
prep = [int(x) for x in sys.argv[2].split(',')]
procs = int(sys.argv[3])
ckpt = sys.argv[4]

ns = {'__name__': '__main__', 'display': lambda *a, **k: None}
for i in prep:
    src = '\n'.join(l for l in ''.join(nb['cells'][i]['source']).splitlines() if not l.strip().startswith(('%', '!')))
    src = src.replace('from IPython.display import display', 'pass')
    exec(compile(src, f'cell{i}', 'exec'), ns)

import numpy as np, pyblp
from pyblp.configurations.optimization import scipy_optimizer
pyblp.options.verbose = False
pd_ = ns['product_data']
print('N =', len(pd_), ' markets =', pd_.market_ids.nunique(), flush=True)

history = json.load(open(ckpt)) if os.path.exists(ckpt) else []
if history:
    best = min(history, key=lambda r: r['obj'])
    sigma0 = np.diag(best['theta'])
    print(f'RESUMING from checkpoint: {len(history)} evaluations, best objective {best["obj"]:.6f}, theta {best["theta"]}', flush=True)
else:
    sigma0 = np.identity(3)
    print('Starting from identity', flush=True)


def checkpointing_bfgs(initial, bounds, objective_function, iteration_callback, **opts):
    def wrapped(values):
        out = objective_function(values)
        history.append({'theta': [float(v) for v in np.asarray(values).flatten()], 'obj': float(out[0])})
        json.dump(history, open(ckpt + '.tmp', 'w')); os.replace(ckpt + '.tmp', ckpt)
        return out
    return scipy_optimizer(initial, bounds, wrapped, iteration_callback, method='BFGS', compute_gradient=True, **opts)


X1 = pyblp.Formulation('0 + prices + product_tracking_err + product_past_1yr_ret + log_product_fund_age',
                       absorb='C(product_ids) + C(market_ids)')
X2 = pyblp.Formulation('0 + prices + log_product_fund_age + product_past_1yr_ret')
integ = pyblp.Integration('monte_carlo', size=3000, specification_options={'seed': 623543})
opt = pyblp.Optimization(checkpointing_bfgs, {'gtol': 1e-7}, compute_gradient=True)
if os.environ.get('FINALIZE') == '1':  # no optimization: report results at the best checkpointed point
    opt = pyblp.Optimization('return')
    print('FINALIZE: results at the best checkpointed point, no optimization', flush=True)

t = time.time()
with pyblp.parallel(procs):
    problem = pyblp.Problem((X1, X2), pd_, integration=integ)
    results = problem.solve(sigma0, optimization=opt, se_type='clustered')
    print(results)
    print(f'solve wall time: {time.time()-t:.1f}s', flush=True)
    el = results.compute_elasticities()
    means = results.extract_diagonal_means(el)
    print('BLP_3RC mean own-price elasticity:', means.flatten().mean(), flush=True)
