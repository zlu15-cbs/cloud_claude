"""Raw-entry fee tiers: a fund is 'cheap' if its expense ratio in its first month with a recorded fee in the full raw
index CSV (1994-2025) is at or below that month's q-th percentile across all index funds with a recorded fee.
Used by step2g (logit IV), step8 (robustness) and step7 (BLP, group names 'raw10', 'raw20', ...)."""
import pandas as pd

RAW = 'nonLev_funds_product_month_level_v2_patched.csv'


def raw_entry_tiers(qs=(0.10, 0.20, 0.30), population=None, path=RAW):
    """DataFrame indexed by product_j with columns raw<pct> (1.0 cheap / 0.0 not), plus entry month and fee.
    population: optional set of product_j used to compute the monthly cutoffs (default: all funds in the raw file)."""
    raw = pd.read_csv(path, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
    base = raw if population is None else raw[raw.product_j.isin(population)]
    cut = base.groupby('month_t').product_exp_ratio.quantile(list(qs)).unstack()
    entry = raw.sort_values('month_t').groupby('product_j').first()
    for q in qs:
        entry[f'raw{round(q * 100)}'] = (entry.product_exp_ratio <= entry.month_t.map(cut[q]) + 1e-9).astype(float)
    return entry
