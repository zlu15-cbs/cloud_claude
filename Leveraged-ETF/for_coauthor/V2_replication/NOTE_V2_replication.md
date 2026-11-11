# Replicating V2, our preferred demand specification (index market, logit IV)

Danny,

Please replicate **V2**, our preferred demand specification for the index market (Table 2 Panel A sample), on your data, together with its downstream results. Everything V2 needs is in this zip: one Python script that reads only your own files, and below the definitions and the numbers you should get.

> **Update, 11 November 2026: the cheap indicator has changed.** This note and `replicate_V2.py` describe V2 as first sent, with cheap measured in a fund's first month in the index CSV (§3.3). Everything else below is current.
>
> The current definition:

- **Cheap:** a fund is cheap if its expense ratio in its entry month is at or below the 20th percentile of that month's expense ratios across all index funds; ties count as cheap. The entry month is the fund's first month on or after January 2005 with a fee that CRSP reports. It is measured on your source panel (`index_funds_preprocess_oct2026.csv`), which has each fund's first year; the index CSV does not.
- **Why 2005:** the status is fixed five years before the estimation window opens, on a cross-section of 925 funds.
- **Everything else is unchanged:** Z is the median fee of same-family, same-share-type funds in another of the six broad asset classes; money market funds are dropped.

| | Non-cheap α (SE) | × cheap (SE) | Min F | Share e > 0 | Negative MC B0–B65 (own η) |
|---|---|---|---|---|---|
| **V2 now** (2005 start, source panel, 20th percentile) | −3.385 (0.541) | −20.059 (0.784) | 177 | 0 | 0.067–0.087 |
| 15th percentile | −7.527 (0.880) | −29.120 (1.972) | 128 | 0 | 0.000–0.001 |
| 25th percentile | −3.967 (0.607) | −17.409 (0.840) | 144 | 0 | 0.018–0.026 |
| V2 as first sent (cheap from a fund's first month in the index CSV) | −3.642 (0.419) | −20.562 (0.646) | 316 | 0 | 0.053–0.082 |

- `replicate_V2.py` still reproduces the last row. The current V2 is produced by `sc_v2_robust.py` and `sc_v2_final.py` in `for_coauthor/spec_summary_replication/`, which need your source panel as a second input.
- Results, robustness and the supply side for the current V2 are in `RESULTS_spec_summary.md`, section 3. Where the numbers in §5 below differ from that file, that file is current.

## 1. What we ask

1. Run `replicate_V2.py` on your index CSV and your CRSP quarterly fund summary (§2). It takes about 40 minutes, mostly the conduct tests.
2. Check your output against the numbers in §5. Our run reproduces them exactly from `nonLev_funds_product_month_level_v2_patched.csv`.
3. Send us `V2_demand.csv`, `V2_table5.csv`, `V2_mc.csv`, `V2_conduct.csv` and the log. If your numbers differ, compare your `V2_Z.csv` (the instrument per fund-month) with ours first. It is 5 MB, so it is not in this zip; we will send it on request.

If you prefer your own code, §3 and §4 define every step.

## 2. Files and how to run

| File | Content |
|---|---|
| `NOTE_V2_replication.md` | this note |
| `replicate_V2.py` | the whole pipeline: sample, cheap indicator, instrument, demand, supply side, conduct test |
| `requirements.txt` | package versions we used |
| `our_outputs/` | our `V2_*.csv` outputs and run log, for comparison (except `V2_Z.csv`, available on request) |

```
python replicate_V2.py --index-csv nonLev_funds_product_month_level_v2_patched.csv \
                       --crsp CRSP_fund_summary_2026_qtrly_combined.csv
```

- **Inputs.**
    - `--index-csv`: the CSV your notebook `main_Danny_Oct2026_index_market.ipynb` reads in cell 3.
    - `--crsp`: CRSP's quarterly fund summary. Columns used: `crsp_fundno`, `quarter`, `fund_name`, `lipper_class`, `lipper_asset_cd`, `crsp_obj_cd`, `inst_fund`, `retail_fund`.
- **Options.**
    - `--no-conduct` skips the pyRVtest runs.
    - `--donor-mmf sample` drops only the 4 in-sample money market funds from the donor pool (§3.2). That reproduces our first V2 run (α = −3.607), for reference.
- **Outputs (`V2_*.csv`):**
    - `demand`: coefficients, SEs, F, elasticity summaries (the file also has lead-test columns, which we no longer use);
    - `table5`: own elasticities of the 15 Table 5 funds;
    - `scale`: η by conduct;
    - `mc`: negative-MC statistics;
    - `where`: location of negative MCs by group;
    - `conduct`: MCS p-values, TRV and F for each instrument set and η scheme;
    - `Z`: the instrument per fund-month;
    - `rows_without_Z`: why rows lack the instrument;
    - `money_market_funds`: the funds flagged in §3.2.

## 3. Definitions

### 3.1 Sample
- **Your notebook's filters, unchanged** (cells 3 and 4, copied verbatim into `load_sample()`): Table 2 Panel A, 108,300 fund-months.
    - share ≥ 0.0001;
    - January 2010 to August 2024;
    - `prefer` ∈ {1,…,5};
    - price > 0;
    - non-missing `Conduct_IV_csent_index_resid`.
- Markets are calendar months (`market_ids`), and products are CRSP share classes (`product_ids` = `crsp_fundno`). Shares are `product_mtna / market_share_m_denom_alt1`, as in your notebook.

### 3.2 Money market funds are dropped
- **Four money market funds are in the Table 2 sample** (437 fund-months; not index funds):
    - JPMorgan 100% US Treasury Securities Money Market Fund, Institutional (17490) and Agency (17491) classes;
    - Allspring (formerly Wells Fargo) 100% Treasury Money Market Fund, Institutional (62651);
    - Evergreen Instl 100% Treasury Money Market Fund (10509).
- **Flag rule:** a fund is a money market fund if a CRSP fund name contains "money market" AND, in some quarter, its Lipper class is MM, ITM, IUS, UST or IMM, or its CRSP style code starts with IM. Lipper class, CRSP style code and fund name agree on all four.
- **Drop:**
    - from the demand estimation and the supply side;
    - and from the instrument's donor pool, together with the 12 other money-market share classes in the index CSV (16 in all).
- **Supply sample:** 107,863 fund-months.
- **Why it matters.** These funds drove the earlier steep slopes: model 1 goes from −8.0 to −3.3 without them. The paper's IV on all rows (our "model 6") goes from −8.1 to −3.0.

### 3.3 Cheap indicator (`gene_idx`)
`gene_idx_j` = 1 if fund j's expense ratio in its **first month with a recorded fee in the full index CSV** (1994–2025, before any sample filter) is at or below the **20th percentile of that month's expense ratios across all funds in the CSV** with a recorded fee. Ties count as cheap.
- The indicator is fixed per fund. It covers 47.0% of estimation fund-months.
- The percentile is taken over the whole CSV, money market funds included. Excluding the 16 money market funds would move the cutoffs by little; we kept the definition as estimated.

### 3.4 The Hausman instrument Z

For fund j in month t:

    Z_jt = median expense ratio, in month t, of the donor funds k that satisfy all four conditions:
      (1) k is in the index CSV in month t with a recorded expense ratio, and k is not a money market fund;
      (2) same family:        firm_f_old(k) = firm_f_old(j);
      (3) same share class:   share_class(k) = share_class(j), in month t;
      (4) other asset class:  asset_class(k) ≠ asset_class(j).

- **Donors are not limited to the Table 2 sample.** Condition (1) uses every fund in the index CSV that month, including funds your sample filters later drop (share < 0.0001, `prefer` = 6). In 2010 and later, 77% of donor fund-months are outside Table 2.
    - **This matters.** With donors restricted to Table 2 fund-months, demand slopes upward: α = +0.62, 51% of fund-months with e > 0.
- **Unweighted median** of the donors' current-month expense ratios. There is no lag and no AUM weight.
- **Missing Z.** Z is missing when j has no `firm_f_old`, or when no donor satisfies (2)–(4) that month. Those rows stay in the market (in the shares, in s₀ and on the supply side) but are not used to estimate demand (§5.1).
- **Family** = `firm_f_old`, the CSV's family code: CRSP's management-company code (`mgmt_cd`), upper-cased. It is not `firm_f` (the parent firm, used as `firm_ids` for ownership). Rows without `firm_f_old` get no Z.
- **Share class**, per fund-month:
    1. ETF if `ETF_ind` = 1;
    2. otherwise institutional if CRSP `inst_fund` = Y;
    3. otherwise retail if CRSP `retail_fund` = Y;
    4. otherwise a fund-name rule (`share_class_keywords()`, about 0.3% of mutual-fund rows).

    CRSP flags are matched by `crsp_fundno` and calendar quarter.
- **Asset class**, one of six, assigned per tracked index (`market_m_index`): every fund tracking an index gets the same class, which is the most common fund-level class among the CSV's funds tracking that index.
    - The fund-level class is the fund's most common Lipper class over its CRSP quarters, mapped as in the table below.
    - If a fund has no Lipper class (0.04% of rows), its most common CRSP style code is used.
    - If neither exists, a name and index-cluster rule is used (`classify_fallback()`).

| Lipper class (CRSP `lipper_class`) | Asset class |
|---|---|
| MAT\*, MTA\* (target date, target allocation), FX, GX (flexible), B, BT (balanced), CV (convertibles) | allocation |
| RE, GRE, IRE (real estate), CM\* (commodities), AU (gold), RR (real return) | real_asset |
| LSE, OS, AED, AGM, ABR, AMS, MFF, EMN, DSB, DL, ALT (alternatives), CRX (currency), EMP (energy MLP) | other |
| any other class with `lipper_asset_cd` TX or MB (taxable bond, municipal, money market) | bond |
| IML\*, ILC\*, ISM\*, IEI, IFCE, IFGE, GML\*, GLC\*, GLV\*, GLG\*, EM, EU, CH, LT, JA, XJ, PC, INR, FM, IF, GL, GEI, GSME, GTK, GNR, GFS, GH, GIF (international, global, regional, emerging equity) | intl_equity |
| all other equity classes (S&P 500, size and style, US sectors, equity income) | us_equity |

**Example.** Fund j is family F's institutional S&P 500 index fund (us_equity) in month t. In month t family F also has:

| F's fund | Share class | Asset class | Fee (%) | Donor? |
|---|---|---|---|---|
| total bond index | inst | bond | 0.05 | yes |
| developed-markets index | inst | intl_equity | 0.07 | yes |
| target-date 2040 index | inst | allocation | 0.10 | yes |
| mid-cap index | inst | us_equity | 0.04 | no: same asset class |
| total bond index | retail | bond | 0.15 | no: other share class |

Z_jt = median(0.05, 0.07, 0.10) = 0.07. Funds of other families never enter.

**How Z differs from the paper's `BLP_IV_hausman_exp_ratio`.** Our reading of the paper's variable is the lagged-AUM-weighted mean expense ratio of same-`firm_f_old` funds tracking a different `market_m_index`. Please correct us if that is wrong.

| | Paper's IV | Z (V2) |
|---|---|---|
| Family | `firm_f_old` | `firm_f_old` |
| Donors excluded | same tracked index | same asset class (six classes) |
| Share class | any | same as j (CRSP flags) |
| Statistic | lagged-AUM-weighted mean | unweighted median, current month |
| Money market funds | included | excluded |

### 3.5 Demand

    ln s_jt − ln s_0t = α p_jt + α_x (p_jt × gene_idx_j) + β1 TE_jt + β2 R_jt + β3 ln Age_jt + μ_j + τ_t + ξ_jt

- **Variables:**
    - p = `prices` (expense ratio, %);
    - TE = |`product_tracking_err`|;
    - R = `product_past_1yr_ret`;
    - ln Age = `log_product_fund_age`;
    - μ_j are fund fixed effects and τ_t month fixed effects.
- **Estimation:** pyblp 1.3.0 logit. The excluded instruments are Z and Z × gene_idx (exactly identified). SEs are clustered by month.
- **First-stage F:** Sanderson–Windmeijer, cluster-robust, for p and p × gene_idx.
- **Own elasticity:** e_jt = (α + α_x gene_idx_j) p_jt (1 − s_jt).
- **Table 5 funds:** the top 5 funds by AUM in the last month for each of BlackRock, Vanguard and SSGA. Elasticities are measured in each fund's last market.

### 3.6 Supply side (all 107,863 fund-months)
- **Markups:** from the logit first-order conditions with ownership by `firm_ids`. The conduct candidates are:
    - PC: zero markup;
    - B0: firm Bertrand;
    - B25, B50, B65: profit weight κ = 0.25, 0.50, 0.65 among BlackRock, Vanguard and SSGA (your κ specifications 2, 3 and 6).
- **Marginal cost:** MC = p + η ln(TNA) − markup.
- **Scale η, by candidate:**
    - the dependent variable is p − markup, winsorized 1/99 within calendar year;
    - it is regressed by 2SLS on ln AUM, instrumented by `rotator`, with |TE|, ln age, fund FE and month FE;
    - SEs are clustered by month.
- **Negative-MC share:** the mean over months of the within-month share with MC < 0, at the candidate's own η.
- **Conduct test:** pyRVtest 0.3.2 with the markups supplied directly. The cost side is ln age, TE and past return, with fund and month FE. Settings: `demand_adjustment=False`, `clustering_adjustment=True`. "Selected" means MCS p ≥ 0.05.
    - **Instrument sets:**
        - main: rival2 × csent_index;
        - alternatives: rival2 × bab_usa, × fmax, × rotator, × csent_income3; rival3 × csent_index.
    - **η schemes:**
        - A: η = 0.024 for all candidates;
        - B: each candidate's own η;
        - C: the PC η for all candidates;
        - A and C again with markups capped 1/99 within calendar year (your convention).

## 4. Choices behind V2 and the alternatives we rejected

| Choice | V2 | Alternatives tried | Why V2 |
|---|---|---|---|
| Cheap definition | gene_idx: entry fee ≤ 20th percentile of the full index CSV | danny_crsp / danny_idx: launch fee < 20th percentile of the prior-year launch cohort, at cutoffs from 3% to 20% | Your definition leaves non-cheap demand flat or upward-sloping at every cutoff and with every instrument (25% of fund-months with e > 0 in your benchmark). |
| Instrument exclusion | other asset class | other cluster, other index | Without money market funds, the cluster and index exclusions give upward-sloping demand. |
| Asset-class source | Lipper class (CRSP) | our cluster map plus name keywords; CRSP style code | Lipper places target-date funds, LifeStrategy funds and single-country funds correctly. It improves every demand screen, and the downstream results do not change. |
| Share class | CRSP `inst_fund` / `retail_fund` flags | name keywords | Uses CRSP's flags rather than our name parsing. |
| Rows | every row with Z defined | parent firm (`firm_f`) as family for the 112 funds without `firm_f_old`, with or without a fallback | With that fill, demand slopes upward for 55% of fund-months. |
| Money market funds | dropped | kept | They are not index funds and they drove the earlier steep slopes. |

## 5. Results you should get (`--donor-mmf all`, our run)

### 5.1 Rows

| Rows | Fund-months | Funds |
|---|---|---|
| Table 2 Panel A (your notebook) | 108,300 | 1,302 |
| minus the 4 money market funds = supply sample | 107,863 | 1,298 |
| without Z: (a) no `firm_f_old` (mostly insurance-channel trusts: VALIC, Voya, Prudential, John Hancock) | 7,771 | 112 |
| without Z: (b) family has no fund in another asset class that month | 2,533 | 68 |
| without Z: (c) other-class funds exist, none in the same share class | 1,490 | 60 |
| **demand estimation rows** | **96,069** | **1,148** |

### 5.2 Scorecard

V2 and two earlier models, scored on the same rows as our earlier scorecard. The earlier columns include the money market funds and use all 108,300 rows on the supply side.
- ✓ = desirable, ~ = borderline, ✗ = undesirable.
- Downstream rows give the range over the candidates at each candidate's own η.

| | **V2 (to replicate)** | Model 1, first run (with money market funds) | Your benchmark: paper IV × danny_crsp (model 7) |
|---|---|---|---|
| **Specification** | | | |
| Instrument | Z (§3.4) | Z with name-keyword asset classes | paper's `BLP_IV_hausman_exp_ratio` |
| Instrument excludes same | asset class (Lipper) | asset class (keywords) | tracked index |
| Cheap interaction | gene_idx | gene_idx | danny_crsp |
| Estimation rows | 96,069 | 97,294 | 108,300 |
| **Demand outcomes** | | | |
| Non-cheap α (SE) | −3.64 (0.42) | −8.02 (1.31) | +5.85 |
| Cheap total α | −24.2 | −32.7 | −14.9 |
| Table 5 funds with \|e\| > 1 | 5/15 | 7/15 | 5/15 |
| **Demand screens** | | | |
| No upward slope (e > 0 share) | ✓ 0 | ✓ 0 | ✗ 0.25 |
| First-stage F (min) | ✓ 316 | ✓ 114 | ✓ 44 |
| Fee heterogeneity (cheap vs non-cheap) | ✓ | ✓ | ✓ |
| **Downstream outcomes** | | | |
| Scale η range (PC–B65; SE about 0.005) | 0.0210–0.0220 | 0.0205–0.0212 | 0.0193–0.0205 |
| Negative-markup share | ✓ 0 | ✓ 0 | ✗ 0.25 |
| Negative-MC share (B0–B65) | 0.053–0.082 | 0 | 0 |
| Min MC (% of assets) | −0.21 | −0.02 | +0.03 |
| **MC screens** | | | |
| Magnitude: ≤ 2% below −0.20%, none below −0.60% | ✓ (0–0.02% below −0.20%) | ✓ | ✓ mechanical |
| Location: not at Vanguard or SPY | ✗ Vanguard (59% of negatives at B0); SPY never | – none | – none |
| **Conduct** | | | |
| Main IV selected set | PC, B50, B65 | PC, B50, B65 | PC |
| Alternative IVs (majority) | PC | PC | PC |
| B0 and B25 rejected | ✓ | ✓ | ✓ |
| Robust to η scheme and capping | ✓ same sets under A, B, C and capped A, C | ✓ | ✓ |
| **Overall** | **pass demand screens; MC location caveat** | pass, but driven by money market funds | demand fails |

- **The tight bound** (≤ 1% below −0.10%, none below −0.30%) passes for B0 and B25 only. At B50 and B65, 1.6% and 3.0% of fund-months fall below −0.10%.
- **Where the negative MCs sit** (B0):
    - only non-cheap funds;
    - Vanguard: 13% of its fund-months, 59% of all negatives;
    - BlackRock 5%, SSGA 4%, other firms 2%;
    - spread across asset classes: 4–6%.

### 5.3 Demand

| | Estimate (SE) |
|---|---|
| α (price) | −3.642 (0.419) |
| α_x (price × gene_idx) | −20.562 (0.646) |
| \|Tracking error\| | −0.428 (0.053) |
| Past 1-year return | 0.427 (0.034) |
| Log age | 0.572 (0.007) |
| SW F: price / price × cheap | 315.8 / 335.6 |
| Average own elasticity | −1.93 |

**Table 5 funds** (own elasticity in the last market; cheap = gene_idx):

| Fund | Cheap | e |
|---|---|---|
| iShares Core S&P 500 ETF | 1 | −0.70 |
| iShares Core MSCI EAFE ETF | 1 | −1.68 |
| iShares Core US Aggregate Bond ETF | 1 | −0.72 |
| iShares Russell 1000 Growth ETF | 1 | −4.33 |
| iShares Core S&P Mid-Cap ETF | 1 | −1.20 |
| SPDR S&P 500 ETF Trust | 1 | −2.10 |
| SPDR Gold Shares | 0 | −1.45 |
| Technology Select Sector SPDR | 0 | −0.29 |
| Financial Select Sector SPDR | 0 | −0.29 |
| SPDR Portfolio S&P 500 ETF | 1 | −0.48 |
| Vanguard Total Stock Market, Institutional Plus | 1 | −0.46 |
| Vanguard 500 Index, Admiral | 1 | −0.94 |
| Vanguard 500 Index, ETF | 1 | −0.70 |
| Vanguard Total Stock Market, ETF | 1 | −0.71 |
| Vanguard Total Stock Market, Admiral | 1 | −0.94 |

These are rounded; `V2_table5.csv` has full precision.

### 5.4 Supply side

| | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|
| η (SE) | 0.0211 (0.0051) | 0.0210 (0.0049) | 0.0215 (0.0049) | 0.0218 (0.0049) | 0.0220 (0.0050) |
| Mean markup (%) | 0 | 0.191 | 0.203 | 0.219 | 0.233 |
| Negative-MC share (mean over months) | 0 | 0.053 | 0.061 | 0.074 | 0.082 |
| Share below −0.10% | 0 | 0.0009 | 0.0051 | 0.0163 | 0.0303 |
| Share below −0.20% | 0 | 0 | 0 | 0 | 0.0002 |
| Min MC (%) | 0.142 | −0.126 | −0.148 | −0.183 | −0.212 |

### 5.5 Conduct (MCS p-values; selected if p ≥ 0.05)

| Instrument set | Scheme A (η 0.024) | Scheme B (own η) | Scheme C (PC η) | A capped | C capped |
|---|---|---|---|---|---|
| **Main: rival2 × csent_index** | PC (1.00), B50 (0.19), B65 (0.79) | PC, B50 (0.14), B65 (0.70) | PC, B50 (0.20), B65 (0.81) | PC, B50 (0.20), B65 (0.80) | PC, B50 (0.20), B65 (0.81) |
| rival2 × csent_income3 | PC, B50 (0.26), B65 (0.86) | PC, B50 (0.18), B65 (0.76) | PC, B50 (0.26), B65 (0.87) | PC, B50 (0.26), B65 (0.87) | PC, B50 (0.27), B65 (0.88) |
| rival3 × csent_index | PC | PC | PC | PC | PC |
| rival2 × bab_usa / fmax / rotator | PC | PC | PC | PC | PC |

- **Main instrument, scheme A:**
    - PC vs B65: T^RV = −0.26;
    - B0 and B25 are rejected (p = 0.00; T^RV vs B65 = 2.4 and 1.8);
    - the pairwise F statistics are 146–184.
- **Minimum pairwise F over all schemes:** 140 for the main instrument and 68–156 for the alternatives.

## 6. Open points
- **The paper's IV.** Please confirm or correct our reading of `BLP_IV_hausman_exp_ratio` (§3.4). We match your values within 0.0005 on 83% of rows only.
- **Money market funds.** They are in the Table 2 sample and therefore in the paper's published estimates. Dropping them moves the paper's own Table 2 IV estimate as well.
- **Fee data.** Our runs use your CSV as it is, with no expense-ratio corrections applied.
- **Outside-option funds as donors.** Most donors (77% of donor fund-months) are funds in the outside option: share below 0.01% or `prefer` = 6. With donors limited to Table 2 fund-months, V2 fails (§3.4), so the result depends on these funds.
    - **The referee question:** why should outside-option funds act as donors?
    - **Our proposed defence:** their fees reflect family-wide cost shocks, and they are not competing products in the inside market.
    - We would like your view on whether this argument holds up.

Gene
