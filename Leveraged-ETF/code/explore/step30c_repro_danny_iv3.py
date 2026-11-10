import numpy as np, pandas as pd
P = r"C:\Users\zlu15\Dropbox\P16_LeverageMKT\Data\source_intake\raw data"
pp = pd.read_csv(P + r"\index_funds_preprocess_oct2026.csv", usecols=['crsp_fundno','quarter','month','index','ETF','exp_ratio','fund_name','fund_family','L1_mtna1'])
fl = pd.read_csv(P + r"\CRSP_fund_summary_2026_qtrly_combined.csv", usecols=['crsp_fundno','quarter','retail_fund','inst_fund'], encoding='latin-1')
n0 = len(pp)
pp = pp.merge(fl, on=['crsp_fundno','quarter'], how='left')
print('rows before/after flag merge', n0, len(pp), '(R merge all.x would also duplicate)')
nm = pp.fund_name.fillna('').str.lower()
sc = pd.Series(pd.NA, index=pp.index, dtype=object)
sc[pp.ETF == 1] = 'etf'
c = sc.isna() & ((pp.inst_fund == 'Y') | nm.str.contains('institutional|inst|class i|class k|class y|class z|class r6|premier|select|admiral'))
sc[c] = 'inst'
c = sc.isna() & ((pp.retail_fund == 'Y') | nm.str.contains('investor|retail|class a|class c|class r|class t|service|advisor'))
sc[c] = 'retail'
sc[sc.isna()] = 'other'
pp['sc'] = sc
pp['mk'] = np.round(pp.month * 12).astype(int)
don = pp[pp.L1_mtna1.notna()]
# median over same family, same sc, other index, other fund; focal exp_ratio non-missing
keys = ['mk','fund_family','sc']
g_all = don.groupby(keys).exp_ratio.apply(lambda s: s.dropna().tolist()).rename('all')
g_idx = don.groupby(keys + ['index']).exp_ratio.apply(lambda s: s.dropna().tolist()).rename('own')
f = pp[pp.exp_ratio.notna() & pp.fund_family.notna()][['crsp_fundno','mk','fund_family','sc','index']].drop_duplicates(['crsp_fundno','mk'])
f = f.join(g_all, on=keys).join(g_idx, on=keys + ['index'])
def med(r):
    a = r['all'] if isinstance(r['all'], list) else []
    o = r['own'] if isinstance(r['own'], list) else []
    a = list(a)
    for v in o: a.remove(v)
    return np.median(a) if a else np.nan
f['V'] = f.apply(med, axis=1)
patch = pd.read_csv(P + r"\patch_hausman_share_class_exp_ratio_IV.csv")
patch['mk'] = np.round(patch.month_t * 12).astype(int)
m = patch.merge(f[['crsp_fundno','mk','V']].rename(columns={'crsp_fundno':'product_j'}), on=['product_j','mk'], how='left')
both = m.V.notna() & m.IV3_exp_ratio_med.notna()
d = (m.V - m.IV3_exp_ratio_med).abs()
print('defined: patch', m.IV3_exp_ratio_med.notna().sum(), 'repro', m.V.notna().sum(), 'both', both.sum())
print('exact share', (d[both] < 1e-9).mean().round(4), '| within .005', (d[both] < .005).mean().round(4))
print('sc shares', pp.sc.value_counts(normalize=True).round(3).to_dict())
x = m[m.V.isna() & m.IV3_exp_ratio_med.notna()].merge(pp[['crsp_fundno','mk','exp_ratio','fund_family','L1_mtna1','sc','index']].rename(columns={'crsp_fundno':'product_j'}), on=['product_j','mk'])
print('extra rows', len(x), '| focal exp_ratio NA', x.exp_ratio.isna().mean().round(3), '| family NA', x.fund_family.isna().mean().round(3))
print(x.head(3).to_string())
