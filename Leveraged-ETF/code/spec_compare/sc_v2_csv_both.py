import sys, numpy as np, pandas as pd, pyblp
sys.path.insert(0,'/home/user/cloud_claude/Leveraged-ETF/code/spec_compare')
import replicate_V2 as v2
from sc_build import DATA, PANEL
from sc_demand import fit
from sc_v2_source_donors import downstream
pyblp.options.verbose=False
d=pd.read_pickle(PANEL); nomm=(d.mmf==0).to_numpy(); fam=d.firm_f_old.notna().to_numpy()
cf=pd.read_csv(f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv',usecols=['product_j','month_t','product_exp_ratio']).dropna()
x=cf[cf.month_t>=2005-1e-9]
e=x.sort_values('month_t').groupby('product_j').first(); ct=x.groupby('month_t').product_exp_ratio.quantile(0.20)
ch=(e.product_exp_ratio<=e.month_t.map(ct)+1e-9).astype(float)
print('CSV: funds in the cross-section in January 2005:',int(np.isclose(x.month_t,2005).sum()),'| p20 that month',round(float(ct[ct.index[np.isclose(ct.index,2005)][0]]),3))
d['cheap']=d.product_ids.map(ch); d['gene_idx']=d.cheap
m=nomm&d.Z.notna().to_numpy()
print('unclassified estimation rows:',int(d.cheap[m].isna().sum()))
o,res,dd,b=fit(d[m].reset_index(drop=True),'Z',['cheap'])
t5=v2.table5(res,dd,d)
ds=downstream(d[nomm].assign(cheap=lambda z:z.cheap.fillna(0)).reset_index(drop=True),['cheap'],b); dx=downstream(d[nomm&fam].reset_index(drop=True),['cheap'],b)
print(f"cheap from the CSV (from 2005) + CSV donors | N {o['N']:,} cheap share {dd.cheap.mean():.3f} | non-cheap {o['b_prices']:.3f} ({o['se_prices']:.3f}) x cheap {o['b_cheap']:.3f} ({o['se_cheap']:.3f}) F {o['min_F']:.0f} | e>0 {o['share_pos_e']:.3f} | avg e {o['avg_e']:.2f} | T5 {int((t5.own_elasticity<-1).sum())}/15 | neg MC {ds['B0'][0]:.3f}-{ds['B65'][0]:.3f} (no VA {dx['B0'][0]:.3f}-{dx['B65'][0]:.3f}) | Vanguard B0 {ds['B0'][3]:.2f}")
