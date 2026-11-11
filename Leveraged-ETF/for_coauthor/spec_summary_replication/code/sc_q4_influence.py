"""Which funds drive the sign of T2 without the variable-annuity funds? IV slope = sum(z~ y~) / sum(z~ p~) after fund and month
effects and controls are partialled out; each fund's share of the numerator and denominator is its influence.
'Slope without the fund' subtracts the fund's terms (approximate: the fixed effects are not re-estimated)."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2
from sc_build import PANEL
from sc_q4 import entry_quartile
pd.set_option('display.width', 250, 'display.max_colwidth', 46)
d = pd.read_pickle(PANEL)
d = d[d.firm_f_old.notna()].reset_index(drop=True)
d['q'] = d.product_ids.map(entry_quartile())
d['y'] = np.log(d.shares)
R = v2.resid(d, ['y', 'prices', 'demand_instruments0'])
d['num'] = R[:, 2] * R[:, 0]; d['den'] = R[:, 2] * R[:, 1]; d['zr'] = R[:, 2]; d['pr'] = R[:, 1]
N, D = d.num.sum(), d.den.sum()
print(f'T2 without VA funds, paper instrument: slope {N / D:.3f} (numerator {N:.2f}, denominator {D:.3f}); rows {len(d):,}')
g = d.groupby('q')[['num', 'den']].sum()
g['fund_months'] = d.groupby('q').size(); g['funds'] = d.groupby('q').product_ids.nunique()
g['slope_without_group'] = (N - g.num) / (D - g.den); g['sd_resid_fee'] = d.groupby('q').pr.std(); g['sd_resid_iv'] = d.groupby('q').zr.std()
print('by entry-fee quartile:'); print(g.round(3).to_string())
f = d.groupby('product_ids').agg(name=('product_fund_name', 'last'), firm=('firm_ids', 'first'), q=('q', 'first'), months=('num', 'size'), num=('num', 'sum'), den=('den', 'sum'),
                                 fee_min=('prices', 'min'), fee_max=('prices', 'max'), iv_min=('demand_instruments0', 'min'), iv_max=('demand_instruments0', 'max'),
                                 aum=('product_mtna', 'mean'), first=('month_t', 'min'), last=('month_t', 'max'))
f['slope_without'] = (N - f.num) / (D - f.den)
f['name'] = f.name.str[:46]
print('\n20 funds with the largest effect on the slope (all quartiles):')
print(f.reindex((f.slope_without - N / D).abs().sort_values(ascending=False).index).head(20).round(3).to_string())
q4 = f[f.q == 4]
print('\nquartile 4 funds, by effect on the slope:')
print(q4.reindex((q4.slope_without - N / D).abs().sort_values(ascending=False).index).head(15).round(3).to_string())
order = (f.slope_without - N / D).sort_values().index   # funds whose removal lowers the slope most
n_, d_ = N, D
print('\ncumulative removal of the most influential funds (largest positive push first):')
for k, j in enumerate(order[:12], 1):
    n_ -= f.num[j]; d_ -= f.den[j]
    print(f'  {k:2d} funds removed -> slope {n_ / d_:8.3f}   (last removed: {f.name[j]}, quartile {int(f.q[j])})')
f.to_csv('sc_q4_influence.csv')
