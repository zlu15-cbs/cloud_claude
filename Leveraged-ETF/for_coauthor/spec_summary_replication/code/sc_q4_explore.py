"""(1) Why the top entry-fee quartile has so few Table 2 funds; (2) family-code changes; (3) CRSP's index-fund flag."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sc_build import CRSP, DATA, PANEL
from sc_q4 import entry_quartile
pd.set_option('display.width', 250, 'display.max_colwidth', 60)
d = pd.read_pickle(PANEL)
q = entry_quartile(); d['q'] = d.product_ids.map(q)
cf = pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv', usecols=['product_j', 'month_t', 'product_mtna', 'market_share_m_denom_alt1', 'prefer', 'product_exp_ratio', 'firm_f_old', 'firm_f'])
cf['q'] = cf.product_j.map(q); cf['share'] = cf.product_mtna / cf.market_share_m_denom_alt1
w = cf[(cf.month_t >= 2010) & (cf.month_t <= 2024 + 8 / 12) & cf.product_exp_ratio.notna()]
print('1. Funds by entry-fee quartile: the whole index CSV in 2010-2024, and the Table 2 sample')
g = w.groupby('q')
t = pd.DataFrame({'csv_funds': g.product_j.nunique(), 'csv_fund_months': g.size(), 'median_assets_m': g.product_mtna.median(), 'share_fund_months_above_size_cut': g.apply(lambda z: (z.share >= 0.0001).mean()),
                  'prefer_1to5': g.apply(lambda z: z.prefer.isin([1, 2, 3, 4, 5]).mean()), 'table2_funds': d.groupby('q').product_ids.nunique(), 'table2_fund_months': d.groupby('q').size()})
print(t.round(3).to_string())
print('size cut: market share >= 0.0001, i.e. assets of about', round(float((w.market_share_m_denom_alt1 * 0.0001).median())), 'million (median month)')

print('\n2. Family-code changes within a fund (Table 2 sample)')
for col in ('firm_f_old', 'firm_ids'):
    n = d[d[col].notna()].groupby('product_ids')[col].nunique()
    ch = n[n > 1].index
    print(f'  {col}: {len(ch)} of {d.product_ids.nunique()} funds have more than one value; by entry-fee quartile {d[d.product_ids.isin(ch)].drop_duplicates("product_ids").q.value_counts().sort_index().to_dict()}; '
          f'fund-months of those funds {int(d.product_ids.isin(ch).sum()):,}')
src = pd.read_csv(f'{DATA}/danny/index_funds_preprocess_oct2026.csv', usecols=['crsp_fundno', 'month', 'mgmt_cd', 'mgmt_name', 'fund_family'])
print('  source panel: distinct mgmt_cd', src.mgmt_cd.nunique(), '| distinct fund_family', src.fund_family.nunique(), '| mgmt_cd == fund_family on', round(float((src.mgmt_cd.fillna('') == src.fund_family.fillna('')).mean()), 3), 'of rows')
print('  parent firms (firm_ids) in Table 2:', d.firm_ids.nunique(), '| family codes (firm_f_old):', d.firm_f_old.nunique(), '| family codes per parent firm (mean):', round(d.groupby('firm_ids').firm_f_old.nunique().mean(), 2))
ch = d[d.firm_f_old.notna()].groupby('product_ids').firm_f_old.nunique(); ch = ch[ch > 1].index
x = d[d.product_ids.isin(ch) & (d.q == 4)].sort_values('month_t')
print('  top-quartile funds with a family-code change:')
print(x.groupby('product_ids').agg(name=('product_fund_name', 'last'), codes=('firm_f_old', lambda s: ' -> '.join(pd.unique(s))), firms=('firm_ids', lambda s: ' -> '.join(pd.unique(s)))).to_string())
# size of the instrument's jump at a family-code change vs other months
d = d.sort_values(['product_ids', 'month_t'])
d['dz'] = d.groupby('product_ids').demand_instruments0.diff().abs(); d['dp'] = d.groupby('product_ids').prices.diff().abs()
d['chg'] = (d.firm_f_old != d.groupby('product_ids').firm_f_old.shift()) & d.groupby('product_ids').firm_f_old.shift().notna() & d.firm_f_old.notna()
print(f'  months with a family-code change: {int(d.chg.sum())}; mean |change in instrument| in those months {d.dz[d.chg].mean():.3f} vs {d.dz[~d.chg].mean():.4f} otherwise; mean |change in fee| {d.dp[d.chg].mean():.4f} vs {d.dp[~d.chg].mean():.4f}')
big = d[(d.dz > 0.15)]
print(f'  months in which the instrument moves by more than 0.15: {len(big)} ({big.product_ids.nunique()} funds); of these with a family-code change {int(big.chg.sum())}; with a fee change above 0.02: {int((big.dp > 0.02).sum())}')

print('\n3. CRSP index_fund_flag (B index-based, D pure index, E enhanced index) for Table 2 funds')
cr = pd.read_csv(CRSP, usecols=['crsp_fundno', 'quarter', 'index_fund_flag', 'et_flag', 'crsp_obj_cd', 'lipper_class', 'turn_ratio'], encoding='latin-1', dtype=str)
cr['crsp_fundno'] = cr.crsp_fundno.astype(float).astype(int)
cr = cr[cr.crsp_fundno.isin(set(d.product_ids))]
flag = cr.dropna(subset=['index_fund_flag']).groupby('crsp_fundno').index_fund_flag.agg(lambda s: s.value_counts().index[0])
ever = cr.groupby('crsp_fundno').index_fund_flag.agg(lambda s: ''.join(sorted(set(s.dropna()))))
et = cr.dropna(subset=['et_flag']).groupby('crsp_fundno').et_flag.agg(lambda s: s.value_counts().index[0])
turn = pd.to_numeric(cr.turn_ratio, errors='coerce').groupby(cr.crsp_fundno).median()
obj = cr.dropna(subset=['crsp_obj_cd']).groupby('crsp_fundno').crsp_obj_cd.agg(lambda s: s.value_counts().index[0])
f = d.groupby('product_ids').agg(name=('product_fund_name', 'last'), q=('q', 'first'), months=('prices', 'size'), aum=('product_mtna', 'mean'), fee=('prices', 'mean'), firm=('firm_ids', 'last'), va=('firm_f_old', lambda s: s.isna().all()))
f['flag'] = f.index.map(flag).fillna('none'); f['ever'] = f.index.map(ever); f['et'] = f.index.map(et).fillna('-'); f['turn'] = f.index.map(turn); f['obj'] = f.index.map(obj)
tot = d.product_mtna.sum()
f['aum_share'] = d.groupby('product_ids').product_mtna.sum() / tot
print(f.groupby('flag').agg(funds=('q', 'size'), fund_months=('months', 'sum'), aum_share=('aum_share', 'sum'), mean_fee=('fee', 'mean'), median_turnover=('turn', 'median'), etf=('et', lambda s: (s == 'F').mean()), va=('va', 'mean')).round(3).to_string())
print('flag by entry-fee quartile (funds):'); print(pd.crosstab(f.q, f.flag).to_string())
print('funds whose flag is not constant over time:', int((f.ever.str.len() > 1).sum()), f.ever.value_counts().to_dict())
for nm in ('PIMCO', 'Russell Investment', 'DB Commodity', 'DB Agric', 'SPDR S&P 500 ETF', 'Vanguard 500 Index', 'iShares MSCI Taiwan', 'Covered Call', 'Dimensional', 'IndexPLUS', 'Enhanced', 'Morningstar'):
    s = f[f.name.str.contains(nm, case=False, regex=False)]
    print(f'  name contains "{nm}": {len(s)} funds; flags {s.flag.value_counts().to_dict()}; objective codes {s.obj.value_counts().head(4).to_dict()}')
print('\nfunds with no flag, largest 25:'); print(f[f.flag == 'none'].sort_values('aum', ascending=False).head(25)[['name', 'q', 'aum', 'fee', 'et', 'turn', 'obj']].round(2).to_string())
print('\nfunds flagged E (enhanced) or B (index-based), largest 25:'); print(f[f.flag.isin(['E', 'B'])].sort_values('aum', ascending=False).head(25)[['name', 'flag', 'q', 'aum', 'fee', 'et', 'turn', 'obj']].round(2).to_string())
f.to_csv('sc_q4_fundflags.csv')
