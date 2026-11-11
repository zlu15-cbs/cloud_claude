"""Who are the high-entry-fee funds, and does their demand slope upward?

Entry-fee rank: percentile rank of the fund's fee in its entry-month cross-section (first month on or after January 2005,
index CSV). Checks: (1) who is in each rank quartile; (2) a separate fee slope per quartile (dummies, not a line);
(3) the top quartile and the top half estimated alone, split by broad-based / specialized; (4) the largest top-quartile funds.
Instrument: V2's Z (and Z x group). Money market funds dropped.
"""
import os, sys
import numpy as np, pandas as pd, pyblp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2
from sc_build import DATA, PANEL
from sc_demand import fit
pyblp.options.verbose = False
pd.set_option('display.width', 250, 'display.max_columns', 30, 'display.max_colwidth', 48)
d = pd.read_pickle(PANEL)
cf = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'month_t', 'product_exp_ratio', 'product_fund_name']).dropna(subset=['product_exp_ratio'])
x = cf[cf.month_t >= 2005 - 1e-9]
x = x.assign(r=x.groupby('month_t').product_exp_ratio.rank(pct=True))
e = x.sort_values('month_t').groupby('product_j').first()
d['rank'] = d.product_ids.map(e.r); d['entry_fee'] = d.product_ids.map(e.product_exp_ratio)
d['name'] = d.product_ids.map(cf.groupby('product_j').product_fund_name.last())
d['q'] = np.clip(np.ceil(d['rank'] * 4), 1, 4)
d['spec'] = (d.broad_specialized != 'broad-based').astype(float)
m = (d.mmf == 0) & d.Z.notna() & d['rank'].notna()
est = d[m].reset_index(drop=True)
print('1. Who is in each entry-fee quartile (estimation fund-months)')
g = est.groupby('q')
tab = pd.DataFrame({'fund_months': g.size(), 'funds': g.product_ids.nunique(), 'mean_fee': g.prices.mean(), 'specialized': g.spec.mean(),
                    'etf': g.apply(lambda z: (z.share_class == 'etf').mean()), 'retail': g.apply(lambda z: (z.share_class == 'retail').mean()),
                    'inst': g.apply(lambda z: (z.share_class == 'inst').mean()), 'us_equity': g.apply(lambda z: (z.asset_class == 'us_equity').mean()),
                    'aum_share': g.product_mtna.sum() / est.product_mtna.sum(),
                    'within_fund_fee_sd': g.apply(lambda z: (z.prices - z.groupby('product_ids').prices.transform('mean')).std())})
print(tab.round(3).to_string())
print('asset class by quartile:'); print(pd.crosstab(est.q, est.asset_class, normalize='index').round(2).to_string(), flush=True)

def line(lab, o, zs):
    print(f"{lab:62s} N {o['N']:>6,} | base {o['b_prices']:8.3f} ({o['se_prices']:.3f}) | " + ' | '.join(f"x {z} {o['b_'+z]:.3f} ({o['se_'+z]:.3f})" for z in zs) + f" | F {o['min_F']:.0f} | e>0 {o['share_pos_e']:.3f}", flush=True)

print('\n2. A separate fee slope per quartile (base = quartile 1)')
for k in (2, 3, 4): est[f'q{k}'] = (est.q == k).astype(float)
o, res, dd, b = fit(est, 'Z', ['q2', 'q3', 'q4']); line('quartile dummies', o, ['q2', 'q3', 'q4'])
print('   implied slope by quartile:', {1: round(b['prices'], 2), **{k: round(b['prices'] + b[f'px_q{k}'], 2) for k in (2, 3, 4)}})
est['q34s'] = ((est.q >= 3) & (est.spec == 1)).astype(float); est['q34b'] = ((est.q >= 3) & (est.spec == 0)).astype(float)
o, res, dd, b = fit(est, 'Z', ['q2', 'q34b', 'q34s']); line('quartile 2; top half broad; top half specialized', o, ['q2', 'q34b', 'q34s'])
print('   implied slope:', {'q1': round(b['prices'], 2), 'q2': round(b['prices'] + b['px_q2'], 2), 'top half broad': round(b['prices'] + b['px_q34b'], 2), 'top half specialized': round(b['prices'] + b['px_q34s'], 2)})

print('\n3. Subsamples estimated alone (one slope, own fund and month effects)')
for lab, mm in (('quartile 1', est.q == 1), ('quartile 2', est.q == 2), ('quartile 3', est.q == 3), ('quartile 4', est.q == 4), ('top half (3-4)', est.q >= 3),
                ('top half, broad-based', (est.q >= 3) & (est.spec == 0)), ('top half, specialized', (est.q >= 3) & (est.spec == 1)),
                ('top half, ETF', (est.q >= 3) & (est.share_class == 'etf')), ('top half, mutual funds', (est.q >= 3) & (est.share_class != 'etf')),
                ('top half, US equity', (est.q >= 3) & (est.asset_class == 'us_equity')), ('top half, not US equity', (est.q >= 3) & (est.asset_class != 'us_equity'))):
    try:
        o, *_ = fit(est[mm].reset_index(drop=True), 'Z', []); line(lab, o, [])
    except Exception as ex:
        print(lab, 'failed:', str(ex)[:80])

print('\n4. Linear rank model with specialized funds removed, and with a separate line for them')
o, res, dd, b = fit(est[est.spec == 0].reset_index(drop=True), 'Z', ['rank']); line('rank 0-1, broad-based funds only', o, ['rank'])
o, res, dd, b = fit(est[est.spec == 1].reset_index(drop=True), 'Z', ['rank']); line('rank 0-1, specialized funds only', o, ['rank'])

print('\n5. The 25 largest funds in quartile 4 and in quartile 3 (by mean assets)')
for k in (4, 3):
    t = est[est.q == k].groupby('product_ids').agg(name=('name', 'first'), firm=('firm_ids', 'first'), type=('share_class', 'first'), asset=('asset_class', 'first'),
        label=('broad_specialized', 'first'), index=('market_m_index', 'first'), entry_fee=('entry_fee', 'first'), fee_first=('prices', 'first'), fee_last=('prices', 'last'),
        mean_aum=('product_mtna', 'mean'), months=('prices', 'size')).sort_values('mean_aum', ascending=False).head(25)
    t['index'] = t['index'].astype(str).str[:34]
    print(f'quartile {k}'); print(t.round(2).to_string())
