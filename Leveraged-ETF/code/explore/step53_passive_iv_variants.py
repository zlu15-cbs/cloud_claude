"""Carry Danny's 25 Nov leveraged-instrument redesign over to the passive instruments, and test them.

    python -I step53_passive_iv_variants.py PACKAGE_DIR NAMES_CSV PROCS      # PACKAGE_DIR = section3_replication/

His v13 package leaves the passive sample, instruments and fits unchanged. In the leveraged market he replaced the
rival counts with versions that (i) apply no fee or tracking gate, (ii) use binary ETF / mutual-fund access instead
of the three-way CRSP flag, and (iii) add benchmark breadth. The passive IV1 and IV4 still match rivals on the
fund's own lagged fee (within 10 bp), tracking error and three-way access. This script rebuilds the passive rival
instruments from his prepared construction panels (read-only; none of his code is run), checks that the gated
versions reproduce his archived IV1, IV2 and IV4 exactly, and then builds:

  n1_3 / n1_v / n1_a   IV1 without the fee and tracking gates; access matched three-way / ETF-MF / not at all
  x4_3 / x4_v / x4_a   IV4 (certified exits in [t-12, t-1]) without the gates; same three access rules
  r2_a                 IV2 (prior other-family offerings outside the fund's asset class) without the vehicle match
  br_v / br_a          breadth: distinct other benchmarks offered by other families in the same asset class
                       (and vehicle / any vehicle), current month, broad roster (his leveraged IV1 design)

Screens as step51/52 (fund FE; month FE; month-clustered SE): static (Table 7) and with the lagged share.
Writes step53_passive_iv_variants.csv (coefficients only) and step53_new_ivs.npz in the working directory
(instrument columns keyed by his source_row; not for upload).
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step51_one_menu as m
from step51_one_menu import Panel, IV, CON, BASE


def read(P, name):
    return pd.read_csv(f'{P}/data/iv_inputs/{name}.csv.gz', keep_default_na=False, low_memory=False)


def local_stock(f, gate, access, band=.10):
    """Other-family certified rivals in the inside menu at t-1, same asset class; optional gates and access rule."""
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
        mt &= t.p8.to_numpy()[:, None] == d.p8.to_numpy()
        mt &= d.certified.to_numpy(bool)
        if access == 3:
            mt &= t.access3.to_numpy()[:, None] == d.access3.to_numpy()
        elif access == 2:
            mt &= t.vehicle.to_numpy()[:, None] == d.vehicle.to_numpy()
        if gate in (True, 'fee'):
            mt &= abs(t.price.to_numpy()[:, None] - d.price.to_numpy()) <= band + 1e-12
        if gate in (True, 'tracking'):
            mt &= abs(t.tracking.to_numpy()[:, None] - d.tracking.to_numpy()) <= .02
        out[tr] = mt.sum(1)
    return out


def exits(f, hist, ev, gate, access, band=.10):
    """Certified liquidations in [t-12, t-1] of other-family classes in the same asset class as the focal t-1 anchor."""
    out = np.zeros(len(f))
    num = lambda s: pd.to_numeric(s, errors='coerce')
    hist = hist.assign(access3=num(hist.access3), price=num(hist.price), tracking=num(hist.tracking))
    ev = ev.assign(access3=num(ev.access3), price=num(ev.price), tracking=num(ev.tracking))
    idx = hist.set_index(['crsp_id', 'month'])
    anchor = idx.reindex(pd.MultiIndex.from_arrays([f.crsp_id, f.month - 1])).reset_index(drop=True)
    veh = lambda a: (a == 2).astype(int)
    for month, rows in f.groupby('month', sort=False).indices.items():
        d = ev.loc[ev.event_month.between(month - 12, month - 1)]
        if d.empty:
            continue
        a = anchor.iloc[rows]
        sup = a.family.notna() & a.family.ne('') & a.p8.notna() & a.p8.ne('')
        sup &= a.access3.isin([0, 1, 2]) & np.isfinite(a.price) & np.isfinite(a.tracking)
        r, a = rows[sup.to_numpy()], a.loc[sup]
        mt = f.iloc[r].crsp_id.to_numpy()[:, None] != d.crsp_id.to_numpy()
        mt &= a.family.to_numpy()[:, None] != d.family.to_numpy()
        mt &= a.p8.to_numpy()[:, None] == d.p8.to_numpy()
        mt &= d.p8.ne('').to_numpy()
        if access == 3:
            mt &= a.access3.to_numpy()[:, None] == d.access3.to_numpy()
        elif access == 2:
            mt &= veh(a.access3.to_numpy())[:, None] == veh(d.access3.to_numpy())
        if gate:
            mt &= abs(a.price.to_numpy()[:, None] - d.price.to_numpy()) <= band + 1e-12
            mt &= abs(a.tracking.to_numpy()[:, None] - d.tracking.to_numpy()) <= .02 + 1e-12
        out[r] = mt.sum(1)
    return out


def remote(f, b, vehicle):
    """Other-family prior offerings outside the fund's (possible) asset class; optional same-vehicle match."""
    out = np.zeros(len(f))
    don = b.loc[b.certified.astype(bool) & b.family.ne('') & b.benchmark.ne('')]
    menus = don.groupby('month', sort=False).indices
    for month, rows in f.groupby('month', sort=False).indices.items():
        pos = menus.get(month - 1)
        if pos is None:
            continue
        d, x = don.iloc[pos], f.iloc[rows]
        mt = np.where(x.certified.to_numpy(bool)[:, None], x.p8.to_numpy()[:, None] != d.p8.to_numpy(), d.p8.eq('direct_real_asset').to_numpy())
        if vehicle:
            mt = mt & (x.vehicle.to_numpy()[:, None] == d.vehicle.to_numpy())
        mt &= x.family.to_numpy()[:, None] != d.family.to_numpy()
        mt &= x.benchmark.to_numpy()[:, None] != d.benchmark.to_numpy()
        mt &= x.crsp_id.astype(str).to_numpy()[:, None] != d.crsp_id.astype(str).to_numpy()
        out[rows] = mt.sum(1)
    return out


def breadth(f, b, vehicle):
    """Distinct other benchmarks offered this month by other families in the same asset class (and vehicle)."""
    don = b.loc[b.certified.astype(bool) & b.family.ne('') & b.benchmark.ne('')]
    keys = ['month', 'p8'] + (['vehicle'] if vehicle else [])
    fams = don.groupby(keys + ['benchmark']).family.agg(lambda s: frozenset(s)).reset_index()
    groups = {k: dict(zip(g.benchmark, g.family)) for k, g in fams.groupby(keys)}
    out, cache = np.zeros(len(f)), {}
    cols = [f[k].to_numpy() for k in keys]
    fam, bm, cert = f.family.to_numpy(), f.benchmark.to_numpy(), f.certified.to_numpy(bool)
    for i in range(len(f)):
        if not cert[i] or bm[i] == '' or fam[i] == '':
            continue
        gk = tuple(c[i] for c in cols)
        ck = (gk, fam[i], bm[i])
        if ck not in cache:
            g = groups.get(gk, {})
            cache[ck] = sum(1 for b_, fs in g.items() if b_ != bm[i] and (len(fs) > 1 or fam[i] not in fs))
        out[i] = cache[ck]
    return out


def main(P, names):
    d = m.prep(P, f'{P}/data/iv_inputs', names)
    f, b = read(P, 'passive_focal'), read(P, 'passive_broad')
    assert (f.source_row.to_numpy() == np.load(f'{P}/data/prepared/passive.npz', allow_pickle=False)['source_row']).all()
    hist, ev = read(P, 'passive_exit_history'), read(P, 'passive_certified_exits')
    chk = {'IV1': (local_stock(f, True, 3), IV[1]), 'IV2': (remote(f, b, True), IV[2]), 'IV4': (exits(f, hist, ev, True, 3), IV[4])}
    for k, (mine, col) in chk.items():
        print(f'reproduce {k}: max abs difference from his archived column {np.abs(mine - d[col].to_numpy()).max():.3g}', flush=True)
    new = {'n1_3': local_stock(f, False, 3), 'n1_v': local_stock(f, False, 2), 'n1_a': local_stock(f, False, 0),
           'x4_3': exits(f, hist, ev, False, 3), 'x4_v': exits(f, hist, ev, False, 2), 'x4_a': exits(f, hist, ev, False, 0),
           'r2_a': remote(f, b, False), 'br_v': breadth(f, b, True), 'br_a': breadth(f, b, False)}
    np.savez_compressed('step53_new_ivs.npz', source_row=f.source_row.to_numpy(), **new)
    for k, v in new.items():
        d[k] = v
    old = {'n1': IV[1], 'x4': IV[4], 'r2': IV[2]}
    print('\nNew columns: mean, SD, share positive, correlation with the archived instrument it replaces')
    for k, v in new.items():
        ref = old.get(k[:2])
        print(f'  {k}: {v.mean():8.3f} {v.std():8.3f} {float((v > 0).mean()):.3f}' + (f'  corr {np.corrcoef(v, d[ref])[0, 1]:.3f}' if ref else ''))

    SETS = {'his five': IV,
            'gates removed (3-way access)': [IV[0], 'n1_3', IV[2], IV[3], 'x4_3'],
            'gates removed, ETF/MF access': [IV[0], 'n1_v', IV[2], IV[3], 'x4_v'],
            'one menu: no access match, IV2 any vehicle': [IV[0], 'n1_a', 'r2_a', IV[3], 'x4_a'],
            'one menu, no IV2': [IV[0], 'n1_a', IV[3], 'x4_a'],
            'one menu + breadth': [IV[0], 'n1_a', 'br_a', IV[3], 'x4_a'],
            'ETF/MF access + breadth, no IV2': [IV[0], 'n1_v', 'br_v', IV[3], 'x4_v']}
    cols = BASE + list(new) + ['y_lag']
    L = d.dropna(subset=['y_lag'])
    pans = {'static': Panel(d, ['market_ids'], BASE + list(new), 'static'), 'lag': Panel(L, ['market_ids'], cols, 'lag')}
    sub = {(k, v): Panel((d if k == 'static' else L)[lambda x: x.etf == v], ['market_ids'], BASE + list(new) + (['y_lag'] if k == 'lag' else []),
                         f'{k}; {"ETF" if v else "mutual-fund"} rows') for k in ('static', 'lag') for v in (0, 1)}
    for mode, con in (('static', ()), ('lag', ('y_lag',))):
        p = pans[mode]
        print(f'\n=== {mode}: one instrument at a time (logit fee slope)')
        for k in list(new):
            p.tag = mode
            p.est(['prices'], [k], f'{k} alone', con)
        for name, Z in SETS.items():
            print(f'--- {mode}: {name}')
            p.tag = f'{mode}; {name}'
            p.est(['prices'], Z, 'logit', con)
            p.est(['prices', 'K'], Z, 'K', con)
            p.est(['prices', 'K', 'Ka'], Z, 'K + age K', con)
            for j in range(1, len(Z)):
                p.est(['prices', 'K'], [z for i, z in enumerate(Z) if i != j], f'K, without {Z[j].replace("demand_instruments", "IV")}', con)
            for v in (0, 1):
                q = sub[(mode, v)]
                q.tag = f'{mode}; {name}; {"ETF" if v else "mutual-fund"} rows'
                q.est(['prices'], Z, 'logit', con)
    pd.DataFrame(m.ROWS).to_csv('step53_passive_iv_variants.csv', index=False)


if __name__ == '__main__':
    m.PROCS = int(sys.argv[3])
    main(sys.argv[1], sys.argv[2])
