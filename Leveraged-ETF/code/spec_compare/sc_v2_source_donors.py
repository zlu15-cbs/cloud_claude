"""V2 with the instrument's donors taken from Danny's full source panel instead of the index CSV.

The index CSV (579,632 fund-months) is the source panel index_funds_preprocess_oct2026.csv (675,551) after the build
script's estimation filter. The 95,919 rows it drops (mostly a fund's first 12 months, and funds in families with a single
index) can still be donors. Variants of V2's instrument Z (same family, same share type, other Lipper-6 asset class,
median fee, money market funds removed):
  Z_csv        donors from the index CSV (V2 as reported)
  Z_src        donors from the full source panel
  Z_csv_obs    index-CSV donors whose fee is observed: CRSP reports an expense ratio for the fund in that quarter or earlier
  Z_src_obs    the same restriction on the source-panel donors
"Not observed" = the build script filled the fee from funds with the same first five letters in the name (or backward).
Demand: price + price x cheap, instruments Z and Z x cheap, V2's sample; cheap (gene_idx) is held fixed.
Also checks the source panel as the donor pool of the paper's IV0 (index exclusion, lag-AUM weights).
    SC_DATA=... SC_SOURCE=/path/index_funds_preprocess_oct2026.csv python sc_v2_source_donors.py
SC_ETF=csv (default) uses the index CSV's ETF_ind, as V2 does; SC_ETF=source uses the source panel's ETF column.
Writes sc_v2_source_donors_etf_<flag>.csv.
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

pyblp.options.verbose = False
SOURCE = os.environ.get('SC_SOURCE', f'{DATA}/danny/index_funds_preprocess_oct2026.csv')


def downstream(d, zs, b):
    """negative-MC share at each candidate's own eta, on the supply rows d."""
    alpha = np.full(len(d), b['prices']) + sum(b[f'px_{z}'] * d[z].to_numpy() for z in zs)
    p, logq = d.prices.to_numpy(), np.log(d.product_mtna.to_numpy())
    out = {}
    for m, k in v2.CONDUCT.items():
        if k is None:
            continue
        mu = v2.markups(d, alpha, k)
        eta = v2.scale_iv(d, p - mu)['eta']
        mc = p + eta * logq - mu
        ns = v2.neg_stats(d, mc)
        out[m] = (ns['neg_share'], ns['mc_min'], ns['share_below_m020'], float((mc[(d.firm_ids == 'Vanguard').to_numpy()] < 0).mean()))
    return out


def main():
    d = pd.read_pickle(PANEL)
    d['gene_idx'] = d.cheap
    nomm = (d.mmf == 0).to_numpy()

    # ---- the source panel in the index CSV's column names, so that V2's own instrument code runs on it
    src = pd.read_csv(SOURCE, usecols=['crsp_fundno', 'month', 'index', 'exp_ratio', 'fund_name', 'mgmt_cd', 'ETF', 'L1_mtna1'])
    src = src.rename(columns={'crsp_fundno': 'product_j', 'month': 'month_t', 'index': 'market_m_index', 'exp_ratio': 'product_exp_ratio',
                              'fund_name': 'product_fund_name', 'mgmt_cd': 'firm_f_old', 'ETF': 'ETF_ind', 'L1_mtna1': 'product_L1_mtna'})
    src['market_m_cluster'] = np.nan
    # hold V2's ETF flag fixed: the index CSV's ETF_ind where the fund-month (else the fund) is in the CSV; the source panel's
    # own ETF column differs from it for some funds and would change share types for reasons unrelated to the donor pool
    cf = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'month_t', 'ETF_ind', 'market_m_index'])
    src['mk'] = np.round(src.month_t * 12).astype(int)
    cf['mk'] = np.round(cf.month_t * 12).astype(int)
    src = src.merge(cf[['product_j', 'mk', 'ETF_ind']].rename(columns={'ETF_ind': 'etf_csv'}), on=['product_j', 'mk'], how='left')
    etf_fund = cf.groupby('product_j').ETF_ind.max()
    n_diff = int((src.etf_csv.notna() & (src.etf_csv != src.ETF_ind)).sum())
    if os.environ.get('SC_ETF', 'csv') == 'csv':
        src['ETF_ind'] = src.etf_csv.fillna(src.product_j.map(etf_fund)).fillna(src.ETF_ind)
    print(f"ETF flag: source panel differs from the index CSV on {n_diff:,} common fund-months; flag used: {os.environ.get('SC_ETF', 'csv')}", flush=True)
    src = src.drop(columns=['etf_csv', 'mk'])
    tmp = f'{CACHE}/source_as_index.csv'
    src.to_csv(tmp, index=False)
    crsp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'fund_name', 'lipper_class', 'crsp_obj_cd', 'exp_ratio'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    crsp = crsp[crsp.crsp_fundno.isin(set(src.product_j))]
    mmf = v2.money_market_funds(crsp, set(src.product_j))
    er = pd.to_numeric(crsp.exp_ratio, errors='coerce')
    first_fee_q = crsp[er.notna() & (er.abs() < 0.5)].assign(q=lambda x: x.quarter.astype(float)).groupby('crsp_fundno').q.min()
    del crsp
    print(f'source panel: {len(src):,} fund-months, {src.product_j.nunique():,} funds; money market funds {len(mmf)}', flush=True)

    raw = v2.build_instrument(tmp, CRSP, mmf)            # donors with a fee, money market funds removed; asset and share classes
    raw['mk'] = np.round(raw.month_t * 12).astype(int)
    # hold V2's asset class fixed for every index that is in the index CSV (the class is assigned per index)
    v2raw = v2.build_instrument(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', CRSP, mmf)
    ac_v2 = v2raw.dropna(subset=['market_m_index']).drop_duplicates('market_m_index').set_index('market_m_index').asset_class
    ac_new = raw.market_m_index.map(ac_v2).fillna(raw.asset_class)
    print(f'asset class: {int((ac_new != raw.asset_class).sum()):,} donor-pool rows reset to V2\'s class for their index', flush=True)
    raw['asset_class'] = ac_new
    del v2raw
    csv = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'month_t'])
    csv_keys = pd.MultiIndex.from_arrays([csv.product_j, np.round(csv.month_t * 12).astype(int)])
    raw['in_csv'] = pd.MultiIndex.from_arrays([raw.product_j, raw.mk]).isin(csv_keys)
    raw['fee_observed'] = raw.quarter >= raw.product_j.map(first_fee_q)       # NaN first quarter -> False
    fam = raw.firm_f_old.notna()
    print(f'donor-pool rows (fee present, not money market): {len(raw):,}; with a family code {int(fam.sum()):,}; in the index CSV {int(raw.in_csv.sum()):,}; '
          f'source-only {int((~raw.in_csv).sum()):,} (with a family code {int((~raw.in_csv & fam).sum()):,})')
    print(f'fee observed (CRSP reports one for the fund in that quarter or earlier): all {raw.fee_observed.mean():.3f}; with a family code {raw.fee_observed[fam].mean():.3f}; '
          f'without {raw.fee_observed[~fam].mean():.3f}; source-only rows with a family code {raw.fee_observed[~raw.in_csv & fam].mean():.3f}')
    so = raw[~raw.in_csv & fam]
    first = so.mk - raw.groupby('product_j').mk.transform('min').reindex(so.index)
    print(f'source-only donor rows with a family code: {len(so):,}; within the fund\'s first 12 months {float((first < 12).mean()):.3f}; '
          f'since 2010 {int((so.month_t >= 2010).sum()):,}')

    def z_from(mask, name):
        sub = raw[mask].copy()
        sub[name] = v2.leave_out(sub, 'firm_f_old', 'asset_class', 'share_class', name)
        # targets must be looked up by fund-month even if the target row itself is not a donor in this variant
        keys = ['firm_f_old', 'month_t', 'share_class']
        tab = pd.concat([sub[sub.asset_class != a].groupby(keys).product_exp_ratio.median().rename(name).reset_index().assign(asset_class=a)
                         for a in sorted(raw.asset_class.dropna().unique())])
        return raw[['product_j', 'month_t'] + keys[:1] + keys[2:] + ['asset_class']].merge(tab, on=keys + ['asset_class'], how='left')[name].to_numpy()
    raw['Z_src'] = z_from(np.ones(len(raw), bool), 'Z_src')
    raw['Z_csv'] = z_from(raw.in_csv.to_numpy(), 'Z_csv')
    raw['Z_src_obs'] = z_from(raw.fee_observed.to_numpy(), 'Z_src_obs')
    raw['Z_csv_obs'] = z_from((raw.in_csv & raw.fee_observed).to_numpy(), 'Z_csv_obs')
    names = ['Z_csv', 'Z_src', 'Z_csv_obs', 'Z_src_obs']
    d = d.merge(raw[['product_j', 'month_t', 'fee_observed'] + names].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
    ok = d.Z.notna() & nomm
    if os.environ.get('SC_ETF', 'csv') != 'csv':
        d['sc_new'] = d.merge(raw[['product_j', 'month_t', 'share_class']].rename(columns={'product_j': 'product_ids', 'share_class': 'sc_new'}), on=['product_ids', 'month_t'], how='left').sc_new.to_numpy()
        print('Table 2 fund-months whose share type changes with the source ETF flag:', int((d.sc_new != d.share_class)[nomm & d.sc_new.notna().to_numpy()].sum()))
    dz = (d.Z_csv - d.Z).abs()[ok]
    print(f'check: Z_csv rebuilt through the source panel equals V2\'s Z on {float((dz < 1e-9).mean()):.4f} of V2\'s rows; defined on {int((d.Z_csv.notna() & nomm).sum()):,} (V2: {int(ok.sum()):,})')
    print(f'Table 2 fund-months whose own fee is not observed: {int((d.fee_observed == False).sum()):,} of {len(d):,}; among rows with a family code {int(((d.fee_observed == False) & d.firm_f_old.notna()).sum()):,}')  # noqa: E712
    R = pd.DataFrame(v2.resid(d[ok].reset_index(drop=True).fillna({n: 0 for n in names}), names), columns=names)
    print('rows where the instrument changes relative to Z_csv (V2 rows):', {n: int(((d[n] - d.Z_csv).abs()[ok] > 1e-9).sum() + (d[n].isna() & ok).sum()) for n in names[1:]})

    # ---- the paper's IV0 rebuilt on the source panel (index exclusion, lag-AUM weights, blank families pooled)
    w = src.copy()
    w['fam'] = w.firm_f_old.fillna('')
    wt = w.product_L1_mtna.fillna(0.0)
    x = w.product_exp_ratio.fillna(0.0) * wt
    g1, g2 = [w.fam, w.month_t], [w.fam, w.month_t, w.market_m_index]
    den = wt.groupby(g1).transform('sum') - wt.groupby(g2).transform('sum')
    w['R_src'] = ((x.groupby(g1).transform('sum') - x.groupby(g2).transform('sum')) / den).where(den > 1e-9)
    chk = d[['product_ids', 'month_t', 'demand_instruments0']].merge(w[['product_j', 'month_t', 'R_src']].rename(columns={'product_j': 'product_ids'}),
                                                                      on=['product_ids', 'month_t'], how='left')
    dd0 = (chk.R_src - chk.demand_instruments0).abs()
    print(f'paper IV0 rebuilt on the source panel: defined on {int(chk.R_src.notna().sum()):,} of {len(chk):,} Table 2 rows; equal to the original within 1e-8 on '
          f'{float((dd0 < 1e-8).mean()):.4f}, within 0.0005 on {float((dd0 < 5e-4).mean()):.4f} (from the index CSV: 0.34 and 0.90)', flush=True)

    # ---- V2 with each instrument
    sup = d[nomm].reset_index(drop=True)
    sup_nova = d[nomm & d.firm_f_old.notna().to_numpy()].reset_index(drop=True)
    common = nomm & d[names].notna().all(axis=1).to_numpy()
    rows = []
    for n in names:
        for rname, mask in (('own rows', nomm & d[n].notna().to_numpy()), ('common rows', common)):
            o, res, dd, b = fit(d[mask].reset_index(drop=True), n, ['cheap'])
            t5 = v2.table5(res, dd, d)
            r = dict(instrument=n, rows=rname, N=o['N'], funds=o['funds'], alpha=o['b_prices'], se=o['se_prices'], alpha_x=o['b_cheap'], se_x=o['se_cheap'],
                     min_F=o['min_F'], share_pos_e=o['share_pos_e'], avg_e=o['avg_e'], t5_lt_m1=int((t5.own_elasticity < -1).sum()), t5_n=len(t5))
            if rname == 'own rows':
                for tag, s_ in (('', sup), ('_noVA', sup_nova)):
                    ds = downstream(s_, ['cheap'], b)
                    r.update({f'negmc_B0{tag}': ds['B0'][0], f'negmc_B65{tag}': ds['B65'][0], f'minmc_B65{tag}': ds['B65'][1],
                              f'below020_B65{tag}': ds['B65'][2], f'vanguard_B0{tag}': ds['B0'][3]})
            rows.append(r)
            extra = (f" | neg MC B0-B65 {r['negmc_B0']:.3f}-{r['negmc_B65']:.3f} (no VA {r['negmc_B0_noVA']:.3f}-{r['negmc_B65_noVA']:.3f}) | min MC {r['minmc_B65']:.2f} "
                     f"| Vanguard B0 {r['vanguard_B0']:.2f}") if rname == 'own rows' else ''
            print(f"{n:10s} {rname:11s} N {r['N']:,} | non-cheap {r['alpha']:.3f} ({r['se']:.3f}) | x cheap {r['alpha_x']:.3f} ({r['se_x']:.3f}) | F {r['min_F']:.1f} "
                  f"| e>0 {r['share_pos_e']:.3f} | avg e {r['avg_e']:.2f} | T5 {r['t5_lt_m1']}/{r['t5_n']}{extra}", flush=True)
            pd.DataFrame(rows).to_csv(f"sc_v2_source_donors_etf_{os.environ.get('SC_ETF', 'csv')}.csv", index=False)
    os.remove(tmp)


if __name__ == '__main__':
    pd.set_option('display.width', 250)
    main()
