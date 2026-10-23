"""Broad asset class of an index fund, for leave-out-asset-class Hausman instruments (step24).
Mapped clusters first (as in step2_logit_screen.ASSET_CLASS); otherwise keywords in the fund name and the tracked-index
code. Classes: us_equity, intl_equity, bond, allocation (target date, balanced, multi-asset), real_asset (commodity,
gold, REIT, real estate)."""
import re

import numpy as np
import pandas as pd

CLUSTER = {1: 'us_equity', 5: 'us_equity', 6: 'us_equity', 7: 'us_equity', 10: 'us_equity', 11: 'us_equity', 12: 'us_equity',
           23: 'us_equity', 3: 'intl_equity', 9: 'intl_equity', 46: 'intl_equity',
           2: 'bond', 16: 'bond', 25: 'bond', 26: 'bond', 52: 'bond', 17: 'allocation', 21: 'real_asset'}
KW = [
    ('allocation', r'target date|target retirement|retirement|lifestrategy|life strategy|allocation|balanced|lifecycle|life cycle|lifepath|multi-asset|target \d{4}'),
    ('real_asset', r'\bgold\b|silver|precious|commodit|\boil\b|natural gas|reit\b|real estate|realty|infrastructure|metals'),
    ('bond', r'bond|treasury|treas\b|govt|government|municipal|muni\b|tips\b|inflation|corporate|aggregate|fixed income|high yield|credit|mortgage|securitized|floating rate|duration|t-bill|money market|\bagg\b|ultra short|income fund'),
    ('intl_equity', r'international|intl|emerging|developed|ex-us|ex us|ex-u\.s|world|global|europe|euro|japan|china|india|brazil|pacific|asia|eafe|acwi|canada|mexico|korea|taiwan|germany|united kingdom|\buk\b|france|australia|latin|frontier|foreign|\bem\b'),
]
IDX_BOND = re.compile(r'^(L[A-Z0-9]*TR(UU)?|LMBITR|IBOX|C0A0|H0A0|BCOM)', re.I)


def classify(df):
    """df with market_m_cluster, product_fund_name, market_m_index -> Series of classes."""
    ac = df.market_m_cluster.map(CLUSTER)
    name = df.product_fund_name.fillna('').str.lower()
    out = pd.Series(np.nan, index=df.index, dtype=object)
    for cls, pat in KW:
        hit = name.str.contains(pat, regex=True) & out.isna()
        out[hit] = cls
    idx = df.market_m_index.fillna('').astype(str)
    out[out.isna() & idx.str.match(IDX_BOND)] = 'bond'
    out[idx.str.startswith('BCOM') & ac.isna()] = 'real_asset'
    res = ac.fillna(out).fillna('us_equity')
    return res


def classify_by_index(df):
    """One class per tracked index: the most common fund-level class among funds tracking it (so all share classes of a
    portfolio, and all funds tracking the same index, get the same class)."""
    fund_cls = classify(df)
    key = df.market_m_index.fillna('_none_' + df.product_j.astype(str))
    tab = pd.DataFrame({'key': key, 'cls': fund_cls, 'pj': df.product_j}).drop_duplicates(['pj'])
    mode = tab.groupby('key').cls.agg(lambda s: s.value_counts().index[0])
    return key.map(mode)
