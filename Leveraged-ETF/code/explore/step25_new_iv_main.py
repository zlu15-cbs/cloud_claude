"""Full results for the recommended spec: logit IV with expense ratio x cheap (entry tier), instrumented by the
share-class-matched Hausman IV (median fee of the same family's same-share-class funds outside the fund's asset class).

Sample: Table 2 Panel A fund-months with a family id (firm_f_old) and the instrument defined (97,429).
Fixed effects: fund + month (as Table 2) and fund + month x asset class. SE clustered by month throughout.
Outputs:
  step25_table.csv      columns (1) logit OLS, (2) logit IV no interaction, (3) logit IV with cheap (main), each for
                        both FE sets; also (2p)/(3p) with the paper's Hausman IV on the same rows
  step25_cutoffs.csv    main model at the 10th / 15th / 20th percentiles, both FE sets
  step25_dropfirm.csv   main model dropping Vanguard / BlackRock / State Street (fund + month FE)
  step25_split.csv      split-sample first stage / reduced form / IV by cheap status, cutoffs x FE sets
  step25_leads.csv      lead tests on the main model's residual (k = 12, 24, 36)
  step25_funds.csv      the 15 Table 5 funds, every model

    python step25_new_iv_main.py      # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd
import pyblp
import pyhdfe
from scipy import stats

import common
from asset_class import classify_by_index
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables, summarize, CONTROLS, H
from tiers import RAW

pyblp.options.verbose = False

raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                'product_exp_ratio', 'ETF_ind', 'product_fund_name'])
raw = raw[raw.product_exp_ratio.notna() & raw.firm_f_old.notna()].copy()
raw['fam'] = raw.firm_f_old
raw['ac'] = classify_by_index(raw)
nm = raw.product_fund_name.fillna('').str.lower()
mf = raw.ETF_ind == 0
inst = mf & nm.str.contains(r'institutional|inst\b|class i\b|premier|select|class k\b|class z\b|class y\b|class r6|admiral')
retail = mf & ~inst & nm.str.contains(r'investor|retail|class a\b|class c\b|class r\b|class t\b|service|advisor')
raw['sc'] = np.select([~mf, inst, retail], ['etf', 'inst', 'retail'], 'mf_other')
tab = pd.concat([raw[raw.ac != a].groupby(['fam', 'month_t', 'sc']).product_exp_ratio.median().rename('Z').reset_index().assign(ac=a)
                 for a in sorted(raw.ac.unique())])
tab_n = pd.concat([raw[raw.ac != a].groupby(['fam', 'month_t', 'sc']).size().rename('Z_n').reset_index().assign(ac=a)
                   for a in sorted(raw.ac.unique())])

d0 = add_variables(common.load('index'))
N_TABLE2 = len(d0)
funds = top15(d0)
d = d0.merge(raw[['product_j', 'month_t', 'fam', 'ac', 'sc']].rename(columns={'product_j': 'product_ids'}),
             on=['product_ids', 'month_t'], how='inner')
d = d.merge(tab, on=['fam', 'month_t', 'ac', 'sc'], how='left').merge(tab_n, on=['fam', 'month_t', 'ac', 'sc'], how='left')
d = d[d.Z.notna()].reset_index(drop=True)
d['Z_paper'] = d[H]
d['mkt_ac'] = d.market_ids.astype(str) + '_' + d.ac
d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))
print(f'Table 2 sample {N_TABLE2:,}; with a family id and the instrument defined {len(d):,} ({len(d) / N_TABLE2:.3f}); '
      f'funds {d.product_ids.nunique()} of {d0.product_ids.nunique()}; Table 5 funds kept {funds.product_ids.isin(d.product_ids).sum()} of 15', flush=True)
print('instrument: median number of funds behind each value', float(d.Z_n.median()), '| share of values from a single fund',
      round(float((d.Z_n == 1).mean()), 3), '| corr with the paper IV', round(float(np.corrcoef(d.Z, d.Z_paper)[0, 1]), 3), flush=True)
print('asset classes (fund-months):', d.ac.value_counts(normalize=True).round(3).to_dict(), '| share classes:',
      d.sc.value_counts(normalize=True).round(3).to_dict(), flush=True)
FE = {'fund + month': 'market_ids', 'fund + month x asset class': 'mkt_ac'}


def resid(dd, cols, tfe):
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd[tfe])[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    M = alg.residualize(dd[cols].to_numpy(float))
    return M - W @ np.linalg.lstsq(W, M, rcond=None)[0]


def cl_wald(y, X, g):
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    u = y - X @ b
    sc = pd.DataFrame(X * u[:, None]).groupby(g).sum().to_numpy()
    V = XtXi @ (sc.T @ sc) @ XtXi
    return float(b @ np.linalg.pinv(V) @ b)


def sw_f(dd, endog, excl, tfe):
    """Sanderson-Windmeijer first-stage F, FE = fund + tfe, clustered by month."""
    X = resid(dd, endog, tfe)
    Z = resid(dd, excl, tfe)
    g = dd.market_ids.to_numpy()
    k, L = len(endog), len(excl)
    out = {}
    for j, name in enumerate(endog):
        x = X[:, j]
        if k > 1:
            Xo = np.delete(X, j, axis=1)
            Pz = Z @ np.linalg.lstsq(Z, Xo, rcond=None)[0]
            x = x - Xo @ np.linalg.lstsq(Pz, x, rcond=None)[0]
        out[name] = cl_wald(x, Z, g) / (L - k + 1)
    return out


def model(dd, tfe, z=None, cheap=None, label=''):
    """z=None -> OLS (price is its own instrument)."""
    dd = dd.reset_index(drop=True).copy()
    dd = dd.drop(columns=[c for c in dd.columns if c.startswith('demand_instruments')])
    zz = dd.prices.to_numpy(float) if z is None else dd[z].to_numpy(float)
    dd['demand_instruments0'] = zz
    terms, endog, excl = ['prices'], ['prices'], ['demand_instruments0']
    if cheap:
        dd['px'] = dd.prices * dd[cheap]
        dd['demand_instruments1'] = zz * dd[cheap]
        terms.append(f'I(prices*{cheap})'); endog.append('px'); excl.append('demand_instruments1')
    res = pyblp.Problem(pyblp.Formulation(' + '.join(terms + CONTROLS), absorb=f'C(product_ids) + C({tfe})'), dd).solve(se_type='clustered')
    f = sw_f(dd, endog, excl, tfe) if z is not None else {}
    row, fr = summarize(label, dict(tier='A'), dd, res, funds[funds.product_ids.isin(dd.product_ids)], [], f, {})
    e = res.extract_diagonals(res.compute_elasticities()).flatten()
    row.update(share_pos_e=float((e > 0).mean()), min_F=min(f.values()) if f else np.nan,
               n15_gt1=sum(abs(q['e_last']) > 1 for q in fr), n15=len(fr))
    b = dict(zip(res.beta_labels, res.beta.flatten()))
    if cheap:
        kx = next(k for k in b if cheap in k)
        row['cheap_total'] = b['prices'] + b[kx]
        row['b_cheap_x'], row['se_cheap_x'] = row.pop(f'b[{kx}]'), row.pop(f'se[{kx}]')
    for r in fr:
        r['model'] = label
    return row, fr, res, dd


table, fund_rows = [], []
for fe_name, tfe in FE.items():
    specs = [('(1) logit OLS', None, None), ('(2) logit IV', 'Z', None), ('(3) logit IV x cheap (main)', 'Z', 'raw20'),
             ('(2p) paper IV, same rows', 'Z_paper', None), ('(3p) paper IV x cheap, same rows', 'Z_paper', 'raw20')]
    for col, z, cheap in specs:
        label = f'{fe_name} | {col}'
        row, fr, res, dd = model(d, tfe, z, cheap, label)
        row.update(fe=fe_name, column=col)
        table.append(row); fund_rows += fr
        print(f"{label:62s} price {row['b[prices]']:7.2f} ({row['se[prices]']:.2f})"
              + (f" | x cheap {row['b_cheap_x']:7.2f} ({row['se_cheap_x']:.2f}) total {row['cheap_total']:7.2f}" if cheap else '')
              + f" | min F {row['min_F']:.1f} | avg e {row['avg_own_elasticity']:.2f} | |e|>1 {row['share_abs_e_gt1']:.2f} | e>0 {row['share_pos_e']:.3f}"
              f" | negMC {row['share_neg_mc_bertrand_firm']:.2f} | 15>1 {row['n15_gt1']}/{row['n15']}", flush=True)
        if col.startswith('(3) '):  # lead tests on the main model's residual
            dd = dd.assign(xi=res.xi.flatten())
            zt = resid(dd, ['Z'], tfe)[:, 0]
            dd['zt'] = zt
            lt = {}
            for k in (12, 24, 36):
                lag = dd[['product_ids', 'month_key', 'xi']].assign(month_key=dd.month_key + k)
                m = dd[['product_ids', 'month_key', 'zt', 'market_ids']].merge(lag, on=['product_ids', 'month_key'])
                y = (m.xi - m.groupby('product_ids').xi.transform('mean')).to_numpy()
                x = (m.zt - m.groupby('product_ids').zt.transform('mean')).to_numpy()
                bb = (x @ y) / (x @ x); u = y - bb * x
                se = np.sqrt(((pd.Series(x * u).groupby(m.market_ids.to_numpy()).sum()) ** 2).sum()) / (x @ x)
                lt[f'lead{k}_t'] = float(bb / se)
            print(f'   lead tests (main model residual): {lt}', flush=True)
            pd.DataFrame([dict(fe=fe_name, **lt)]).to_csv(f'step25_leads_{tfe}.csv', index=False)
pd.DataFrame(table).to_csv('step25_table.csv', index=False)

# cutoffs
cut = []
for fe_name, tfe in FE.items():
    for q in (10, 15, 20):
        row, fr, _, _ = model(d, tfe, 'Z', f'raw{q}', f'{fe_name} | cutoff {q}')
        row.update(fe=fe_name, cutoff=q, share_funds_cheap=float(d.groupby('product_ids')[f'raw{q}'].first().mean()))
        cut.append(row); fund_rows += fr
        print(f"cutoff {q} | {fe_name:28s} rest {row['b[prices]']:7.2f} ({row['se[prices]']:.2f}) | x cheap {row['b_cheap_x']:7.2f} ({row['se_cheap_x']:.2f}) "
              f"total {row['cheap_total']:7.2f} | min F {row['min_F']:.1f} | avg e {row['avg_own_elasticity']:.2f} | e>0 {row['share_pos_e']:.3f} | "
              f"negMC {row['share_neg_mc_bertrand_firm']:.2f} | 15>1 {row['n15_gt1']}/{row['n15']}", flush=True)
pd.DataFrame(cut).to_csv('step25_cutoffs.csv', index=False)

# drop one big firm (fund + month FE, 20th pct)
drop = []
for firm in ('Vanguard', 'BlackRock', 'State Street Global Advisors'):
    s = d[d.firm_ids != firm]
    row, _, _, _ = model(s, 'market_ids', 'Z', 'raw20', f'drop {firm}')
    row.update(dropped=firm)
    drop.append(row)
    print(f"drop {firm:30s} N {len(s):,} rest {row['b[prices]']:7.2f} ({row['se[prices]']:.2f}) | cheap total {row['cheap_total']:7.2f} | min F {row['min_F']:.1f} | e>0 {row['share_pos_e']:.3f}", flush=True)
pd.DataFrame(drop).to_csv('step25_dropfirm.csv', index=False)

# split sample
split = []
for fe_name, tfe in FE.items():
    for q in (10, 15, 20):
        for grp, mask in (('not cheap', d[f'raw{q}'] == 0), ('cheap', d[f'raw{q}'] == 1)):
            s = d[mask].reset_index(drop=True)
            R = resid(s, ['delta', 'prices', 'Z', 'Z_paper'], tfe)
            g = s.market_ids.to_numpy()
            y, p = R[:, 0], R[:, 1]
            for k, zname in ((2, 'new'), (3, 'paper')):
                h = R[:, k]
                fs = (h @ p) / (h @ h); u = p - fs * h
                fse = np.sqrt(((pd.Series(h * u).groupby(g).sum()) ** 2).sum()) / (h @ h)
                rf = (h @ y) / (h @ h); u = y - rf * h
                rse = np.sqrt(((pd.Series(h * u).groupby(g).sum()) ** 2).sum()) / (h @ h)
                iv = (h @ y) / (h @ p); u = y - iv * p
                ivse = np.sqrt(((pd.Series(h * u).groupby(g).sum()) ** 2).sum()) / abs(h @ p)
                split.append(dict(fe=fe_name, cutoff=q, group=grp, instrument=zname, funds=s.product_ids.nunique(), N=len(s),
                                  fs=fs, fs_F=(fs / fse) ** 2, rf=rf, rf_t=rf / rse, iv=iv, iv_se=ivse))
S = pd.DataFrame(split)
S.to_csv('step25_split.csv', index=False)
pd.set_option('display.width', 250)
print(S.round(3).to_string(index=False))
pd.DataFrame(fund_rows).to_csv('step25_funds.csv', index=False)
