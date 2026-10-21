"""Build the markdown tables for EXPLORATION_price_heterogeneity.md from the logged result CSVs.

    python make_report_tables.py LOGS_EXPLORE_DIR > tables.md
"""
import os
import sys

import pandas as pd

L = sys.argv[1]
summ = pd.concat([pd.read_csv(os.path.join(L, f)) for f in ('step2_summary.csv', 'step2_summary_A7.csv')])
funds = pd.concat([pd.read_csv(os.path.join(L, f)) for f in ('step2_funds.csv', 'step2_funds_A7.csv')])
pos = pd.read_csv(os.path.join(L, 'step3_positive_loading.csv')).set_index('spec')


def price_terms(r):
    out = []
    for c in r.index:
        if c.startswith('b[') and ('prices' in c) and pd.notna(r[c]):
            t = c[2:-1]
            out.append(f'{t}: {r[c]:.3f} ({r["se[" + t + "]"]:.3f})')
    return '; '.join(out)


def fstats(r):
    v = [r[c] for c in r.index if c.startswith('F[') and pd.notna(r[c])]
    return f'{min(v):.1f}' + (' **<10**' if min(v) < 10 else '')


f15 = pd.DataFrame({'n15_gt1_last': funds.e_last.abs().gt(1).groupby(funds.spec).sum(),
                    'med15_last': funds.groupby('spec').e_last.median()})
print('| Spec | Tier | N | Price terms: coef (clustered SE) | min first-stage F | Avg own e | share abs(e)>1: all / broad / Big 3 | 15 funds: n abs(e)>1 (last mkt), median e | share e>0 loading | neg. MC: single-product / firm Bertrand |')
print('|---|---|---|---|---|---|---|---|---|---|')
for _, r in summ.iterrows():
    f = f15.loc[r.spec]
    print(f'| {r.spec} | {r.tier} | {int(r.N):,} | {price_terms(r)} | {fstats(r)} | {r.avg_own_elasticity:.3f} | '
          f'{r.share_abs_e_gt1:.2f} / {r.share_abs_e_gt1_broad:.2f} / {r.share_abs_e_gt1_big3:.2f} | '
          f'{int(f.n15_gt1_last)}/15, {f.med15_last:.2f} | {pos.loc[r.spec, "share_positive_loading"]:.3f} | '
          f'{r.share_neg_mc_single_product:.2f} / {r.share_neg_mc_bertrand_firm:.2f} |')

print('\nTier C diagnostics')
print('| Spec | z | within-fund corr(z, xi) | lead t-stat k=1 / 3 / 12 | within-fund AR(1) of xi |')
print('|---|---|---|---|---|')
for _, r in summ[summ.tier == 'C'].iterrows():
    for c in [c for c in r.index if c.startswith('corr_within[') and pd.notna(r[c])]:
        z = c[len('corr_within['):-1]
        print(f'| {r.spec} | {z} | {r[c]:.3f} | {r[f"lead1_t[{z}]"]:.2f} / {r[f"lead3_t[{z}]"]:.2f} / '
              f'{r[f"lead12_t[{z}]"]:.2f} | {r.xi_AR1_within:.3f} |')

# 15-fund table: paper Table 5 vs baseline and the best specs (last-market elasticity; mean firm-Bertrand markup level)
step1 = pd.read_csv(os.path.join(L, 'step1_blp1.csv'))[['product_ids', 'name', 'p', 's']]
step1['paper_e'] = -8.348 * step1.p * (1 - step1.s)  # = Table 5 to within 0.0005 (step 1b)
cols = [('baseline', 'logit IV baseline'), ('A1_broad', 'A1 broad, logit IV'), ('B1_logp_c0.01', 'B1 log p, logit IV')]
blp = [('A1_broad', 'A1 broad, BLP 1RC'), ('B1_logp_c0.01', 'B1 log p, BLP 1RC'), ('A5_fee_tercile', 'A5 fee tercile, BLP 1RC')]
t = step1.copy()
for spec, lab in cols:
    t[lab] = t.product_ids.map(funds[funds.spec == spec].set_index('product_ids').e_last)
for spec, lab in blp:
    f = pd.read_csv(os.path.join(L, f'step4_{spec}_funds.csv')).set_index('product_ids')
    t[lab] = t.product_ids.map(f.e_last)
    t[lab + ' markup'] = t.product_ids.map(f.mu_bertrand_firm_mean)
print('\n15 Table-5 funds: own elasticity in the last market')
labs = ['paper_e'] + [l for _, l in cols] + [l for _, l in blp]
print('| Fund | p (%) | ' + ' | '.join(['Table 5 (= -8.348 p(1-s))'] + labs[1:]) + ' |')
print('|---|---|' + '---|' * len(labs))
for _, r in t.iterrows():
    print(f'| {r["name"].split(": ")[-1][:48]} | {r.p:.2f} | ' + ' | '.join(f'{r[l]:.2f}' for l in labs) + ' |')
print('\nSame funds: mean Bertrand markup level (p - mc, percentage points; firm ownership), BLP 1RC specs')
print('| Fund | p (%) | ' + ' | '.join(l for _, l in blp) + ' |')
print('|---|---|' + '---|' * len(blp))
for _, r in t.iterrows():
    print(f'| {r["name"].split(": ")[-1][:48]} | {r.p:.2f} | ' + ' | '.join(f'{r[l + " markup"]:.3f}' for _, l in blp) + ' |')
