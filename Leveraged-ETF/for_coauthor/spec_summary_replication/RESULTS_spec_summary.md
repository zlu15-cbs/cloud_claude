# Four demand specifications for the index market, with and without the variable-annuity funds: which results survive?

## Scorecard: all 4 models, with an alternative for T2 and A5

**Caution.** Column 2 is Danny's own specification, built from the category10 labels in his handoff zip; it reproduces his coefficient exactly (−5.713, SE 0.747). "A5" is the broad-based interaction, which is Table A7 in our copy of the paper. Column 3 is V2 with the cheap indicator rebuilt on Danny's source panel (section 1); the version first sent to Danny took it from the index CSV and had fewer negative marginal costs (section 9). V2's non-cheap slope depends on excluding the whole broad asset class from the instrument's donors: with Danny's finer category10 classes it turns positive (section 9). No test here establishes that any instrument satisfies the exclusion restriction.

✓ = desirable, ~ = borderline, ✗ = undesirable, – = not applicable. "With VA" is each specification as written. "Alternative" is T2 or A5 with the instrument rebuilt to exclude the target's whole asset class (the six Lipper-based classes V2 uses), pooled share types, lag-AUM weights and donors from Danny's source panel; it is the only version of each with downward-sloping demand once the variable-annuity funds are out (section 10). "No VA" drops the 112 variable-annuity funds (7,771 fund-months) from the sample: they leave the demand estimation and the supply side, and their assets count in the outside good. Downstream rows give the range over B0–B65 at each candidate's own estimated η; conduct uses η scheme A (0.024). Sources: `logs/spec_compare/sc_demand.csv`, `sc_a5_demand.csv`, `sc_exva_demand.csv`, `sc_scale.csv`, `sc_mc.csv`, `sc_where.csv` and their `sc_a5_*` and `sc_exva_*` counterparts, `sc_conduct_*.csv`.

| | 1 T2, with VA | 1 T2, no VA | 1 T2 alternative, no VA | 2 Modified T2 (Danny), with VA | 2 Modified T2, no VA | 3 V2, with VA | 3 V2, no VA | 4 A5 (broad), with VA | 4 A5, no VA | 4 A5 alternative, no VA |
|---|---|---| --- |---|---|---|---|---|---| --- |
| **Specification** | | |  | | | | | | |  |
| Instrument | paper IV0 | paper IV0 | IV0 rebuilt, six-asset-class exclusion | IV0 rebuilt with a category10 exclusion | same | Z (V2) | Z (V2) | paper IV0 | paper IV0 | IV0 rebuilt, six-asset-class exclusion |
| Donors exclude the target's | index | index | Lipper-6 asset class | index and category10 class | same | Lipper-6 asset class, other share types | same | index | index | Lipper-6 asset class |
| Price interaction | none | none | none | none | none | cheap | cheap | broad-based | broad-based | broad-based |
| Estimation rows | 108,300 | 100,529 | 98,151 | 108,300 (2,502 on original IV0) | 100,529 | 96,069 | 96,069 | 108,300 | 100,529 | 98,151 |
| Supply rows | 108,300 | 100,529 | 100,529 | 108,300 | 100,529 | 107,863 | 100,092 | 108,300 | 100,529 | 100,529 |
| **Demand outcomes** | | |  | | | | | | |  |
| Base price coefficient (SE) | −5.606 (1.310) | **+7.244 (1.987)** | −4.123 (0.736) | −5.713 (0.747) | **+1.485 (1.079)** | −2.010 (0.412) | −2.010 (0.412) | −7.503 (1.770) | **+4.009 (1.588)** | −3.983 (0.754) |
| Interaction (SE) | – | – | – | – | – | −20.542 (0.576) | −20.542 (0.576) | −5.278 (0.372) | −6.924 (0.428) | −4.413 (0.382) |
| Average own elasticity | −1.61 | +1.91 | −1.09 | −1.64 | +0.39 | −1.52 | −1.52 | −2.86 | +0.31 | −1.52 |
| Asset-weighted own elasticity | −0.72 | +0.89 | −0.51 | −0.74 | +0.18 | −1.34 | −1.34 | −1.31 | +0.08 | −0.75 |
| Table 5 funds with e < −1 | 2/15 | 0/15 | 1/15 | 2/15 | 0/15 | 4/15 | 4/15 | 2/15 | 0/15 | 1/15 |
| **Demand screens** | | |  | | | | | | |  |
| Goal A: no upward slope (e > 0 share) | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.49 | ✓ 0 |
| First-stage F (min) | ✓ 34 | ✓ 27 | ✓ 124 | ✓ 129 | ✓ 79 | ✓ 278 | ✓ 278 | ✓ 53 | ✓ 49 | ✓ 162 |
| **Downstream outcomes** | | |  | | | | | | |  |
| Scale η range (PC–B65; SE about 0.005) | 0.0205–0.0213 | 0.0228–0.0235 | 0.0233–0.0245 | 0.0205–0.0213 | 0.0192–0.0247 | 0.0211–0.0255 | 0.0238–0.0287 | 0.0205–0.0208 | 0.0233–0.0250 | 0.0229–0.0233 |
| Negative-markup share | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.49 | ✓ 0 |
| Negative-MC share, η = 0 | 0.52–0.58 | – | 0.61–0.72 | 0.52–0.58 | – | 0.62–0.72 | 0.63–0.74 | 0.39–0.47 | – | 0.54–0.62 |
| Negative-MC share, η = 0.024 | 0.17–0.34 | – | 0.33–0.48 | 0.16–0.33 | – | 0.21–0.35 | 0.23–0.37 | 0–0.04 | – | 0.12–0.37 |
| Goal B: negative-MC share, own η | 0.21–0.36 | – | 0.32–0.48 | 0.20–0.35 | – | 0.22–0.32 | 0.21–0.29 | 0.005–0.088 | – | 0.14–0.39 |
| Min MC (% of assets) | −0.31 | – | −0.46 | −0.30 | – | −0.50 | −0.48 | −0.12 | – | −0.33 |
| **MC screens** | | |  | | | | | | |  |
| Magnitude: ≤ 2% below −0.20%, none below −0.60% | ~ B65 8.9% | – | ✗ 2–29% below −0.20% | ~ B65 6.9% | – | ✗ 8–11% below −0.20% | ✗ 7–11% below −0.20% | ✓ | – | ~ B0–B50 pass; B65 5.8% |
| Location: not at Vanguard or SPY | ✗ Vanguard 81% (B0); SPY at B65 | – | ✗ Vanguard 94% (B0); SPY at B65 | ✗ Vanguard 79% (B0); SPY at B65 | – | ✗ Vanguard 24%, SSGA 43% (B0); SPY never | ✗ Vanguard 25%, SSGA 38% (B0); SPY never | ~ Vanguard 2% (B0), 26% (B65) | – | ✗ Vanguard 32% (B0), 89% (B65); SPY at B65 |
| **Conduct** | | |  | | | | | | |  |
| Main IV selected set | PC | – | PC, B50 (0.17), B65 (0.18) | PC | – | B25 (0.08), B50 (0.59), B65 (1.00); PC rejected | B50 (0.13), B65 (1.00); PC rejected | PC, B65 (0.08) | – | PC, B50 (0.31), B65 (0.42) |
| Alternative IVs (majority) | PC | – | PC | PC | – | B25, B50 | B25, B50 | PC | – | PC |
| B0 and B25 rejected | ✓ | – | ✓ | ✓ | – | ~ B0 rejected; B25 kept (0.08) | ✓ with the main IV | ✓ | – | ✓ |
| **Overall** | **passes only with the VA funds** | **demand slopes upward** | **valid sign without the VA funds; flat slope; MC fails** | **almost identical to T2; passes only with the VA funds** | **demand slopes upward** | **demand slopes down; MC screens fail; conduct favours B50–B65** | **the same without the VA funds** | **passes only with the VA funds** | **49% slope upward** | **valid sign without the VA funds; flat slope; MC fails at B50–B65** |

**What the scorecard says.**
- **T2, the modified T2 and A5 are all fragile.** Their downward-sloping demand, and everything downstream of it, depends on keeping the variable-annuity funds in the estimation. Without those funds T2 and the modified T2 slope upward for every fund-month, and A5 for 49% of them. Section 10 tries 16 versions of the instrument for T2 and A5 without these funds.
- **The alternative columns are the best T2 and A5 can do without the variable-annuity funds.** Excluding the whole asset class from the donors gives slopes of −4.1 (T2) and −4.0 with −4.4 (A5). They are flatter than the published versions, leave 14 of the 15 Table 5 funds inelastic, and have more negative marginal costs (32–48% and 14–39%), mostly at Vanguard.
- **Danny's category10 exclusion barely changes T2.** With the variable-annuity funds in, the coefficient is −5.71 against −5.61, the negative-MC share 20–35% against 21–36%, and the conduct result PC alone in both.
- **V2 and the two alternatives are the specifications with downward-sloping demand once the variable-annuity funds are excluded.** All three rest on the same exclusion of the whole asset class. For V2 the sign holds at the 15th, 20th and 25th percentile cutoffs and with donors from the full source panel (section 9).
- **V2 does not meet goal B.** With the cheap indicator rebuilt on the source panel, 22–32% of marginal costs are negative, about as many as under T2, and 8–11% are below −0.20%. They sit on non-cheap funds across all firms, not on Vanguard's cheap funds as under T2.
- **V2's marginal-cost and conduct results are sensitive to the cheap cutoff.** The negative-MC share is 14–18% at the 15th percentile, 22–32% at the 20th and 1–3% at the 25th.
- **V2's conduct result is different from the others'.** Perfect competition is rejected with the main instrument, and B50 and B65 fit best. Under the two alternatives PC fits best and B50 and B65 are not rejected.

- **Code:** `code/spec_compare/sc_build.py`, `sc_demand.py`, `sc_downstream.py` (column 1), `sc_danny_cat10.py` (column 2), `sc_v2_robust.py` and `sc_v2_final.py` (column 3 and section 9), `sc_a5.py` (column 4), `sc_exva.py` (the "no VA" columns 1 and 4), `sc_t2a5_nova_grid.py` (section 10).
- **Logs and CSVs:** `logs/spec_compare/`.
- **Money market funds:** the 4 in the sample (437 fund-months) stay in columns 1, 2 and 4 and are dropped in column 3, as in each specification's definition.
- **Alternative columns:** `sc_t2a5_nova_grid.py` with `SC_ONLY=lipper6,pooled,wavg`, then `sc_v2_final.py` with `SC_ALT=1`; logs `sc_t2a5_alt.csv`, `sc_alt_*.csv`, `sc_conduct_T2alt.csv`, `sc_conduct_A5alt.csv`.
- **Not run:** downstream MC and conduct for the three "no VA" columns with upward-sloping demand, where markups are negative and the results have no meaning.

## 0. Validation

| Check | Result |
|---|---|
| T2: paper's −5.606 (1.310) | **−5.606 (1.310)**: exact |
| A5: paper's Table A7 Panel A col 2, −7.503 and −5.278 | **−7.503 (1.770) and −5.278 (0.372)**: exact |
| V2 as first sent to Danny (cheap from the index CSV): −3.642 (0.419), −20.562 (0.646), F 315.8, N 96,069 | **exact**, with its downstream and conduct results. Column 3 of this report changes the cheap indicator only (section 1) |
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
| Indicator | – | the paper's `broad_specialized` = "broad-based"; 53% of fund-months | cheap: the fund's expense ratio in its entry month is at or below the 20th percentile of that month's expense ratios across all funds in Danny's source panel. The entry month is the fund's first month in the source panel in or after the first quarter in which CRSP reports an expense ratio for it; only such observed fees enter the percentile. Fixed per fund; 46% of estimation fund-months |
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
- **V2's non-cheap slope depends on the broad-asset-class exclusion.** With Danny's category10 classes as the exclusion it is +2.1 and 54% of fund-months slope upward (section 9). The six broad classes are an identifying assumption: a family's funds in the same broad asset class are taken to share demand shocks.
- **The cheap indicator is left-censored for old funds.** The source panel starts in January 1993, so funds launched earlier are classified on their 1993 fee.
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
| 1 | T2 alternative (six-class exclusion) | no VA | 98,151 | −4.123 (0.736) | | 123.7 | 0 | −1.09 | 1/15 |
| 2 | Modified T2 (Danny) | with VA | 108,300 | −5.713 (0.747) | | 128.8 | 0 | −1.64 | 2/15 |
| 2 | Modified T2 (Danny) | no VA | 100,529 | **+1.485 (1.079)** | | 78.6 | 1.00 | +0.39 | 0/15 |
| 3 | V2 | with or without VA | 96,069 | −2.010 (0.412) | cheap −20.542 (0.576) | 278 | 0 | −1.52 | 4/15 |
| 4 | A5 | with VA | 108,300 | −7.503 (1.770) | broad −5.278 (0.372) | 53.0 | 0 | −2.86 | 2/15 |
| 4 | A5 | no VA | 100,529 | **+4.009 (1.588)** | broad −6.924 (0.428) | 49.0 | 0.49 | +0.31 | 0/15 |
| 4 | A5 alternative (six-class exclusion) | no VA | 98,151 | −3.983 (0.754) | broad −4.413 (0.382) | 162.3 | 0 | −1.52 | 1/15 |

**Reading.**
- **T2, the modified T2 and A5 change sign.** The variable-annuity rows alone also slope upward (+2.32 under T2), so the negative coefficient comes from pooling the two groups under common month effects, not from fee variation within either. This is my reading of the numbers, not a separate test.
- **The category10 exclusion does not protect the result.** Without the variable-annuity funds its coefficient is +1.49 (SE 1.08): positive, though not significantly different from zero. Our earlier Lipper-6 proxy stayed negative there (−3.49), so the outcome depends on which exposure classes are excluded.
- **V2 is unchanged by construction.** Rows without a family code have no Z, so they were never in its estimation. Dropping them changes only the outside share, which the month effects absorb.

## 4. Scale η by conduct candidate: insensitive to demand, slightly higher without the variable-annuity funds

| # | Sample | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|---|
| 1 T2 | with VA | 0.0205 (0.0051) | 0.0213 | 0.0212 | 0.0211 | 0.0209 |
| 1 T2 alternative | no VA | 0.0233 | 0.0245 | 0.0245 | 0.0244 | 0.0244 |
| 2 Modified T2 (Danny) | with VA | 0.0205 | 0.0213 | 0.0212 | 0.0211 | 0.0209 |
| 3 V2 | with VA | 0.0211 (0.0051) | 0.0227 | 0.0237 | 0.0248 | 0.0255 |
| 3 V2 | no VA | 0.0238 (0.0050) | 0.0258 | 0.0267 | 0.0278 | 0.0287 |
| 4 A5 | with VA | 0.0205 | 0.0208 | 0.0208 | 0.0206 | 0.0205 |
| 4 A5 alternative | no VA | 0.0233 | 0.0230 | 0.0230 | 0.0229 | 0.0229 |

**Reading.**
- **η depends little on the demand model or the conduct candidate.** Within a sample the spread is 0.001 for the single-slope models and 0.004 for V2, less than one standard error.
- **The sample moves it more:** 0.021 with the variable-annuity funds and 0.024 without. The difference is about half a standard error.

## 5. Negative marginal costs: a fifth to a third of fund-months in T2, the modified T2 and V2

Monthly-mean share of fund-months with MC < 0, B0 → B65. PC is 0 in every row.

| # | Sample | η = 0 | η = 0.024 | Own η | Share below −0.10% (own η) | Share below −0.20% (own η) | Min MC | Mean markup (%) |
|---|---|---|---|---|---|---|---|---|
| 1 T2 | with VA | 0.52–0.58 | 0.17–0.34 | 0.21–0.36 | 0.028–0.266 | 0–0.089 | −0.31 | 0.22–0.31 |
| 1 T2 alternative | no VA | 0.61–0.72 | 0.33–0.48 | 0.32–0.48 | 0.186–0.386 | 0.021–0.294 | −0.46 | 0.31–0.42 |
| 2 Modified T2 (Danny) | with VA | 0.52–0.58 | 0.16–0.33 | 0.20–0.35 | 0.021–0.256 | 0–0.069 | −0.30 | 0.22–0.30 |
| 3 V2 | with VA | 0.62–0.72 | 0.21–0.35 | 0.22–0.32 | 0.148–0.177 | 0.077–0.113 | −0.50 | 0.33–0.41 |
| 3 V2 | no VA | 0.63–0.74 | 0.23–0.37 | 0.21–0.29 | 0.146–0.169 | 0.067–0.111 | −0.48 | 0.33–0.40 |
| 4 A5 | with VA | 0.39–0.47 | 0–0.04 | 0.005–0.088 | 0–0.0004 | 0 | −0.12 | 0.13–0.17 |
| 4 A5 alternative | no VA | 0.54–0.62 | 0.12–0.37 | 0.14–0.39 | 0.026–0.178 | 0–0.058 | −0.33 | 0.23–0.31 |

**Where the negatives are** (own η; share negative within the group).

| Specification, sample, conduct | Vanguard | SSGA | BlackRock | Other firms | SPY | Cheap / non-cheap |
|---|---|---|---|---|---|---|
| 1 T2, with VA, B0 | **0.81** | 0.03 | 0.04 | 0.01 | 0 | 0.40 / 0.06 |
| 1 T2 alternative, no VA, B0 | **0.94** | 0.12 | 0.14 | 0.10 | 0 | 0.58 / 0.11 |
| 1 T2 alternative, no VA, B65 | **1.00** | 0.67 | 0.55 | 0.11 | **0.85** | 0.77 / 0.22 |
| 2 Modified T2, with VA, B0 | **0.79** | 0.02 | 0.03 | 0 | 0 | 0.39 / 0.05 |
| 2 Modified T2, with VA, B65 | **0.96** | 0.51 | 0.38 | 0 | **0.85** | 0.62 / 0.15 |
| 3 V2, with VA, B0 | 0.24 | 0.43 | 0.16 | 0.20 | 0 | 0 / 0.40 |
| 3 V2, with VA, B65 | 0.38 | 0.64 | 0.44 | 0.18 | 0 | 0.09 / 0.51 |
| 3 V2, no VA, B0 | 0.25 | 0.38 | 0.13 | 0.20 | 0 | 0 / 0.40 |
| 3 V2, no VA, B65 | 0.31 | 0.60 | 0.39 | 0.17 | 0 | 0.03 / 0.51 |
| 4 A5, with VA, B65 | 0.26 | 0.09 | 0.09 | 0 | 0 | 0.16 / 0.03 |
| 4 A5 alternative, no VA, B0 | 0.32 | 0.06 | 0.08 | 0.07 | 0 | 0.23 / 0.05 |
| 4 A5 alternative, no VA, B65 | **0.89** | 0.53 | 0.38 | 0.07 | **0.85** | 0.67 / 0.15 |

**Reading.**
- **Goal B does not separate V2 from the single-slope models on the share.** T2 and the modified T2 have 20% to 36% of marginal costs negative; V2 has 21% to 32%. A5 with the variable-annuity funds has fewer (0.5% to 9%), but its demand is not valid without them.
- **The location differs.** Under T2 the negatives are cheap funds, 79% to 81% of Vanguard's fund-months, and SPY at B65. Under V2 they are non-cheap funds (40% of them at B0), spread across firms, and never SPY.
- **The reason under V2 is the flat non-cheap slope.** At −2.0 a non-cheap fund charging 0.15% has an elasticity of −0.3 and a markup above its fee. Securities lending cannot explain negative costs of this size and frequency, so V2 fails the magnitude screen.
- **T2, the modified T2 and A5 without the variable-annuity funds are not shown.** Their markups are negative for 100%, 100% and 49% of fund-months.

## 6. Conduct test: PC is selected under T2 and the modified T2, and rejected under V2

Selected sets (MCS p ≥ 0.05), η scheme A (0.024); MCS p-values in brackets.

| # | Sample | **Main IV** (rival2 × csent_index) | rival2 × csent_income3 | rival3 × csent_index | rival2 × bab_usa / × fmax / × rotator | Min F, main IV |
|---|---|---|---|---|---|---|
| 1 T2 | with VA | PC (B50 0.02, B65 0.03 rejected) | PC | PC | PC | 67 |
| 1 T2 alternative | no VA | PC, B50 (0.17), B65 (0.18) | PC, B50, B65 | PC | PC | 69 |
| 2 Modified T2 (Danny) | with VA | PC (B50 0.02, B65 0.03 rejected) | PC | PC | PC | 69 |
| 3 V2 | with VA | B25 (0.08), B50 (0.59), B65 (1.00); PC rejected (0.005) | B25, B50, B65 | B25, B50, B65 | B25, B50 (B0 with rotator; B65 with bab_usa) | 121 |
| 3 V2 | no VA | B50 (0.13), B65 (1.00); PC rejected (0.048) | B50, B65 | B25, B50, B65 | B0, B25, B50 | 139 |
| 4 A5 | with VA | PC, B65 (0.08) | PC, B65 | PC | PC | 103 |
| 4 A5 alternative | no VA | PC, B50 (0.31), B65 (0.42) | PC, B50, B65 | PC | PC | 112 |

Schemes B (own η), C (PC η) and A with markups capped give the same sets for columns 1, 2 and 4. For V2, scheme C agrees with A. Under scheme B without the variable-annuity funds PC re-enters the set (p 0.36), so V2's rejection of PC is not robust to the choice of η there.

**Reading.**
- **The single-slope models and A5 select PC;** T2 and the modified T2 reject B50 and B65 as well.
- **V2 points the other way.** B65 fits best, B50 is not rejected, and PC is rejected with the main instrument (p 0.005 with the variable-annuity funds on the supply side, 0.048 without). The alternative instruments favour B25 and B50.
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

## 9. How robust is V2? Sign: yes, except to a finer exclusion. Marginal costs: no

All rows are V2's model (price and price × cheap, instruments Z and Z × cheap), changing one element at a time (`code/spec_compare/sc_v2_robust.py`; `logs/spec_compare/sc_v2_robust.csv`). The negative-MC share is at each candidate's own η.

| Variant | Cheap share of rows | Non-cheap α (SE) | × cheap (SE) | Min F | e > 0 | Table 5 e < −1 | Negative MC B0–B65, with VA | No VA |
|---|---|---|---|---|---|---|---|---|
| **V2 (column 3): cutoff at the 20th percentile** | 0.46 | **−2.010 (0.412)** | −20.542 (0.576) | 278 | 0 | 4/15 | 0.22–0.32 | 0.21–0.29 |
| Cutoff at the 15th percentile | 0.40 | −3.013 (0.327) | −21.461 (0.575) | 333 | 0 | 5/15 | 0.14–0.18 | 0.13–0.17 |
| Cutoff at the 25th percentile | 0.53 | −3.984 (0.556) | −20.189 (0.879) | 195 | 0 | 5/15 | 0.007–0.025 | 0.003–0.016 |
| **Donors from the full source panel** | 0.46 | **−1.701 (0.410)** | −19.787 (0.558) | 298 | 0 | 4/15 | 0.32–0.42 | 0.31–0.40 |
| Cheap from the index CSV (V2 as first sent to Danny) | 0.47 | −3.642 (0.419) | −20.562 (0.646) | 316 | 0 | 5/15 | 0.053–0.082 | 0.041–0.073 |
| **Exclusion by Danny's category10 classes** | 0.46 | **+2.135 (0.592)** | −17.858 (0.549) | 246 | **0.54** | 3/15 | – | – |

**Cutoffs.** At the 15th and 25th percentiles demand slopes down for every fund-month and the cheap term is unchanged (−21.5 and −20.2). The non-cheap slope is steeper than at the 20th percentile (−3.0 and −4.0 against −2.0).

**Donors from the full source panel.** The source panel has 54,945 fund-months with a family code and a fee that are not in the index CSV, mostly a fund's first 12 months; 93% of their fees are reported by CRSP. Using them as donors keeps demand downward-sloping everywhere. The non-cheap slope is −1.70 against −2.01, and the negative-MC share rises to 32–42%.

**Exclusion classes.** Danny's category10 splits equity into US size and style, global developed, emerging, and sector or theme, and bonds into government, credit, municipal and diversified. V2's six classes keep each of those together.
- **With category10 as the exclusion, the non-cheap slope is +2.1 and 54% of fund-months slope upward.**
- **This is the pattern found before** (`RESULTS_best_model1.md` §5c): the finer the exclusion, the more a fund's same-asset-class siblings act as donors, and the more positive the non-cheap slope.
- **So V2's non-cheap result depends on the broad-asset-class exclusion.** That is an identifying assumption, and the data cannot confirm it.

**Reading.**
- **The sign of demand is robust to the cutoff and the donor pool.** No fund-month has e > 0 at the 15th, 20th or 25th percentile cutoff, or with source-panel donors.
- **The cheap slope is stable** (−19.8 to −21.5 across the cutoffs and donor pools).
- **The non-cheap slope and the negative-MC share are not robust.** The share is 14–18% at the 15th percentile, 22–32% at the 20th and 1–3% at the 25th, so it does not move in one direction with the cutoff.
- **The share depends on which large funds fall on each side of the cutoff.** The version first sent to Danny differs from column 3 in the status of 37 funds, among them Vanguard Total Stock Market Investor and Vanguard 500 Investor, and has 5–8% negative.
- **Not done:** the conduct test for these variants.

## 10. T2 and A5 without the variable-annuity funds: only the six-asset-class exclusion gives downward-sloping demand, and it is flat

Sample: Table 2 Panel A minus the 112 variable-annuity funds (100,529 fund-months). The instrument is rebuilt from Danny's full source panel in 16 ways: four exclusions, pooled or same share type, lag-AUM-weighted mean or median. Rows where the instrument is undefined are dropped (`code/spec_compare/sc_t2a5_nova_grid.py`; `sc_t2a5_nova_grid.csv`).

| Exclusion | Share type | Aggregation | T2 price (SE) | T2 e > 0 | T2 negative MC B0–B65 | A5 specialized (SE); × broad | A5 e > 0 | A5 negative MC B0–B65 | Table 5 e < −1 (T2 / A5) |
|---|---|---|---|---|---|---|---|---|---|
| index (paper) | pooled | weighted (paper) | +7.24 (1.99) | 1.00 | – | +4.01 (1.59); −6.92 | 0.49 | – | 0 / 0 |
| index | same type | weighted | +4.68 (0.82) | 1.00 | – | +3.12 (0.78); −5.86 | 0.49 | – | 0 / 0 |
| index | same type | median | +5.16 (0.54) | 1.00 | – | +4.96 (0.55); −6.93 | 0.49 | – | 0 / 0 |
| category20 | pooled | weighted | +4.82 (1.46) | 1.00 | – | +3.13 (1.26); −6.63 | 0.49 | – | 0 / 0 |
| category20 | same type | weighted | +2.67 (0.74) | 1.00 | – | +1.81 (0.73); −5.92 | 0.49 | – | 0 / 0 |
| category10 (Danny) | pooled | weighted | +3.93 (1.46) | 1.00 | – | +2.62 (1.27); −6.08 | 0.49 | – | 0 / 0 |
| category10 | same type | weighted | −0.15 (0.64) | 0 | 1.00 | −0.99 (0.61); −5.56 | 0 | 0.65–0.73 | 0 / 0 |
| category10 | same type | median | +8.97 (1.14) | 1.00 | – | +11.18 (1.55); −11.19 | 0.49 | – | 0 / 0 |
| **six asset classes** | **pooled** | **weighted** | **−4.12 (0.74)** | 0 | **0.32–0.48** | **−3.98 (0.75); −4.41** | 0 | **0.13–0.39** | 1 / 1 |
| six asset classes | same type | weighted | −2.55 (0.42) | 0 | 0.59–0.73 | −2.50 (0.42); −5.43 | 0 | 0.29–0.53 | 1 / 0 |
| six asset classes | same type | median | −0.92 (0.43) | 0 | 0.98 | +0.57 (0.48); −6.71 | 0.49 | – | 0 / 0 |

Not shown: the four versions with pooled share types and a median (first-stage F of 0 to 6 with the money market funds in the sample, all upward-sloping), and category20 with same type and median (+6.78). Dropping the 4 money market funds as well changes no sign except category10 / same type / weighted for T2, which becomes +0.11.

**Reading.**
- **With the paper's exclusion (same index), category20 or category10 and pooled share types, every version slopes upward.** That includes Danny's preferred construction.
- **Only the six-asset-class exclusion gives a clearly negative slope,** −4.1 for T2 and −4.0 with −4.4 for A5. This is the same exclusion V2 relies on.
- **Those versions are not sensible on the other criteria.** One of the 15 Table 5 funds has e < −1, a third to a half of marginal costs are negative under T2 (13% to 39% under A5), and 29% of fund-months are below −0.20% at B65 under T2.
- **The pooled, weighted six-class version is the alternative reported in the scorecard,** because it is the closest to the paper's own construction and has the fewest negative marginal costs of the valid versions.
- **No version meets both goals.** A single slope, or a broad-based interaction, cannot give the low-fee funds a slope steep enough once the variable-annuity funds are out.
- **Variations in share type matter only for the "same type" rows.** T2's and A5's own instruments pool share types.
