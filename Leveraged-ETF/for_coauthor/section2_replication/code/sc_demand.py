"""Spec comparison, step 1b: the demand fits. Index market, logit IV, fund + month FE, SE clustered by month.

  1   T2      paper IV0, no interaction, 108,300 rows                              (reference -5.606)
  2   A5      paper IV0 x fee tercile at the fund's first sample month, 108,300    (CLOUD_PROMPT_explore_price_heterogeneity A5)
  3   V2      Z x cheap, 96,069 rows, money market funds dropped                   (reference -3.642 / -20.562)
  4p  Danny proxy: IV0 rebuilt, donors outside the target's index AND Lipper-6 asset class, pooled share types,
              lag-AUM weights, original IV0 where undefined or where the family code is blank; 108,300 rows
  4q  the same with market_m_cluster as the exposure class
  5   V2 without the cheap interaction: Z only, one slope, V2's rows
Extra rows (not specs): 4p/4q with blank families matched to one another (b), T2 with our reconstructed IV0 (validation),
T2 / A5 / 4p without the 4 money market funds, and spec 5 split into cheap and non-cheap subsamples.
Writes sc_demand.csv, sc_table5.csv, sc_split.csv and /tmp/data/cache/alpha_<spec>.npy (own-price coefficient per supply row).
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
from sc_build import CACHE, PANEL  # noqa: E402

pyblp.options.verbose = False
C = v2.CONTROLS


def fit(est, iv, zs):
    dd = est.drop(columns=[c for c in est.columns if c.startswith('demand_instruments')]).reset_index(drop=True)
    dd['demand_instruments0'] = dd[iv].to_numpy(float)
    endog, excl, terms = ['prices'], ['demand_instruments0'], ['prices']
    for k, z in enumerate(zs):
        dd[f'px_{z}'] = dd.prices * dd[z]
        dd[f'demand_instruments{k + 1}'] = dd[iv].to_numpy(float) * dd[z]
        endog.append(f'px_{z}')
        excl.append(f'demand_instruments{k + 1}')
        terms.append(f'I(prices*{z})')   # must contain `prices` so that pyblp treats the term as endogenous
    res = pyblp.Problem(pyblp.Formulation(' + '.join(terms + C), absorb='C(product_ids) + C(market_ids)'), dd).solve(se_type='clustered')

    def key(lab):
        parts = [x for x in lab.replace(' ', '').split('*') if x != 'prices']
        return f'px_{parts[0]}' if '*' in lab else lab
    b = {key(k): float(v) for k, v in zip(res.beta_labels, res.beta.flatten())}
    se = {key(k): float(v) for k, v in zip(res.beta_labels, res.beta_se.flatten())}
    assert all(f'px_{z}' in b for z in zs), res.beta_labels
    f = v2.sw_f(dd, endog, excl)
    E = res.compute_elasticities()
    own = res.extract_diagonals(E).flatten()
    out = dict(N=len(dd), funds=dd.product_ids.nunique(), markets=dd.market_ids.nunique(), min_F=min(f.values()),
               share_pos_e=float(np.nanmean(own > 0)), avg_e=float(np.nanmean(res.extract_diagonal_means(E))),
               avg_e_pooled=float(np.nanmean(own)), median_e=float(np.nanmedian(own)), share_abs_e_gt1=float(np.nanmean(np.abs(own) > 1)),
               e_p10=float(np.nanpercentile(own, 10)), e_p90=float(np.nanpercentile(own, 90)),
               e_aum_weighted=float(np.nansum(own * dd.product_mtna.to_numpy()) / dd.product_mtna.sum()),
               b_prices=b['prices'], se_prices=se['prices'])
    for z in zs:
        out[f'b_{z}'], out[f'se_{z}'] = b[f'px_{z}'], se[f'px_{z}']
    for c in C:
        out[f'b_{c}'], out[f'se_{c}'] = b[c], se[c]
    dd['Z'] = dd[iv]
    out.update(v2.lead_tests(dd, res))
    out['lead_max_abs_t'] = max(abs(out[f'lead{k}_t']) for k in (12, 24, 36))
    return out, res, dd, b


def main():
    pd.set_option('display.width', 250, 'display.max_columns', 60)
    d = pd.read_pickle(PANEL)
    d['gene_idx'] = d.cheap
    iv0 = d.demand_instruments0
    fam = d.firm_f_old.notna()
    d['iv0'] = iv0
    d['iv4p'] = d.R_ac.where(fam).fillna(iv0)
    d['iv4q'] = d.R_clx.where(fam).fillna(iv0)
    d['iv4p_b'] = d.R_ac.fillna(iv0)
    d['iv4q_b'] = d.R_clx.fillna(iv0)
    d['iv_ridx'] = d.R_idx.where(fam).fillna(iv0)
    for c in ('R_idx', 'R_ac', 'R_clx'):
        ok = d[c].notna() & fam
        dd = (d[c] - iv0).abs()[ok]
        print(f'{c}: defined with a family code on {int(ok.sum()):,} rows; fallback {int((~ok).sum()):,}; equal to IV0 (1e-8) {(dd < 1e-8).mean():.3f}; '
              f'within 0.0005 {(dd < 5e-4).mean():.3f}; corr {np.corrcoef(d[c][ok], iv0[ok])[0, 1]:.3f}', flush=True)
    nomm = d.mmf == 0
    v2rows = nomm & d.Z.notna()
    # name: (label, iv, interactions, estimation rows, supply rows)
    SPECS = {
        '1_T2': ('T2 (paper Table 2 col 2)', 'iv0', [], d.index >= 0, d.index >= 0),
        '2_A5': ('A5 (fee tercile at first sample month)', 'iv0', ['fee_t1', 'fee_t2'], d.index >= 0, d.index >= 0),
        '3_V2': ('V2 (Z x cheap)', 'Z', ['cheap'], v2rows, nomm),
        '4p': ('Danny proxy 4p (index + Lipper-6 exclusion)', 'iv4p', [], d.index >= 0, d.index >= 0),
        '4q': ('Danny proxy 4q (index + cluster exclusion)', 'iv4q', [], d.index >= 0, d.index >= 0),
        '5_V2nocheap': ('V2 without cheap (Z, one slope)', 'Z', [], v2rows, nomm),
        # extra rows
        'x_4p_blank': ('4p, blank families matched', 'iv4p_b', [], d.index >= 0, None),
        'x_4q_blank': ('4q, blank families matched', 'iv4q_b', [], d.index >= 0, None),
        'x_T2_ridx': ('T2 with our reconstructed IV0', 'iv_ridx', [], d.index >= 0, None),
        'x_T2_nommf': ('T2 without money market funds', 'iv0', [], nomm, None),
        'x_A5_nommf': ('A5 without money market funds', 'iv0', ['fee_t1', 'fee_t2'], nomm, None),
        'x_4p_nommf': ('4p without money market funds', 'iv4p', [], nomm, None),
        'x_4q_nommf': ('4q without money market funds', 'iv4q', [], nomm, None),
        'x_T2_v2rows': ('T2 IV0 on V2 rows', 'iv0', [], v2rows, None),
        'x_4p_v2rows': ('4p on V2 rows', 'iv4p', [], v2rows, None),
        'x_5_cheap': ('spec 5, cheap funds only', 'Z', [], v2rows & (d.cheap == 1), None),
        'x_5_noncheap': ('spec 5, non-cheap funds only', 'Z', [], v2rows & (d.cheap == 0), None),
    }
    rows, t5s = [], []
    for name, (label, iv, zs, erows, srows) in SPECS.items():
        est = d[erows].reset_index(drop=True)
        o, res, dd, b = fit(est, iv, zs)
        o = dict(spec=name, label=label, iv=iv, interactions='+'.join(zs), **o)
        t5 = v2.table5(res, dd, d)
        o['t5_gt1'], o['t5_n'] = int((t5.own_elasticity.abs() > 1).sum()), len(t5)
        t5s.append(t5.assign(spec=name))
        if srows is not None:
            sup = d[srows]
            alpha = np.full(len(sup), b['prices']) + sum(b[f'px_{z}'] * sup[z].to_numpy() for z in zs)
            np.save(f'{CACHE}/alpha_{name}.npy', alpha)
            np.save(f'{CACHE}/rows_{name}.npy', np.flatnonzero(np.asarray(srows)))
            o['supply_rows'], o['share_pos_alpha_supply'] = len(sup), float((alpha > 0).mean())
        rows.append(o)
        coefs = ' | '.join([f"p {o['b_prices']:.3f} ({o['se_prices']:.3f})"] + [f"x{z} {o[f'b_{z}']:.3f} ({o[f'se_{z}']:.3f})" for z in zs])
        print(f"{name:14s} N {o['N']:,} | {coefs} | minF {o['min_F']:.1f} | e>0 {o['share_pos_e']:.4f} | avg e {o['avg_e']:.3f} (median {o['median_e']:.2f}, "
              f"AUM-w {o['e_aum_weighted']:.2f}) | |e|>1 {o['share_abs_e_gt1']:.2f} | T5 {o['t5_gt1']}/{o['t5_n']} "
              f"| leads {o['lead12_t']:.2f}/{o['lead24_t']:.2f}/{o['lead36_t']:.2f}", flush=True)
        pd.DataFrame(rows).to_csv('sc_demand.csv', index=False)
    t = pd.concat(t5s)
    t.to_csv('sc_table5.csv', index=False)
    t['short'] = t.name.str[-42:]
    main_specs = [s for s in SPECS if not s.startswith('x_')]
    print(t[t.spec.isin(main_specs)].pivot_table(index=['short', 'price', 'cheap'], columns='spec', values='own_elasticity', sort=False)[main_specs].round(2).to_string())

    # spec 5 decomposition: first stage, reduced form and the within-group fee and Z variation, by cheap group
    est = d[v2rows].reset_index(drop=True)
    out = []
    for g, sub in (('all', est), ('cheap', est[est.cheap == 1]), ('non-cheap', est[est.cheap == 0])):
        sub = sub.reset_index(drop=True)
        sub['delta'] = np.log(sub.shares) - np.log(1 - sub.groupby('market_ids').shares.transform('sum'))
        R = v2.resid(sub, ['prices', 'Z', 'delta'])
        p, z, y = R[:, 0], R[:, 1], R[:, 2]
        out.append(dict(group=g, N=len(sub), share_rows=len(sub) / len(est), funds=sub.product_ids.nunique(), mean_fee=float(sub.prices.mean()),
                        sd_fee_within=float(p.std()), sd_Z_within=float(z.std()), first_stage=float(z @ p / (z @ z)),
                        reduced_form=float(z @ y / (z @ z)), iv_slope=float((z @ y) / (z @ p)), weight_zp=float(z @ p)))
    sp = pd.DataFrame(out)
    sp['weight_in_pooled'] = sp.weight_zp / sp.weight_zp.iloc[1:].sum()
    sp.to_csv('sc_split.csv', index=False)
    print('\nspec 5 by group (each group residualized on its own fund FE, month FE and controls):')
    print(sp.round(4).to_string(index=False))
    # the same with COMMON month FE and controls (the pooled regression's own residuals), split by group
    est['delta'] = np.log(est.shares) - np.log(1 - est.groupby('market_ids').shares.transform('sum'))
    R = v2.resid(est, ['prices', 'Z', 'delta'])
    out = []
    for g, m in (('all', np.ones(len(est), bool)), ('cheap', (est.cheap == 1).to_numpy()), ('non-cheap', (est.cheap == 0).to_numpy())):
        p, z, y = R[m, 0], R[m, 1], R[m, 2]
        out.append(dict(group=g, N=int(m.sum()), zp=float(z @ p), zy=float(z @ y), iv_slope=float((z @ y) / (z @ p)), first_stage=float(z @ p / (z @ z))))
    sp2 = pd.DataFrame(out)
    sp2['weight_in_pooled'] = sp2.zp / sp2.zp.iloc[0]
    sp2.to_csv('sc_split_common_fe.csv', index=False)
    print('\nspec 5: pooled-regression residuals (common month FE and controls), contributions by group:')
    print(sp2.round(4).to_string(index=False))


if __name__ == '__main__':
    main()
