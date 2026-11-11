"""V2 with the cheap indicator classified at a later starting date.

Cheap = the fund's fee in its entry month is at or below the q-th percentile of that month's fees across source-panel funds
(observed fees only). Entry month = the fund's first source-panel month with an observed fee on or after START
(1993 = column 3 of RESULTS_spec_summary.md; 2005; 2010). Cutoffs 15, 20 and 25 percent. Instrument and sample as in V2.
Writes sc_v2_cheap_start.csv.
"""
import sys, numpy as np, pandas as pd, pyblp
sys.path.insert(0,'/home/user/cloud_claude/Leveraged-ETF/code/spec_compare')
import replicate_V2 as v2
from sc_build import CRSP, DATA, PANEL
from sc_demand import fit
from sc_v2_source_donors import downstream
pyblp.options.verbose=False
d=pd.read_pickle(PANEL); nomm=(d.mmf==0).to_numpy(); fam=d.firm_f_old.notna().to_numpy()
src=pd.read_csv(f'{DATA}/danny/index_funds_preprocess_oct2026.csv',usecols=['crsp_fundno','month','exp_ratio']).rename(columns={'crsp_fundno':'product_j','month':'month_t','exp_ratio':'fee'})
c=pd.read_csv(CRSP,usecols=['crsp_fundno','quarter','exp_ratio'],encoding='latin-1',dtype=str); c['crsp_fundno']=c.crsp_fundno.astype(float).astype(int)
er=pd.to_numeric(c.exp_ratio,errors='coerce'); ffq=c[er.notna()&(er.abs()<0.5)].assign(q=lambda x:x.quarter.astype(float)).groupby('crsp_fundno').q.min(); del c
obs=src[src.fee.notna()&((np.floor(np.round(src.month_t*12)/3)/4)>=src.product_j.map(ffq))]
n=obs.groupby('month_t').size()
print('funds in the cross-section: Jan 1993',int(n.get(1993.0,0)),'| Jan 1994',int(n[np.isclose(n.index,1994)].sum()),'| Jan 2000',int(n[np.isclose(n.index,2000)].sum()),'| Jan 2005',int(n[np.isclose(n.index,2005)].sum()),'| Jan 2010',int(n[np.isclose(n.index,2010)].sum()),flush=True)
key={31434:'VTSM-Inv',31432:'V500-Inv',31239:'VBond-Inv',16417:'AGG',31343:'V-FTSE-exUS-ETF'}
t2=set(d.product_ids)
def cheap(start,q):
    x=obs[obs.month_t>=start-1e-9]
    e=x.sort_values('month_t').groupby('product_j').first()
    ct=x.groupby('month_t').fee.quantile(q)
    return (e.fee<=e.month_t.map(ct)+1e-9).astype(float), e
base,_=cheap(1993,.2)
rows=[]
for start in (1993,2005,2010):
    _,e=cheap(start,.2); ee=e[e.index.isin(t2)]
    print(f'entry on or after {start}: Table 2 funds classified {len(ee)} of {len(t2)}; classified in the start month itself (existing funds) {int(np.isclose(ee.month_t,start).sum())}; cutoffs in the start month p15/p20/p25:',[round(float(obs[np.isclose(obs.month_t,start)].fee.quantile(q)),3) for q in (.15,.2,.25)],'| key funds fee then:',{n_:round(float(e.fee.get(f,np.nan)),3) for f,n_ in key.items()},flush=True)
    for q in (.15,.2,.25):
        ch,_=cheap(start,q)
        d['cheap']=d.product_ids.map(ch); d['gene_idx']=d.cheap
        m=nomm&d.Z.notna().to_numpy()&d.cheap.notna().to_numpy()
        o,res,dd,b=fit(d[m].reset_index(drop=True),'Z',['cheap'])
        t5=v2.table5(res,dd,d.assign(cheap=d.cheap.fillna(0),gene_idx=d.cheap.fillna(0)))
        dsup=d.assign(cheap=d.cheap.fillna(0))
        ds=downstream(dsup[nomm].reset_index(drop=True),['cheap'],b); dx=downstream(dsup[nomm&fam].reset_index(drop=True),['cheap'],b)
        st=' '.join(f"{n_}:{int(ch.get(f,-1))}" for f,n_ in key.items())
        r=dict(start=start,cutoff=q,N=o['N'],share_cheap=float(dd.cheap.mean()),alpha=o['b_prices'],se=o['se_prices'],alpha_x=o['b_cheap'],se_x=o['se_cheap'],F=o['min_F'],pos_e=o['share_pos_e'],t5=int((t5.own_elasticity<-1).sum()),negmc_B0=ds['B0'][0],negmc_B65=ds['B65'][0],below020_B65=ds['B65'][2],minmc=ds['B65'][1],vanguard_B0=ds['B0'][3],negmc_B0_noVA=dx['B0'][0],negmc_B65_noVA=dx['B65'][0])
        rows.append(r); pd.DataFrame(rows).to_csv('sc_v2_cheap_start.csv',index=False)
        print(f"start {start} cutoff {int(q*100)}% | N {r['N']:,} cheap share {r['share_cheap']:.3f} | non-cheap {r['alpha']:.3f} ({r['se']:.3f}) x cheap {r['alpha_x']:.3f} ({r['se_x']:.3f}) F {r['F']:.0f} | e>0 {r['pos_e']:.3f} | T5 {r['t5']}/15 | neg MC {r['negmc_B0']:.3f}-{r['negmc_B65']:.3f} (no VA {r['negmc_B0_noVA']:.3f}-{r['negmc_B65_noVA']:.3f}) | <-0.20 at B65 {r['below020_B65']:.3f} | Vanguard B0 {r['vanguard_B0']:.2f} | cheap? {st}",flush=True)
