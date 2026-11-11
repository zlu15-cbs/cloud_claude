"""V2 robustness grid: share-type source, exclusion classes, donor pool and the cheap indicator.

Model throughout: price + price x cheap, instruments Z and Z x cheap, fund and month FE, money market funds dropped.
Z = unweighted median fee of same-family (firm_f_old), same-share-type donors in another exposure class, same month.
  types   csv    V2 as reported: ETF from the index CSV's ETF_ind (the build flags a fund as an ETF if CRSP's et_flag is F
                 in any quarter, OR its name contains "ETF", OR its name contains ishares / spdr / holdrs / streettracks /
                 exchange traded); mutual funds split by CRSP inst_fund / retail_fund
          crsp   ETF only if CRSP's et_flag is F in some quarter; the rest as above
          danny  Danny's approved share types (classified_donors.csv, share_type)
  excl    lipper6  other Lipper-6 asset class (V2)          cat10  other category10 class (Danny's labels; unknown dropped)
  donors  csv      fund-months in the index CSV (V2)         source every fund-month of the source panel with a fee
  cheap   csv      gene_idx from the index CSV (V2)          source the same rule on Danny's source panel, using only fees CRSP reports, with the entry month taken as
                   the fund's first such month on or after January 2005 (START)
    SC_DATA=... SC_SOURCE=.../index_funds_preprocess_oct2026.csv SC_DANNY=.../hausman-robustness-v1/passive python sc_v2_robust.py
Writes sc_v2_robust.csv and sc_v2_robust_table5.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
from sc_build import CACHE, CRSP, DATA, PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402
from sc_v2_source_donors import downstream  # noqa: E402

pyblp.options.verbose = False
SOURCE = os.environ.get('SC_SOURCE', f'{DATA}/danny/index_funds_preprocess_oct2026.csv')
DANNY = os.environ.get('SC_DANNY', f'{DATA}/danny_zip/x/V2_comparison_handoff/outputs/hausman-robustness-v1/passive')
CSVP = f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv'

GRID = [  # label, types, excl, donors, cheap
    ('V2 (cheap classified from 2005, 20th percentile)', 'csv', 'lipper6', 'csv', 'source_obs'),
    ('cutoff 15th percentile', 'csv', 'lipper6', 'csv', 'source_obs_q15'),
    ('cutoff 25th percentile', 'csv', 'lipper6', 'csv', 'source_obs_q25'),
    ('donors from the source panel', 'csv', 'lipper6', 'source', 'source_obs'),
    ('cheap classified from 1993 (the source panel\'s first month)', 'csv', 'lipper6', 'csv', 'source_obs_1993'),
    ('cheap from the index CSV (V2 as first sent to Danny)', 'csv', 'lipper6', 'csv', 'csv'),
    ('category10 exclusion', 'csv', 'cat10', 'csv', 'source_obs'),
]
FILECHECK = [  # one file for both the cheap indicator and the donors, at each cutoff (SC_GRID=filecheck)
    (f'{f} for cheap and donors, cutoff {q}%', 'csv', 'lipper6', dn_, f'{c}{q}')
    for q in (15, 20, 25) for f, dn_, c in (('source panel', 'source', 'srcboth_q'), ('index CSV', 'csv', 'csvboth_q'))]
if os.environ.get('SC_GRID') == 'filecheck':
    GRID = FILECHECK
OUT = 'sc_v2_filecheck' if os.environ.get('SC_GRID') == 'filecheck' else 'sc_v2_robust'
START = 2005   # cheap is classified on the fund's first observed-fee month on or after January of this year


def main():
    d = pd.read_pickle(PANEL)
    d['mk'] = np.round(d.month_t * 12).astype(int)
    nomm = (d.mmf == 0).to_numpy()
    fam_rows = d.firm_f_old.notna().to_numpy()

    src = pd.read_csv(SOURCE, usecols=['crsp_fundno', 'month', 'index', 'exp_ratio', 'fund_name', 'mgmt_cd', 'ETF'])
    src = src.rename(columns={'crsp_fundno': 'product_j', 'month': 'month_t', 'index': 'market_m_index', 'exp_ratio': 'product_exp_ratio',
                              'fund_name': 'product_fund_name', 'mgmt_cd': 'firm_f_old', 'ETF': 'etf_src'})
    src['market_m_cluster'] = np.nan
    src['mk'] = np.round(src.month_t * 12).astype(int)
    cf = pd.read_csv(CSVP, usecols=['product_j', 'month_t', 'ETF_ind', 'product_exp_ratio', 'product_fund_name'])
    cf['mk'] = np.round(cf.month_t * 12).astype(int)
    src = src.merge(cf[['product_j', 'mk', 'ETF_ind']].rename(columns={'ETF_ind': 'etf_csv'}), on=['product_j', 'mk'], how='left')
    src['in_csv'] = src.etf_csv.notna()
    crsp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'fund_name', 'lipper_class', 'crsp_obj_cd', 'et_flag', 'exp_ratio'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    crsp = crsp[crsp.crsp_fundno.isin(set(src.product_j))]
    mmf = v2.money_market_funds(crsp, set(src.product_j))
    etf_crsp = set(crsp.loc[crsp.et_flag == 'F', 'crsp_fundno'])
    er = pd.to_numeric(crsp.exp_ratio, errors='coerce')
    first_fee_q = crsp[er.notna() & (er.abs() < 0.5)].assign(q=lambda x: x.quarter.astype(float)).groupby('crsp_fundno').q.min()
    del crsp
    dn = pd.read_csv(f'{DANNY}/classified_donors.csv', usecols=['fund_id', 'month_key', 'share_type', 'category10'])
    src = src.merge(dn.rename(columns={'fund_id': 'product_j', 'month_key': 'mk'}), on=['product_j', 'mk'], how='left')
    del dn
    etf_csv_fund = cf.groupby('product_j').ETF_ind.max()
    etf_by = {'csv': src.etf_csv.fillna(src.product_j.map(etf_csv_fund)).fillna(src.etf_src),
              'crsp': src.product_j.isin(etf_crsp).astype(float)}
    etf_by['danny'] = etf_by['crsp']
    n_fm = int((etf_by['csv'] != etf_by['crsp']).sum())
    n_f = src.loc[etf_by['csv'] != etf_by['crsp'], 'product_j'].nunique()
    t2 = set(d.product_ids)
    print(f"ETF flag, CSV rule vs CRSP et_flag: differs on {n_fm:,} source fund-months, {n_f} funds ({len(set(src.loc[etf_by['csv'] != etf_by['crsp'], 'product_j']) & t2)} in Table 2)", flush=True)

    # V2's asset class per index (held fixed), from the index CSV build
    v2raw = v2.build_instrument(CSVP, CRSP, mmf)
    ac_v2 = v2raw.dropna(subset=['market_m_index']).drop_duplicates('market_m_index').set_index('market_m_index').asset_class
    del v2raw

    # cheap indicators
    cheap_csv = v2.gene_idx(cf.rename(columns={})[['product_j', 'month_t', 'product_exp_ratio']].dropna())
    cheap_src = v2.gene_idx(src[['product_j', 'month_t', 'product_exp_ratio']].dropna())
    # the same rule using only fund-months whose fee CRSP reports for the fund in that quarter or earlier (no name-based imputation)
    obs = src[src.product_exp_ratio.notna() & ((np.floor(np.round(src.month_t * 12) / 3) / 4) >= src.product_j.map(first_fee_q))]
    cheap_obs_1993 = v2.gene_idx(obs[['product_j', 'month_t', 'product_exp_ratio']])
    obs = obs[obs.month_t >= START - 1e-9]
    cheap_obs = v2.gene_idx(obs[['product_j', 'month_t', 'product_exp_ratio']])
    print(f'cheap classified from {START}: funds in the cross-section in January {START}: {int(np.isclose(obs.month_t, START).sum())}', flush=True)

    def cheap_q(q):   # the same rule at another percentile
        cut = obs.groupby('month_t').product_exp_ratio.quantile(q)
        e = obs.sort_values('month_t').groupby('product_j').first()
        return (e.product_exp_ratio <= e.month_t.map(cut) + 1e-9).astype(float)
    e0 = src[src.product_exp_ratio.notna()].sort_values('month_t').groupby('product_j').first()
    imputed0 = ~((np.floor(np.round(e0.month_t * 12) / 3) / 4) >= e0.index.to_series().map(first_fee_q))
    print(f'source panel: the fee in a fund\'s first month is not observed (imputed or backfilled) for {float(imputed0.mean()):.3f} of funds', flush=True)
    cmp_ = pd.DataFrame({'csv': cheap_csv, 'source': cheap_src}).dropna()
    first_csv = cf.groupby('product_j').mk.min()
    first_src = src[src.product_exp_ratio.notna()].groupby('product_j').mk.min()
    gap = (first_csv - first_src).dropna()
    print(f'cheap indicator: funds in both {len(cmp_):,}; agree {float((cmp_.csv == cmp_.source).mean()):.3f}; cheap share of funds csv {cmp_.csv.mean():.3f}, source {cmp_.source.mean():.3f}; '
          f'first CSV month is later than the first source month for {float((gap > 0).mean()):.3f} of funds (median gap {gap[gap > 0].median():.0f} months)')
    d['cheap_csv'] = d.product_ids.map(cheap_csv)
    d['cheap_source'] = d.product_ids.map(cheap_src)
    d['cheap_source_obs'] = d.product_ids.map(cheap_obs).fillna(d.product_ids.map(cheap_csv))
    d['cheap_source_obs_1993'] = d.product_ids.map(cheap_obs_1993).fillna(d.product_ids.map(cheap_csv))
    for q in (15, 25):
        d[f'cheap_source_obs_q{q}'] = d.product_ids.map(cheap_q(q / 100)).fillna(d.product_ids.map(cheap_csv))
    # the same rule on the index CSV, entry month on or after START
    cobs = cf[['product_j', 'month_t', 'product_exp_ratio']].dropna()
    cobs = cobs[cobs.month_t >= START - 1e-9]
    for q in (15, 20, 25):
        cs = cheap_q(q / 100)
        cut_c = cobs.groupby('month_t').product_exp_ratio.quantile(q / 100)
        ec = cobs.sort_values('month_t').groupby('product_j').first()
        cc = (ec.product_exp_ratio <= ec.month_t.map(cut_c) + 1e-9).astype(float)
        d[f'cheap_srcboth_q{q}'] = d.product_ids.map(cs).fillna(d.product_ids.map(cheap_csv))
        d[f'cheap_csvboth_q{q}'] = d.product_ids.map(cc)
        j_s, j_c = obs[np.isclose(obs.month_t, START)], cobs[np.isclose(cobs.month_t, START)]
        k_s, k_c = float(j_s.product_exp_ratio.quantile(q / 100)), float(j_c.product_exp_ratio.quantile(q / 100))
        fd = d.drop_duplicates('product_ids')
        diff = fd[fd[f'cheap_srcboth_q{q}'] != fd[f'cheap_csvboth_q{q}']]
        print(f'cutoff {q}%: January {START} cutoff source {k_s:.3f} ({len(j_s)} funds, {int(np.isclose(j_s.product_exp_ratio, k_s).sum())} exactly at it) | '
              f'CSV {k_c:.3f} ({len(j_c)} funds, {int(np.isclose(j_c.product_exp_ratio, k_c).sum())} exactly at it) | Table 2 funds whose status differs {len(diff)} '
              f'(cheap only on source {int((diff[f"cheap_srcboth_q{q}"] == 1).sum())}, only on CSV {int((diff[f"cheap_csvboth_q{q}"] == 1).sum())})', flush=True)
    print('funds without an observed-fee entry month (CSV indicator used):', d.loc[~d.product_ids.isin(cheap_obs.index), 'product_ids'].nunique(), flush=True)
    print(f'cheap (source, observed fees): share of Table 2 fund-months {d.cheap_source_obs.mean():.3f}; differs from csv on {int((d.cheap_csv != d.cheap_source_obs).sum()):,} fund-months, {d.loc[d.cheap_csv != d.cheap_source_obs, "product_ids"].nunique()} funds', flush=True)
    assert (d.cheap_csv == d.cheap).all()
    print(f'Table 2 fund-months: cheap csv {d.cheap_csv.mean():.3f}, source {d.cheap_source.mean():.3f}; differ on {int((d.cheap_csv != d.cheap_source).sum()):,} fund-months, '
          f'{d.loc[d.cheap_csv != d.cheap_source, "product_ids"].nunique()} funds (csv-cheap only {d.loc[(d.cheap_csv == 1) & (d.cheap_source == 0), "product_ids"].nunique()}, '
          f'source-cheap only {d.loc[(d.cheap_csv == 0) & (d.cheap_source == 1), "product_ids"].nunique()})', flush=True)

    raws = {}
    for typ in ('csv', 'crsp', 'danny'):
        tmp = f'{CACHE}/source_as_index_{typ}.csv'
        src.assign(ETF_ind=etf_by[typ])[['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old', 'product_exp_ratio',
                                         'ETF_ind', 'product_fund_name']].to_csv(tmp, index=False)
        raw = v2.build_instrument(tmp, CRSP, mmf)
        os.remove(tmp)
        raw['mk'] = np.round(raw.month_t * 12).astype(int)
        raw['asset_class'] = raw.market_m_index.map(ac_v2).fillna(raw.asset_class)
        raw = raw.merge(src[['product_j', 'mk', 'in_csv', 'share_type', 'category10']], on=['product_j', 'mk'], how='left')
        if typ == 'danny':
            raw['share_class'] = raw.share_type.map({0: 'retail', 1: 'inst', 2: 'etf'})
        raw['cat10'] = raw.category10
        raws[typ] = raw
    print('share types of Table 2 fund-months:', {t: raws[t].merge(d[['product_ids', 'mk']].rename(columns={'product_ids': 'product_j'}), on=['product_j', 'mk']).share_class.value_counts().to_dict() for t in raws}, flush=True)

    x = raws['csv'].merge(d[['product_ids', 'mk']].rename(columns={'product_ids': 'product_j'}), on=['product_j', 'mk'])
    print('Table 2 fund-months, Lipper-6 class (rows) by category10 (columns):')
    print(pd.crosstab(x.asset_class, x.cat10.fillna(-1).astype(int)).to_string(), flush=True)

    def build_z(raw, excl, donors):
        ecol = 'asset_class' if excl == 'lipper6' else 'cat10'
        don = raw[(raw.in_csv if donors == 'csv' else True) & raw[ecol].notna() & raw.share_class.notna() & raw.firm_f_old.notna()]
        keys = ['firm_f_old', 'month_t', 'share_class']
        tab = pd.concat([don[don[ecol] != a].groupby(keys).product_exp_ratio.median().rename('z').reset_index().assign(**{ecol: a})
                         for a in sorted(don[ecol].unique())])
        z = raw[['product_j', 'mk'] + keys + [ecol]].merge(tab, on=keys + [ecol], how='left')
        return z[['product_j', 'mk', 'z']].rename(columns={'product_j': 'product_ids'})

    rows, t5s = [], []
    for label, typ, excl, donors, cheap in GRID:
        z = build_z(raws[typ], excl, donors)
        dd0 = d.drop(columns=['Z']).merge(z, on=['product_ids', 'mk'], how='left').rename(columns={'z': 'Z'})
        dd0['cheap'] = dd0[f'cheap_{cheap}']
        dd0['gene_idx'] = dd0.cheap
        mask = nomm & dd0.Z.notna().to_numpy()
        o, res, dd, b = fit(dd0[mask].reset_index(drop=True), 'Z', ['cheap'])
        t5 = v2.table5(res, dd, dd0)
        r = dict(variant=label, types=typ, excl=excl, donors=donors, cheap=cheap, N=o['N'], funds=o['funds'], alpha=o['b_prices'], se=o['se_prices'],
                 alpha_x=o['b_cheap'], se_x=o['se_cheap'], min_F=o['min_F'], share_pos_e=o['share_pos_e'], avg_e=o['avg_e'],
                 share_cheap=float(dd.cheap.mean()), t5_lt_m1=int((t5.own_elasticity < -1).sum()), t5_n=len(t5))
        for tag, m_ in (('', nomm), ('_noVA', nomm & fam_rows)):
            ds = downstream(dd0[m_].reset_index(drop=True), ['cheap'], b)
            r.update({f'negmc_B0{tag}': ds['B0'][0], f'negmc_B65{tag}': ds['B65'][0], f'minmc_B65{tag}': ds['B65'][1], f'vanguard_B0{tag}': ds['B0'][3]})
        if label.startswith('V2 (cheap classified from 2005'):   # save the new V2 for the conduct test, with and without VA funds
            for nm, m_ in (('V2n', nomm), ('V2nx', nomm & fam_rows)):
                sup = dd0[m_]
                np.save(f'{CACHE}/alpha_{nm}.npy', b['prices'] + b['px_cheap'] * sup.cheap.to_numpy())
                np.save(f'{CACHE}/rows_{nm}.npy', np.flatnonzero(m_))
            np.save(f'{CACHE}/cheap_V2n.npy', dd0.cheap.to_numpy())
        rows.append(r)
        t5s.append(t5.assign(variant=label))
        print(f"{label:58s} N {r['N']:,} | non-cheap {r['alpha']:.3f} ({r['se']:.3f}) | x cheap {r['alpha_x']:.3f} ({r['se_x']:.3f}) | F {r['min_F']:.0f} | e>0 {r['share_pos_e']:.3f} "
              f"| T5 {r['t5_lt_m1']}/{r['t5_n']} | neg MC {r['negmc_B0']:.3f}-{r['negmc_B65']:.3f} (no VA {r['negmc_B0_noVA']:.3f}-{r['negmc_B65_noVA']:.3f}) | min MC {r['minmc_B65']:.2f} | Vanguard {r['vanguard_B0']:.2f}", flush=True)
        pd.DataFrame(rows).to_csv(f'{OUT}.csv', index=False)
    pd.concat(t5s).to_csv(f'{OUT}_table5.csv', index=False)


if __name__ == '__main__':
    pd.set_option('display.width', 250)
    main()
