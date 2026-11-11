"""Entry-fee quartile per fund: percentile rank of the fund's fee in its entry-month cross-section (index CSV; entry month =
first month on or after January 2005, or the fund's first month if it has none), cut at 0.25 / 0.50 / 0.75."""
import numpy as np
import pandas as pd
from sc_build import DATA


def entry_quartile():
    cf = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna()
    def er(x):
        return x.assign(r=x.groupby('month_t').product_exp_ratio.rank(pct=True)).sort_values('month_t').groupby('product_j').r.first()
    r_all = er(cf)
    r = er(cf[cf.month_t >= 2005 - 1e-9]).reindex(r_all.index).fillna(r_all)
    return np.clip(np.ceil(r * 4), 1, 4)
