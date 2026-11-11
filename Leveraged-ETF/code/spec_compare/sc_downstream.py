"""Spec comparison, step 2 (downstream, no conduct) and step 3 (conduct test), for the specs fitted by sc_demand.py.

    python sc_downstream.py                 # markups, scale eta by candidate, negative MC, location -> sc_scale/mc/where.csv
    python sc_downstream.py conduct SPEC    # pyRVtest for one spec, eta schemes A (0.024), B (own eta), C (PC eta) -> sc_conduct_SPEC.csv

Conventions as in code/explore/downstream.py and RESULTS_downstream.md (functions taken from replicate_V2.py, which
reproduces them): candidates PC, B0, B25, B50, B65; MC = p + eta ln(TNA) - markup; eta by 2SLS (rotator) under each
candidate; negative-MC share = mean over months of the within-month share.
Supply rows: all 108,300 for specs 1, 2, 4p, 4q; 107,863 (money market funds dropped) for specs 3 and 5.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
from sc_build import CACHE, PANEL  # noqa: E402

SPECS = ['1_T2', '2_A5', '3_V2', '4p', '4q', '5_V2nocheap']


def supply(d_all, spec):
    rows = np.load(f'{CACHE}/rows_{spec}.npy')
    if spec in ('V2n', 'V2nx'):   # the new V2 uses the cheap indicator rebuilt on the source panel (location tables group by it)
        d_all = d_all.assign(cheap=np.load(f'{CACHE}/cheap_V2n.npy'))
    d = d_all.iloc[rows].reset_index(drop=True)
    return d, np.load(f'{CACHE}/alpha_{spec}.npy')


def downstream():
    d_all = pd.read_pickle(PANEL)
    sc, mcs, wh = [], [], []
    for spec in SPECS:
        d, alpha = supply(d_all, spec)
        p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
        nm = d.product_fund_name.fillna('').str.lower()
        groups = {'firm': np.where(d.firm_ids.isin(v2.BIG3), d.firm_ids, 'other firms'),
                  'SPY': d.product_fund_name.fillna('').str.startswith('SPDR S&P 500 ETF Trust'),
                  'cheap': d.cheap, 'asset_class': d.ac_all.fillna('none'),
                  'size': np.select([nm.str.contains('small|micro'), nm.str.contains('mid')], ['small/micro', 'mid'], 'other'),
                  'mmf': d.mmf}
        mus = {}
        for m, k in v2.CONDUCT.items():
            mu = v2.markups(d, alpha, k)
            mus[m] = mu
            s = v2.scale_iv(d, p - mu)
            sc.append(dict(spec=spec, candidate=m, **s))
            for eta_name, eta in (('0', 0.0), ('0.024', 0.024), ('own', s['eta'])):
                mc = p + eta * logq - mu
                mcs.append(dict(spec=spec, candidate=m, eta_scheme=eta_name, eta=eta, mean_markup=float(mu.mean()),
                                median_markup=float(np.median(mu)), share_neg_markup=float((mu < 0).mean()),
                                share_markup_gt_price=float((mu > p).mean()), **v2.neg_stats(d, mc)))
                if eta_name == 'own' and k is not None:
                    neg = mc < 0
                    for gname, gv in groups.items():
                        for g, idx in pd.Series(np.arange(len(d))).groupby(np.asarray(gv)).groups.items():
                            idx = np.asarray(idx)
                            wh.append(dict(spec=spec, candidate=m, group_by=gname, group=str(g), fund_months=len(idx),
                                           share_neg=float(neg[idx].mean()),
                                           share_of_all_neg=float(neg[idx].sum() / neg.sum()) if neg.sum() else np.nan))
        np.savez(f'{CACHE}/mus_{spec}.npz', **mus)
        S, M = pd.DataFrame(sc), pd.DataFrame(mcs)
        S.to_csv('sc_scale.csv', index=False)
        M.to_csv('sc_mc.csv', index=False)
        pd.DataFrame(wh).to_csv('sc_where.csv', index=False)
        print(f'\n=== {spec}: supply rows {len(d):,}; alpha range {alpha.min():.2f} to {alpha.max():.2f}')
        print(S[S.spec == spec].round(4).to_string(index=False))
        print(M[M.spec == spec].drop(columns=['spec', 'neg_share_pooled', 'mc_p1', 'mc_mean']).round(4).to_string(index=False), flush=True)
        W = pd.DataFrame(wh)
        w = W[(W.spec == spec) & (W.candidate == 'B0')]
        print('  B0, own eta, share negative by group: ' + ' | '.join(f'{r.group_by}={r.group}: {r.share_neg:.2f} ({r.share_of_all_neg:.2f})' for r in w.itertuples()), flush=True)


def conduct(spec):
    d_all = pd.read_pickle(PANEL)
    d, _ = supply(d_all, spec)
    del d_all
    z = np.load(f'{CACHE}/mus_{spec}.npz')
    mus = {m: z[m] for m in v2.CONDUCT}
    eta = pd.read_csv('sc_scale.csv').query('spec == @spec').set_index('candidate').eta
    year = pd.Series(np.floor(d.month_t))
    capped = {m: v2.winsor_by_year(mus[m], year) if v2.CONDUCT[m] is not None else mus[m] for m in v2.CONDUCT}
    runs = [('A: eta 0.024', mus, {m: 0.024 for m in v2.CONDUCT}),
            ('B: own eta', mus, {m: float(eta[m]) for m in v2.CONDUCT}),
            ('C: PC eta', mus, {m: float(eta['PC']) for m in v2.CONDUCT}),
            ('A capped 1/99 by year', capped, {m: 0.024 for m in v2.CONDUCT})]
    out = []
    for name, mu, etas in runs:
        cd = v2.conduct_test(d, mu, etas).assign(eta_scheme=name, spec=spec)
        out.append(cd)
        pd.concat(out).to_csv(f'sc_conduct_{spec}.csv', index=False)
        v2.log(f'{spec} conduct [{name}] ' + ' | '.join(
            f'{iv.split(":")[0]}: {[f"{r.candidate} ({r.mcs_p:.2f})" for r in cd[(cd.iv_set == iv) & cd.selected].itertuples()]}'
            for iv in v2.CONDUCT_IV))
        main_iv = cd[cd.iv_set == list(v2.CONDUCT_IV)[0]]
        v2.log('   main IV: ' + ' | '.join(f'{r.candidate} p {r.mcs_p:.3f} T vs B65 {r.TRV_vs_B65:.2f}' for r in main_iv.itertuples())
               + f' | min F {np.nanmin(main_iv[[c for c in main_iv if c.startswith("F_vs_")]].to_numpy()):.0f}')


if __name__ == '__main__':
    pd.set_option('display.width', 250, 'display.max_columns', 40)
    if len(sys.argv) > 1 and sys.argv[1] == 'conduct':
        conduct(sys.argv[2])
    else:
        downstream()
