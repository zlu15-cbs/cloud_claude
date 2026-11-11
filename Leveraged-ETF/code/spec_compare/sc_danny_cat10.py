"""Danny's preferred specification with his own category10 labels (column 2 of RESULTS_spec_summary.md, no longer a proxy).

Table 2 col 2 unchanged except IV0: lag-AUM-weighted mean fee of same-family donors (blank families pooled, as in the
original), excluding the target's exact benchmark and its category10 class; donors with an unknown category are left out;
all share types pooled; the original IV0 where the rebuilt one is undefined or the target's category is unknown (2,502 rows).
Inputs from Danny's handoff zip (v2_matched_comparison_handoff_20261110.zip, folder outputs/hausman-robustness-v1/passive):
classified_donors.csv (675,551 rows: fee, weight, family, benchmark, category10) and classified_targets.csv (108,300 rows).
Reference: -5.713 (0.747).
    SC_DANNY=/path/to/outputs/hausman-robustness-v1/passive python sc_danny_cat10.py [downstream | conduct D10 | conduct D10x]
  D10   all 108,300 rows          D10x  without the variable-annuity funds (100,529 rows)
"""
import os
import sys

import numpy as np
import pandas as pd
import pyblp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_V2 as v2  # noqa: E402
import sc_downstream  # noqa: E402
from sc_build import CACHE, DATA, PANEL  # noqa: E402
from sc_demand import fit  # noqa: E402

pyblp.options.verbose = False
DANNY = os.environ.get('SC_DANNY', f'{DATA}/danny_zip/x/V2_comparison_handoff/outputs/hausman-robustness-v1/passive')


def build_iv():
    dn = pd.read_csv(f'{DANNY}/classified_donors.csv', usecols=['fund_id', 'month_key', 'benchmark', 'family', 'fee', 'weight', 'category10'])
    tg = pd.read_csv(f'{DANNY}/classified_targets.csv', usecols=['fund_id', 'month_key', 'benchmark', 'family', 'stored_IV0', 'category10', 'variable_annuity'])
    dn['fam'] = dn.family.fillna('')
    tg['fam'] = tg.family.fillna('')

    def rebuilt(s, cats):
        w, x = s.weight.fillna(0.0), (s.fee * s.weight).fillna(0.0)
        g = [s.fam, s.month_key]

        def look(v, cols):
            t = v.groupby(g + [s[c] for c in cols], dropna=False).sum().rename('v').reset_index()
            t.columns = ['fam', 'month_key'] + cols + ['v']
            return tg.merge(t, on=['fam', 'month_key'] + cols, how='left').v.fillna(0).to_numpy()
        if cats:
            num = look(x, []) - look(x, ['benchmark']) - look(x, ['category10']) + look(x, ['benchmark', 'category10'])
            den = look(w, []) - look(w, ['benchmark']) - look(w, ['category10']) + look(w, ['benchmark', 'category10'])
        else:
            num, den = look(x, []) - look(x, ['benchmark']), look(w, []) - look(w, ['benchmark'])
        return np.where(den > 1e-9, num / np.where(den > 1e-9, den, 1), np.nan)
    tg['r_bench'] = rebuilt(dn, False)
    print(f'original IV0 rebuilt from the donor file: max abs difference from the stored IV0 {float((tg.r_bench - tg.stored_IV0).abs().max()):.1e}')
    tg['r_cat10'] = rebuilt(dn[dn.category10.notna()], True)
    tg.loc[tg.category10.isna(), 'r_cat10'] = np.nan
    print(f'category10 instrument: fallback rows {int(tg.r_cat10.isna().sum()):,} (Danny: 2,502); variable-annuity rows {int(tg.variable_annuity.sum()):,}')
    return tg


def demand():
    tg = build_iv()
    d = pd.read_pickle(PANEL)
    d['gene_idx'] = d.cheap
    d['mk'] = np.round(d.month_t * 12).astype(int)
    d = d.merge(tg[['fund_id', 'month_key', 'r_cat10', 'variable_annuity']].rename(columns={'fund_id': 'product_ids', 'month_key': 'mk'}),
                on=['product_ids', 'mk'], how='left')
    d['iv10'] = d.r_cat10.fillna(d.demand_instruments0)
    fam = d.firm_f_old.notna().to_numpy()
    assert ((d.variable_annuity == 1).to_numpy() == ~fam).all()
    rows, t5s = [], []
    for name, mask in (('D10', np.ones(len(d), bool)), ('D10x', fam)):
        o, res, dd, b = fit(d[mask].reset_index(drop=True), 'iv10', [])
        t5 = v2.table5(res, dd, d)
        o = dict(spec=name, **o, t5_lt_m1=int((t5.own_elasticity < -1).sum()), t5_n=len(t5))
        t5s.append(t5.assign(spec=name))
        np.save(f'{CACHE}/alpha_{name}.npy', np.full(int(mask.sum()), b['prices']))
        np.save(f'{CACHE}/rows_{name}.npy', np.flatnonzero(mask))
        rows.append(o)
        print(f"{name:5s} N {o['N']:,} | price {o['b_prices']:.3f} ({o['se_prices']:.3f}) | F {o['min_F']:.1f} | e>0 {o['share_pos_e']:.3f} | avg e {o['avg_e']:.2f} "
              f"(AUM-w {o['e_aum_weighted']:.2f}) | Table 5 e<-1 {o['t5_lt_m1']}/{o['t5_n']}", flush=True)
    pd.DataFrame(rows).to_csv('sc_danny_cat10_demand.csv', index=False)
    pd.concat(t5s).to_csv('sc_danny_cat10_table5.csv', index=False)


if __name__ == '__main__':
    pd.set_option('display.width', 250, 'display.max_columns', 40)
    sc_downstream.SPECS = ['D10', 'D10x']
    if len(sys.argv) > 1 and sys.argv[1] == 'downstream':
        sc_downstream.downstream()
    elif len(sys.argv) > 1 and sys.argv[1] == 'conduct':
        sc_downstream.conduct(sys.argv[2])
    else:
        demand()
