"""Why is the retail fee slope about zero in specification B (step48/49)? Diagnostics and candidate fixes.

    python -I step50_retail_slope.py PACKAGE_DIR IV_INPUTS_DIR NAMES_CSV

Uses step48's sample, corrected access flag and 2SLS routine (fund FE, month-clustered SE). Linear models only.
 1  Fee level and within-class fee variation by access.
 2  Logit IV separately by access (fund + month FE, Danny's five IVs), and one instrument at a time within retail.
 3  Which flag choice produces the zero: original flag; first-record flag without the Admiral recode; corrected.
 4  Retail split by share-class type (from the class name): Vanguard Admiral, other no-load, broker-sold (A/C/R...).
 5  Fixed-effect alternatives: month FE; month x ETF FE.
 6  Candidate fixes for the preferred specification (with K): slope groups {no-load retail+institutional, broker-sold, ETF}.
Writes step50_retail_slope.csv (coefficients only).
"""
import os
import re
import sys
import numpy as np
import pandas as pd
import pyhdfe

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step48_access_spec_linear as s48
from step48_access_spec_linear import IV, CON

ROWS = []


def run(d, endog, excl, fe_cols, label):
    """2SLS on DataFrame d with fund FE + the given FE columns, via step48.tsls."""
    d = d.reset_index(drop=True)
    fid = pd.factorize(d.product_ids)[0]
    ids = [pd.factorize(d[c].astype(str) if isinstance(c, str) else c)[0] for c in fe_cols]
    s48.d = d
    s48.algs = {'fe': pyhdfe.create(np.column_stack([fid] + ids), drop_singletons=False)}
    s48.clu = pd.factorize(d.market_ids)[0]
    row, b, u = s48.tsls(endog, excl, 'fe', label)
    ROWS.append(row)
    return row, b


def class_type(name):
    n = str(name)
    if re.search(r'Admiral', n):
        return 'admiral'
    if re.search(r'Class (A|B|C|R\d?|T|N|S|K|M|J)\b|; (A|C|R\d?|N|T) (Shares|Class)|Service|Advisor|Retirement|Adviser|Class (A|C)\d', n):
        return 'broker'
    return 'noload'


def main(P, D, names):
    d = s48.load(P, D, names)
    nm = pd.read_csv(names).set_index('product_ids').product_fund_name
    d['name'] = d.product_ids.map(nm)
    d['ma'] = d.market_ids.astype(str) + '_' + d.access.astype(int).astype(str)
    d['mao'] = d.market_ids.astype(str) + '_' + d.access_orig.astype(int).astype(str)
    d['me'] = d.market_ids.astype(str) + '_' + d.etf.astype(int).astype(str)

    print('\n1. Fee level and variation by access (0 retail, 1 institutional, 2 ETF); fee in the units of `prices`')
    fid = pd.factorize(d.product_ids)[0]
    alg = pyhdfe.create(np.column_stack([fid, pd.factorize(d.ma)[0]]), drop_singletons=False)
    d['p_within'] = alg.residualize(d[['prices']].to_numpy(float))[:, 0]
    d['dp'] = d.sort_values('month').groupby('product_ids').prices.diff()
    tot = d.groupby('market_ids').product_mtna.transform('sum')
    for a, g in d.groupby('access'):
        print(f'  access {int(a)}: classes {g.product_ids.nunique():4d}, fund-months {len(g):6,d}, mean AUM share {float((g.product_mtna / tot[g.index]).groupby(g.market_ids).sum().mean()):.3f}; '
              f'fee p10/p50/p90 {g.prices.quantile(.1):.4f}/{g.prices.median():.4f}/{g.prices.quantile(.9):.4f}, AUM-weighted {np.average(g.prices, weights=g.product_mtna):.4f}; '
              f'within SD {g.p_within.std():.4f}; months with a fee change {float((g.dp.abs() > 1e-9).mean()):.3f}')

    print('\n2. Logit IV by access, alone (fund + month FE, five IVs)')
    for a, lab in ((0, 'retail'), (1, 'institutional'), (2, 'ETF')):
        run(d[d.access == a], ['prices'], IV, ['market_ids'], f'logit, {lab} only')
    print('   retail only, one instrument at a time')
    for k in range(5):
        run(d[d.access == 0], ['prices'], [IV[k]], ['market_ids'], f'logit, retail, IV{k} alone')

    print('\n3. Which flag choice gives the zero retail slope (logit B: fee, fee x inst, fee x ETF; month x access FE)')
    run(d, ['prices', 'p_inst', 'p_etf'], IV + s48.IVX, ['ma'], 'logit B, corrected flag')
    run(d, ['prices', 'p_inst_o', 'p_etf_o'], IV + s48.IVXO, ['mao'], 'logit B, original flag')
    d0 = s48.load(P, D, None)   # first-record / pre-2019 rule, no Admiral recode
    d0['ma'] = d0.market_ids.astype(str) + '_' + d0.access.astype(int).astype(str)
    run(d0, ['prices', 'p_inst', 'p_etf'], IV + s48.IVX, ['ma'], 'logit B, time-invariant flag, Admiral not recoded')

    print('\n4. Retail by share-class type')
    d['ctype'] = np.where(d.access == 0, d.name.map(class_type), '')
    r = d[d.access == 0]
    for t, g in r.groupby('ctype'):
        print(f'  {t:8s}: classes {g.product_ids.nunique():4d}, fund-months {len(g):6,d}, retail AUM share {g.product_mtna.sum() / r.product_mtna.sum():.3f}, '
              f'median fee {g.prices.median():.4f}, within SD {g.p_within.std():.4f}')
        print('     e.g.', '; '.join(g.drop_duplicates('product_ids').sort_values('product_mtna', ascending=False).name.head(4).str.slice(0, 60)))
    for t in ('admiral', 'noload', 'broker'):
        g = r[r.ctype == t]
        if g.product_ids.nunique() > 5:
            run(g, ['prices'], IV, ['market_ids'], f'logit, retail {t} only')
    for t in ('admiral', 'noload', 'broker'):
        d[f'r_{t}'] = (d.ctype == t).astype(float)
    d['broker'] = d.r_broker
    d['p_broker'] = d.prices * d.broker
    for k in (0, 1):
        d[f'iv{k}_broker'] = d[f'demand_instruments{k}'] * d.broker
    IVB = ['iv0_broker', 'iv1_broker']
    d['seg4'] = d.market_ids.astype(str) + '_' + (d.access + 3 * d.broker).astype(int).astype(str)
    run(d, ['prices', 'p_broker', 'p_inst', 'p_etf'], IV + s48.IVX + IVB, ['ma'], 'logit B + fee x broker-sold (month x access FE)')
    run(d, ['prices', 'p_broker', 'p_inst', 'p_etf'], IV + s48.IVX + IVB, ['seg4'], 'logit B + fee x broker-sold (month x 4-segment FE)')

    print('\n5. Fixed-effect alternatives (logit; fee x access slopes)')
    run(d, ['prices', 'p_inst', 'p_etf'], IV + s48.IVX, ['market_ids'], 'logit, month FE')
    run(d, ['prices', 'p_inst', 'p_etf'], IV + s48.IVX, ['me'], 'logit, month x ETF FE')

    print('\n6. Candidate fixes with the random-coefficient term K')
    run(d, ['prices', 'p_inst', 'p_etf', 'K'], IV + s48.IVX, ['ma'], 'B (reference)')
    run(d, ['prices', 'p_broker', 'p_inst', 'p_etf', 'K'], IV + s48.IVX + IVB, ['seg4'], 'B4: B + fee x broker-sold, month x 4-segment FE')
    run(d, ['prices', 'p_broker', 'p_etf', 'K'], IV + ['iv0_etf', 'iv1_etf'] + IVB, ['seg4'], 'B3: slopes {no-load retail + inst, broker, ETF}')
    run(d, ['prices', 'p_broker', 'p_etf', 'pp2', 'mpe'], IV + ['iv0_etf', 'iv1_etf'] + IVB, ['seg4'], 'B3-split')
    nb = d[d.broker == 0]
    run(nb, ['prices', 'p_inst', 'p_etf'], IV + s48.IVX, ['ma'], 'logit B, broker-sold classes dropped (shares unchanged)')
    run(nb, ['prices', 'p_inst', 'p_etf', 'K'], IV + s48.IVX, ['ma'], 'B, broker-sold classes dropped (shares unchanged)')
    pd.DataFrame(ROWS).to_csv('step50_retail_slope.csv', index=False)


if __name__ == '__main__':
    main(*sys.argv[1:4])
