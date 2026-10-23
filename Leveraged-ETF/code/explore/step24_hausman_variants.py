"""Alternative Hausman instruments for the fee, built from the raw index file, and their tests.

Family = firm_f_old (firm_f where missing). Asset class from asset_class.classify (us_equity, intl_equity, bond,
allocation, real_asset). For fund j (family f, class a) in month t, over the family's OTHER-ASSET-CLASS funds that month:
  Z_orig      the data's BLP_IV_hausman_exp_ratio (family's other-INDEX funds, previous-month-AUM-weighted mean)
  Z_ac_aum    leave out the asset class, previous-month-AUM-weighted mean   (isolates the leave-out change)
  Z_ac_mean   leave out the asset class, equal-weighted mean
  Z_ac_med    leave out the asset class, median
  Z_ac_veh    leave out the asset class, median over funds of the same vehicle (ETF vs mutual fund)
  Z_ac_sc     leave out the asset class, median over funds of the same share class (ETF / institutional MF /
              retail MF / other MF; parsed from names as in step2_logit_screen.add_variables)
Tests, each instrument on the rows where it is defined (the original H on the same rows for comparison):
  (a) one-slope logit IV (Table 2 col 2): slope, first-stage F, avg own elasticity
  (b) main spec, entry tier 20th pct (instruments Z, Z x cheap): non-cheap and cheap slopes, SW F, Table 5 > 1
  (c) split sample, 20th pct: first-stage F, reduced-form t, IV slope for non-cheap and cheap funds separately
  (d) lead tests: within-fund xi_hat(t-k) from (a) on Z_t (Z net of fund FE, month FE, controls), k = 12, 24, 36
  (e) placebo: Z_ac_med and Z_ac_sc rebuilt from a randomly drawn OTHER family (20 derangements of families):
      first-stage F and IV slope pooled and by group. A family-cost instrument should beat its placebos clearly.

    python step24_hausman_variants.py        # from a folder holding the index CSV; writes step24_*.csv
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe

import common
from asset_class import classify_by_index
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, build, first_stage_f, summarize, CONTROLS, H
from tiers import RAW

pyblp.options.verbose = False
rng = np.random.default_rng(623543)

# ---------------- raw file: families, classes, vehicles, share classes ----------------
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old', 'firm_f',
                                'product_exp_ratio', 'product_L1_mtna', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna()].copy()
raw['fam'] = raw.firm_f_old.fillna(raw.firm_f)
raw = raw[raw.fam.notna()]
raw['ac'] = classify_by_index(raw)  # one class per tracked index
nm = raw.product_fund_name.fillna('').str.lower()
mf = raw.ETF_ind == 0
inst = mf & nm.str.contains(r'institutional|inst\b|class i\b|premier|select|class k\b|class z\b|class y\b|class r6|admiral')
retail = mf & ~inst & nm.str.contains(r'investor|retail|class a\b|class c\b|class r\b|class t\b|service|advisor')
raw['sc'] = np.select([~mf, inst, retail], ['etf', 'inst', 'retail'], 'mf_other')
raw['veh'] = np.where(mf, 'mf', 'etf')
CLASSES = sorted(raw.ac.unique())
print(f'raw rows {len(raw):,}; families {raw.fam.nunique()}; classes {raw.ac.value_counts(normalize=True).round(3).to_dict()}', flush=True)


def leave_class_table(stat, by=()):
    """(fam, month_t, *by, ac_target) -> statistic of the family's funds outside ac_target."""
    out = []
    for a in CLASSES:
        x = raw[raw.ac != a]
        keys = ['fam', 'month_t', *by]
        if stat == 'median':
            v = x.groupby(keys).product_exp_ratio.median()
        elif stat == 'mean':
            v = x.groupby(keys).product_exp_ratio.mean()
        else:  # previous-month-AUM-weighted mean
            x = x[x.product_L1_mtna.notna() & (x.product_L1_mtna > 0)]
            g = x.assign(w=x.product_L1_mtna, wx=x.product_L1_mtna * x.product_exp_ratio).groupby(keys)
            v = g.wx.sum() / g.w.sum()
        out.append(v.rename('z').reset_index().assign(ac=a))
    return pd.concat(out)


def leave_index_table(stat, same_class=False):
    """(fam, month_t, market_m_index) -> statistic of the family's funds tracking other indices (optionally same class)."""
    x = raw[raw.product_L1_mtna.notna() & (raw.product_L1_mtna > 0)] if stat == 'aum' else raw
    keys = ['fam', 'month_t'] + (['ac'] if same_class else [])
    x = x.assign(w=x.product_L1_mtna if stat == 'aum' else 1.0)
    x = x.assign(wx=x.w * x.product_exp_ratio)
    tot = x.groupby(keys)[['wx', 'w']].sum()
    own = x.groupby(keys + ['market_m_index'])[['wx', 'w']].sum()
    j = own.join(tot, rsuffix='_tot', on=keys)
    j['z'] = (j.wx_tot - j.wx) / (j.w_tot - j.w)
    return j.z.where(np.isfinite(j.z)).dropna().reset_index()[keys + ['market_m_index', 'z']]


def leave_index_median():
    """median fee of the family's funds tracking other indices (exact, by looping over family-months)."""
    rows = []
    for (f, t), g in raw.groupby(['fam', 'month_t']):
        if g.market_m_index.nunique() < 2:
            continue
        v = g.product_exp_ratio.to_numpy(); ix = g.market_m_index.to_numpy()
        for m in np.unique(ix):
            rows.append((f, t, m, float(np.median(v[ix != m]))))
    return pd.DataFrame(rows, columns=['fam', 'month_t', 'market_m_index', 'z'])


tables = {'Z_ac_aum': (leave_class_table('aum'), ()), 'Z_ac_mean': (leave_class_table('mean'), ()),
          'Z_ac_med': (leave_class_table('median'), ()), 'Z_ac_veh': (leave_class_table('median', ('veh',)), ('veh',)),
          'Z_ac_sc': (leave_class_table('median', ('sc',)), ('sc',))}
fund = raw[['product_j', 'month_t', 'fam', 'ac', 'veh', 'sc', 'market_m_index']]
for name, (tab, by) in tables.items():
    fund = fund.merge(tab.rename(columns={'z': name}), on=['fam', 'month_t', 'ac', *by], how='left')
idx_tables = {'Z_idx_aum': leave_index_table('aum'), 'Z_idx_med': leave_index_median(),
              'Z_idx_sameac_aum': leave_index_table('aum', same_class=True)}
for name, tab in idx_tables.items():
    on = ['fam', 'month_t', 'market_m_index'] + (['ac'] if 'ac' in tab.columns else [])
    fund = fund.merge(tab.rename(columns={'z': name}), on=on, how='left')

# ---------------- estimation sample ----------------
d = add_variables(common.load('index'))
funds = top15(d)
d = d.drop(columns=[c for c in ('fam', 'ac', 'veh', 'sc') if c in d]).merge(fund.drop(columns='market_m_index').rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
d['Z_orig'] = d[H]
d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))
ZS = ['Z_orig', 'Z_idx_aum', 'Z_idx_med', 'Z_idx_sameac_aum', 'Z_ac_aum', 'Z_ac_mean', 'Z_ac_med', 'Z_ac_veh', 'Z_ac_sc']
print('coverage in estimation sample:', {z: round(float(d[z].notna().mean()), 3) for z in ZS}, flush=True)


def partial(dd, cols):
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    M = alg.residualize(dd[cols].to_numpy(float))
    return pd.DataFrame(M - W @ np.linalg.lstsq(W, M, rcond=None)[0], columns=cols, index=dd.index)


def coef(y, x, g):
    b = float((x @ y) / (x @ x))
    u = y - b * x
    return b, float(np.sqrt(((pd.Series(x * u).groupby(g).sum()) ** 2).sum()) / (x @ x))


def iv1(y, p, z, g):
    b = float((z @ y) / (z @ p))
    u = y - b * p
    return b, float(np.sqrt(((pd.Series(z * u).groupby(g).sum()) ** 2).sum()) / abs(z @ p))


def manual(dd, z):
    """pooled and split (20th pct) first stage F / reduced-form t / IV, group-specific FE in the split."""
    out = {}
    for grp, mask in (('all', np.ones(len(dd), bool)), ('noncheap', (dd.raw20 == 0).to_numpy()), ('cheap', (dd.raw20 == 1).to_numpy())):
        s = dd[mask]
        R = partial(s, ['delta', 'prices', z])
        g = s.market_ids.to_numpy()
        y, p, h = R.delta.to_numpy(), R.prices.to_numpy(), R[z].to_numpy()
        fs, fse = coef(p, h, g)
        rf, rse = coef(y, h, g)
        b, se = iv1(y, p, h, g)
        out.update({f'{grp}_fsF': (fs / fse) ** 2, f'{grp}_fs': fs, f'{grp}_rf_t': rf / rse, f'{grp}_iv': b, f'{grp}_iv_se': se})
    return out


def logit(dd, z, inter=None):
    dd = dd.reset_index(drop=True).copy()
    zz = dd[z].to_numpy(float)
    dd = dd.drop(columns=[c for c in dd.columns if c.startswith('demand_instruments')])
    spec = dict(tier='A', z=[inter] if inter else [])
    dd['demand_instruments0'] = zz
    dd2, formula, endog, excl, exog = build(dd, spec)  # builds demand_instruments1 = Z x cheap from demand_instruments0
    res = pyblp.Problem(pyblp.Formulation(formula, absorb='C(product_ids) + C(market_ids)'), dd2).solve(se_type='clustered')
    f = first_stage_f(dd2, endog, excl, exog)
    return dd2, res, f


def lead_tests(dd, xi, z):
    dd = dd.reset_index(drop=True).assign(xi=xi)
    R = partial(dd, [z])
    dd['zt'] = R[z].to_numpy()
    out = {}
    for k in (12, 24, 36):
        lag = dd[['product_ids', 'month_key', 'xi']].assign(month_key=dd.month_key + k)
        m = dd[['product_ids', 'month_key', 'zt', 'market_ids']].merge(lag, on=['product_ids', 'month_key'])
        y = (m.xi - m.groupby('product_ids').xi.transform('mean')).to_numpy()
        x = (m.zt - m.groupby('product_ids').zt.transform('mean')).to_numpy()
        b, se = coef(y, x, m.market_ids.to_numpy())
        out[f'lead{k}_t'] = b / se
    return out


rows, fund_rows = [], []
for z in ZS:
    s = d[d[z].notna()].copy()
    for inst_name in ([z] if z == 'Z_orig' else [z, 'Z_orig']):
        tag = f'{z} | instrument {inst_name}'
        row = dict(variant=z, instrument=inst_name, N=len(s), coverage=len(s) / len(d),
                   corr_with_H=float(np.corrcoef(s[z], s.Z_orig)[0, 1]))
        dd, res, f = logit(s, inst_name)
        row.update(one_slope=float(res.beta[0, 0]), one_slope_se=float(res.beta_se[0, 0]), one_slope_F=f['prices'],
                   one_slope_avg_e=float(res.extract_diagonal_means(res.compute_elasticities()).flatten().mean()))
        row.update(lead_tests(s, res.xi.flatten(), inst_name))
        dd, res, f = logit(s, inst_name, 'raw20')
        b = dict(zip(res.beta_labels, res.beta.flatten())); se = dict(zip(res.beta_labels, res.beta_se.flatten()))
        kx = next(k for k in b if 'raw20' in k)
        r2, fr = summarize(tag, dict(tier='A'), dd, res, funds, [], f, {})
        e = res.extract_diagonals(res.compute_elasticities()).flatten()
        row.update(main_rest=b['prices'], main_rest_se=se['prices'], main_cheap_total=b['prices'] + b[kx],
                   main_cheap_x_se=se[kx], main_minF=min(f.values()), main_avg_e=r2['avg_own_elasticity'],
                   main_share_pos=float((e > 0).mean()), main_negmc=r2['share_neg_mc_bertrand_firm'],
                   main_n15=sum(abs(x['e_last']) > 1 for x in fr))
        fund_rows += fr
        row.update(manual(s, inst_name))
        rows.append(row)
        print(f"{tag:40s} N {row['N']:6d} corrH {row['corr_with_H']:.2f} | one slope {row['one_slope']:6.2f} ({row['one_slope_se']:.2f}) F {row['one_slope_F']:6.1f} | "
              f"main rest {row['main_rest']:6.2f} ({row['main_rest_se']:.2f}) cheap {row['main_cheap_total']:7.2f} minF {row['main_minF']:5.1f} 15>1 {row['main_n15']} e>0 {row['main_share_pos']:.2f} | "
              f"split noncheap F {row['noncheap_fsF']:5.1f} iv {row['noncheap_iv']:6.2f} ({row['noncheap_iv_se']:.2f}) | cheap F {row['cheap_fsF']:5.1f} iv {row['cheap_iv']:7.2f} | "
              f"lead t 12/24/36 {row['lead12_t']:.1f}/{row['lead24_t']:.1f}/{row['lead36_t']:.1f}", flush=True)
pd.DataFrame(rows).to_csv('step24_hausman_variants.csv', index=False)
pd.DataFrame(fund_rows).to_csv('step24_funds.csv', index=False)

# ---------------- placebo: another family's fees ----------------
# Each family is mapped (fixed over time) to a random partner among the 30 broadest families (most fund-months in at
# least 4 classes), never itself; the fund's instrument is then rebuilt from the partner's funds.
breadth = raw.groupby('fam').agg(n=('product_j', 'size'), k=('ac', 'nunique'))
pool = breadth[breadth.k >= 4].sort_values('n', ascending=False).index[:30].to_numpy()
fams = d.fam.dropna().unique()
idx_aum = idx_tables['Z_idx_aum']
plac = []
for rep in range(20):
    mp = {f: rng.choice(pool[pool != f]) for f in fams}
    for z in ('Z_idx_aum', 'Z_ac_med', 'Z_ac_sc'):
        s0 = d[['product_ids', 'month_t', 'fam', 'ac', 'sc', 'veh', 'market_m_index']].copy()
        s0['fam'] = s0.fam.map(mp)
        if z == 'Z_idx_aum':  # partner's AUM-weighted mean over all its funds not tracking the fund's index
            tab = raw[raw.product_L1_mtna > 0].assign(wx=lambda x: x.product_L1_mtna * x.product_exp_ratio)
            tot = tab.groupby(['fam', 'month_t'])[['wx', 'product_L1_mtna']].sum()
            own = tab.groupby(['fam', 'month_t', 'market_m_index'])[['wx', 'product_L1_mtna']].sum()
            s1 = s0.merge(tot.reset_index(), on=['fam', 'month_t'], how='left').merge(
                own.reset_index().rename(columns={'wx': 'wx_o', 'product_L1_mtna': 'w_o'}), on=['fam', 'month_t', 'market_m_index'], how='left')
            Pv = ((s1.wx - s1.wx_o.fillna(0)) / (s1.product_L1_mtna - s1.w_o.fillna(0))).to_numpy()
        else:
            tab, by = tables[z]
            Pv = s0.merge(tab.rename(columns={'z': 'P'}), on=['fam', 'month_t', 'ac', *by], how='left').P.to_numpy()
        dd = d.assign(P=Pv)
        dd = dd[np.isfinite(dd.P)]
        r = dict(rep=rep, variant=z, N=len(dd), corr_with_H=float(np.corrcoef(dd.P, dd.Z_orig)[0, 1]))
        r.update(manual(dd, 'P'))
        plac.append(r)
    print(f'placebo {rep} done', flush=True)
P = pd.DataFrame(plac)
P.to_csv('step24_placebo.csv', index=False)
pd.set_option('display.width', 250)
cols = ['N', 'all_fsF', 'all_iv', 'noncheap_fsF', 'noncheap_iv', 'cheap_fsF', 'cheap_iv']
for z in ('Z_idx_aum', 'Z_ac_med', 'Z_ac_sc'):
    q = P[P.variant == z][cols].quantile([0.1, 0.5, 0.9]).round(2)
    print(f'\nplacebo {z} (partner family), quantiles over 20 draws:\n{q.to_string()}', flush=True)
