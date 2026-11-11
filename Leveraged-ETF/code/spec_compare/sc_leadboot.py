"""Does within-fund demeaning create a mechanical correlation in the lead test? A bootstrap under the null.

Null: the instrument is strictly exogenous, i.e. unrelated to the demand shock at every lead and lag.
Each draw flips the sign of every fund's whole residual path (Rademacher, one draw per fund). This keeps each fund's
serial correlation, panel length and months, and every step of the procedure, but makes the shocks unrelated to the
instrument by construction. Then, exactly as in the real test:
  1. delta* = fitted part + flipped residual;  2. re-estimate the IV model (same instruments, fund and month FE);
  3. take the new residual, regress it on the instrument k months later, both demeaned within fund on the matched sample.
If demeaning (or re-estimation) induced a mechanical correlation, the draws would not be centred on zero.
Reports, per specification and k: the actual coefficient and fund-clustered t; the mean and SD of the bootstrap
coefficients; the share of draws with |t*| > 1.96 (should be about 0.05); the bootstrap p-value of the actual coefficient.
Writes sc_leadboot.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
import pyhdfe

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
from sc_build import PANEL  # noqa: E402

B = 499
C = v2.CONTROLS


def main():
    rng = np.random.default_rng(20261111)
    d = pd.read_pickle(PANEL)
    d['IV0'] = d.demand_instruments0
    fam = d.firm_f_old.notna().to_numpy()
    d['iv4p'] = d.R_ac.where(fam).fillna(d.IV0)
    d['broad'] = ((d.broad_specialized == 'broad-based').groupby(d.product_ids).transform('mean') > 0.5).astype(float)
    allr = np.ones(len(d), bool)
    v2rows = (d.mmf == 0).to_numpy() & d.Z.notna().to_numpy()
    SPECS = {'1 T2': ('IV0', [], allr), '1 T2, no VA': ('IV0', [], fam), '2 Danny proxy': ('iv4p', [], allr), '2 Danny proxy, no VA': ('iv4p', [], fam),
             '3 V2': ('Z', ['cheap'], v2rows), '4 A5': ('IV0', ['broad'], allr), '4 A5, no VA': ('IV0', ['broad'], fam)}
    out = []
    for name, (iv, zs, mask) in SPECS.items():
        dd = d[mask].reset_index(drop=True)
        dd['delta'] = np.log(dd.shares) - np.log(1 - dd.groupby('market_ids').shares.transform('sum'))
        f = pd.factorize(dd.product_ids)[0]
        alg = pyhdfe.create(np.column_stack([f, pd.factorize(dd.market_ids)[0]]), drop_singletons=False)
        X = np.column_stack([dd.prices] + [dd.prices * dd[z] for z in zs] + [dd[c] for c in C]).astype(float)
        Zm = np.column_stack([dd[iv]] + [dd[iv] * dd[z] for z in zs] + [dd[c] for c in C]).astype(float)
        Xt, Zt, yt = alg.residualize(X), alg.residualize(Zm), alg.residualize(dd.delta.to_numpy(float)[:, None])[:, 0]
        A = np.linalg.solve(Zt.T @ Xt, Zt.T)                       # exactly identified IV: beta = (Z'X)^-1 Z'y
        beta = A @ yt
        xi = yt - Xt @ beta
        W = alg.residualize(dd[C].to_numpy(float))
        z0 = alg.residualize(dd[[iv]].to_numpy(float))[:, 0]
        zt = z0 - W @ np.linalg.lstsq(W, z0, rcond=None)[0]         # instrument net of controls and both FE
        mk = dd.month_key.to_numpy()
        pos = pd.Series(np.arange(len(dd)), index=pd.MultiIndex.from_arrays([dd.product_ids, mk]))
        for k in (12, 24, 36):
            tgt = pd.MultiIndex.from_arrays([dd.product_ids, mk + k])
            ok = tgt.isin(pos.index)
            i_xi = np.flatnonzero(ok)                                # xi at t
            i_z = pos.reindex(tgt[ok]).to_numpy()                    # Z at t + k
            g = f[i_xi]
            G = pd.Series(g)
            x = zt[i_z] - G.map(pd.Series(zt[i_z]).groupby(g).mean()).to_numpy()
            xx = x @ x

            def stat(e):
                y = e[i_xi]
                y = y - G.map(pd.Series(y).groupby(g).mean()).to_numpy()
                b = (x @ y) / xx
                s = pd.Series(x * (y - b * x)).groupby(g).sum().to_numpy()
                return b, b / (np.sqrt(s @ s) / xx)
            b0, t0 = stat(xi)
            bs, ts = np.empty(B), np.empty(B)
            for r in range(B):
                sign = rng.choice([-1.0, 1.0], size=f.max() + 1)[f]
                ystar = alg.residualize((sign * xi)[:, None])[:, 0] + Xt @ beta
                bs[r], ts[r] = stat(ystar - Xt @ (A @ ystar))
            row = dict(spec=name, k=k, pairs=len(i_xi), b=b0, t_fund=t0, boot_mean_b=bs.mean(), boot_sd_b=bs.std(ddof=1),
                       boot_mean_t=ts.mean(), boot_sd_t=ts.std(ddof=1), boot_reject_196=float((np.abs(ts) > 1.96).mean()),
                       boot_p=float((1 + (np.abs(ts) >= abs(t0)).sum()) / (B + 1)), t_from_boot_sd=b0 / bs.std(ddof=1))
            out.append(row)
            print(f"{name:22s} k {k} | b {b0:7.3f} t(fund) {t0:6.2f} | bootstrap under the null: mean b {row['boot_mean_b']:7.4f} sd b {row['boot_sd_b']:.3f} "
                  f"| mean t {row['boot_mean_t']:5.2f} sd t {row['boot_sd_t']:.2f} | share |t|>1.96 {row['boot_reject_196']:.3f} | p {row['boot_p']:.3f}", flush=True)
            pd.DataFrame(out).to_csv('sc_leadboot.csv', index=False)


if __name__ == '__main__':
    main()
