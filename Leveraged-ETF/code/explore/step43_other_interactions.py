"""Can price interactions with ETF, institutional share class and broad-based replace (or improve on) the cheap
interaction of V2? Index market, logit IV, V2 pipeline (for_coauthor/V2_replication/replicate_V2.py) unchanged except for
the set of price interactions.

  delta = a p + sum_k a_k (p x z_k) + |TE| + past 1y return + log age + fund FE + month FE
  excluded instruments: IV and IV x z_k (exactly identified); SE clustered by month.

Indicators z_k, all fixed per fund (fund FE absorb the main effects):
  cheap      gene_idx (V2)
  etf        ETF_ind
  inst       mutual fund whose CRSP-flag share class (V2's) is institutional in most of its Table 2 months
  broad      the paper's label, broad_specialized == "broad-based" (Table A7)
  broadfix   the same label made consistent within a tracked index: the most common label among the funds of that
             market_m_index (repairs SPY, SPDR Portfolio S&P 500 and VTI's ETF class, which are labelled specialized)
Two instruments:
  Z      V2's instrument, on the rows where it is defined (96,069)
  paper  the paper's BLP_IV_hausman_exp_ratio, on all supply rows (107,863)
Money market funds are dropped throughout, as in V2. Supply side: all 107,863 rows; MC at each candidate's own eta.

    python step43_other_interactions.py --index-csv ... --crsp ...
Writes step43_demand.csv, step43_table5.csv, step43_where.csv.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'for_coauthor', 'V2_replication'))
import replicate_V2 as v2  # noqa: E402

pyblp.options.verbose = False
C = v2.CONTROLS

SPECS = {
    'none': [],
    'cheap (V2)': ['cheap'],
    'etf': ['etf'],
    'inst': ['inst'],
    'broad': ['broad'],
    'broadfix': ['broadfix'],
    'etf+inst': ['etf', 'inst'],
    'etf+broad': ['etf', 'broad'],
    'inst+broad': ['inst', 'broad'],
    'etf+inst+broad': ['etf', 'inst', 'broad'],
    'etf+inst+broadfix': ['etf', 'inst', 'broadfix'],
    'cheap+etf': ['cheap', 'etf'],
    'cheap+inst': ['cheap', 'inst'],
    'cheap+broad': ['cheap', 'broad'],
    'cheap+broadfix': ['cheap', 'broadfix'],
    'cheap+etf+inst': ['cheap', 'etf', 'inst'],
    'cheap+etf+inst+broad': ['cheap', 'etf', 'inst', 'broad'],
}


def fit(est, zs, iv):
    dd = est.drop(columns=[c for c in est.columns if c.startswith('demand_instruments')]).reset_index(drop=True)
    dd['demand_instruments0'] = dd[iv].to_numpy(float)
    endog, excl, terms = ['prices'], ['demand_instruments0'], ['prices']
    for k, z in enumerate(zs):
        dd[f'px_{z}'] = dd.prices * dd[z]
        dd[f'demand_instruments{k + 1}'] = dd[iv].to_numpy(float) * dd[z]
        endog.append(f'px_{z}')
        excl.append(f'demand_instruments{k + 1}')
        terms.append(f'I(prices*{z})')   # must contain `prices` so that pyblp treats the term as endogenous
    res = pyblp.Problem(pyblp.Formulation(' + '.join(terms + C), absorb='C(product_ids) + C(market_ids)'), dd).solve(
        se_type='clustered')
    def key(lab):  # 'prices*etf' or 'etf*prices' -> 'px_etf'
        parts = [x for x in lab.replace(' ', '').split('*') if x != 'prices']
        return f'px_{parts[0]}' if '*' in lab else lab
    b = {key(k): v for k, v in zip(res.beta_labels, res.beta.flatten())}
    se = {key(k): v for k, v in zip(res.beta_labels, res.beta_se.flatten())}
    assert all(f'px_{z}' in b for z in zs), res.beta_labels
    f = v2.sw_f(dd, endog, excl)
    own = res.extract_diagonals(res.compute_elasticities()).flatten()
    out = dict(N=len(dd), min_F=min(f.values()), share_pos_e=float(np.nanmean(own > 0)), avg_e=float(np.nanmean(own)),
               share_abs_e_gt1=float(np.nanmean(np.abs(own) > 1)), b_prices=b['prices'], se_prices=se['prices'])
    for z in zs:
        out[f'b_{z}'], out[f'se_{z}'] = b[f'px_{z}'], se[f'px_{z}']
    return out, res, dd, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--index-csv', default='nonLev_funds_product_month_level_v2_patched.csv')
    ap.add_argument('--crsp', default='CRSP_fund_summary_2026_qtrly_combined.csv')
    a = ap.parse_args()
    pd.set_option('display.width', 250, 'display.max_columns', 40)

    d_all = v2.load_sample(a.index_csv)
    raw_all = pd.read_csv(a.index_csv, usecols=['product_j', 'month_t', 'product_exp_ratio', 'product_fund_name']).dropna(
        subset=['product_exp_ratio'])
    crsp = pd.read_csv(a.crsp, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    mmf = v2.money_market_funds(crsp, set(raw_all.product_j))
    del crsp
    mmf_sample = sorted(set(mmf) & set(d_all.product_ids))
    raw = v2.build_instrument(a.index_csv, a.crsp, mmf)
    d = d_all[~d_all.product_ids.isin(mmf_sample)].reset_index(drop=True)
    d = d.join(v2.gene_idx(raw_all).rename('cheap'), on='product_ids')
    d = d.merge(raw[['product_j', 'month_t', 'Z', 'asset_class', 'share_class']].rename(columns={'product_j': 'product_ids'}),
                on=['product_ids', 'month_t'], how='left')
    d['gene_idx'] = d.cheap

    # indicators, fixed per fund
    d['etf'] = d.groupby('product_ids').ETF_ind.transform('max').astype(float)
    d['inst'] = ((d.share_class == 'inst').groupby(d.product_ids).transform('mean') > 0.5).astype(float) * (1 - d.etf)
    lab = (d.broad_specialized == 'broad-based').astype(float)
    d['broad'] = (lab.groupby(d.product_ids).transform('mean') > 0.5).astype(float)
    key_i = d.market_m_index.fillna('_none_' + d.product_ids.astype(str))
    fund_lab = pd.DataFrame({'i': key_i, 'b': d.broad, 'pj': d.product_ids}).drop_duplicates('pj')
    d['broadfix'] = key_i.map((fund_lab.groupby('i').b.mean() > 0.5).astype(float))
    d['paper'] = d.demand_instruments0
    Z = ['cheap', 'etf', 'inst', 'broad', 'broadfix']
    print(f'supply rows {len(d):,}; rows with Z {d.Z.notna().sum():,}; paper IV missing {d.paper.isna().sum()}')
    print('share of fund-months:', d[Z].mean().round(3).to_dict())
    print('share of fund-months, Z rows:', d.loc[d.Z.notna(), Z].mean().round(3).to_dict())
    print('correlation across fund-months:\n', d[Z].corr().round(2))
    print('mean fee by group (1 / 0):', {z: (round(d.prices[d[z] == 1].mean(), 3), round(d.prices[d[z] == 0].mean(), 3)) for z in Z})
    print('broad vs broadfix differ on', int((d.broad != d.broadfix).sum()), 'fund-months,',
          d.loc[d.broad != d.broadfix, 'product_ids'].nunique(), 'funds')

    p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
    van = (d.firm_ids == 'Vanguard').to_numpy()
    rows, t5s, whs = [], [], []
    for iv in ('Z', 'paper'):
        est = d[d[iv].notna()].reset_index(drop=True)
        for name, zs in SPECS.items():
            o, res, dd, b = fit(est, zs, iv)
            o = dict(iv=iv, spec=name, **o)
            dd['Z'] = dd[iv]
            o.update(v2.lead_tests(dd, res))
            dd['gene_idx'] = dd.cheap
            t5 = v2.table5(res, dd, d_all)
            o['t5_gt1'] = int((t5.own_elasticity.abs() > 1).sum())
            o['t5_n'] = len(t5)
            t5s.append(t5.assign(iv=iv, spec=name))
            # supply side on all rows
            alpha = np.full(len(d), b['prices']) + sum(b[f'px_{z}'] * d[z].to_numpy() for z in zs)
            o['share_pos_alpha_supply'] = float((alpha > 0).mean())
            for m, k in v2.CONDUCT.items():
                if k is None:
                    continue
                mu = v2.markups(d, alpha, k)
                eta = v2.scale_iv(d, p - mu)['eta']
                mc = p + eta * logq - mu
                ns = v2.neg_stats(d, mc)
                o.update({f'{m}_eta': eta, f'{m}_neg_markup': float((mu < 0).mean()), f'{m}_neg_mc': ns['neg_share'],
                          f'{m}_below_m020': ns['share_below_m020'], f'{m}_below_m060': ns['share_below_m060'],
                          f'{m}_mc_min': ns['mc_min']})
                neg = mc < 0
                if m == 'B0':
                    o['B0_vanguard_share_neg'] = float(neg[van].mean())
                    o['B0_vanguard_share_of_all_neg'] = float(neg[van].sum() / neg.sum()) if neg.sum() else np.nan
                    for g in Z:
                        for v in (0, 1):
                            idx = (d[g] == v).to_numpy()
                            whs.append(dict(iv=iv, spec=name, group=g, value=v, fund_months=int(idx.sum()),
                                            share_neg=float(neg[idx].mean())))
            rows.append(o)
            coefs = ' | '.join([f"p {o['b_prices']:.2f} ({o['se_prices']:.2f})"] + [f"x{z} {o[f'b_{z}']:.2f} ({o[f'se_{z}']:.2f})" for z in zs])
            print(f"[{iv:5s}] {name:22s} N {o['N']:,} | {coefs} | minF {o['min_F']:.1f} | e>0 {o['share_pos_e']:.3f} | avg e {o['avg_e']:.2f} "
                  f"| T5 {o['t5_gt1']}/{o['t5_n']} | leads {o['lead12_t']:.1f}/{o['lead24_t']:.1f}/{o['lead36_t']:.1f} "
                  f"| negMC B0 {o['B0_neg_mc']:.3f} B65 {o['B65_neg_mc']:.3f} | <-0.20 B0 {o['B0_below_m020']:.3f} B65 {o['B65_below_m020']:.3f} "
                  f"| min MC {o['B65_mc_min']:.2f} | neg markup {o['B0_neg_markup']:.3f} | Vanguard {o['B0_vanguard_share_neg']:.2f}", flush=True)
            pd.DataFrame(rows).to_csv('step43_demand.csv', index=False)
    pd.concat(t5s).to_csv('step43_table5.csv', index=False)
    pd.DataFrame(whs).to_csv('step43_where.csv', index=False)
    t = pd.concat(t5s)
    t['short'] = t.name.str[:38]
    for iv in ('Z', 'paper'):
        print(f'\nTable 5 own elasticities, instrument {iv}')
        print(t[t.iv == iv].pivot_table(index=['short', 'price'], columns='spec', values='own_elasticity', sort=False)[list(SPECS)].round(2).to_string())


if __name__ == '__main__':
    main()
