"""Do the Hausman instruments survive asset-class x month fixed effects (which absorb asset-class-wide fee trends,
leaving only family-specific variation)? Family-id rows only (as in step24).

Instruments: Z_orig (the data's Hausman IV) and Z_ac_sc (median fee of the family's same-share-class funds outside the
fund's asset class). Fixed effects: fund + month (as in Table 2) versus fund + month x asset class.
For each: one-slope logit IV, main spec (entry tier 20th pct), split-sample first stage / IV for cheap and non-cheap
funds, lead tests (k = 12, 24, 36); and the partner-family placebo (20 draws) under each FE set.

    python step24c_class_month_fe.py      # from a folder holding the index CSV; writes step24c_*.csv
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe

import common
from asset_class import classify_by_index
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, first_stage_f, summarize, CONTROLS, H
from tiers import RAW

pyblp.options.verbose = False
rng = np.random.default_rng(623543)

raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                'product_exp_ratio', 'product_L1_mtna', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna() & raw.firm_f_old.notna()].copy()
raw['fam'] = raw.firm_f_old
raw['ac'] = classify_by_index(raw)
nm = raw.product_fund_name.fillna('').str.lower()
mf = raw.ETF_ind == 0
inst = mf & nm.str.contains(r'institutional|inst\b|class i\b|premier|select|class k\b|class z\b|class y\b|class r6|admiral')
retail = mf & ~inst & nm.str.contains(r'investor|retail|class a\b|class c\b|class r\b|class t\b|service|advisor')
raw['sc'] = np.select([~mf, inst, retail], ['etf', 'inst', 'retail'], 'mf_other')
CLASSES = sorted(raw.ac.unique())
tab_sc = pd.concat([raw[raw.ac != a].groupby(['fam', 'month_t', 'sc']).product_exp_ratio.median().rename('z').reset_index().assign(ac=a)
                    for a in CLASSES])
x = raw[raw.product_L1_mtna > 0].assign(wx=lambda q: q.product_L1_mtna * q.product_exp_ratio)
tot = x.groupby(['fam', 'month_t'])[['wx', 'product_L1_mtna']].sum().reset_index()
own = x.groupby(['fam', 'month_t', 'market_m_index'])[['wx', 'product_L1_mtna']].sum().reset_index().rename(columns={'wx': 'wx_o', 'product_L1_mtna': 'w_o'})

d = add_variables(common.load('index'))
funds = top15(d)
d = d.merge(raw[['product_j', 'month_t', 'fam', 'ac', 'sc']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='inner')
d = d.merge(tab_sc.rename(columns={'z': 'Z_ac_sc'}), on=['fam', 'month_t', 'ac', 'sc'], how='left')
d = d[d.Z_ac_sc.notna()].reset_index(drop=True)
d['Z_orig'] = d[H]
d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))
d['mkt_ac'] = d.market_ids.astype(str) + '_' + d.ac
print(f'N {len(d):,} (family-id rows with Z_ac_sc defined); classes {d.ac.value_counts(normalize=True).round(3).to_dict()}', flush=True)
FE = {'month': 'market_ids', 'month x class': 'mkt_ac'}


def partial(dd, cols, tfe):
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd[tfe])[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    M = alg.residualize(dd[cols].to_numpy(float))
    return pd.DataFrame(M - W @ np.linalg.lstsq(W, M, rcond=None)[0], columns=cols, index=dd.index)


def coef(y, x, g):
    b = float((x @ y) / (x @ x)); u = y - b * x
    return b, float(np.sqrt(((pd.Series(x * u).groupby(g).sum()) ** 2).sum()) / (x @ x))


def iv1(y, p, z, g):
    b = float((z @ y) / (z @ p)); u = y - b * p
    return b, float(np.sqrt(((pd.Series(z * u).groupby(g).sum()) ** 2).sum()) / abs(z @ p))


def manual(dd, z, tfe):
    out = {}
    for grp, mask in (('all', np.ones(len(dd), bool)), ('noncheap', (dd.raw20 == 0).to_numpy()), ('cheap', (dd.raw20 == 1).to_numpy())):
        s = dd[mask]
        R = partial(s, ['delta', 'prices', z], tfe)
        g = s.market_ids.to_numpy()
        y, p, h = R.delta.to_numpy(), R.prices.to_numpy(), R[z].to_numpy()
        fs, fse = coef(p, h, g); rf, rse = coef(y, h, g); b, se = iv1(y, p, h, g)
        out.update({f'{grp}_fsF': (fs / fse) ** 2, f'{grp}_rf_t': rf / rse, f'{grp}_iv': b, f'{grp}_iv_se': se})
    return out


def logit(dd, z, tfe, cheap=None):
    dd = dd.reset_index(drop=True).copy()
    zz = dd[z].to_numpy(float)
    dd = dd.drop(columns=[c for c in dd.columns if c.startswith('demand_instruments')])
    dd['demand_instruments0'] = zz
    terms, endog, excl = ['prices'], ['prices'], ['demand_instruments0']
    if cheap:
        dd['demand_instruments1'] = zz * dd[cheap]; dd['px'] = dd.prices * dd[cheap]
        terms.append(f'I(prices*{cheap})'); endog.append('px'); excl.append('demand_instruments1')
    formula = ' + '.join(terms + CONTROLS)
    res = pyblp.Problem(pyblp.Formulation(formula, absorb=f'C(product_ids) + C({tfe})'), dd).solve(se_type='clustered')
    ids = dd.copy(); ids['market_ids_orig'] = ids.market_ids
    f = first_stage_f(dd.assign(market_ids=dd[tfe]), endog, excl, CONTROLS)
    return dd, res, f


def leads(dd, xi, z, tfe):
    dd = dd.reset_index(drop=True).assign(xi=xi)
    dd['zt'] = partial(dd, [z], tfe)[z].to_numpy()
    out = {}
    for k in (12, 24, 36):
        lag = dd[['product_ids', 'month_key', 'xi']].assign(month_key=dd.month_key + k)
        m = dd[['product_ids', 'month_key', 'zt', 'market_ids']].merge(lag, on=['product_ids', 'month_key'])
        y = (m.xi - m.groupby('product_ids').xi.transform('mean')).to_numpy()
        xx = (m.zt - m.groupby('product_ids').zt.transform('mean')).to_numpy()
        b, se = coef(y, xx, m.market_ids.to_numpy())
        out[f'lead{k}_t'] = b / se
    return out


rows = []
for fe_name, tfe in FE.items():
    for z in ('Z_orig', 'Z_ac_sc'):
        row = dict(fe=fe_name, instrument=z, N=len(d))
        dd, res, f = logit(d, z, tfe)
        row.update(one_slope=float(res.beta[0, 0]), one_slope_se=float(res.beta_se[0, 0]), one_slope_F=f['prices'])
        row.update(leads(d, res.xi.flatten(), z, tfe))
        dd, res, f = logit(d, z, tfe, 'raw20')
        b = dict(zip(res.beta_labels, res.beta.flatten())); se = dict(zip(res.beta_labels, res.beta_se.flatten()))
        kx = next(k for k in b if 'raw20' in k)
        r2, fr = summarize(f'{fe_name}|{z}', dict(tier='A'), dd, res, funds[funds.product_ids.isin(dd.product_ids)], [], f, {})
        e = res.extract_diagonals(res.compute_elasticities()).flatten()
        row.update(main_rest=b['prices'], main_rest_se=se['prices'], main_cheap_total=b['prices'] + b[kx], main_cheap_x_se=se[kx],
                   main_minF=min(f.values()), main_avg_e=r2['avg_own_elasticity'], main_share_pos=float((e > 0).mean()),
                   main_n15=sum(abs(q['e_last']) > 1 for q in fr), main_n15_of=len(fr))
        row.update(manual(d, z, tfe))
        rows.append(row)
        print(f"FE {fe_name:13s} {z:7s} | one slope {row['one_slope']:6.2f} ({row['one_slope_se']:.2f}) F {row['one_slope_F']:6.1f} | main rest {row['main_rest']:6.2f} ({row['main_rest_se']:.2f}) "
              f"cheap {row['main_cheap_total']:7.2f} minF {row['main_minF']:6.1f} e>0 {row['main_share_pos']:.2f} 15>1 {row['main_n15']}/{row['main_n15_of']} | "
              f"split noncheap F {row['noncheap_fsF']:6.1f} iv {row['noncheap_iv']:6.2f} ({row['noncheap_iv_se']:.2f}) | cheap F {row['cheap_fsF']:6.1f} iv {row['cheap_iv']:7.2f} ({row['cheap_iv_se']:.2f}) | "
              f"lead t {row['lead12_t']:.1f}/{row['lead24_t']:.1f}/{row['lead36_t']:.1f}", flush=True)
pd.DataFrame(rows).to_csv('step24c_class_month_fe.csv', index=False)

# placebo under both FE sets
breadth = raw.groupby('fam').agg(n=('product_j', 'size'), k=('ac', 'nunique'))
pool = breadth[breadth.k >= 4].sort_values('n', ascending=False).index[:30].to_numpy()
fams = d.fam.unique()
plac = []
for rep in range(20):
    mp = {f: rng.choice(pool[pool != f]) for f in fams}
    s0 = d[['product_ids', 'month_t', 'fam', 'ac', 'sc', 'market_m_index']].copy()
    s0['fam'] = s0.fam.map(mp)
    p_sc = s0.merge(tab_sc.rename(columns={'z': 'P'}), on=['fam', 'month_t', 'ac', 'sc'], how='left').P.to_numpy()
    s1 = s0.merge(tot, on=['fam', 'month_t'], how='left').merge(own, on=['fam', 'month_t', 'market_m_index'], how='left')
    p_or = ((s1.wx - s1.wx_o.fillna(0)) / (s1.product_L1_mtna - s1.w_o.fillna(0))).to_numpy()
    for z, P in (('Z_orig', p_or), ('Z_ac_sc', p_sc)):
        dd = d.assign(P=P)
        dd = dd[np.isfinite(dd.P)].reset_index(drop=True)
        for fe_name, tfe in FE.items():
            r = dict(rep=rep, instrument=z, fe=fe_name, N=len(dd))
            r.update(manual(dd, 'P', tfe))
            plac.append(r)
    print(f'placebo {rep} done', flush=True)
P = pd.DataFrame(plac)
P.to_csv('step24c_placebo.csv', index=False)
pd.set_option('display.width', 250)
cols = ['N', 'all_fsF', 'all_iv', 'noncheap_fsF', 'noncheap_iv', 'cheap_fsF', 'cheap_iv']
for z in ('Z_orig', 'Z_ac_sc'):
    for fe_name in FE:
        q = P[(P.instrument == z) & (P.fe == fe_name)][cols].quantile([0.1, 0.5, 0.9]).round(2)
        print(f'\nplacebo {z}, FE {fe_name}:\n{q.to_string()}', flush=True)
