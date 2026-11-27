"""IV1 and IV4 with rivals matched on the fee at entry instead of last month's fee, following our "cheap" definition.

    python -I step60_entry_fee_band.py PACKAGE_DIR NAMES_CSV RAW_INDEX_CSV PROCS

Danny's IV1 / IV4 count rivals whose fee LAST MONTH is within 10 bp of the fund's own, so they move when rivals
reprice. "Cheap" (tiers.py) classifies a fund once, by its expense ratio in its first month in the full raw index
file (1994-2025), relative to all index funds that month. Using the same predetermined quantity for the matching
makes the counts move only when rivals enter or exit:

  lvl<w>   |entry fee of rival - entry fee of fund| <= w basis points                       (w = 5, 10, 15, 20)
  pct<w>   |entry-fee percentile of rival - of fund| <= w points, percentile within the raw   (w = 5, 10, 20)
           file's funds in each fund's own entry month ("relative to the market at the time")
  tier     same cheap tier: both at or below, or both above, the 20th percentile at entry   (our main cutoff)

Everything else is as in his IV1 / IV4: other family, same asset class (P8) and three-way access, tracking error
within 0.02 last month, inside menu at t-1 (IV1) or certified liquidations in [t-12, t-1] (IV4).
Screens as step51-55: fund and month FE, his controls, month-clustered SE and month-clustered Hansen J.
Writes step60_entry_fee_band.csv (coefficients only) and step60_new_ivs.npz in the working directory (not for upload).
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step51_one_menu as m
import step53_passive_iv_variants as s53
import tiers
from step51_one_menu import Panel, IV, BASE


def entry_table(raw_path):
    """Per fund: entry month, entry fee, cheap tier (20th percentile), and the entry fee's percentile that month."""
    e = tiers.raw_entry_tiers(qs=(0.20,), path=raw_path)
    raw = pd.read_csv(raw_path, usecols=['product_j', 'month_t', 'product_exp_ratio']).dropna(subset=['product_exp_ratio'])
    raw['pct'] = raw.groupby('month_t').product_exp_ratio.rank(pct=True, method='max')
    first = raw.sort_values('month_t').groupby('product_j').first()
    e['pct'] = first.pct.reindex(e.index)
    return e.rename(columns={'product_exp_ratio': 'fee0', 'month_t': 'month0', 'raw20': 'cheap'})


def close(a, b, kind, w):
    """Match matrix on the entry attribute: a (focal, n) against b (donor, k)."""
    if kind == 'tier':
        return a[:, None] == b[None, :]
    return np.abs(a[:, None] - b[None, :]) <= w + 1e-12


def local_stock(f, attr, kind, w):
    out = np.zeros(len(f))
    menus = f.groupby('month', sort=False).indices
    for month, rows in menus.items():
        dr = menus.get(month - 1)
        if dr is None:
            continue
        d = f.iloc[dr]
        prev = pd.Index(d.model_id).get_indexer(f.iloc[rows].model_id)
        ok = prev >= 0
        tr, t = rows[ok], d.iloc[prev[ok]]
        sup = t.certified.to_numpy(bool)
        tr, t = tr[sup], t.iloc[np.flatnonzero(sup)]
        mt = t.model_id.to_numpy()[:, None] != d.model_id.to_numpy()
        mt &= t.inside_family.to_numpy()[:, None] != d.inside_family.to_numpy()
        mt &= t.access3.to_numpy()[:, None] == d.access3.to_numpy()
        mt &= t.p8.to_numpy()[:, None] == d.p8.to_numpy()
        mt &= d.certified.to_numpy(bool)
        mt &= abs(t.tracking.to_numpy()[:, None] - d.tracking.to_numpy()) <= .02
        a, b = t[attr].to_numpy(float), d[attr].to_numpy(float)
        mt &= close(a, b, kind, w) & np.isfinite(a)[:, None] & np.isfinite(b)[None, :]
        out[tr] = mt.sum(1)
    return out


def exits(f, hist, ev, attr, kind, w):
    out = np.zeros(len(f))
    num = lambda s: pd.to_numeric(s, errors='coerce')
    hist = hist.assign(access3=num(hist.access3), price=num(hist.price), tracking=num(hist.tracking))
    ev = ev.assign(access3=num(ev.access3), price=num(ev.price), tracking=num(ev.tracking))
    anchor = hist.set_index(['crsp_id', 'month']).reindex(pd.MultiIndex.from_arrays([f.crsp_id, f.month - 1])).reset_index(drop=True)
    fa = f[attr].to_numpy(float)
    for month, rows in f.groupby('month', sort=False).indices.items():
        d = ev.loc[ev.event_month.between(month - 12, month - 1)]
        if d.empty:
            continue
        a = anchor.iloc[rows]
        sup = (a.family.notna() & a.family.ne('') & a.p8.notna() & a.p8.ne('') & a.access3.isin([0, 1, 2]) & np.isfinite(a.price) & np.isfinite(a.tracking)).to_numpy()
        r, a = rows[sup], a.loc[sup]
        mt = f.iloc[r].crsp_id.to_numpy()[:, None] != d.crsp_id.to_numpy()
        mt &= a.family.to_numpy()[:, None] != d.family.to_numpy()
        mt &= a.access3.to_numpy()[:, None] == d.access3.to_numpy()
        mt &= a.p8.to_numpy()[:, None] == d.p8.to_numpy()
        mt &= d.p8.ne('').to_numpy()
        mt &= abs(a.tracking.to_numpy()[:, None] - d.tracking.to_numpy()) <= .02 + 1e-12
        x, y = fa[r], d[attr].to_numpy(float)
        mt &= close(x, y, kind, w) & np.isfinite(x)[:, None] & np.isfinite(y)[None, :]
        out[r] = mt.sum(1)
    return out


VARIANTS = [('lvl5', 'fee0', 'band', 0.05), ('lvl10', 'fee0', 'band', 0.10), ('lvl15', 'fee0', 'band', 0.15), ('lvl20', 'fee0', 'band', 0.20),
            ('pct5', 'pct', 'band', 0.05), ('pct10', 'pct', 'band', 0.10), ('pct20', 'pct', 'band', 0.20), ('tier', 'cheap', 'tier', 0)]
MAIN = ('lvl10', 'pct10', 'tier')


def main(P, names, raw_path):
    d = m.prep(P, f'{P}/data/iv_inputs', names)
    e = entry_table(raw_path)
    f, hist, ev = s53.read(P, 'passive_focal'), s53.read(P, 'passive_exit_history'), s53.read(P, 'passive_certified_exits')
    for c in ('fee0', 'pct', 'cheap', 'month0'):
        f[c] = f.crsp_id.map(e[c]).to_numpy()
        ev[c] = pd.to_numeric(ev.crsp_id, errors='coerce').map(e[c]).to_numpy()
    per = f.drop_duplicates('crsp_id')
    print(f'funds {len(per)}; entry before Jan 2010: {(per.month0 < 2010).mean():.3f}; cheap at entry (20th pct): {per.cheap.mean():.3f}; '
          f'entry fee p10/p50/p90 {per.fee0.quantile(.1):.2f}/{per.fee0.median():.2f}/{per.fee0.quantile(.9):.2f}; exits with an entry fee {int(ev.fee0.notna().sum())} of {len(ev)}')
    d['fee0'], d['cheap0'] = f.fee0.to_numpy(), f.cheap.to_numpy()
    print('share of fund-months whose current fee is within 10 bp of the entry fee: %.3f; correlation of fee and entry fee across fund-months %.3f' % (
        (np.abs(d.prices - d.fee0) <= 0.10).mean(), np.corrcoef(d.prices, d.fee0)[0, 1]))
    new = {}
    for name, attr, kind, w in VARIANTS:
        new[f'e1_{name}'], new[f'e4_{name}'] = local_stock(f, attr, kind, w), exits(f, hist, ev, attr, kind, w)
    np.savez_compressed('step60_new_ivs.npz', source_row=f.source_row.to_numpy(), **new)
    for k, v in new.items():
        d[k] = v
    print('\nNew columns: mean, SD, correlation with his IV1 / IV4')
    for k, v in new.items():
        print(f'  {k}: {v.mean():7.3f} {v.std():7.3f}   corr {np.corrcoef(v, d[IV[1] if k[1] == "1" else IV[4]])[0, 1]:.3f}')

    L = d.dropna(subset=['y_lag'])
    cols = BASE + list(new)
    pans = {'static': Panel(d, ['market_ids'], cols, 'static'), 'lag': Panel(L, ['market_ids'], cols + ['y_lag'], 'lag')}
    sub = {(k, v): Panel((d if k == 'static' else L)[lambda x: x.etf == v], ['market_ids'], cols + (['y_lag'] if k == 'lag' else []), '') for k in ('static', 'lag') for v in (0, 1)}
    for mode, con in (('static', ()), ('lag', ('y_lag',))):
        p = pans[mode]
        print(f'\n=== {mode}: his five instruments (reference)')
        p.tag = f'{mode}; his five'
        p.est(['prices'], [IV[1]], 'IV1 alone, logit', con)
        p.est(['prices'], IV, 'logit', con)
        p.est(['prices', 'K'], IV, 'fee K', con)
        if mode == 'static':
            p.est(['prices', 'Ka'], IV, 'age K', con)
        for name, attr, kind, w in VARIANTS:
            Z = [IV[0], f'e1_{name}', IV[2], IV[3], f'e4_{name}']
            print(f'--- {mode}: entry-fee matching, {name}')
            p.tag = f'{mode}; {name}'
            p.est(['prices'], [f'e1_{name}'], 'entry-matched IV1 alone, logit', con)
            p.est(['prices'], [f'e4_{name}'], 'entry-matched IV4 alone, logit', con)
            p.est(['prices'], Z, 'logit', con)
            p.est(['prices', 'K'], Z, 'fee K', con)
            if mode == 'static':
                p.est(['prices', 'Ka'], Z, 'age K', con)
            if name in MAIN:
                for j in range(5):
                    Zj = [z for i, z in enumerate(Z) if i != j]
                    lab = Z[j].replace('demand_instruments', 'IV')
                    p.est(['prices', 'K'], Zj, f'fee K, without {lab}', con)
                    if mode == 'static':
                        p.est(['prices', 'Ka'], Zj, f'age K, without {lab}', con)
                p.est(['prices', 'K', 'Ka'], Z, 'fee K + age K', con)
                for v in (0, 1):
                    q = sub[(mode, v)]
                    q.tag = f'{mode}; {name}; {"ETF" if v else "mutual-fund"} rows'
                    q.est(['prices'], Z, 'logit', con)
    pd.DataFrame(m.ROWS).to_csv('step60_entry_fee_band.csv', index=False)


if __name__ == '__main__':
    m.PROCS = int(sys.argv[4])
    main(sys.argv[1], sys.argv[2], sys.argv[3])
