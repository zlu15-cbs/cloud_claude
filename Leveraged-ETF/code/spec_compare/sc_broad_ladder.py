"""Why does price x broad-based slope upward for specialized funds under V2's instrument Z but not under the paper's IV0?
A ladder between the two instruments, one construction choice at a time, all with the same demand model:

    delta = a p + a_b (p x broad) + controls + fund FE + month FE;  instruments IV, IV x broad;  SE clustered by month

Instruments (same family firm_f_old, same month, donors from the whole index CSV, money market funds dropped):
    exclusion    idx = donors tracking another index (paper)      ac  = donors in another Lipper-6 asset class (V2)
    share type   pool = any share type (paper)                    same = the target's share type (V2)
    aggregation  wavg = lag-AUM-weighted mean (paper)             med  = unweighted median (V2)
  idx/pool/wavg rebuilds the paper's IV0 from our file; ac/same/med is V2's Z.  'IV0' is the original column.
Rows: 'own' = every non-money-market row where the instrument is defined; 'common' = rows where all 8 are defined.
Also, per instrument: the single slope (no interaction) and the slope on the broad and specialized subsamples.
Writes sc_broad_ladder.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
from sc_build import CRSP, INDEX, PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402

pyblp.options.verbose = False


def leave_out(r, excl, same_type, agg):
    keys = ['firm_f_old', 'month_t'] + (['share_class'] if same_type else [])
    rr = r[r.firm_f_old.notna()]
    if agg == 'wavg':
        w = rr.product_L1_mtna.fillna(0.0)
        x = rr.product_exp_ratio * w
        g1, g2 = [rr[k] for k in keys], [rr[k] for k in keys + [excl]]
        num = x.groupby(g1).transform('sum') - x.groupby(g2).transform('sum')
        den = w.groupby(g1).transform('sum') - w.groupby(g2).transform('sum')
        return (num / den).where(den > 1e-9).reindex(r.index)
    out = pd.Series(np.nan, index=r.index)
    fee, lab = rr.product_exp_ratio.to_numpy(), pd.factorize(rr[excl])[0]
    pos = rr.index.to_numpy()
    for idx in rr.groupby(keys).indices.values():
        f, l = fee[idx], lab[idx]
        for u in np.unique(l):
            m = l != u
            if m.any():
                out.loc[pos[idx[~m]]] = np.median(f[m])
    return out


def main():
    pd.set_option('display.width', 250, 'display.max_columns', 40)
    d = pd.read_pickle(PANEL)
    d = d[d.mmf == 0].reset_index(drop=True)
    d['gene_idx'] = d.cheap
    d['broad'] = ((d.broad_specialized == 'broad-based').groupby(d.product_ids).transform('mean') > 0.5).astype(float)
    d['spec_'] = 1 - d.broad

    crsp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    ids = set(pd.read_csv(INDEX, usecols=['product_j']).product_j)
    mmf = v2.money_market_funds(crsp, ids)
    del crsp
    raw = v2.build_instrument(INDEX, CRSP, mmf)
    w = pd.read_csv(INDEX, usecols=['product_j', 'month_t', 'product_L1_mtna'])
    raw = raw.merge(w, on=['product_j', 'month_t'], how='left')
    raw['market_m_index'] = raw.market_m_index.fillna('_none_' + raw.product_j.astype(str))
    names = []
    for excl, ecol in (('idx', 'market_m_index'), ('ac', 'asset_class')):
        for typ in ('pool', 'same'):
            for agg in ('wavg', 'med'):
                n = f'{excl}/{typ}/{agg}'
                raw[n] = leave_out(raw, ecol, typ == 'same', agg)
                names.append(n)
                v2.log(f'built {n}: defined on {raw[n].notna().mean():.3f} of donor-pool rows')
    assert np.allclose(raw['ac/same/med'].fillna(-1), raw.Z.fillna(-1)), 'ac/same/med must equal V2 Z'
    d = d.merge(raw[['product_j', 'month_t'] + names].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
    d['IV0'] = d.demand_instruments0
    common = d[names].notna().all(axis=1)
    fam = d.firm_f_old.notna()
    print(f'rows: all {len(d):,}; with family code {int(fam.sum()):,}; common to the 8 instruments {int(common.sum()):,}; '
          f'broad share {d.broad.mean():.3f}', flush=True)
    print('correlation of the instruments on the common rows (within fund and month):')
    R = pd.DataFrame(v2.resid(d[common].reset_index(drop=True), ['IV0'] + names + ['prices']), columns=['IV0'] + names + ['prices'])
    print(R.corr().round(2).to_string(), flush=True)

    runs = [('IV0', 'all', d.index >= 0), ('IV0', 'family code', fam), ('IV0', 'common', common)]
    for n in names:
        runs += [(n, 'own', d[n].notna()), (n, 'common', common)]
    rows = []
    for iv, rname, mask in runs:
        est = d[np.asarray(mask)].reset_index(drop=True)
        o, res, dd, b = fit(est, iv, ['broad'])
        r = dict(iv=iv, rows=rname, N=o['N'], b_spec=o['b_prices'], se_spec=o['se_prices'], b_xbroad=o['b_broad'], se_xbroad=o['se_broad'],
                 broad_total=o['b_prices'] + o['b_broad'], min_F=o['min_F'], share_pos_e=o['share_pos_e'],
                 lead12=o['lead12_t'], lead24=o['lead24_t'], lead36=o['lead36_t'])
        o1 = fit(est, iv, [])[0]
        r.update(one_slope=o1['b_prices'], one_slope_se=o1['se_prices'], one_slope_F=o1['min_F'])
        for g, v in (('specialized', 0), ('broad', 1)):
            og = fit(est[est.broad == v].reset_index(drop=True), iv, [])[0]
            r.update({f'sub_{g}': og['b_prices'], f'sub_{g}_se': og['se_prices'], f'sub_{g}_F': og['min_F'], f'sub_{g}_N': og['N']})
        # first stage by group on the pooled residuals: coefficient of the fee on the instrument
        Rg = v2.resid(est, ['prices', iv])
        for g, v in (('specialized', 0), ('broad', 1)):
            m = (est.broad == v).to_numpy()
            r[f'fs_{g}'] = float(Rg[m, 1] @ Rg[m, 0] / (Rg[m, 1] @ Rg[m, 1]))
        rows.append(r)
        print(f"{iv:14s} {rname:11s} N {r['N']:>7,} | specialized {r['b_spec']:6.2f} ({r['se_spec']:.2f}) | x broad {r['b_xbroad']:6.2f} ({r['se_xbroad']:.2f}) "
              f"| F {r['min_F']:6.1f} | e>0 {r['share_pos_e']:.2f} | leads {r['lead12']:.1f}/{r['lead24']:.1f}/{r['lead36']:.1f} "
              f"| one slope {r['one_slope']:6.2f} ({r['one_slope_se']:.2f}) | subsamples: spec {r['sub_specialized']:6.2f} ({r['sub_specialized_se']:.2f}, F {r['sub_specialized_F']:.0f}) "
              f"broad {r['sub_broad']:6.2f} ({r['sub_broad_se']:.2f}, F {r['sub_broad_F']:.0f}) | first stage spec {r['fs_specialized']:.3f} broad {r['fs_broad']:.3f}", flush=True)
        pd.DataFrame(rows).to_csv('sc_broad_ladder.csv', index=False)


if __name__ == '__main__':
    main()
