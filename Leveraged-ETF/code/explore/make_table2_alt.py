"""Assemble the Table2_alt tables (markdown) from the result CSVs.

    python make_table2_alt.py LOGS_EXPLORE_DIR > tables.md

Per panel and cutoff, columns: Table 2 as published and replicated (logit OLS, logit IV, BLP 1 RC), then the
interaction model: logit OLS, logit IV, BLP 1 RC with the notebook's extra instrument (index: BLP_IV_newproduct_1,
LETF: BLP_IV_rival_funds1), BLP 1 RC with the squared Hausman IV as the extra instrument, and BLP 1 RC with
H, H x cheap and an uninteracted BLP_IV_newproduct_3 (exactly identified). Panel B (LETF) is Table 2 without an interaction.
"""
import os
import sys

import pandas as pd

E = sys.argv[1]
logit = pd.read_csv(os.path.join(E, 'table2_alt_logit.csv'))
VARS = [('prices', 'Expense ratio'), ('cheap', 'Expense ratio × cheap'), ('product_past_1yr_ret', 'Past 1-yr return'),
        ('log_product_fund_age', 'Age (log)'), ('product_tracking_err', 'Tracking error')]
# Table 2 col 3 (BLP 1 RC), replicated with the unmodified notebook cells (RESULTS_table2.md)
COL3 = {'index': {'b[prices]': -6.771, 'se[prices]': 0.837, 'b[product_past_1yr_ret]': 0.414,
                  'se[product_past_1yr_ret]': 0.034, 'b[log_product_fund_age]': 0.580, 'se[log_product_fund_age]': 0.010,
                  'b[product_tracking_err]': -0.505, 'se[product_tracking_err]': 0.074, 'sigma': 0.027,
                  'sigma_se': 0.013, 'N': 108300, 'avg_own_elasticity': -1.950},
        'lev': {'b[prices]': -6.484, 'se[prices]': 0.072, 'b[product_past_1yr_ret]': 0.261,
                'se[product_past_1yr_ret]': 0.037, 'b[log_product_fund_age]': 0.779, 'se[log_product_fund_age]': 0.045,
                'b[product_tracking_err]': -1.546, 'se[product_tracking_err]': 0.264, 'sigma': 2.084, 'sigma_se': 0.102,
                'N': 15401, 'avg_own_elasticity': -5.911}}


def read(path):
    p = os.path.join(E, path)
    return pd.read_csv(p).iloc[0].to_dict() if os.path.exists(p) else None


def coef(r, v):
    if r is None:
        return 'n/a'
    for k in r:
        if k.startswith('b[') and ((v == 'cheap' and ('raw' in k or 'cheap' in k)) or k == f'b[{v}]'):
            if pd.notna(r[k]):
                return f'{r[k]:.3f} ({r["se" + k[1:]]:.3f})'
    return ''


def val(r, keys, fmt):
    if r is None:
        return 'n/a'
    for k in keys:
        if k in r and pd.notna(r[k]):
            return fmt.format(r[k])
    return ''


for panel, title in (('index', 'Panel A: Passive index funds'), ('lev', 'Panel B: Passive leveraged funds')):
    base = {c: logit[(logit.panel == panel) & (logit.cutoff == 'none (Table 2)') & (logit.column == c)].iloc[0].to_dict()
            for c in ('OLS', 'IV')}
    for q in (10, 15, 20):
        alt = {c: logit[(logit.panel == panel) & (logit.cutoff == f'{q}th pct') & (logit.column == c)].iloc[0].to_dict()
               for c in ('OLS', 'IV')}
        if panel == 'index':
            blp_n, blp_h = read(f'step4_A11_raw{q}_summary.csv'), read(f'step4_A11_raw{q}_hsq_summary.csv')
            blp_3 = read(f'step4_A11_raw{q}_newproduct_3_noint_summary.csv')
            cols = [('(1) Logit OLS', base['OLS']), ('(2) Logit IV', base['IV']), ('(3) BLP 1 RC', COL3[panel]),
                    ('(1′) Logit OLS', alt['OLS']), ('(2′) Logit IV', alt['IV']),
                    ('(3′) BLP 1 RC, notebook IVs', blp_n), ('(3″) BLP 1 RC, Hausman² IV', blp_h),
                    ('(3‴) BLP 1 RC, newproduct_3 (exactly identified)', blp_3)]
        else:  # Panel B: no interaction (not significant in the paper's A7 logit); Table 2 as is
            if q != 10:
                continue
            cols = [('(1) Logit OLS', base['OLS']), ('(2) Logit IV', base['IV']), ('(3) BLP 1 RC', COL3[panel])]
        share = alt['IV']['share_funds_cheap']
        if panel == 'index':
            print(f'\n#### {title}: cheap = fee at first raw month ≤ {q}th percentile ({share:.0%} of funds)\n')
        else:
            print(f'\n#### {title}: no interaction (Table 2 as published and replicated)\n')
        print('| | ' + ' | '.join(h for h, _ in cols) + ' |')
        print('|---|' + '---|' * len(cols))
        for v, lab in VARS:
            print(f'| {lab} | ' + ' | '.join('' if (v == 'cheap' and h.startswith(('(1)', '(2)', '(3)'))) else coef(r, v)
                                            for h, r in cols) + ' |')
        print('| RC sd, expense ratio | ' + ' | '.join(
            (f'{r["sigma"]:.3f} ({r["sigma_se"]:.3f})' if r is not None and 'sigma' in r and pd.notna(r.get('sigma'))
             else ('' if 'BLP' not in h else 'n/a')) for h, r in cols) + ' |')
        print('| N | ' + ' | '.join(val(r, ['N'], '{:,.0f}') for _, r in cols) + ' |')
        print('| Weakest first-stage F | ' + ' | '.join(val(r, ['min_F'], '{:.1f}') for _, r in cols) + ' |')
        print('| **Avg own-price elasticity** | ' + ' | '.join(
            val(r, ['avg_own_e_market_mean', 'avg_own_elasticity'], '**{:.3f}**') for _, r in cols) + ' |')
        print('| Share abs(e) > 1 | ' + ' | '.join(val(r, ['share_abs_e_gt1'], '{:.2f}') for _, r in cols) + ' |')
        print('| Share e > 0 (upward-sloping) | ' + ' | '.join(val(r, ['share_pos_e'], '{:.3f}') for _, r in cols) + ' |')
        print('| Share negative MC (firm Bertrand) | ' + ' | '.join(
            val(r, ['share_neg_mc', 'share_neg_mc_bertrand_firm'], '{:.2f}') for _, r in cols) + ' |')

print('\n#### The 15 Table 5 funds: own elasticity in the last month (Panel A)\n')
funds = pd.read_csv(os.path.join(E, 'table2_alt_funds.csv'))
iv = funds[funds.column == 'IV']
PAPER = {16416: -0.242, 56419: -0.580, 16417: -0.249, 16448: -1.494, 16437: -0.415, 27635: -0.725, 29218: -3.325,
         28279: -0.665, 28277: -0.666, 29250: -0.167, 63885: -0.160, 31461: -0.323, 50485: -0.243, 31466: -0.244,
         31462: -0.326}
blp = {}
for q in (10, 15, 20):
    for tag, f in (('n', f'step4_A11_raw{q}_funds.csv'), ('h', f'step4_A11_raw{q}_hsq_funds.csv'),
                   ('3', f'step4_A11_raw{q}_newproduct_3_noint_funds.csv')):
        p = os.path.join(E, f)
        if os.path.exists(p):
            blp[(q, tag)] = pd.read_csv(p).set_index('product_ids').e_last
heads = ['Table 5', 'Logit IV (Table 2)'] + [f'{q}th: cheap? / logit IV / BLP notebook IVs / BLP Hausman² / BLP newproduct_3'
                                             for q in (10, 15, 20)]
print('| Fund | p (%) | ' + ' | '.join(heads) + ' |')
print('|---|---|' + '---|' * len(heads))
for pid, r in iv[iv.cutoff == 'none (Table 2)'].set_index('product_ids').iterrows():
    cells = [f'{PAPER[pid]:.2f}', f'{r.e_last:.2f}']
    for q in (10, 15, 20):
        x = iv[(iv.cutoff == f'{q}th pct') & (iv.product_ids == pid)].iloc[0]
        n = f'{blp[(q, "n")][pid]:.2f}' if (q, 'n') in blp else 'n/a'
        h = f'{blp[(q, "h")][pid]:.2f}' if (q, 'h') in blp else 'n/a'
        n3 = f'{blp[(q, "3")][pid]:.2f}' if (q, '3') in blp else 'n/a'
        cells.append(f'{"yes" if x.cheap else "no"} / {x.e_last:.2f} / {n} / {h} / {n3}')
    print(f'| {r["name"]} | {r.p:.2f} | ' + ' | '.join(cells) + ' |')
