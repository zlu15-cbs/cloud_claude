"""Reverse-engineer BLP_IV_hausman_exp_ratio (the Hausman IV used in every demand model; it arrives precomputed in the
index CSV and no notebook builds it).

Best match found: for fund j (fund family f = firm_f_old, tracked index m) in month t,
    H_jt = sum_{k in f, index(k) != m} ER_kt * AUM_{k,t-1} / sum_{k in f, index(k) != m} AUM_{k,t-1}
i.e. the previous-month-AUM-weighted average expense ratio of the same family's funds that track OTHER indices, over
all funds in the raw file. Also checks the two other Hausman variants: product_mgmt_fee is in basis points while the
expense ratio is in percent, and BLP_IV_hausman_op_cost = H_exp_ratio - H_mgmt_fee (mixing the two units).

    python step23_hausman_reconstruct.py     # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd

import common
from tiers import RAW

r = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'market_m_index', 'market_m_cluster', 'firm_f_old', 'firm_f', 'product_exp_ratio',
                              'product_mtna', 'product_L1_mtna', 'product_mgmt_fee', 'BLP_IV_hausman_exp_ratio',
                              'BLP_IV_hausman_op_cost', 'BLP_IV_hausman_mgmt_fee', 'product_ticker'])
r = r[r.product_exp_ratio.notna()].copy()
H = r.BLP_IV_hausman_exp_ratio


def rec(weight, firm='firm_f_old', leave='market_m_index'):
    w = r[weight]
    x = r.product_exp_ratio * w
    g1, g2 = [r[firm], r.month_t], [r[firm], r.month_t, r[leave]]
    v = (x.groupby(g1).transform('sum') - x.groupby(g2).transform('sum')) / (w.groupby(g1).transform('sum') - w.groupby(g2).transform('sum'))
    return v.where(np.isfinite(v))


rows = []
for weight in ('product_L1_mtna', 'product_mtna'):
    for leave in ('market_m_index', 'market_m_cluster'):
        v = rec(weight, leave=leave)
        ok = v.notna()
        dd = (v[ok] - H[ok]).abs()
        rows.append(dict(weight=weight, leave_out=leave, defined=float(ok.mean()), match_0005=float((dd < 5e-4).mean()),
                         corr=float(np.corrcoef(v[ok], H[ok])[0, 1])))
print(pd.DataFrame(rows).round(4).to_string(index=False))
r['rec'] = rec('product_L1_mtna')
d = common.load('index')
m = d[['product_ids', 'month_t', 'demand_instruments0']].merge(
    r[['product_j', 'month_t', 'rec', 'firm_f_old']].rename(columns={'product_j': 'product_ids'}), on=['product_ids', 'month_t'], how='left')
dd = (m.rec - m.demand_instruments0).abs()
print(f'estimation sample: N {len(m):,}; reconstruction defined {m.rec.notna().mean():.3f} (family id missing {m.firm_f_old.isna().mean():.3f}); '
      f'match < 0.0005: {(dd < 5e-4).mean():.3f}; < 0.005: {(dd < 5e-3).mean():.3f}; '
      f'corr {np.corrcoef(m.rec[m.rec.notna()], m.demand_instruments0[m.rec.notna()])[0, 1]:.4f}')
print('mgmt fee <= 100 x expense ratio (i.e. in basis points):', round(float((r.product_mgmt_fee <= 100 * r.product_exp_ratio + 1e-6).mean()), 3),
      '| SPY mgmt fee / expense ratio:', r[r.product_ticker == 'SPY'][['product_mgmt_fee', 'product_exp_ratio']].iloc[-1].to_dict())
print('H_op_cost + H_mgmt_fee == H_exp_ratio:',
      round(float(((r.BLP_IV_hausman_op_cost + r.BLP_IV_hausman_mgmt_fee - H).abs() < 1e-3).mean()), 4))
