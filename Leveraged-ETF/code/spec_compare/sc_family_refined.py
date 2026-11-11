"""Refined family ID, starting from Danny's ownership ID (firm_f in the index CSV).

Principle: a fund's family is the firm that runs and markets it and earns most of its expense ratio. A trustee, an
administrator, a licensing sponsor, a white-label ETF platform or a second legal name of the same firm is not a family.

Rules, applied in this order to each fund's history of firm_f:
  1. ALIAS     two labels of one firm -> one name, everywhere (e.g. PDR Services -> State Street Global Advisors).
  2. ARTIFACT  a change of label between two specific names that is not a change of the firm running the fund:
               'fwd'  the earlier spell takes the later name (trustee / administrator / platform listed before the sponsor);
               'back' the later spell takes the earlier name (sponsor's fund relabelled to its platform).
  3. Every remaining change of name is a REAL acquisition or transfer. Nothing is decided fund by fund: a transition that is
     in neither table is real by default and is listed in the output, so the tables can be audited and extended.
The classification of each pair is a judgment from the firm names and public ownership history; it is recorded in
family_transitions.csv next to the number of funds it affects.

    family, switches = refined_family()      # fund-month refined ID; real switches (fund, month, from, to)
"""
import numpy as np
import pandas as pd
from sc_build import DATA

CSVP = f'{DATA}/nonLev_funds_product_month_level_v2_patched.csv'

ALIAS = {   # label -> canonical name of the same firm
    'PDR Services': 'State Street Global Advisors',            # licensing sponsor of the SPDR trusts; State Street runs them
    'Unknown': 'State Street Global Advisors',                 # the two GE RSP funds after GE Asset Management was sold to State Street
    'Directed Services': 'Voya Investments',
    'DBX Strategic Advisors': 'DWS',
    'MML Investment Advisers': 'MassMutual',
    'David L. Babson & Co.': 'MassMutual',
    'ProFunds': 'ProShares',
    'GW Capital Management': 'Empower Funds',
    'Maxim Capital Management': 'Empower Funds',
    'Krane Funds Advisors': 'KraneShares',
    'Banc One Investment Advisors': 'One Group Mutual Funds',
    'Everence Capital Management': 'Praxis Mutual Funds',
    'Crossmark Global Investments': 'Steward Funds',
    'Rafferty Asset Management': 'Direxion',
    'CWM Advisors': 'Inspire ETFs',
    'American General': 'AIG',
    'SunAmerica Asset Management': 'AIG',
    'Waddell & Reed': 'Ivy Investments',
    'SRN Advisors': 'Siren',
    'Northwestern Mutual Investment Services': 'Mason Street Advisors',
    'Empowered Funds': 'Alpha Architect',
    'Advantus Capital Management': 'Securian Asset Management',
    'CCM Partners': 'Shelton Capital Management',
    'Citizens Trust': 'Citizens Advisers',
    'TortoiseEcofin': 'Tortoise',
    'U.S. Trust Company of Boston': 'Boston Trust',
    'Eclipse Funds': 'New York Life Investments',
    'KeyCorp': 'Victory Capital Management',
    'Provident Institutional Management': 'BlackRock',
    'Nations Funds': 'Columbia Threadneedle Investments',
    'Woodward Funds': 'First Chicago NBD',
    'Rational Advisors': 'Strategy Shares',
    'Factor Advisors': 'ETF Managers Group',
    'FFCM': "O'Shares Investment Advisers",
    'ETFis Capital': 'Virtus Investment Partners',
    'Federated Securities': 'Federated Hermes',
}
BNY, ETC, TIDAL = 'BNY Mellon Investment Management', 'Exchange Traded Concepts', 'FolioBeyond'
ARTIFACT = {   # (earlier name, later name) after ALIAS -> 'fwd' or 'back'
    # trustee listed before the sponsor
    (BNY, 'Invesco'): 'fwd', (BNY, 'BlackRock'): 'fwd', (BNY, 'State Street Global Advisors'): 'fwd', (BNY, 'Wilshire'): 'fwd',
    # administrator or distributor listed before the adviser
    ('BISYS Fund Services', 'Mississippi Valley Advisors'): 'fwd', ('SEI', 'U.S. Bancorp Asset Management'): 'fwd', ('SEI', 'HighMark Capital Management'): 'fwd',
    ('First Data Investor Services Group', 'Fleet Investment Advisers'): 'fwd', ('First Data Investor Services Group', 'Old Kent Bank'): 'fwd',
    ('Forum Financial Services', 'Allspring'): 'fwd', ('Russell Investments', 'State Street Global Advisors'): 'fwd',
    # white-label ETF platform listed before (or after) the brand that sponsors the fund
    (ETC, 'Vident'): 'fwd', (ETC, 'ROBO Global'): 'fwd', (ETC, 'Capital Link'): 'fwd', (ETC, 'Loncar'): 'fwd', (ETC, 'Amplify'): 'fwd', (ETC, 'GraniteShares'): 'fwd',
    (ETC, 'Recon Capital Advisors'): 'fwd', (ETC, 'VanEck'): 'fwd',
    ('Toroso Investments', 'SoFi'): 'fwd', ('Toroso Investments', 'SP Funds'): 'fwd',
    (TIDAL, 'SP Funds'): 'fwd', (TIDAL, 'SoFi'): 'fwd', (TIDAL, 'Gotham Asset Management'): 'fwd',
    ('SP Funds', TIDAL): 'back', ('SoFi', TIDAL): 'back', ('Gotham Asset Management', TIDAL): 'back', ('SonicShares', TIDAL): 'back',
    ('Astor Investment Management', 'Northern Lights'): 'back', ('Gotham Asset Management', 'FundVantage Trust'): 'back',
    ('Vest Financial', 'First Trust'): 'fwd',
    # one fund (US Global Jets ETF) whose sponsor U.S. Global Investors is mislabelled as UBS for some months
    ('UBS Global Asset Management', 'U.S. Global Investors'): 'fwd', ('U.S. Global Investors', 'UBS Global Asset Management'): 'back',
}


def _spells(x):
    """(start row, end row, name) runs of one fund's name series."""
    v = x.to_numpy()
    cut = np.flatnonzero(np.r_[True, v[1:] != v[:-1]])
    return [[a, b, v[a]] for a, b in zip(cut, np.r_[cut[1:], len(v)])]


def refined_family(start=None, end=None):
    cf = pd.read_csv(CSVP, usecols=['product_j', 'month_t', 'firm_f']).dropna(subset=['firm_f']).sort_values(['product_j', 'month_t']).reset_index(drop=True)
    cf['fam'] = cf.firm_f.replace(ALIAS)
    out = cf.fam.to_numpy().copy()
    sw = []
    for j, idx in cf.groupby('product_j').indices.items():
        sp = _spells(cf.fam.iloc[idx])
        if len(sp) == 1:
            continue
        changed = True
        while changed:           # apply artifact relabels until none is left, merging equal neighbours
            changed = False
            for k in range(len(sp) - 1):
                kind = ARTIFACT.get((sp[k][2], sp[k + 1][2]))
                if kind == 'fwd':
                    sp[k][2] = sp[k + 1][2]; changed = True
                elif kind == 'back':
                    sp[k + 1][2] = sp[k][2]; changed = True
            m = [sp[0]]
            for s in sp[1:]:
                if s[2] == m[-1][2]:
                    m[-1][1] = s[1]
                else:
                    m.append(s)
            sp = m
        for a, b, nm in sp:
            out[idx[a:b]] = nm
        for k in range(1, len(sp)):
            sw.append(dict(product_j=j, month_t=cf.month_t.iloc[idx[sp[k][0]]], family_from=sp[k - 1][2], family_to=sp[k][2]))
    cf['family'] = out
    sw = pd.DataFrame(sw, columns=['product_j', 'month_t', 'family_from', 'family_to'])
    if start is not None:
        sw = sw[(sw.month_t >= start - 1e-9) & (sw.month_t <= end + 1e-9)]
    return cf[['product_j', 'month_t', 'firm_f', 'family']], sw


def transitions_table():
    """Every transition in Danny's ID, with its classification under the rules."""
    cf = pd.read_csv(CSVP, usecols=['product_j', 'month_t', 'firm_f']).dropna(subset=['firm_f']).sort_values(['product_j', 'month_t'])
    p = cf.groupby('product_j').firm_f.shift()
    c = cf[(cf.firm_f != p) & p.notna()].assign(prev=p)
    t = c.groupby(['prev', 'firm_f']).agg(funds=('product_j', 'nunique'), first_month=('month_t', 'min'), last_month=('month_t', 'max')).reset_index()
    a, b = t.prev.replace(ALIAS), t.firm_f.replace(ALIAS)
    t['rule'] = np.where(a == b, 'alias', [('artifact_' + ARTIFACT[k]) if k in ARTIFACT else 'real' for k in zip(a, b)])
    return t.sort_values(['rule', 'funds'], ascending=[True, False])


if __name__ == '__main__':
    pd.set_option('display.width', 250, 'display.max_rows', 300, 'display.max_colwidth', 60)
    from sc_build import PANEL
    t = transitions_table(); t.to_csv('family_transitions.csv', index=False)
    print('transitions in Danny\'s ID by rule (pairs / funds):'); print(t.groupby('rule').agg(pairs=('funds', 'size'), funds=('funds', 'sum')).to_string())
    fam, sw_all = refined_family()
    n0 = fam.groupby('product_j').firm_f.nunique(); n1 = fam.groupby('product_j').family.nunique()
    print(f'funds in the index CSV with more than one family: Danny\'s ID {int((n0 > 1).sum())}, refined {int((n1 > 1).sum())}; distinct families {fam.firm_f.nunique()} -> {fam.family.nunique()}')
    d = pd.read_pickle(PANEL); d = d[d.firm_f_old.notna()]
    _, sw = refined_family(2010, 2024 + 8 / 12)
    sw = sw[sw.product_j.isin(set(d.product_ids))]
    f = d.groupby('product_ids').agg(name=('product_fund_name', 'last'), months=('prices', 'size'), aum=('product_mtna', 'mean'))
    sw = sw.join(f, on='product_j')
    print(f'\nTable 2 without VA funds, 2010-2024: funds with a real acquisition or transfer {sw.product_j.nunique()} (of {len(f)}); fund-months {int(f.months[f.index.isin(sw.product_j)].sum()):,}; '
          f'asset share {(f.aum * f.months)[f.index.isin(sw.product_j)].sum() / (f.aum * f.months).sum():.4f}')
    print(sw.groupby(['family_from', 'family_to']).agg(funds=('product_j', 'nunique'), first=('month_t', 'min'), last=('month_t', 'max')).sort_values('funds', ascending=False).round(2).to_string())
    sw.sort_values('aum', ascending=False).to_csv('family_real_switches_table2.csv', index=False)
    print(sw.sort_values('aum', ascending=False)[['name', 'family_from', 'family_to', 'month_t', 'months', 'aum']].round(2).to_string(index=False))
    for j, nm in ((27635, 'SPY'), (24697, 'QQQ'), (16513, 'iShares Silver'), (24698, 'DB Commodity')):
        x = fam[(fam.product_j == j) & (fam.month_t >= 2010)]
        print(f'{nm}: {" -> ".join(pd.unique(x.firm_f))}  =>  {" -> ".join(pd.unique(x.family))}')
