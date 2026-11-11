"""Is the lead test's inference valid? Recompute its t-statistics with standard errors clustered by month (as reported
so far), by fund, and two-way (fund and month), for specifications 1-4 with and without the variable-annuity funds.

Lead test: regress the demand residual xi_{j,t} on the instrument k months later, Z_{j,t+k} (k = 12, 24, 36). Z is first
residualized on the controls, fund FE and month FE; both variables are then demeaned within fund on the matched sample.
xi and Z are persistent within fund, so month-only clustering can overstate the t-statistic.
Also a mirror test (xi_{j,t} on Z_{j,t-k}). Writes sc_leadcheck.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
from sc_build import PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402

pyblp.options.verbose = False


def tstats(dd, res, k):
    dd = dd.assign(xi=res.xi.flatten())
    dd['zt'] = v2.resid(dd, ['Z'])[:, 0]
    lag = dd[['product_ids', 'month_key', 'xi']].assign(month_key=dd.month_key + k)   # xi_t matched to Z_{t+k}
    m = dd[['product_ids', 'month_key', 'zt']].merge(lag, on=['product_ids', 'month_key'])
    y = (m.xi - m.groupby('product_ids').xi.transform('mean')).to_numpy()
    x = (m.zt - m.groupby('product_ids').zt.transform('mean')).to_numpy()
    b = (x @ y) / (x @ x)
    s = pd.Series(x * (y - b * x))
    vm = (s.groupby(m.month_key.to_numpy()).sum() ** 2).sum()
    vf = (s.groupby(m.product_ids.to_numpy()).sum() ** 2).sum()
    vh = (s ** 2).sum()
    se = lambda v: np.sqrt(max(v, 1e-300)) / (x @ x)
    return dict(b=b, t_month=b / se(vm), t_fund=b / se(vf), t_twoway=b / se(vm + vf - vh), n=len(m), funds=m.product_ids.nunique())


def main():
    d = pd.read_pickle(PANEL)
    d['gene_idx'] = d.cheap
    d['IV0'] = d.demand_instruments0
    fam = d.firm_f_old.notna().to_numpy()
    d['iv4p'] = d.R_ac.where(fam).fillna(d.IV0)
    d['broad'] = ((d.broad_specialized == 'broad-based').groupby(d.product_ids).transform('mean') > 0.5).astype(float)
    allr = np.ones(len(d), bool)
    v2rows = (d.mmf == 0).to_numpy() & d.Z.notna().to_numpy()
    SPECS = {'1 T2': ('IV0', [], allr), '1 T2, no VA': ('IV0', [], fam), '2 Danny proxy': ('iv4p', [], allr), '2 Danny proxy, no VA': ('iv4p', [], fam),
             '3 V2': ('Z', ['cheap'], v2rows), '4 A5': ('IV0', ['broad'], allr), '4 A5, no VA': ('IV0', ['broad'], fam)}
    rows = []
    for name, (iv, zs, mask) in SPECS.items():
        o, res, dd, b = fit(d[mask].reset_index(drop=True), iv, zs)
        dd['Z'] = dd[iv]
        for k in (12, 24, 36, -12, -24):
            r = dict(spec=name, k=k, **tstats(dd, res, k))
            rows.append(r)
            print(f"{name:22s} k {k:4d} | b {r['b']:8.3f} | t month {r['t_month']:6.2f} | t fund {r['t_fund']:6.2f} | t two-way {r['t_twoway']:6.2f} | n {r['n']:,} funds {r['funds']}", flush=True)
        pd.DataFrame(rows).to_csv('sc_leadcheck.csv', index=False)


if __name__ == '__main__':
    main()
