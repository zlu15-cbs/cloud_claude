"""One menu: passive mutual-fund classes and ETFs pooled, one fee coefficient. Which specification choices help?

    python -I step51_one_menu.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV PROCS [BLOCKS]     # BLOCKS e.g. ABCDEF (default)

Danny's Tables 7-10 package, read without running his code. Linear (Salanie-Wolak) screens as step48: fund FE,
controls, month-clustered SE, cluster Hansen J, conditional first-stage F. The coefficient on K = p (p/2 - e_t)
is sigma^2 of the fee random coefficient. No fee slope or month effect differs between mutual funds and ETFs
unless a row is marked "reference" or "diagnostic".

A  What the month effects are crossed with (time-varying tastes within the one menu):
     month | month + ETF x trend | month + ETF x year | month x asset class (his 8-class P8) |
     month x asset class + ETF x year | month x benchmark index | reference: month x ETF.
   For each: logit fee slope; K; K split into own-fee p^2/2 and market-position -p e_t; K + age K.
   Diagnostic: logit slope on mutual-fund rows and on ETF rows.
B  A second random coefficient on the vehicle (ETF dummy D), correlated with the fee coefficient:
     K_DD = D (1/2 - S_ETF,t),  K_pD = p D - e_t D - S_ETF,t p   (S_ETF,t = ETF inside share).
C  Fee x broad-index fund (his `broad`), a product-type interaction that is not the vehicle.
D  Inertia: lagged log share ratio as a control.
E  Mean fee sensitivity that moves over time: fee x trend (instruments x trend), with and without K.
F  Instrument robustness of the leading rows: one instrument at a time (logit), IV0 + one other (K).
Writes step51_one_menu.csv (coefficients only).
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import pyhdfe

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step48_access_spec_linear as s48
from step48_access_spec_linear import IV, CON

ROWS = []
PROCS = 4
_G = {}


def _resid(cols):
    if _G.get('A') is not None:      # fund FE + FE columns + fund-specific linear trends: sparse least squares
        from scipy.sparse.linalg import lsmr
        return np.column_stack([_G['M'][:, c] - _G['A'] @ lsmr(_G['A'], _G['M'][:, c], atol=1e-10, btol=1e-10, maxiter=5000)[0] for c in cols])
    alg = pyhdfe.create(_G['ids'], drop_singletons=False, residualize_method='lsmr')
    out = np.zeros((_G['M'].shape[0], len(cols)))
    live = [i for i, c in enumerate(cols) if np.ptp(_G['M'][:, c]) > 0]     # a constant column (e.g. ETF x trend on mutual-fund rows) stays zero
    if live:
        out[:, live] = alg.residualize(_G['M'][:, [cols[i] for i in live]])
    return out


class Panel:
    """Columns of d residualized on fund FE + the given FE columns, computed once."""

    def __init__(self, d, fe, cols, tag, fund_trend=False):
        d = d.reset_index(drop=True)
        t0 = time.time()
        self.tag, self.cols, self.n = tag, list(cols), len(d)
        _G['ids'] = np.column_stack([pd.factorize(d.product_ids)[0]] + [pd.factorize(d[c].astype(str))[0] for c in fe])
        _G['M'] = d[self.cols].to_numpy(float)
        _G['A'] = None
        if fund_trend:
            from scipy import sparse
            n, ids = len(d), _G['ids']
            blocks = [sparse.csr_matrix((np.ones(n), (np.arange(n), ids[:, j])), shape=(n, ids[:, j].max() + 1)) for j in range(ids.shape[1])]
            tt = (d.t - d.t.mean()).to_numpy()
            blocks.append(sparse.csr_matrix((tt, (np.arange(n), ids[:, 0])), shape=(n, ids[:, 0].max() + 1)))
            _G['A'] = sparse.hstack(blocks).tocsr()
        chunks = [list(c) for c in np.array_split(np.arange(len(self.cols)), PROCS)]
        with ProcessPoolExecutor(PROCS) as ex:       # fork: workers inherit _G
            parts = list(ex.map(_resid, chunks))
        self.R = dict(zip(self.cols, np.column_stack(parts).T))
        self.clu = pd.factorize(d.market_ids)[0]
        print(f'  [panel {tag}: {len(d):,} rows, {len(self.cols)} columns, {time.time() - t0:.0f}s]', flush=True)

    def est(self, endog, excl, label, controls=(), dep='y'):
        R, clu = self.R, self.clu
        con = list(CON) + list(controls)
        y = R[dep]
        Xe, Ze, W = (np.column_stack([R[c] for c in v]) for v in (endog, excl, con))
        k, L = len(endog), len(excl)
        X, Zm = np.column_stack([Xe, W]), np.column_stack([Ze, W])
        Xh = Zm @ np.linalg.lstsq(Zm, X, rcond=None)[0]
        b = np.linalg.solve(Xh.T @ X, Xh.T @ y)
        u = y - X @ b
        sc = pd.DataFrame(Xh * u[:, None]).groupby(clu).sum().to_numpy()
        Vi = np.linalg.inv(Xh.T @ Xh)
        se = np.sqrt(np.diag(Vi @ sc.T @ sc @ Vi))
        gz = pd.DataFrame(Zm * u[:, None]).groupby(clu).sum().to_numpy()
        J = float(gz.sum(0) @ np.linalg.pinv(gz.T @ gz) @ gz.sum(0)) if L > k else np.nan
        Fs = []
        for i in range(k):      # conditional first-stage F, as step48
            A = np.column_stack([Xh[:, j] for j in range(k) if j != i] + [W])
            xr = X[:, i] - A @ np.linalg.lstsq(A, X[:, i], rcond=None)[0]
            Zr = Ze - A @ np.linalg.lstsq(A, Ze, rcond=None)[0]
            c = np.linalg.lstsq(Zr, xr, rcond=None)[0]
            e = xr - Zr @ c
            s = pd.DataFrame(Zr * e[:, None]).groupby(clu).sum().to_numpy()
            Zi = np.linalg.pinv(Zr.T @ Zr)
            Fs.append(float(c @ np.linalg.pinv(Zi @ s.T @ s @ Zi) @ c) / max(L - (k - 1), 1))
        row = dict(spec=f'{self.tag} | {label}', N=self.n, n_excl=L, J=J, J_df=L - k)
        for i, t in enumerate(endog):
            row[t], row[t + '_se'], row[t + '_F'] = b[i], se[i], Fs[i]
        for i, t in enumerate(con[len(CON):]):
            row[t], row[t + '_se'] = b[k + len(CON) + i], se[k + len(CON) + i]
        ROWS.append(row)
        print(f'{self.tag} | {label}'.ljust(62), ' '.join(f'{t} {b[i]:+.3f} ({se[i]:.3f}) F {Fs[i]:.1f};' for i, t in enumerate(endog)),
              ' '.join(f'[{t} {row[t]:+.3f} ({row[t + "_se"]:.3f})]' for t in con[len(CON):]),
              f'J {J:.1f} on {L - k} df' if L > k else 'just identified', flush=True)
        return row


def prep(P, D, names):
    d = s48.load(P, D, names)
    f = pd.read_csv(f'{D}/passive_focal.csv.gz')
    d['p8'], d['bm'] = f.p8.to_numpy(), f.benchmark.astype(str).to_numpy()
    d['broad'] = np.load(f'{P}/data/prepared/passive.npz', allow_pickle=False)['broad']
    d['year'] = (d.month // 12).astype(int)
    d['t'] = (d.month - d.month.min()) / 12.0
    d['etf_t'] = d.etf * d.t
    d['etf_year'] = np.where(d.etf == 1, 'E' + d.year.astype(str), 'M')
    d['mp8'] = d.market_ids.astype(str) + '_' + d.p8.astype(str)
    d['mbm'] = d.market_ids.astype(str) + '_' + d.bm
    d['me'] = d.market_ids.astype(str) + '_' + d.etf.astype(int).astype(str)
    d['S_etf'] = (d.shares * d.etf).groupby(d.market_ids).transform('sum')
    d['K_DD'] = d.etf * (0.5 - d.S_etf)
    d['K_pD'] = d.prices * d.etf - d.e_t * d.etf - d.S_etf * d.prices
    d['n_etf'] = d.groupby('market_ids').etf.transform('sum')
    d['etf_logn'] = d.etf * np.log(d.n_etf)
    d['etf_fracn'] = d.etf * d.n_etf / d.groupby('market_ids').etf.transform('size')
    d['p_broad'], d['p_t'] = d.prices * d.broad, d.prices * d.t
    for k in range(5):
        d[f'z{k}_etf'], d[f'z{k}_broad'], d[f'z{k}_t'] = d[IV[k]] * d.etf, d[IV[k]] * d.broad, d[IV[k]] * d.t
    x = d.sort_values(['product_ids', 'month'])
    lag = x.groupby('product_ids').y.shift(1)
    lag[x.groupby('product_ids').month.diff() != 1] = np.nan
    d['y_lag'] = lag
    return d


ZE, ZT, ZB = [f'z{k}_etf' for k in range(5)], [f'z{k}_t' for k in range(5)], ['z0_broad', 'z1_broad']
BASE = ['y', 'prices', 'K', 'pp2', 'mpe', 'Ka'] + CON + IV
ALL = BASE + ['etf_t', 'K_DD', 'K_pD', 'etf_logn', 'etf_fracn', 'p_broad', 'p_t', 'p_etf'] + ZE + ZT + ZB
FES = [('month', ['market_ids'], ()), ('month + ETF x trend', ['market_ids'], ('etf_t',)), ('month + ETF x year', ['market_ids', 'etf_year'], ()),
       ('month x asset class', ['mp8'], ()), ('month x asset class + ETF x year', ['mp8', 'etf_year'], ()),
       ('month x benchmark', ['mbm'], ()), ('reference: month x ETF', ['me'], ())]


def main(P, D, names, blocks):
    d = prep(P, D, names)
    print('fund-months with a same-month rival on the same benchmark: %.3f; benchmarks %d; asset classes %d' % (
        (d.groupby('mbm').product_ids.transform('size') > 1).mean(), d.bm.nunique(), d.p8.nunique()))
    pan = {}
    for lab, fe, con in FES:
        key = tuple(fe)
        if key not in pan:
            pan[key] = Panel(d, fe, ALL, '+'.join(fe))
    P_ = lambda lab: next(pan[tuple(fe)] for l, fe, c in FES if l == lab)
    if 'A' in blocks:
        print('\nA. What the month effects are crossed with (common fee slope, five IVs)')
        for lab, fe, con in FES:
            p = pan[tuple(fe)]
            p.tag = lab
            p.est(['prices'], IV, 'logit', con)
            p.est(['prices', 'K'], IV, 'K', con)
            p.est(['prices', 'pp2', 'mpe'], IV, 'split', con)
            p.est(['prices', 'K', 'Ka'], IV, 'K + age K', con)
        for lab, fe in (('month', ['market_ids']), ('month x asset class', ['mp8']), ('month x benchmark', ['mbm'])):
            for v, vl in ((0, 'mutual-fund rows'), (1, 'ETF rows')):
                q = Panel(d[d.etf == v], fe, BASE, f'{lab}; diagnostic, {vl}')
                q.est(['prices'], IV, 'logit')
                q.est(['prices', 'K'], IV, 'K')
    if 'B' in blocks:
        print('\nB. Vehicle random coefficient, correlated with the fee coefficient')
        for lab in ('month', 'month x asset class'):
            p = P_(lab)
            p.tag = lab
            p.est(['prices', 'K', 'K_pD'], IV + ZE, 'fee RC + fee-vehicle covariance; ETF x trend as control', ('etf_t',))
            p.est(['prices', 'K', 'K_pD', 'K_DD'], IV + ZE + ['etf_logn', 'etf_fracn'], 'fee RC, vehicle RC, covariance')
            p.est(['prices', 'K', 'K_DD'], IV + ['etf_logn', 'etf_fracn'], 'fee RC, vehicle RC, no covariance')
            p.est(['prices', 'K_pD', 'K_DD'], IV + ZE + ['etf_logn', 'etf_fracn'], 'no fee RC; vehicle RC and covariance')
    if 'C' in blocks:
        print('\nC. Fee x broad-index fund')
        print('   broad: share of fund-months %.3f, of AUM %.3f; ETF share of broad fund-months %.3f' % (
            d.broad.mean(), d.product_mtna[d.broad == 1].sum() / d.product_mtna.sum(), d.etf[d.broad == 1].mean()))
        for lab in ('month', 'month x asset class'):
            p = P_(lab)
            p.tag = lab
            p.est(['prices', 'p_broad'], IV + ZB, 'logit + fee x broad')
            p.est(['prices', 'p_broad', 'K'], IV + ZB, 'K + fee x broad')
            p.est(['prices', 'p_broad', 'pp2', 'mpe'], IV + ZB, 'split + fee x broad')
    if 'D' in blocks:
        print('\nD. Inertia: lagged log share ratio as a control (long-run slope = fee slope / (1 - coefficient on the lag))')
        x = d.dropna(subset=['y_lag'])
        for lab, fe in (('month', ['market_ids']), ('month x asset class', ['mp8'])):
            for m, sl in ((slice(None), 'all'), (x.etf == 0, 'diagnostic, mutual-fund rows'), (x.etf == 1, 'diagnostic, ETF rows')):
                q = Panel(x[m], fe, BASE + ['y_lag'], f'{lab}; {sl}')
                q.est(['prices'], IV, 'logit + lagged share', ('y_lag',))
                q.est(['prices', 'K'], IV, 'K + lagged share', ('y_lag',))
    if 'E' in blocks:
        print('\nE. Fee sensitivity that moves over time: fee x trend (t in years from the first month)')
        print('   share-weighted mean fee e_t: first year %.3f, last year %.3f' % (d.e_t[d.year == d.year.min()].mean(), d.e_t[d.year == d.year.max()].mean()))
        for lab in ('month', 'month + ETF x trend', 'month x asset class', 'month x asset class + ETF x year'):
            p = P_(lab)
            p.tag = lab
            con = ('etf_t',) if lab == 'month + ETF x trend' else ()
            p.est(['prices', 'p_t'], IV + ZT, 'logit + fee x trend', con)
            p.est(['prices', 'p_t', 'K'], IV + ZT, 'K + fee x trend', con)
            p.est(['prices', 'p_t', 'pp2'], IV + ZT, 'own-fee term p^2/2 only + fee x trend', con)
            p.est(['prices', 'p_t', 'K', 'Ka'], IV + ZT, 'K + age K + fee x trend', con)
    if 'F' in blocks:
        print('\nF. Instrument robustness')
        for lab in ('month', 'month x asset class', 'month x benchmark'):
            p = P_(lab)
            p.tag = lab
            for k in range(5):
                p.est(['prices'], [IV[k]], f'logit, IV{k} alone')
            for k in range(1, 5):
                p.est(['prices', 'K'], [IV[0], IV[k]], f'K, IV0 + IV{k}')
            for k in range(5):
                p.est(['prices', 'K'], [v for j, v in enumerate(IV) if j != k], f'K, all but IV{k}')
    pd.DataFrame(ROWS).to_csv('step51_one_menu.csv', index=False)


if __name__ == '__main__':
    PROCS = int(sys.argv[4])
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[5] if len(sys.argv) > 5 else 'ABCDEF')
