# Four demand specifications for the index market, with and without the variable-annuity funds: which results survive?

## Scorecard: all 4 models

**Caution.** Column 2 is now Danny's own specification, built from the category10 labels in his handoff zip; it reproduces his coefficient exactly (−5.713, SE 0.747). "A5" is the broad-based interaction, which is Table A7 in our copy of the paper. V2 is shown as originally defined; section 9 reports robustness checks of it, two of which it does not pass (Danny's category10 classes as the exclusion, and a different classification of 37 funds as cheap). No test here establishes that any instrument satisfies the exclusion restriction.

✓ = desirable, ~ = borderline, ✗ = undesirable, – = not applicable. "With VA" is each specification as written. "No VA" drops the 112 variable-annuity funds (7,771 fund-months) from the sample: they leave the demand estimation and the supply side, and their assets count in the outside good. Downstream rows give the range over B0–B65 at each candidate's own estimated η; conduct uses η scheme A (0.024). Sources: `logs/spec_compare/sc_demand.csv`, `sc_a5_demand.csv`, `sc_exva_demand.csv`, `sc_scale.csv`, `sc_mc.csv`, `sc_where.csv` and their `sc_a5_*` and `sc_exva_*` counterparts, `sc_conduct_*.csv`.

| | 1 T2, with VA | 1 T2, no VA | 2 Modified T2 (Danny), with VA | 2 Modified T2, no VA | 3 V2, with VA | 3 V2, no VA | 4 A5 (broad), with VA | 4 A5, no VA |
|---|---|---|---|---|---|---|---|---|
| **Specification** | | | | | | | | |
| Instrument | paper IV0 | paper IV0 | IV0 rebuilt with a category10 exclusion | same | Z (V2) | Z (V2) | paper IV0 | paper IV0 |
| Donors exclude the target's | index | index | index and category10 class | same | Lipper-6 asset class, other share types | same | index | index |
| Price interaction | none | none | none | none | cheap | cheap | broad-based | broad-based |
| Estimation rows | 108,300 | 100,529 | 108,300 (2,502 on original IV0) | 100,529 | 96,069 | 96,069 | 108,300 | 100,529 |
| Supply rows | 108,300 | 100,529 | 108,300 | 100,529 | 107,863 | 100,092 | 108,300 | 100,529 |
| **Demand outcomes** | | | | | | | | |
| Base price coefficient (SE) | −5.606 (1.310) | **+7.244 (1.987)** | −5.713 (0.747) | **+1.485 (1.079)** | −3.642 (0.419) | −3.642 (0.419) | −7.503 (1.770) | **+4.009 (1.588)** |
| Interaction (SE) | – | – | – | – | −20.562 (0.646) | −20.562 (0.646) | −5.278 (0.372) | −6.924 (0.428) |
| Average own elasticity | −1.61 | +1.91 | −1.64 | +0.39 | −1.93 | −1.93 | −2.86 | +0.31 |
| Asset-weighted own elasticity | −0.72 | +0.89 | −0.74 | +0.18 | −1.61 | −1.61 | −1.31 | +0.08 |
| Table 5 funds with e < −1 | 2/15 | 0/15 | 2/15 | 0/15 | 5/15 | 5/15 | 2/15 | 0/15 |
| **Demand screens** | | | | | | | | |
| Goal A: no upward slope (e > 0 share) | ✓ 0 | ✗ 1.00 | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.49 |
| First-stage F (min) | ✓ 34 | ✓ 27 | ✓ 129 | ✓ 79 | ✓ 316 | ✓ 316 | ✓ 53 | ✓ 49 |
| **Downstream outcomes** | | | | | | | | |
| Scale η range (PC–B65; SE about 0.005) | 0.0205–0.0213 | 0.0228–0.0235 | 0.0205–0.0213 | 0.0192–0.0247 | 0.0210–0.0220 | 0.0238–0.0250 | 0.0205–0.0208 | 0.0233–0.0250 |
| Negative-markup share | ✓ 0 | ✗ 1.00 | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.49 |
| Negative-MC share, η = 0 | 0.52–0.58 | – | 0.52–0.58 | – | 0.33–0.46 | 0.35–0.48 | 0.39–0.47 | – |
| Negative-MC share, η = 0.024 | 0.17–0.34 | – | 0.16–0.33 | – | 0.04–0.07 | 0.04–0.08 | 0–0.04 | – |
| Goal B: negative-MC share, own η | 0.21–0.36 | – | 0.20–0.35 | – | 0.053–0.082 | **0.041–0.073** | 0.005–0.088 | – |
| Min MC (% of assets) | −0.31 | – | −0.30 | – | −0.21 | −0.19 | −0.12 | – |
| **MC screens** | | | | | | | | |
| Magnitude: ≤ 2% below −0.20%, none below −0.60% | ~ B65 8.9% | – | ~ B65 6.9% | – | ✓ | ✓ | ✓ | – |
| Location: not at Vanguard or SPY | ✗ Vanguard 81% (B0); SPY at B65 | – | ✗ Vanguard 79% (B0); SPY at B65 | – | ✗ Vanguard 13% (B0) | ✗ Vanguard 10% (B0) | ~ Vanguard 2% (B0), 26% (B65) | – |
| **Conduct** | | | | | | | | |
| Main IV selected set | PC | – | PC | – | PC, B50 (0.19), B65 (0.79) | PC (0.52), B50 (0.05), B65 (1.00) | PC, B65 (0.08) | – |
| Alternative IVs (majority) | PC | – | PC | – | PC | PC | PC | – |
| B0 and B25 rejected | ✓ | – | ✓ | – | ✓ | ✓ | ✓ | – |
| **Overall** | **passes only with the VA funds** | **demand slopes upward** | **almost identical to T2; passes only with the VA funds** | **demand slopes upward** | **passes demand screens; MC location caveat** | **unchanged; slightly fewer negative MCs** | **passes only with the VA funds** | **49% slope upward** |

**What the scorecard says.**
- **T2, the modified T2 and A5 are all fragile.** Their downward-sloping demand, and everything downstream of it, depends on keeping the variable-annuity funds in the estimation. Without those funds T2 and the modified T2 slope upward for every fund-month, and A5 for 49% of them.
- **Danny's category10 exclusion barely changes T2.** With the variable-annuity funds in, the coefficient is −5.71 against −5.61, the negative-MC share 20–35% against 21–36%, Vanguard's negative share 79% against 81%, and the conduct result PC alone in both.
- **V2 is the only specification that survives the exclusion.** The variable-annuity funds were never in its demand estimation. Dropping them from the supply side lowers the negative-MC share slightly (4.1–7.3%) and moves the conduct result toward B65.
- **So the choice is no longer between column 2 and column 3.** If the variable-annuity funds are excluded, columns 1, 2 and 4 do not deliver downward-sloping demand, and V2 is the remaining candidate.
- **V2 is not robust on every dimension** (section 9). It holds up with donors from Danny's full source panel and with CRSP's own ETF flag. It does not hold up with Danny's category10 classes as the exclusion (the non-cheap slope turns positive), and its low negative-MC share depends on how 37 funds near the cheap cutoff are classified.

- **Code:** `code/spec_compare/sc_build.py`, `sc_demand.py`, `sc_downstream.py` (columns 1 and 3), `sc_danny_cat10.py` (column 2), `sc_a5.py` (column 4), `sc_exva.py` (the "no VA" columns), `sc_v2_source_donors.py` (section 9).
- **Logs and CSVs:** `logs/spec_compare/`.
- **Money market funds:** the 4 in the sample (437 fund-months) stay in columns 1, 2 and 4 and are dropped in column 3, as in each specification's definition.
- **Not run:** downstream MC and conduct for the three "no VA" columns with upward-sloping demand, where markups are negative and the results have no meaning.

## 0. Validation

| Check | Result |
|---|---|
| T2: paper's −5.606 (1.310) | **−5.606 (1.310)**: exact |
| A5: paper's Table A7 Panel A col 2, −7.503 and −5.278 | **−7.503 (1.770) and −5.278 (0.372)**: exact |
| V2: −3.642 (0.419), −20.562 (0.646), F 315.8, N 96,069 | **exact**, with its downstream and conduct results |
| Danny's modified T2: −5.713 (0.747), 2,502 rows on the original IV0 | **−5.713 (0.747), 2,502 rows**: exact, from the labels in his handoff zip. Our earlier Lipper-6 proxy gave −9.107 and is no longer used |
| Paper's IV0 rebuilt from Danny's donor file | equal to the stored IV0 on all 108,300 rows (largest difference 2e-13) |
| T2 negative-MC share, B0, η = 0: Danny's 0.5156 | **0.516** |
| Scale under PC: Danny's 0.0205 (0.0051) | **0.0205 (0.0051)** |

## 1. What V2 is, next to T2 and A5

V2 is not in the current paper. All three models are logit demand estimated by IV, with the same dependent variable, controls, fixed effects and clustering. They differ in the price interaction, the instrument and the rows used.

    T2:  ln s_jt − ln s_0t = α p_jt                               + β1 |TE_jt| + β2 R_jt + β3 ln Age_jt + μ_j + τ_t + ξ_jt
    A5:  ln s_jt − ln s_0t = α p_jt + α_b (p_jt × broad_j)        + (the same)
    V2:  ln s_jt − ln s_0t = α p_jt + α_c (p_jt × cheap_j)        + (the same)

p is the expense ratio in percent, TE the tracking error, R the past one-year return, μ_j fund (share-class) effects and τ_t month effects. Standard errors are clustered by month.

| Element | T2 (paper Table 2 col 2) | A5 (paper Table A7 col 2) | V2 |
|---|---|---|---|
| Price interaction | none | broad-based | cheap |
| Indicator | – | the paper's `broad_specialized` = "broad-based"; 53% of fund-months | `gene_idx`: the fund's expense ratio in its first month in the index CSV is at or below the 20th percentile of that month's expense ratios across all funds in the CSV. Fixed per fund; 47% of estimation fund-months |
| Own-price slope | α for every fund | α (specialized), α + α_b (broad-based) | α (non-cheap), α + α_c (cheap) |
| Instrument | the paper's `BLP_IV_hausman_exp_ratio` (IV0) | IV0 and IV0 × broad | Z and Z × cheap |
| Donor funds: family | same `firm_f_old`; funds with a blank code are treated as one family | same as T2 | same `firm_f_old`; funds with a blank code get no instrument |
| Donor funds: what is excluded | funds tracking the same index | same as T2 | funds in the same asset class (six classes from CRSP's Lipper class: US equity, international equity, bond, allocation, real asset, other) |
| Donor funds: share type | any | any | the same type as the fund (ETF, institutional or retail, from `ETF_ind` and CRSP's `inst_fund` and `retail_fund` flags) |
| Donor funds: aggregation | mean fee weighted by lagged AUM | same as T2 | unweighted median fee, same month |
| Donor pool | every fund in the source panel that month | same as T2 | every fund in the index CSV that month, including funds outside the Table 2 sample; money market funds removed |
| Money market funds (4 funds, 437 fund-months) | in the sample | in the sample | dropped from the sample and from the donors |
| Rows used to estimate demand | 108,300 | 108,300 | 96,069 |
| Supply-side rows | 108,300 | 108,300 | 107,863 |

**Why V2 uses 96,069 rows.** A row enters the demand estimation only if Z is defined for it. The other rows stay in the market shares, the outside good and the supply side.

| Rows | Fund-months |
|---|---|
| Table 2 Panel A sample | 108,300 |
| minus the 4 money market funds | 107,863 |
| minus variable-annuity funds (no family code) | −7,771 |
| minus rows whose family has no fund in another asset class that month | −2,533 |
| minus rows whose family has such funds, but none of the same share type | −1,490 |
| **V2 demand estimation rows** | **96,069** |

**Reading.**
- **V2 changes three things relative to T2:** a cheap interaction, a stricter instrument (other asset class, same share type, median), and a sample without money market funds and without rows that lack a family instrument.
- **A5 changes one thing relative to T2:** the broad-based interaction. Its instrument and sample are T2's.
- **The modified T2 (column 2) changes only the instrument's exclusion:** donors must also be outside the fund's category10 class (Danny's ten exposure groups), and donors with an unknown category are left out. Share types stay pooled, the lag-AUM weights stay, and rows where the rebuilt instrument is undefined keep the original IV0.
- **Full definitions and code for V2:** `for_coauthor/V2_replication/NOTE_V2_replication.md` and `replicate_V2.py`.

## 2. Gene's proposal: exclude the variable-annuity funds from the sample

**Who they are.**
- The 7,771 fund-months without a family code (`firm_f_old`) are all variable-annuity funds, and there are no other variable-annuity funds in the sample.
- The flag is CRSP's `vau_fund`. Of the 112 funds, 109 carry it in every quarter and 3 in some quarters. None of the other 1,190 funds ever carries it.
- Examples: VALIC Company I Stock Index Fund, Voya US Stock Index Portfolio, Prudential Series Fund Stock Index Portfolio, Vanguard Variable Insurance Fund Equity Index Portfolio, John Hancock Variable Insurance Trust 500 Index Trust. Full list: `logs/spec_compare/sc_blank_family_funds.csv`.
- They average 1.7% of inside-market assets (3.5% in 2010, 0.8% in 2024).

**Why exclude them.**
- **They are not bought in the open market.** These funds are chosen from an insurer's menu inside a contract, so the expense ratio is not the price the investor trades off against other index funds.
- **Their fee data are not reliable, which is the harder reason.** In 85% of firm-months every variable-annuity fund of a firm has the same expense ratio in the CSV. Neither the price nor any family instrument is reliable for them (section 7).
- **Their instrument in the paper is not a family instrument.** CRSP has no management code for them, so their family code is blank, and blank codes match one another in IV0. Their donors are other insurers' funds.

**What each treatment gives for Table 2 col 2** (`sc_blank_family_check.log`).

| Treatment of the variable-annuity funds | Price coefficient (SE) | First-stage F |
|---|---|---|
| As in the paper: pooled as one "family" | −5.606 (1.310) | 34 |
| Kept, with their true families (parent firm) | −0.340 (0.049) | 314 |
| **Excluded from the sample (proposal)** | **+7.244 (1.987)** | 27 |

**Reading.**
- **The paper's coefficient exists only under the first treatment.** Each of the two alternatives removes the negative slope.
- **Excluding them is the cleaner choice,** because the true-family version rests on the fee data described in section 7.

## 3. Demand with and without the variable-annuity funds: T2, the modified T2 and A5 change sign

| # | Specification | Sample | N | Price (SE) | Interaction (SE) | Min F | e > 0 | Avg e | Table 5 e < −1 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | T2 | with VA | 108,300 | −5.606 (1.310) | | 33.6 | 0 | −1.61 | 2/15 |
| 1 | T2 | no VA | 100,529 | **+7.244 (1.987)** | | 26.6 | 1.00 | +1.91 | 0/15 |
| 2 | Modified T2 (Danny) | with VA | 108,300 | −5.713 (0.747) | | 128.8 | 0 | −1.64 | 2/15 |
| 2 | Modified T2 (Danny) | no VA | 100,529 | **+1.485 (1.079)** | | 78.6 | 1.00 | +0.39 | 0/15 |
| 3 | V2 | with or without VA | 96,069 | −3.642 (0.419) | cheap −20.562 (0.646) | 315.8 | 0 | −1.93 | 5/15 |
| 4 | A5 | with VA | 108,300 | −7.503 (1.770) | broad −5.278 (0.372) | 53.0 | 0 | −2.86 | 2/15 |
| 4 | A5 | no VA | 100,529 | **+4.009 (1.588)** | broad −6.924 (0.428) | 49.0 | 0.49 | +0.31 | 0/15 |

**Reading.**
- **T2, the modified T2 and A5 change sign.** The variable-annuity rows alone also slope upward (+2.32 under T2), so the negative coefficient comes from pooling the two groups under common month effects, not from fee variation within either. This is my reading of the numbers, not a separate test.
- **The category10 exclusion does not protect the result.** Without the variable-annuity funds its coefficient is +1.49 (SE 1.08): positive, though not significantly different from zero. Our earlier Lipper-6 proxy stayed negative there (−3.49), so the outcome depends on which exposure classes are excluded.
- **V2 is unchanged by construction.** Rows without a family code have no Z, so they were never in its estimation. Dropping them changes only the outside share, which the month effects absorb.

## 4. Scale η by conduct candidate: insensitive to demand, slightly higher without the variable-annuity funds

| # | Sample | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|---|
| 1 T2 | with VA | 0.0205 (0.0051) | 0.0213 | 0.0212 | 0.0211 | 0.0209 |
| 2 Modified T2 (Danny) | with VA | 0.0205 | 0.0213 | 0.0212 | 0.0211 | 0.0209 |
| 3 V2 | with VA | 0.0211 (0.0051) | 0.0210 | 0.0215 | 0.0218 | 0.0220 |
| 3 V2 | no VA | 0.0238 (0.0050) | 0.0238 | 0.0244 | 0.0247 | 0.0250 |
| 4 A5 | with VA | 0.0205 | 0.0208 | 0.0208 | 0.0206 | 0.0205 |

**Reading.**
- **η does not depend on the demand model or the conduct candidate.** Within a sample the spread is 0.001.
- **The sample moves it more:** 0.021 with the variable-annuity funds and 0.024 without. The difference is about half a standard error.

## 5. Negative marginal costs: the modified T2 is as bad as T2; V2 is low with or without the variable-annuity funds

Monthly-mean share of fund-months with MC < 0, B0 → B65. PC is 0 in every row.

| # | Sample | η = 0 | η = 0.024 | Own η | Share below −0.10% (own η) | Share below −0.20% (own η) | Min MC | Mean markup (%) |
|---|---|---|---|---|---|---|---|---|
| 1 T2 | with VA | 0.52–0.58 | 0.17–0.34 | 0.21–0.36 | 0.028–0.266 | 0–0.089 | −0.31 | 0.22–0.31 |
| 2 Modified T2 (Danny) | with VA | 0.52–0.58 | 0.16–0.33 | 0.20–0.35 | 0.021–0.256 | 0–0.069 | −0.30 | 0.22–0.30 |
| 3 V2 | with VA | 0.33–0.46 | 0.04–0.07 | 0.053–0.082 | 0.001–0.030 | 0–0.0002 | −0.21 | 0.19–0.23 |
| 3 V2 | no VA | 0.35–0.48 | 0.04–0.08 | **0.041–0.073** | 0.0001–0.016 | 0 | −0.19 | 0.19–0.23 |
| 4 A5 | with VA | 0.39–0.47 | 0–0.04 | 0.005–0.088 | 0–0.0004 | 0 | −0.12 | 0.13–0.17 |

**Where the negatives are** (own η; share negative within the group).

| Specification, sample, conduct | Vanguard | SSGA | BlackRock | Other firms | SPY | Cheap / non-cheap |
|---|---|---|---|---|---|---|
| 1 T2, with VA, B0 | **0.81** | 0.03 | 0.04 | 0.01 | 0 | 0.40 / 0.06 |
| 2 Modified T2, with VA, B0 | **0.79** | 0.02 | 0.03 | 0 | 0 | 0.39 / 0.05 |
| 2 Modified T2, with VA, B65 | **0.96** | 0.51 | 0.38 | 0 | **0.85** | 0.62 / 0.15 |
| 3 V2, with VA, B0 | 0.13 | 0.04 | 0.05 | 0.02 | 0 | 0 / 0.10 |
| 3 V2, no VA, B0 | 0.10 | 0.02 | 0.04 | 0.01 | 0 | 0 / 0.08 |
| 3 V2, no VA, B65 | 0.16 | 0.19 | 0.06 | 0.01 | 0 | 0 / 0.14 |
| 4 A5, with VA, B65 | 0.26 | 0.09 | 0.09 | 0 | 0 | 0.16 / 0.03 |

**Reading.**
- **Goal B separates V2 from the single-slope models.** T2 and the modified T2 have 20% to 36% of marginal costs negative, mostly at Vanguard, and reach SPY at B65. V2 has 4% to 8%.
- **The reason is the slope on the low-fee funds.** A single slope of −5.7 gives a fund charging 0.03% an elasticity of −0.17 and a markup several times its fee. V2 gives the cheap funds −24.2.
- **V2's negatives stay on non-cheap funds,** with Vanguard at 10% to 16%. Securities lending cannot explain those, so the location caveat remains.
- **T2, the modified T2 and A5 without the variable-annuity funds are not shown.** Their markups are negative for 100%, 100% and 49% of fund-months.

## 6. Conduct test: B0 and B25 are rejected throughout; the weight on B65 rises without the variable-annuity funds

Selected sets (MCS p ≥ 0.05), η scheme A (0.024); MCS p-values in brackets.

| # | Sample | **Main IV** (rival2 × csent_index) | rival2 × csent_income3 | rival3 × csent_index | rival2 × bab_usa / × fmax / × rotator | Min F, main IV |
|---|---|---|---|---|---|---|
| 1 T2 | with VA | PC (B50 0.02, B65 0.03 rejected) | PC | PC | PC | 67 |
| 2 Modified T2 (Danny) | with VA | PC (B50 0.02, B65 0.03 rejected) | PC | PC | PC | 69 |
| 3 V2 | with VA | PC, B50 (0.19), B65 (0.79) | PC, B50, B65 | PC | PC | 140 |
| 3 V2 | no VA | PC (0.52), B50 (0.05), B65 (1.00) | PC, B50, B65 | PC | PC | 157 |
| 4 A5 | with VA | PC, B65 (0.08) | PC, B65 | PC | PC | 103 |

Schemes B (own η), C (PC η) and A with markups capped 1/99 by year give the same sets, with one exception: for V2 without the variable-annuity funds, B50 sits at the 5% line (p 0.05 to 0.07) and drops out under scheme C.

**Reading.**
- **B0 and B25 are rejected in every row.** PC is never rejected. T2 and the modified T2 also reject B50 and B65.
- **Without the variable-annuity funds, B65 becomes the best-fitting model under V2** (MCS p of 1.00, with PC at 0.52). With them, PC fits best. The two are not separable in either sample.
- **This is reported, not used to choose.** The demand criteria come first.

## 7. The fee data for the variable-annuity funds: imputed, not observed

**Why a result with their true families is not trustworthy either.** Rebuilding the instrument for these funds with their true families gives a Table 2 coefficient of about −0.3 (section 1). On those rows the rebuilt instrument tracks each fund's own fee almost one for one (first-stage F in the thousands). The cause is the fee data (`sc_blank_family_check.log`):

- In 85% of firm-months, every variable-annuity fund of a firm has the same expense ratio in the index CSV.
- Allianz's funds are all at 0.400% in 2010–2016, then all at 0.535% in 2018 and 0.458% in 2020.
- Mutual of America's funds, including its S&P 500 index fund, are all at 0.13% in 2010, 1.05% in 2012, 1.42% in 2014 and 1.93% in 2022.

**Where these fees come from: they are imputed, not observed** (`logs/spec_compare/sc_source_panel_check.log`).
- CRSP has no expense ratio in 97% of the quarterly records of the variable-annuity funds, against 6% for the other funds in the sample. For 99 of the 112 funds it has none in any record.
- Danny's build script (`5_fund_market_data_for_Matteo_v6_nonlev_etf.R`, lines 89–99) fills a missing expense ratio with the mean fee of the funds whose names share the same first five letters, first on the same date and then over all dates.
- So the "price" of a variable-annuity fund is an average of the fees of other funds with a similar name, which are mostly the same firm's funds. A family instrument for these funds is then nearly the fund's own price by construction, and it cannot identify the slope.

**This settles the question we had for Danny.** The fees are an imputation in the build, not CRSP as reported. It is a further reason to exclude these funds: their prices are not observed.

## 8. Danny's source panel and the index CSV: what the 96,000 missing rows are

Danny's note counts 675,551 passive source rows; the index CSV has 579,632. The source panel is `index_funds_preprocess_oct2026.csv` in the shared Dropbox, and the CSV is that panel after one filter in the build script (`sc_source_panel_check.log`).

| Rows in the source panel but not in the index CSV | Fund-months |
|---|---|
| No past one-year return or tracking error (a fund's first 12 months) | 38,713 |
| No expense ratio | 29,114 |
| Assets or lagged assets missing or not positive | 3,430 |
| Fund-level data complete, but the paper's Hausman instrument is undefined (the family has no fund on another index that month) | 23,178 |
| Index-level conduct instrument missing | 426 |
| Not explained by this reconstruction | 1,058 |
| **Total** | **95,919** |

**Reading.**
- **The CSV is the estimation-ready subset of the source panel.** Every CSV row is in the source panel, with the same fee and family code.
- **The paper's instrument is built before the filter,** so 60,773 of the missing rows (9.5% of all usable donor rows) are donors in IV0 but are absent from any instrument rebuilt from the CSV. This is why our rebuild of IV0 matches the original on only 90% of rows.
- **V2's instrument draws donors from the CSV only.** Section 9 rebuilds it on the full source panel.

## 9. How robust is V2? Donor pool and ETF flag: yes. Exclusion classes and the cheap cutoff: no

All rows are V2's model (price and price × cheap, instruments Z and Z × cheap), changing one element at a time (`code/spec_compare/sc_v2_robust.py`, `sc_v2_source_donors.py`; `logs/spec_compare/sc_v2_robust.csv`). The negative-MC share is at each candidate's own η.

| Variant | N | Non-cheap α (SE) | × cheap (SE) | Min F | e > 0 | Table 5 e < −1 | Negative MC B0–B65, with VA | No VA |
|---|---|---|---|---|---|---|---|---|
| **V2 as reported** | 96,069 | **−3.642 (0.419)** | −20.562 (0.646) | 316 | 0 | 5/15 | 0.053–0.082 | 0.041–0.073 |
| Donors from the full source panel | 96,224 | −3.254 (0.419) | −19.649 (0.612) | 301 | 0 | 5/15 | 0.078–0.103 | 0.065–0.097 |
| Source-panel donors with observed fees only | 96,197 | −3.575 (0.402) | −19.927 (0.582) | 298 | 0 | 5/15 | 0.057–0.087 | 0.045–0.077 |
| ETF flag from CRSP (`et_flag`) | 96,814 | −3.575 (0.398) | −21.097 (0.675) | 424 | 0 | 5/15 | 0.057–0.086 | 0.044–0.076 |
| Danny's approved share types | 96,814 | −3.575 (0.398) | −21.097 (0.675) | 424 | 0 | 5/15 | 0.057–0.086 | 0.044–0.076 |
| CRSP ETF flag and source-panel donors | 96,969 | −3.282 (0.421) | −20.295 (0.683) | 386 | 0 | 5/15 | 0.077–0.101 | 0.063–0.096 |
| **Cheap rebuilt on the source panel, observed fees** | 96,069 | **−2.010 (0.412)** | −20.542 (0.576) | 278 | 0 | 4/15 | **0.22–0.32** | 0.21–0.29 |
| Cheap rebuilt on the source panel, imputed entry fees included | 96,069 | −1.970 (0.360) | −19.265 (0.406) | 329 | 0 | 4/15 | 0.24–0.36 | 0.23–0.33 |
| **Exclusion by Danny's category10 classes** | 95,912 | **+1.448 (0.646)** | −16.514 (0.649) | 281 | **0.53** | 3/15 | – | – |
| CRSP ETF flag, source donors, source cheap (observed), category10 | 96,831 | +3.064 (0.684) | −16.851 (0.599) | 259 | 0.54 | 2/15 | – | – |

**Donor pool.** The rows of the source panel that are not in the CSV are not like the variable-annuity funds. Of the 54,945 that have a family code and can be donors, 59% are a fund's first 12 months, and 93% have a fee that CRSP reports. They are absent from the CSV because they lack a one-year return history, not because their fees are missing.

**ETF flag.** This is not an error in CRSP. The build script (lines 662–672) sets `ETF_ind` = 1 if CRSP's `et_flag` is F in any quarter, or the fund name contains "ETF", or the name contains "ishares", "spdr", "holdrs", "streettracks" or "exchange traded".
- The name rules flag 110 funds in the source panel that CRSP never marks as an ETF (103 in the CSV, 14 in the Table 2 sample).
- They are of two kinds: BlackRock's index mutual funds, which carry the iShares name (for example "iShares Russell 2000 Small-Cap Index Fund; Institutional Shares"), and funds of ETFs (for example "LVIP Vanguard Domestic Equity ETF Fund", "Morningstar Balanced ETF Asset Allocation Portfolio"). 34 of the 110 are variable-annuity funds.
- No fund that CRSP marks as an ETF is missed. So the error is systematic but one-sided and small.
- With CRSP's flag, V2 is unchanged (−3.58 and −21.10) and the first stage is stronger. Danny's approved share types give the identical result.
- **Correction to my earlier message:** the "corrected flag" row I reported before (−4.88) used the source panel's own `ETF` column. That column applies the same name rules quarter by quarter, so it was not a correction. Those numbers should be disregarded.

**Cheap indicator.** `gene_idx` uses a fund's first month in the CSV, which is 6 months (median) after its first month in the source panel, because the CSV needs a one-year return. Rebuilding it on the source panel, using only fees that CRSP reports, changes the status of 37 funds (3,068 fund-months).
- **Demand still slopes down everywhere,** but the non-cheap slope falls to −2.0 and the negative-MC share rises to 22–32%.
- **The funds that matter are large Vanguard classes at the cutoff.** Vanguard Total Stock Market Investor and Vanguard 500 Investor charged 0.20% and 0.19% in their first month in each file. That ties the 20th-percentile cutoff of 0.20% in January 1994 (cheap, since ties count), and is above the cutoff of 0.14% in 1993 (not cheap).
- **Neither date is these funds' true entry.** Both files start in 1993–94, decades after the funds launched. The result shows that V2's marginal-cost numbers depend on a knife-edge classification of a few very large funds.
- **Including imputed entry fees makes it worse and is not a valid version:** 30% of funds have an imputed or backfilled fee in their first source month (iShares Core US Aggregate Bond shows 0.515% against a true 0.20%).

**Exclusion classes.** Danny's category10 splits equity into US size and style, global developed, emerging, and sector or theme, and bonds into government, credit, municipal and diversified. V2's six classes keep each of those together.
- **With category10 as the exclusion, V2's non-cheap slope is +1.45 and 53% of fund-months slope upward.**
- **This is the pattern found before** (`RESULTS_best_model1.md` §5c): the finer the exclusion, the more a fund's same-asset-class siblings act as donors, and the more positive the non-cheap slope (14 Lipper groups −0.25, 783 clusters +0.40).
- **So V2 rests on excluding the whole broad asset class.** That is an identifying assumption, namely that a family's funds in the same broad asset class share demand shocks, and the data cannot confirm it.

**Reading.**
- **V2 passes the checks on data handling:** donor pool, imputed donor fees, ETF flag, share types.
- **V2 does not pass two checks on its design:** the exclusion level, which decides the sign of the non-cheap slope, and the cheap classification of a few large funds, which decides how many marginal costs are negative.
- **The cheap slope is stable throughout** (−16.5 to −21.1 for the interaction). What moves is the non-cheap slope.
- **Not done:** the conduct test for these variants.
