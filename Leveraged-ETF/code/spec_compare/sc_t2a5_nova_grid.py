"""T2 and A5 without the variable-annuity funds: does any reasonable version of the Hausman instrument give a sensible
demand equation? Grid over the instrument's construction, donors from Danny's full source panel:
  exclusion    index (paper) | cat20 | cat10 (Danny's labels) | lipper6 (V2's six asset classes)
  share type   pooled (paper) | same type (ETF from CRSP's et_flag; institutional / retail from CRSP flags)
  aggregation  lag-AUM-weighted mean (paper) | unweighted median
Sample: Table 2 Panel A minus the 112 variable-annuity funds (100,529 fund-months); rows where the instrument is undefined
are dropped (no fallback to the original IV0). A second pass also drops the 4 money market funds.
T2: one slope. A5: price + price x broad-based (paper's label), instruments IV and IV x broad.
For every version with no upward-sloping demand, the negative-MC share at each candidate's own eta is computed.
Writes sc_t2a5_nova_grid.csv.
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
from sc_broad_ladder import leave_out  # noqa: E402
from sc_build import CACHE, CRSP, DATA, PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402
from sc_v2_source_donors import downstream  # noqa: E402

pyblp.options.verbose = False
SOURCE = os.environ.get('SC_SOURCE', f'{DATA}/danny/index_funds_preprocess_oct2026.csv')
DANNY = os.environ.get('SC_DANNY', f'{DATA}/danny_zip/x/V2_comparison_handoff/outputs/hausman-robustness-v1/passive')
CSVP = f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv'


def main():
    d = pd.read_pickle(PANEL)
    d['mk'] = np.round(d.month_t * 12).astype(int)
    d['gene_idx'] = d.cheap
    d['broad'] = ((d.broad_specialized == 'broad-based').groupby(d.product_ids).transform('mean') > 0.5).astype(float)
    nova = d.firm_f_old.notna().to_numpy()
    nomm = (d.mmf == 0).to_numpy()

    src = pd.read_csv(SOURCE, usecols=['crsp_fundno', 'month', 'index', 'exp_ratio', 'fund_name', 'mgmt_cd', 'L1_mtna1'])
    src = src.rename(columns={'crsp_fundno': 'product_j', 'month': 'month_t', 'index': 'market_m_index', 'exp_ratio': 'product_exp_ratio',
                              'fund_name': 'product_fund_name', 'mgmt_cd': 'firm_f_old', 'L1_mtna1': 'product_L1_mtna'})
    if os.environ.get('SC_FAMILY'):   # coarser family definition (see sc_q4.remap_family)
        from sc_q4 import remap_family
        src['firm_f_old'] = remap_family(src, os.environ['SC_FAMILY'])
        print('family definition:', os.environ['SC_FAMILY'], '| distinct families', src.firm_f_old.nunique(), '| funds with more than one family', int((src.dropna(subset=['firm_f_old']).groupby('product_j').firm_f_old.nunique() > 1).sum()), flush=True)
    src['market_m_cluster'] = np.nan
    crsp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd', 'et_flag'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    crsp = crsp[crsp.crsp_fundno.isin(set(src.product_j))]
    mmf = v2.money_market_funds(crsp, set(src.product_j))
    src['ETF_ind'] = src.product_j.isin(set(crsp.loc[crsp.et_flag == 'F', 'crsp_fundno'])).astype(float)
    del crsp
    tmp = f'{CACHE}/source_as_index_grid.csv'
    src.to_csv(tmp, index=False)
    raw = v2.build_instrument(tmp, CRSP, [])        # donors: every source fund-month with a fee (money market funds kept, as in the paper)
    os.remove(tmp)
    v2raw = v2.build_instrument(CSVP, CRSP, mmf)
    ac_v2 = v2raw.dropna(subset=['market_m_index']).drop_duplicates('market_m_index').set_index('market_m_index').asset_class
    del v2raw
    raw['lipper6'] = raw.market_m_index.map(ac_v2).fillna(raw.asset_class)
    raw['mk'] = np.round(raw.month_t * 12).astype(int)
    raw = raw.merge(src[['product_j', 'month_t', 'product_L1_mtna']], on=['product_j', 'month_t'], how='left')
    dn = pd.read_csv(f'{DANNY}/classified_donors.csv', usecols=['fund_id', 'month_key', 'category10', 'category20'])
    raw = raw.merge(dn.rename(columns={'fund_id': 'product_j', 'month_key': 'mk', 'category10': 'cat10', 'category20': 'cat20'}), on=['product_j', 'mk'], how='left')
    raw['index'] = raw.market_m_index.fillna('_none_' + raw.product_j.astype(str))
    print(f'donor pool: {len(raw):,} source fund-months with a fee', flush=True)

    DROPQ4 = os.environ.get('SC_DROPQ4') == '1'   # drop the funds in the top entry-fee quartile from the sample
    if os.environ.get('SC_PURE') == '1':   # keep only funds that CRSP flags as pure index funds in most quarters
        from sc_q4 import pure_index_funds
        keepp = d.product_ids.isin(pure_index_funds(d.product_ids)).to_numpy()
        print(f'not flagged as pure index funds, dropped: {int((nova & ~keepp).sum()):,} fund-months, {d.loc[nova & ~keepp, "product_ids"].nunique()} funds', flush=True)
        nova = nova & keepp
    if DROPQ4:
        from sc_q4 import entry_quartile
        keep = (d.product_ids.map(entry_quartile()) < 4).to_numpy()
        print(f'top entry-fee quartile dropped: {int((nova & ~keep).sum()):,} fund-months, {d.loc[nova & ~keep, "product_ids"].nunique()} funds', flush=True)
        nova = nova & keep
    rows = []
    only = os.environ.get('SC_ONLY')      # e.g. 'lipper6,pooled,wavg' to run one version and save it as T2alt / A5alt
    for excl in ('index', 'cat20', 'cat10', 'lipper6'):
        for typ in ('pooled', 'same type'):
            for agg in ('wavg', 'med'):
                if only and only != f'{excl},{typ},{agg}':
                    continue
                sub = raw[raw[excl].notna()].copy()
                sub['iv'] = leave_out(sub, excl, typ == 'same type', agg)
                dd0 = d.merge(sub[['product_j', 'mk', 'iv']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'mk'], how='left')
                for sample, base in (('no VA', nova), ('no VA, no money market', nova & nomm)):
                    mask = base & dd0.iv.notna().to_numpy()
                    est = dd0[mask].reset_index(drop=True)
                    r = dict(exclusion=excl, share_type=typ, aggregation=agg, sample=sample, N=int(mask.sum()))
                    for model, zs in (('T2', []), ('A5', ['broad'])):
                        o, res, dd, b = fit(est, 'iv', zs)
                        t5 = v2.table5(res, dd, dd0)
                        r.update({f'{model}_price': o['b_prices'], f'{model}_se': o['se_prices'], f'{model}_F': o['min_F'], f'{model}_pos_e': o['share_pos_e'],
                                  f'{model}_avg_e': o['avg_e'], f'{model}_t5': int((t5.own_elasticity < -1).sum())})
                        if zs:
                            r.update(A5_xbroad=o['b_broad'], A5_xbroad_se=o['se_broad'])
                        if only and sample == 'no VA' and not DROPQ4 and not os.environ.get('SC_FAMILY') and not os.environ.get('SC_PURE'):
                            sup = dd0[base]
                            np.save(f'{CACHE}/alpha_{model}alt.npy', np.full(len(sup), b['prices']) + sum(b[f'px_{z}'] * sup[z].to_numpy() for z in zs))
                            np.save(f'{CACHE}/rows_{model}alt.npy', np.flatnonzero(base))
                            r.update({f'{model}_e_aum': o['e_aum_weighted'], f'{model}_avg_e_mkt': o['avg_e']})
                            t5.assign(spec=f'{model}alt').to_csv(f'sc_alt_table5_{model}.csv', index=False)
                        if o['share_pos_e'] == 0 and sample == 'no VA':
                            ds = downstream(dd0[base].reset_index(drop=True), zs, b)
                            r.update({f'{model}_negmc_B0': ds['B0'][0], f'{model}_negmc_B65': ds['B65'][0], f'{model}_below020_B65': ds['B65'][2],
                                      f'{model}_minmc_B65': ds['B65'][1], f'{model}_vanguard_B0': ds['B0'][3]})
                    rows.append(r)
                    mc = lambda m: (f" negMC {r[f'{m}_negmc_B0']:.2f}-{r[f'{m}_negmc_B65']:.2f}" if f'{m}_negmc_B0' in r else '')
                    print(f"{excl:8s} {typ:9s} {agg:4s} {sample:22s} N {r['N']:>7,} | T2 {r['T2_price']:6.2f} ({r['T2_se']:.2f}) F {r['T2_F']:5.0f} e>0 {r['T2_pos_e']:.2f} T5 {r['T2_t5']}{mc('T2')} "
                          f"| A5 {r['A5_price']:6.2f} ({r['A5_se']:.2f}) x broad {r['A5_xbroad']:6.2f} F {r['A5_F']:5.0f} e>0 {r['A5_pos_e']:.2f} T5 {r['A5_t5']}{mc('A5')}", flush=True)
                    pd.DataFrame(rows).to_csv('sc_t2a5_alt.csv' if only else 'sc_t2a5_nova_grid.csv', index=False)


if __name__ == '__main__':
    main()
