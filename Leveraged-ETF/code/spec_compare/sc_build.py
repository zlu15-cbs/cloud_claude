"""Spec comparison, step 1a: build the estimation panel once and cache it outside the repo (/tmp/data/cache/panel.pkl).

Adds to the Table 2 Panel A sample (Danny's notebook filters, replicate_V2.load_sample; 108,300 fund-months):
  mmf        1 for the 4 money market funds in the sample
  cheap      gene_idx (V2)
  Z, asset_class, share_class   V2's instrument and its classes (money market funds out of the donor pool)
  fee_t1, fee_t2                lowest / middle fee tercile of funds at the fund's first sample month (spec A5)
  R_idx      our reconstruction of the paper's IV0: lag-AUM-weighted mean fee of same-family (firm_f_old; blank
             families match one another, as in the historical code) funds in the month tracking another market_m_index
  R_ac       the same, donors also outside the target's Lipper 6 asset class            -> proxy 4p
  R_clx      the same, donors also outside the target's market_m_cluster                -> proxy 4q
  iv4p, iv4q R_ac / R_clx, falling back to the ORIGINAL IV0 (demand_instruments0) where undefined
  iv_ridx    R_idx with the same fallback (validation only: how far is our donor file from Danny's)
Donors come from the 579,632-row index CSV. Danny's source panel has 675,551 rows, so R_idx is not his IV0 exactly.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402

DATA = os.environ.get('SC_DATA', '/tmp/data')
INDEX = f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv'
CRSP = f'{DATA}/CRSP_fund_summary_2026_qtrly_combined.csv'
CACHE = f'{DATA}/cache'
PANEL = f'{CACHE}/panel.pkl'


def weighted_leave_out(r, excl):
    """sum_k fee_k L1AUM_k / sum_k L1AUM_k over same family-month donors outside every class in `excl` (union)."""
    fam = r.firm_f_old.fillna('')
    w = r.product_L1_mtna.fillna(0.0)
    x = r.product_exp_ratio.fillna(0.0) * w
    base = [fam, r.month_t]

    def s(v, cols):
        return v.groupby(base + [r[c] for c in cols]).transform('sum')
    num, den = s(x, []), s(w, [])
    if len(excl) == 1:
        num, den = num - s(x, excl), den - s(w, excl)
    else:  # inclusion-exclusion for the union of two classes
        a, b = excl
        num = num - s(x, [a]) - s(x, [b]) + s(x, [a, b])
        den = den - s(w, [a]) - s(w, [b]) + s(w, [a, b])
    return (num / den).where(den > 1e-9)


def main():
    os.makedirs(CACHE, exist_ok=True)
    d = v2.load_sample(INDEX)
    v2.log(f'Table 2 Panel A sample: {len(d):,} fund-months, {d.product_ids.nunique():,} funds')
    raw_all = pd.read_csv(INDEX, usecols=['product_j', 'month_t', 'product_exp_ratio', 'product_fund_name']).dropna(subset=['product_exp_ratio'])
    crsp = pd.read_csv(CRSP, usecols=['crsp_fundno', 'fund_name', 'lipper_class', 'crsp_obj_cd'], encoding='latin-1', dtype=str)
    crsp['crsp_fundno'] = crsp.crsp_fundno.astype(float).astype(int)
    mmf = v2.money_market_funds(crsp, set(raw_all.product_j))
    del crsp
    mmf_sample = sorted(set(mmf) & set(d.product_ids))
    d['mmf'] = d.product_ids.isin(mmf_sample).astype(int)
    d = d.join(v2.gene_idx(raw_all).rename('cheap'), on='product_ids')
    del raw_all
    v2.log(f'money market funds: {len(mmf)} in the CSV, {len(mmf_sample)} in the sample ({int(d.mmf.sum())} fund-months)')

    raw = v2.build_instrument(INDEX, CRSP, mmf)          # V2: money market funds out of the donor pool
    d = d.merge(raw[['product_j', 'month_t', 'Z', 'asset_class', 'share_class']].rename(columns={'product_j': 'product_ids'}),
                on=['product_ids', 'month_t'], how='left')
    del raw
    v2.log(f'V2 instrument defined on {int((d.Z.notna() & (d.mmf == 0)).sum()):,} non-MMF rows (expected 96,069)')

    # A5: fee tercile of funds at the fund's first sample month (step2_logit_screen.add_variables)
    first = d.sort_values('month_t').groupby('product_ids').first()
    terc = pd.qcut(first['prices'].rank(method='first'), 3, labels=False)
    d['fee_t1'] = d.product_ids.map(terc == 0).astype(float)
    d['fee_t2'] = d.product_ids.map(terc == 1).astype(float)

    # proxies for Danny's preferred IV0: all donors (money market funds included, as in the paper's IV0)
    r = v2.build_instrument(INDEX, CRSP, [])[['product_j', 'month_t', 'asset_class']].rename(columns={'asset_class': 'ac_all'})
    w = pd.read_csv(INDEX, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old',
                                    'product_exp_ratio', 'product_L1_mtna', 'BLP_IV_hausman_exp_ratio'])
    w = w.merge(r, on=['product_j', 'month_t'], how='left')
    w['market_m_index'] = w.market_m_index.fillna('_none_' + w.product_j.astype(str))
    w['R_idx'] = weighted_leave_out(w, ['market_m_index'])
    w['R_ac'] = weighted_leave_out(w, ['ac_all'])        # the class is assigned per index, so it nests the index
    w['R_clx'] = weighted_leave_out(w, ['market_m_index', 'market_m_cluster'])
    nest = w.groupby('market_m_index').ac_all.nunique().max()
    v2.log(f'asset classes per tracked index (max): {nest}; clusters: {w.market_m_cluster.nunique()}; indices: {w.market_m_index.nunique()}')
    d = d.merge(w[['product_j', 'month_t', 'ac_all', 'R_idx', 'R_ac', 'R_clx']].rename(columns={'product_j': 'product_ids'}),
                on=['product_ids', 'month_t'], how='left')
    del w, r
    iv0 = d.demand_instruments0
    rows = []
    for name, col in (('iv_ridx', 'R_idx'), ('iv4p', 'R_ac'), ('iv4q', 'R_clx')):
        d[name] = d[col].fillna(iv0)
        ok = d[col].notna()
        dd = (d[col] - iv0).abs()[ok]
        rows.append(dict(iv=name, raw_defined=int(ok.sum()), fallback_rows=int((~ok).sum()),
                         fallback_rows_blank_family=int((~ok & d.firm_f_old.isna()).sum()),
                         equal_to_iv0_1e8=float((dd < 1e-8).mean()), within_0005=float((dd < 5e-4).mean()),
                         corr_with_iv0=float(np.corrcoef(d[col][ok], iv0[ok])[0, 1]),
                         corr_with_iv0_blank_family=float(np.corrcoef(d[col][ok & d.firm_f_old.isna()], iv0[ok & d.firm_f_old.isna()])[0, 1])))
    v = pd.DataFrame(rows)
    v.to_csv('sc_iv_proxy_check.csv', index=False)
    print(v.round(4).to_string(index=False), flush=True)
    d.to_pickle(PANEL)
    v2.log(f'panel cached: {len(d):,} rows, {d.shape[1]} columns')


if __name__ == '__main__':
    main()
