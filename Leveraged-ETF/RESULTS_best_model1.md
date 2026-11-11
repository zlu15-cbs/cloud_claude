# Recommended "model 1" (index market, logit IV)

**Code and outputs.**
- `code/explore/step38_best_model1.py`: the variants and their downstream checks.
- `code/explore/step39_models_no_mmf.py`: models 1–9 re-estimated without the money market funds.
- Logs: `logs/step38.log`, `logs/step39.log`, `logs/step38_{demand,mc,scale,conduct,where,classes}.csv`, `logs/step39_demand.csv`.

## 1. Recommendation: V2 = model 1 without money market funds, with Lipper asset classes, without the keyword grid

| Element | Model 1 as run | **Recommended (V2)** |
|---|---|---|
| Money market funds | 4 funds, 437 fund-months, in the sample | **dropped** from estimation, the supply side and the donors |
| Asset class used by the instrument | our cluster map → name keywords → index code | **Lipper class** (CRSP-supplied), most common per index |
| Share class | CRSP flags | CRSP flags (unchanged) |
| Family | `firm_f_old` | `firm_f_old` (unchanged) |
| Row filter | rows where the old keyword-Z was defined | **none**: every row with the instrument defined |
| Cheap | gene_idx | gene_idx (unchanged) |

## 2. Results

**Demand.**

| | Model 1 as run (R0) | **V2** |
|---|---|---|
| N (funds-months) | 97,294 | 96,142 |
| Non-cheap α (SE) | −8.02 (1.31) | **−3.61 (0.42)** |
| Cheap α_x (SE) | −24.67 (1.26) | −20.60 (0.65) |
| Total slope for cheap funds | −32.7 | −24.2 |
| Min first-stage F (SW, cluster-robust) | 114 | **311** |
| Average own elasticity | −3.28 | −1.93 |
| Share of fund-months with e > 0 | 0 | **0** |
| Table 5 funds with \|e\| > 1 | 7/15 | 5/15 |

**Downstream** (107,863 fund-months: all of Table 2 except the money market funds).

| | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|
| Scale η (SE 0.005) | 0.0211 | 0.0209 | 0.0215 | 0.0218 | 0.0220 |
| Negative-MC share (own η) | 0 | 0.055 | 0.063 | 0.075 | 0.084 |
| Share of fund-months below −0.10% | 0 | 0.001 | 0.006 | 0.018 | 0.032 |
| Share of fund-months below −0.20% | 0 | 0 | 0 | 0 | 0.0002 |
| Min MC (%) | – | −0.13 | −0.15 | −0.19 | −0.22 |

- **First-round bound** (at most 2% below −0.20%, none below −0.60%): **passes** for every candidate.
- **Tight bound** (at most 1% below −0.10%, none below −0.30%): passes for B0 and B25; B50 and B65 exceed the 1% share.
- **Location** (B0):
    - **Fails rule 3.** All negatives are non-cheap funds, and 58% sit at Vanguard (13% of Vanguard fund-months), where lending is at cost.
    - Within asset classes they are spread evenly: about 5–6% each.
    - SPY is never negative.

**Conduct** (pyRVtest, η = 0.024; MCS p in brackets).

| Instrument | Selected | PC vs B65 (T) | Min F |
|---|---|---|---|
| **Main**: rival2 × csent_index | PC, B50 (0.20), B65 (0.80) | −0.25 | 141 |
| rival2 × csent_income3 | PC, B50, B65 | −0.16 | 158 |
| rival3 × csent_index | PC | −2.37 | 118 |
| rival2 × bab_usa / fmax / rotator | PC | −3.6 to −4.1 | 70–99 |

B0 and B25 are rejected under every instrument (T −5 to −11).

## 3. Why V2

1. **Four money market funds drove model 1's steep slope.** The JPMorgan 100% US Treasury Securities MMF (two classes), Wells Fargo 100% Treasury MMF and Evergreen 100% Treasury MMF are in the 108,300-row Table 2 sample.
    - Lipper class (money market), the CRSP style code (IM*) and the fund names identify the same four funds.
    - They are not index funds.
    - Without them, model 1 goes from −8.0 to −3.3 (`step39`). The 622 rows outside the old grid moved the slope to −15 almost entirely through one of these funds: dropping it alone gives −7.3.
    - The earlier zero-negative-MC result for models 1 and 6 depended on these funds.
2. **Among the valid specifications, V2 is best on the demand criteria**, which the project rules put first:
    - no upward slope;
    - the highest precision (SE 0.42);
    - F 311;
3. **Lipper classes are consistent with the share-class ruling** (CRSP-supplied, not name keywords) and fix the clear errors of both earlier classifications:
    - target-date and target-risk funds (Vanguard LifeStrategy, TIAA Lifecycle, Russell strategy funds) become allocation;
    - single-country iShares funds become international equity;
    - sector ETFs become US equity.

    They also improve every demand screen relative to our classes on the same rows (V1 → V2: α −3.04 → −3.61).
4. **Dropping the old keyword grid** removes a filter with no reason under the CRSP-flag ruling.
5. **Keeping all rows fails, so V2 does not do it.** Giving the 112 family-less funds their parent firm (`firm_f`) as family, with or without a fallback instrument, makes demand slope up for 55% of fund-months (V3–V7). The family-less funds are mostly insurance-channel trusts, and the parent firm's retail and ETF fees evidently don't shift their fees. The supply side still uses all 107,863 rows.

## 4. What changes in the earlier conclusions (`RESULTS_downstream.md` scorecard)

| Model | With money market funds | Without (`step39`) |
|---|---|---|
| 1 ours | −8.02, valid, zero negative MC | −3.35, valid (V2 is its refined version) |
| 2 cluster exclusion | −3.64, valid | **+0.40, 53% e > 0: invalid** |
| 3 index exclusion | −1.25, valid | **+1.49, invalid** |
| 4 no interaction | −0.85 | −0.94 (flat) |
| 5 paper IV, grid rows | −2.72, valid (F 13) | **+2.03, invalid** |
| 6 paper IV, all rows | −8.13, valid (F 18) | **−3.03 (SE 1.85), valid**, F 41 |
| 7 Danny's benchmark | +5.85, 25% e > 0 | +7.90, 25% e > 0 |
| 8, 9 | invalid | invalid |

- **Exclusion ladder.** Only the asset-class rung survives. The "open choice of exclusion level" is settled by the data.
- **Runner-up: model 6 without money market funds** (the paper's instrument on all rows). It is valid, but much less precise (SE 1.85, F 41) and built from an instrument whose construction is unknown for the 7% family-less rows. Its downstream has not been run.
- **The sec-lending picture changes.** No valid specification now reaches zero negative MC. The best (V2) passes the first-round size bound, but its negatives sit at Vanguard's non-cheap classes.

## 5. Variable definitions (V2)

**Sample.**
- **Market** t = calendar month, Jan 2010 – Aug 2024 (`market_ids`).
- **Products** j = share classes (`product_ids` = CRSP `crsp_fundno`) of passive unlevered index funds in the Table 2 Panel A sample. That is Danny's notebook `main_Danny_Oct2026_index_market.ipynb`, cells 2–4, on `nonLev_funds_product_month_level_v2_patched.csv`: 108,300 fund-months.
- **Money market funds dropped:** `crsp_fundno` 17490, 17491, 62651, 10509 (437 fund-months), leaving 107,863.
- **Estimation rows:** the 96,142 with Z defined.

**Demand.**

    δ_jt = ln s_jt − ln s_0t = α p_jt + α_x (p_jt × cheap_j) + β1 TE_jt + β2 R_jt + β3 ln Age_jt + μ_j + τ_t + ξ_jt

| Symbol | Variable | Definition |
|---|---|---|
| s_jt | `shares` | Market share in Danny's CSV, unchanged. s_0t = 1 − Σ_j s_jt over the Table 2 products of month t. |
| p_jt | `prices` | Expense ratio in percent. The fee patch in `data_patch/` is **not** applied. |
| TE_jt | `product_tracking_err` | Tracking error (paper's variable) |
| R_jt | `product_past_1yr_ret` | Past 1-year return (paper's variable) |
| ln Age_jt | `log_product_fund_age` | Log fund age (paper's variable) |
| μ_j, τ_t | | Fund (share-class) and month fixed effects |
| cheap_j | `gene_idx` | 1 if the fund's expense ratio in its **first month in the raw index file** (1994–2025, before any sample filter) is ≤ the 20th percentile of that month's expense ratios across all index funds in the raw file; ties count as cheap. Fixed per fund; 47.1% of estimation fund-months. Code: `tiers.raw_entry_tiers`. |

- **Instruments:** Z_jt and Z_jt × cheap_j.
- **Standard errors:** clustered by month.
- **First-stage F:** Sanderson–Windmeijer, cluster-robust.
- **Own elasticity:** e_jt = (α + α_x cheap_j) p_jt (1 − s_jt).

**Instrument.**

    Z_jt = median expense ratio of the donor funds k, where k:
      • is in the raw index file in month t, with a recorded fee, and is not a money market fund;
      • has the same family as j: firm_f_old(k) = firm_f_old(j), CRSP's management-company code;
      • has the same share class as j;
      • has a different asset class from j.

- **Share class:**
    1. ETF if `ETF_ind` = 1;
    2. else institutional if CRSP `inst_fund` = Y;
    3. else retail if CRSP `retail_fund` = Y;
    4. else the name-keyword class (about 0.3% of mutual-fund rows).

    CRSP flags are matched by `crsp_fundno` and calendar quarter.
- **Asset class:** one of six classes, assigned per tracked index (`market_m_index`) as the most common fund-level class among all raw-file funds tracking that index.
    - Fund-level class = the fund's most common Lipper class (`lipper_class`, CRSP fund summary), mapped as below.
    - Where Lipper is missing (0.04% of rows), the CRSP style-code class is used, then our old class.

| Lipper class | Asset class |
|---|---|
| Mixed-asset target date and target allocation (MAT\*, MTA\*), flexible portfolio (FX, GX), balanced (B, BT), convertibles (CV) | allocation |
| Real estate (RE, GRE, IRE), commodities (CM\*), gold-oriented (AU), real return (RR) | real_asset |
| Alternatives (LSE, OS, AED, AGM, ABR, AMS, MFF, EMN, DSB, DL, ALT), currency (CRX), energy MLP (EMP) | other |
| Any other class with Lipper asset code TX or MB (taxable bond, municipal, money market) | bond |
| International, global, regional and emerging equity (IML\*, ILC\*, ISM\*, IEI, IFCE, IFGE, GML\*, GLC\*, GLV\*, GLG\*, EM, EU, CH, LT, JA, XJ, PC, INR, FM, IF, GL, GEI, GSME, GTK, GNR, GFS, GH, GIF) | intl_equity |
| Other equity (S&P 500, size and style, US sectors, equity income) | us_equity |

**Supply side** (all 107,863 fund-months).
- **Markups:** from the logit first-order conditions, with ownership by `firm_ids` and profit weight κ among BlackRock, Vanguard and SSGA: PC (zero), B0, B25, B50, B65.
- **Marginal cost:** MC = p + η ln(TNA) − markup.
- **Scale η:** 2SLS of MC (winsorized at 1/99 within calendar year) on ln TNA, instrumented by `rotator`, with |TE| and ln age, fund and month FE, clustered by month.
- **Conduct test:** pyRVtest 0.3.2, η = 0.024.
- **Code:** `code/explore/downstream.py`.

## 5b. Final V2: all money market funds out of the donor pool, and why rows lack Z

**Code and outputs.** `code/explore/step40_v2_rows_mmf_donors.py` and `logs/step40.log`. Also `for_coauthor/V2_replication/replicate_V2.py`, a standalone script. In `--donor-mmf sample` mode it reproduces step38's V2 exactly: N, α, SE, F, η, negative-MC share and minimum MC.

**What changed.** step38 dropped from the donor pool only the 4 money market funds that are in the Table 2 sample. The index CSV holds 16 money market share classes.
- **Flag rule:** "money market" in a CRSP name AND a money-market Lipper class or CRSP style code IM\*.
- **Excluded by the rule:**
    - Requiring both conditions keeps out 32066, Wells Fargo Equity Index Fund, which has one stray IMM code in 1998.
    - It also keeps out 94017, Fidelity Series Treasury Bill Index Fund, which has no "money market" in its name.

**Before and after.**

| | V2 (step38: 4 dropped from donors) | **V2 final (all 16 dropped)** |
|---|---|---|
| N | 96,142 | 96,069 |
| α (SE) | −3.607 (0.419) | −3.642 (0.419) |
| α_x (SE) | −20.596 (0.648) | −20.562 (0.646) |
| Min F | 311.1 | 315.8 |
| Table 5 \|e\| > 1 | 5/15 | 5/15 |
| Negative-MC share B0–B65 | 0.055–0.084 | 0.053–0.082 |
| Min MC | −0.215 | −0.212 |
| Conduct, main IV (A) | PC, B50, B65 | PC, B50, B65 |

- Z changes on 987 fund-months (32 funds: JPMorgan, Russell, Allspring), and 73 fund-months lose Z.

**Why demand uses 96,069 of the 107,863 rows.** The rows without Z stay in the shares, in s₀ and on the supply side.

| Reason | Fund-months | Funds | Share cheap | Mean fee |
|---|---|---|---|---|
| (a) no `firm_f_old` (VALIC, Voya, Prudential, John Hancock insurance trusts, etc.) | 7,771 | 112 | 0.15 | 0.61 |
| (b) family has no fund in another asset class that month (abrdn Gold, SEI, USAA, Invesco S&P 500) | 2,533 | 68 | 0.48 | 0.31 |
| (c) other-class funds exist, none in the same share class (BlackRock LifePath K and P classes, SSgA S&P 500 N) | 1,490 | 60 | 0.33 | 0.26 |

## 5c. How coarse should the exclusion be?

**Exclusion levels compared.** Model 1 excluded 5 asset classes (ours) and V2 excludes 6 (Lipper). The finer exclusions tested earlier are much finer: 783 index clusters (model 2) and 1,662 tracked indices (model 3).

**The test.** `code/explore/step41_finer_asset_class.py` and `logs/step41.log` try an intermediate level: 14 Lipper-based groups.
- **Groups:** US large, mid, small and sector; international developed; global; emerging; single region or country; government bond; core and credit bond; municipal bond; allocation; real asset; other.
- **Everything else** is as in the final V2.

| Exclusion (all without money market funds) | Non-cheap α (SE) | Min F | e > 0 | Table 5 \|e\| > 1 | Negative-MC share B0–B65 |
|---|---|---|---|---|---|
| **6 asset classes (V2)** | **−3.64 (0.42)** | 316 | 0 | 5/15 | 0.05–0.08 |
| 14 Lipper groups | −0.25 (0.40) | 440 | 0 | 3/15 | 0.84–0.86 (more than half below −0.60%) |
| 783 clusters (model 2, step39) | +0.40 | | 0.53 | | |
| 1,662 indices (model 3, step39) | +1.49 | | invalid | | |

**Reading.** The finer the exclusion, the flatter the non-cheap slope. That is the pattern expected when the remaining donors share demand shocks with fund j: their fees move with j's demand, which biases α toward zero. The 6-class exclusion is the finest level tested that passes the demand screens.

## 5d. Donors from the whole index CSV vs the Table 2 sample only

**Code and outputs.** `code/explore/step42_donors_table2_only.py` and `logs/step42.log`.

**Setup.** Z_jt uses same-month donors only, so funds before 2010 never enter Z for an estimation row. They matter only for the per-index asset-class assignment. What differs between the two versions is the same-month donors that the Table 2 filters drop: market share below 0.01%, `prefer` = 6 (index R² below 0.95) and fee ≤ 0. In 2010 and later, 362,944 of the 470,807 donor-pool fund-months (77%) are outside Table 2.

| Donors | N | Non-cheap α (SE) | α_x | Min F | e > 0 | Table 5 \|e\| > 1 |
|---|---|---|---|---|---|---|
| **Whole CSV (V2)** | 96,069 | −3.64 (0.42) | −20.56 | 316 | 0 | 5/15 |
| Table 2 fund-months only | 90,163 | +0.62 (0.52) | −17.83 | 279 | **0.51** | 3/15 |

- Z differs on 61,545 rows (correlation 0.90).
- With Table 2 donors only, negative MC is zero. That is mechanical: with upward-sloping demand the markups are negative.

**Reading.** The small and loosely tracking funds of the same family carry most of the instrument's identifying variation. Restricted to Table 2 donors, Z fails the slope screen. Anyone replicating V2 must build Z from the whole CSV.

## 6. Decisions this needs from Gene

1. **Drop the 4 money market funds?** This changes the 108,300-row sample that Danny and the paper use. The paper's own numbers would also move: model 6 without them goes from −8.1 to −3.0.
2. **Use Lipper classes for the asset class**, to be recorded in `DECISIONS.md` next to the share-class ruling.
3. **Whether and how to tell Danny.** Nothing has been sent.
