"""Cheap indicators that use CRSP share classes as the reference universe (demand grid models 2-4; PLAN_demand_grid.md).

danny_founded(L=1, q=20, universe=None)  -- Danny's founded_<L>y_p<q> (coauthor note of 2 Nov 2026, section 4):
    * fee records: CRSP fund summary, collapsed to one record per (crsp_fundno, caldt); effective date max(caldt, fiscal_yearend)
    * launch proxy of a class founded at t = first_offer_dt: first numeric exp_ratio with caldt >= t
    * reference for a target founded at t: classes founded in [t - L calendar years, t), target excluded, whose launch-proxy
      fee is effective before t; universe=None -> all CRSP classes, else the given set of crsp_fundno
    * cheap = target proxy strictly below np.percentile(reference, q) (linear / type 7); missing fee or empty reference -> 0
gene_crsp(q=20)  -- the benchmark rule (tiers.raw_entry_tiers) with an all-CRSP reference:
    * target fee = the fund's fee in its first month in the raw index file (as the benchmark)
    * reference = every CRSP class alive in that month (first_offer_dt <= month end, end_dt missing or >= month start)
      with its latest fee effective on or before the month end; cheap = fee <= 20th percentile (pandas linear), ties cheap
Fees are in percent (CRSP decimal x 100), the units of `prices`.
"""
import numpy as np
import pandas as pd

CRSP = r'C:\Users\zlu15\Dropbox\P16_LeverageMKT\Data\source_intake\raw data\CRSP_fund_summary_2026_qtrly_combined.csv'
IDX = r'C:\Users\zlu15\Dropbox\P16_LeverageMKT\Data\source_intake\raw data\index_funds_preprocess_oct2026.csv'
LEV = r'C:\Users\zlu15\Dropbox\P16_LeverageMKT\Data\source_intake\raw data\final_lev_linktable_2006Q2_2024Q3.csv'

_cache = {}


def crsp_records():
    if 'rec' in _cache:
        return _cache['rec'], _cache['cls']
    s = pd.read_csv(CRSP, usecols=['crsp_fundno', 'caldt', 'exp_ratio', 'fiscal_yearend', 'first_offer_dt', 'end_dt'],
                    dtype={'fiscal_yearend': str, 'first_offer_dt': str, 'end_dt': str, 'caldt': str}, encoding='latin-1')
    s['caldt'] = pd.to_datetime(s.caldt, errors='coerce')
    s['fye'] = pd.to_datetime(s.fiscal_yearend, format='%m/%d/%Y', errors='coerce')
    s['fod'] = pd.to_datetime(s.first_offer_dt, format='%m/%d/%Y', errors='coerce')
    s['end'] = pd.to_datetime(s.end_dt, format='%m/%d/%Y', errors='coerce')
    cls = s.groupby('crsp_fundno').agg(fod=('fod', 'min'), end=('end', 'max'))
    rec = s[s.exp_ratio.notna() & np.isfinite(s.exp_ratio) & s.caldt.notna()]
    n_conflict = int((rec.groupby(['crsp_fundno', 'caldt']).exp_ratio.nunique() > 1).sum())
    rec = rec.sort_values(['crsp_fundno', 'caldt']).drop_duplicates(['crsp_fundno', 'caldt'], keep='last').copy()
    rec['eff'] = rec[['caldt', 'fye']].max(axis=1)
    rec['fee'] = rec.exp_ratio * 100
    print(f'CRSP: {len(s):,} rows, {len(cls):,} classes, {len(rec):,} (class, caldt) fee records, '
          f'{n_conflict} (class, caldt) with conflicting fees (kept last)', flush=True)
    _cache['rec'], _cache['cls'] = rec[['crsp_fundno', 'caldt', 'eff', 'fee']], cls
    return _cache['rec'], cls


def index_universe():
    a = set(pd.read_csv(IDX, usecols=['crsp_fundno'], encoding='latin-1').crsp_fundno.dropna().astype(int))
    b = set(pd.read_csv(LEV, usecols=['crsp_fundno'], encoding='latin-1').crsp_fundno.dropna().astype(int))
    print(f'index universe: {len(a):,} nonleveraged + {len(b):,} leveraged = {len(a | b):,} distinct classes', flush=True)
    return a | b


def launch_proxies():
    rec, cls = crsp_records()
    r = rec.merge(cls[['fod']], left_on='crsp_fundno', right_index=True)
    r = r[r.fod.notna() & (r.caldt >= r.fod)]
    lp = r.groupby('crsp_fundno').first()[['fod', 'caldt', 'eff', 'fee']]
    return lp


def danny_founded(L=1, q=20, universe=None):
    """Series indexed by crsp_fundno: 1/0 cheap for every class with a founding date; plus flags."""
    _, cls = crsp_records()
    lp = launch_proxies()
    donors = lp if universe is None else lp[lp.index.isin(universe)]
    donors = donors.sort_values('fod')
    tg = cls[cls.fod.notna()].join(lp[['fee']], how='left')
    out = []
    for t, g in tg.groupby('fod'):
        lo = t - pd.DateOffset(years=L)
        ref = donors[(donors.fod >= lo) & (donors.fod < t) & (donors.eff < t)]
        ref = ref[~ref.index.isin(g.index)]
        cut = np.percentile(ref.fee.to_numpy(), q) if len(ref) else np.nan
        out.append(pd.DataFrame({'fee': g.fee, 'cut': cut, 'n_ref': len(ref)}, index=g.index))
    o = pd.concat(out)
    o['cheap'] = ((o.fee < o.cut) & o.fee.notna() & o.cut.notna()).astype(int)
    o['flag_missing_fee'] = o.fee.isna().astype(int)
    o['flag_empty_ref'] = o.cut.isna().astype(int)
    return o


def gene_crsp(entry, q=0.20):
    """entry: DataFrame indexed by product_j with month_t (fractional year) and product_exp_ratio (percent) -- the
    output of tiers.raw_entry_tiers. Returns the same index with cut / cheap."""
    rec, cls = crsp_records()
    rec = rec.merge(cls, left_on='crsp_fundno', right_index=True).sort_values('eff')
    out = {}
    for mt in sorted(entry.month_t.unique()):
        mk = int(round(mt * 12))
        y, mo = divmod(mk, 12)  # month_t = year + (calendar month - 1) / 12 (index_funds_preprocess: 1998.1667 <-> 1998-03-31)
        start = pd.Timestamp(year=y, month=mo + 1, day=1)
        end = start + pd.offsets.MonthEnd(0)
        r = rec[rec.eff <= end]
        last = r.groupby('crsp_fundno').fee.last()
        alive = cls.index[(cls.fod <= end) & (cls.end.isna() | (cls.end >= start))]
        ref = last[last.index.isin(alive)]
        out[mt] = (ref.quantile(q) if len(ref) else np.nan, len(ref))
    cut = entry.month_t.map({k: v[0] for k, v in out.items()})
    n = entry.month_t.map({k: v[1] for k, v in out.items()})
    res = pd.DataFrame({'month_t': entry.month_t, 'fee': entry.product_exp_ratio, 'cut': cut, 'n_ref': n}, index=entry.index)
    res['cheap'] = (res.fee <= res.cut + 1e-9).astype(int)
    return res
