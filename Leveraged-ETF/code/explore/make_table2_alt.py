"""Assemble Table2_alt.md from the logit CSV (table2_alt_logit.py) and the BLP 1 RC summaries (step4_blp_shortlist.py).

    python make_table2_alt.py LOGS_EXPLORE_DIR LOGS_DIR > Table2_alt_tables.md
BLP sigma is read from the summary row when present, else parsed from the run log (logs/explore_table2_alt_blp_*.log).
"""
import os
import re
import sys

import pandas as pd

E, L = sys.argv[1], sys.argv[2]
logit = pd.read_csv(os.path.join(E, 'table2_alt_logit.csv'))
funds = pd.read_csv(os.path.join(E, 'table2_alt_funds.csv'))
VARS = [('prices', 'Expense ratio'), ('cheap*prices', 'Expense ratio × cheap'), ('product_past_1yr_ret', 'Past 1-yr return'),
        ('log_product_fund_age', 'Age (log)'), ('product_tracking_err', 'Tracking error')]


def coef(r, v):
    for k in (f'b[{v}]', f'b[{v.replace("cheap*prices", "prices*cheap")}]'):
        if k in r and pd.notna(r[k]):
            return f'{r[k]:.3f} ({r["se" + k[1:]]:.3f})'
    return ''


def sigma_from_log(path):
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    m = re.search(r'Sigma:\s+prices.*?\nprices\s+([+-][\d.E+-]+)\s*\n\s*\(([+-][\d.E+-]+)\)', txt, re.S)
    return (float(m.group(1)), float(m.group(2))) if m else None


def blp_row(panel, q):
    f = os.path.join(E, f'step4_A11_raw{q}_summary.csv' if panel == 'index' else f'step4_lev_A11_raw{q}_summary.csv')
    if not os.path.exists(f):
        return None
    r = pd.read_csv(f).iloc[0]
    if 'sigma' not in r or pd.isna(r.get('sigma')):
        s = sigma_from_log(os.path.join(L, f'explore_table2_alt_blp_{panel}_raw{q}.log'))
        if s:
            r['sigma'], r['sigma_se'] = s
    return r


for panel, title in (('index', 'Panel A: Passive index funds'), ('lev', 'Panel B: Passive leveraged funds')):
    print(f'\n### {title}\n')
    cols, heads = [], []
    for q in ('none (Table 2)', '10th pct', '15th pct', '20th pct'):
        for est in ('OLS', 'IV'):
            r = logit[(logit.panel == panel) & (logit.cutoff == q) & (logit.column == est)]
            if len(r):
                cols.append(('logit', r.iloc[0]))
                heads.append(f'{q}: Logit {est}')
        if q != 'none (Table 2)':
            b = blp_row(panel, int(q[:2]))
            cols.append(('blp', b))
            heads.append(f'{q}: BLP 1 RC')
    print('| | ' + ' | '.join(heads) + ' |')
    print('|---|' + '---|' * len(heads))
    for v, lab in VARS:
        print(f'| {lab} | ' + ' | '.join(coef(r, v) if r is not None else 'running' for _, r in cols) + ' |')
    print('| RC sd, expense ratio | ' + ' | '.join(
        (f'{r["sigma"]:.3f} ({r["sigma_se"]:.3f})' if r is not None and 'sigma' in r and pd.notna(r['sigma']) else
         ('running' if (k == 'blp' and r is None) else '')) for k, r in cols) + ' |')
    def stat(name, fmt, key):
        vals = []
        for k, r in cols:
            if r is None:
                vals.append('running')
            elif key in r and pd.notna(r[key]):
                vals.append(fmt.format(r[key]))
            else:
                vals.append('')
        print(f'| {name} | ' + ' | '.join(vals) + ' |')
    stat('N', '{:,.0f}', 'N')
    stat('Share of funds cheap', '{:.2f}', 'share_funds_cheap')
    stat('Weakest first-stage F', '{:.1f}', 'min_F')
    for k, r in cols:  # harmonise key names between logit and BLP rows
        if r is not None and 'avg_own_elasticity' in r:
            r['avg_own_e_market_mean'] = r['avg_own_elasticity']
        if r is not None and 'share_abs_e_gt1' not in r and 'share_gt1' in r:
            r['share_abs_e_gt1'] = r['share_gt1']
        if r is not None and 'share_neg_mc_bertrand_firm' in r:
            r['share_neg_mc'] = r['share_neg_mc_bertrand_firm']
    stat('**Avg own-price elasticity**', '**{:.3f}**', 'avg_own_e_market_mean')
    stat('Share of fund-months with abs(e) > 1', '{:.2f}', 'share_abs_e_gt1')
    stat('Share with positive own elasticity', '{:.3f}', 'share_pos_e')
    stat('Share with negative implied MC (firm Bertrand)', '{:.2f}', 'share_neg_mc')

print('\n### Table 5 funds: own elasticity in the last market (Panel A)\n')
blpf = {}
for q in (10, 15, 20):
    f = os.path.join(E, f'step4_A11_raw{q}_funds.csv')
    if os.path.exists(f):
        blpf[q] = pd.read_csv(f).set_index('product_ids').e_last
iv = funds[funds.column == 'IV']
base = iv[iv.cutoff == 'none (Table 2)'].set_index('product_ids')
heads = ['Table 5 (paper)'] + ['Logit IV, Table 2'] + [f'{q}th: cheap? / Logit IV / BLP 1 RC' for q in (10, 15, 20)]
print('| Fund | p (%) | ' + ' | '.join(heads) + ' |')
print('|---|---|' + '---|' * len(heads))
PAPER = {16416: -0.242, 56419: -0.580, 16417: -0.249, 16448: -1.494, 16437: -0.415, 27635: -0.725, 29218: -3.325,
         28279: -0.665, 28277: -0.666, 29250: -0.167, 63885: -0.160, 31461: -0.323, 50485: -0.243, 31466: -0.244,
         31462: -0.326}
for pid, r in base.iterrows():
    cells = [f'{PAPER[pid]:.2f}', f'{r.e_last:.2f}']
    for q in (10, 15, 20):
        x = iv[(iv.cutoff == f'{q}th pct') & (iv.product_ids == pid)].iloc[0]
        b = f'{blpf[q][pid]:.2f}' if q in blpf else 'running'
        cells.append(f'{"yes" if x.cheap else "no"} / {x.e_last:.2f} / {b}')
    print(f'| {r["name"]} | {r.p:.2f} | ' + ' | '.join(cells) + ' |')
