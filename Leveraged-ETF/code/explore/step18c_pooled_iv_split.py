"""Why does one common slope on the 1,103 non-switching funds (lag-60 status constant, 20th pct) give +14?

The one-slope logit IV is alpha = sum(h~ y~) / sum(h~ p~), with h~, p~, y~ = Hausman IV, fee and delta after
partialling out fund FE, month FE and the controls (Frisch-Waugh). Both sums split exactly into the cheap funds' part
and the non-cheap funds' part:
    alpha = (RF_cheap + RF_rest) / (FS_cheap + FS_rest)
Each group's own ratio RF_g / FS_g is that group's slope implied by this residual variation. If FS_cheap and FS_rest
have opposite signs, the pooled ratio is not between the two group ratios and can even have the opposite sign.

    python step18c_pooled_iv_split.py     # from a folder holding the index CSV
"""
import numpy as np
import pandas as pd
import pyhdfe

import common
from step2_logit_screen import add_variables, CONTROLS, H
from tiers import RAW

d = add_variables(common.load('index'))
raw = pd.read_csv(RAW, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
raw['month_key'] = np.round(raw.month_t * 12).astype(int)
cut = raw.groupby('month_key').product_exp_ratio.quantile(0.20)
raw['c'] = (raw.product_exp_ratio <= raw.month_key.map(cut) + 1e-9).astype(float)
raw = raw.rename(columns={'product_j': 'product_ids'}).sort_values('month_key')
left = d[['product_ids', 'month_key']].copy()
left['target'] = left.month_key - 60
left = left.sort_values('target')
m = pd.merge_asof(left, raw[['product_ids', 'month_key', 'c']].rename(columns={'month_key': 'target'}),
                  on='target', by='product_ids', direction='backward').set_index(left.index).sort_index()
d['z'] = np.where(m.c.notna(), m.c, d.raw20)
d['delta'] = np.log(d.shares) - np.log(1 - d.groupby('market_ids').shares.transform('sum'))


def split(dd, group, label):
    dd = dd.reset_index(drop=True)
    ids = np.column_stack([pd.factorize(dd.product_ids)[0], pd.factorize(dd.market_ids)[0]])
    alg = pyhdfe.create(ids, drop_singletons=False)
    W = alg.residualize(dd[CONTROLS].to_numpy(float))
    part = lambda c: (lambda M: M - W @ np.linalg.lstsq(W, M, rcond=None)[0])(alg.residualize(dd[[c]].to_numpy(float))).ravel()
    h, p, y = part(H), part('prices'), part('delta')
    rows = []
    for gname, mask in ((f'{label}=1 (cheap)', dd[group] == 1), (f'{label}=0 (not cheap)', dd[group] == 0)):
        mk = mask.to_numpy()
        fs, rf = float(h[mk] @ p[mk]), float(h[mk] @ y[mk])
        rows.append(dict(group=gname, funds=dd[mask].product_ids.nunique(), fund_months=int(mk.sum()),
                         FS=fs, RF=rf, own_ratio=rf / fs,
                         sd_fee_within=float(p[mk].std()), sd_H_within=float(h[mk].std()),
                         corr_H_fee=float(np.corrcoef(h[mk], p[mk])[0, 1])))
    fs, rf = float(h @ p), float(h @ y)
    rows.append(dict(group='pooled', funds=dd.product_ids.nunique(), fund_months=len(dd), FS=fs, RF=rf, own_ratio=rf / fs,
                     sd_fee_within=float(p.std()), sd_H_within=float(h.std()), corr_H_fee=float(np.corrcoef(h, p)[0, 1])))
    return pd.DataFrame(rows)


pd.set_option('display.width', 250)
sw = d.groupby('product_ids').z.transform('nunique') > 1
for name, dd in (('1,103 non-switching funds', d[~sw]), ('all funds (Table 2 sample), split by entry tier', d)):
    grp = 'z' if name.startswith('1,103') else 'raw20'
    t = split(dd, grp, grp)
    print(f'\n=== {name}: one-slope logit IV split into groups ===')
    print(t.round(4).to_string(index=False), flush=True)
    t.to_csv(f'step18c_split_{grp}.csv', index=False)
