# Recommended specification: logit IV with expense ratio × cheap, using a share-class-matched Hausman instrument

This report is self-contained. It presents the recommended demand specification for the index market: the cheap-fund interaction of `MAIN_SPEC_entry_cheap_tier.md`, re-estimated with a better-behaved fee instrument. The evidence on the instrument is summarised here. The full record of every alternative is in `OTHER_SPECS_explored.md`, section 6. All numbers come from `code/explore/step25_new_iv_main.py` (log `logs/explore_step25_new_iv_main.log`, tables `logs/explore/step25_*.csv`), except where another script is named. The paper's own numbers were never changed.

## 1. Summary

- **Model.** Logit IV, linear in the fee, with one extra term (expense ratio × cheap). Cheap means the fund's fee in its first month in the full raw data was at or below that month's 20th percentile across all index funds. Controls and fixed effects are as in Table 2. SE clustered by month.
- **Instrument.** The median expense ratio of the **same fund family's funds of the same share class, outside the fund's asset class**, in the same month. It replaces the paper's Hausman IV, for the reasons in section 2.
- **Results, 20th percentile, 97,429 fund-months:**

  | | Non-cheap slope (SE) | Cheap total | First-stage F | Avg own elasticity | Table 5 funds with \|e\| > 1 |
  |---|---|---|---|---|---|
  | **Fund + month FE (as Table 2)** | **−6.12 (0.85)** | **−28.8** | 167 | −2.68 | **7 / 15** |
  | Fund + month × asset class FE | −3.80 (0.66) | −24.0 | 262 | −1.96 | 5 / 15 |

- **What it shows.** Cheap funds are 4–6 times as fee-sensitive as the rest, and both slopes are now precisely estimated. No fund-month has upward-sloping demand, and negative implied marginal cost falls from 52% (Table 2) to 24–36%. The result is robust to the cutoff, to asset-class × month fixed effects and to dropping any one of the three largest firms. Lead tests on the model's residual are small and change sign (|t| ≤ 2.9); with asset-class × month effects none rejects at the 1% level.
- **Compared with the previous main spec** (the same model with the paper's instrument): the cheap slope is smaller (−24 to −29 against −41), so fewer Table 5 funds clear |e| = 1 (5–7 against 11). The previous non-cheap slope (−8.1, SE 4.3) was weakly identified and depended on Vanguard; it is now pinned down.
- **BLP version** (section 3b). With one random coefficient on the expense ratio and the new IV squared as the extra instrument, σ is estimated at 1.81 (SE 0.24). The means stay close to the logit IV: non-cheap −4.2 (0.6), cheap total −26.3. Average elasticity is −1.90, still 7 of 15 Table 5 funds are above 1, and 0.02% of fund-months slope upward. Caveats: the moments cannot all be set to zero, and the covariance matrix is near-singular.
- **Decision for the authors.** Which instrument to adopt.

## 2. Why change the instrument

**The paper's Hausman IV.** It arrives precomputed in the data (`BLP_IV_hausman_exp_ratio`), and no notebook builds it. I reverse-engineered it (`step23`): it is the previous-month-AUM-weighted average expense ratio of the same family's funds that track other indices. It matches the data exactly wherever the family identifier `firm_f_old` exists. Two checks count against it, and a third is mixed (`step24b`, `step24c`, `step27`):

1. **Table 2's −5.6 is driven by 7% of fund-months.** These are 112 funds, mostly variable-annuity and insurance-channel funds, with no family identifier and an unknown instrument construction.

   | Sample | Price coefficient (SE) |
   |---|---|
   | All fund-months (Table 2 col 2) | −5.61 (1.31) |
   | The 93% with a family identifier | **+7.24 (1.99)** |
   | The 7% without one | **+2.32 (0.54)** |
   | Pooled, separate month FE for the two groups | **+7.64 (2.20)** |

   Both groups give upward-sloping demand; the negative pooled estimate comes from different time trends in the two groups.
2. **Lead tests are mixed.** These ask whether the fund's demand shocks from 12, 24 and 36 months earlier predict today's instrument (procedure in section 5).
   - With the residual of the one-slope Table 2 model on the 97,429 rows, they reject strongly: t = 6.7, 10.7 and 20.3. But that model has upward-sloping demand there (+11.3), so its residual is contaminated.
   - With the residual of the main model (× cheap) and Table 2's fixed effects, they do not reject: t = −1.9, −0.4 and 2.2.
   - Under asset-class × month effects they reject: t = −4.1, −4.0 and −3.3.
   - On the full Table 2 sample they give t = −3.3, −1.5 and 2.1.
3. **Placebo.** A randomly chosen other family's fees predict the fund's fee about half as strongly as its own family's (median first-stage F 13 against 25).

**The new instrument.** For fund j in month t, it is the median expense ratio of the funds that share j's family, share j's share class, and are in a different asset class. Each construction step addresses a weakness of the paper's IV:
- **Outside the asset class.** The paper's IV leaves out only the fund's own index, so close substitutes (for example the family's total-market funds, for an S&P 500 fund) stay in it. Asset classes are assigned per tracked index: US equity, international equity, bonds, allocation and real assets (`code/explore/asset_class.py`).
- **Median.** It is robust to data errors such as the temporary fee spikes found earlier. It also removes the paper's AUM weights, which depend on past demand.
- **Same share class.** Fee-setting differs across ETFs, institutional, retail and other mutual-fund classes, so matching sharpens the first stage. Share class is parsed from fund names.
- **Coverage.** It is defined for 97,429 of the 108,300 Table 2 fund-months (90%) and for 1,164 of the 1,302 funds, including all 15 Table 5 funds. The rows lost are the 7% without a family identifier plus 3% where the family has no same-share-class fund outside the asset class. The median value is computed from 35 funds; 2% of values come from a single fund. Its correlation with the paper's IV is 0.83.

## 3. Panel A: index funds, 20th percentile

Columns (1)–(3) use fund and month fixed effects, as Table 2. (2′) and (3′) add asset-class × month effects, which absorb asset-class-wide fee and demand trends and leave only family-specific variation in the instrument. (2p) and (3p) re-estimate with the paper's instrument on the same 97,429 rows for comparison. The first column is the paper's Table 2 Panel A column (2) as published and replicated, on all 108,300 fund-months. Column (2p) is that exact specification restricted to the 97,429 rows where the new instrument is defined; the drop in rows alone turns −5.6 into +11.3 (section 2). "Avg" is the per-market mean own elasticity, as in Table 2.

| | Table 2 col 2 as published | (1) Logit OLS | (2) Logit IV | **(3) Logit IV × cheap (main)** | (2′) Logit IV | **(3′) Logit IV × cheap** | (2p) Paper IV | (3p) Paper IV × cheap |
|---|---|---|---|---|---|---|---|---|
| Fixed effects | fund + month | fund + month | fund + month | fund + month | fund + month × asset class | fund + month × asset class | fund + month | fund + month |
| Instrument | paper's Hausman | — | share-class Hausman | share-class Hausman | share-class Hausman | share-class Hausman | paper's Hausman | paper's Hausman |
| Expense ratio | −5.606 (1.310) | −1.724 (0.090) | −1.242 (0.582) | −6.116 (0.845) | −1.281 (0.428) | −3.798 (0.660) | 11.263 (3.142) | −2.721 (2.752) |
| Expense ratio × cheap |  |  |  | −22.655 (0.794) |  | −20.238 (0.643) |  | −24.089 (1.447) |
| Cheap total |  |  |  | −28.77 |  | −24.04 |  | −26.81 |
| Past 1-yr return | 0.413 (0.034) | 0.437 (0.038) | 0.438 (0.037) | 0.432 (0.034) | 0.489 (0.039) | 0.496 (0.037) | 0.468 (0.047) | 0.440 (0.035) |
| Age (log) | 0.573 (0.011) | 0.618 (0.007) | 0.619 (0.007) | 0.549 (0.008) | 0.697 (0.009) | 0.644 (0.009) | 0.633 (0.010) | 0.549 (0.010) |
| Tracking error | −0.451 (0.066) | −0.192 (0.039) | −0.173 (0.031) | −1.044 (0.135) | −0.163 (0.026) | −0.942 (0.113) | 0.317 (0.127) | −0.953 (0.179) |
| N | 108,300 | 97,429 | 97,429 | 97,429 | 97,429 | 97,429 | 97,429 | 97,429 |
| Weakest first-stage F | 33.6 |  | 217.5 | 166.6 | 303.1 | 262.1 | 25.0 | 13.2 |
| **Avg own-price elasticity** | **−1.61** | **−0.45** | **−0.33** | **−2.68** | **−0.34** | **−1.96** | **2.96** | **−1.86** |
| Share \|e\| > 1 | 0.53 | 0.10 | 0.03 | 0.87 | 0.03 | 0.75 | 0.72 | 0.71 |
| Share e > 0 (upward-sloping) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| Share negative MC (firm Bertrand) | 0.52 | 0.92 | 0.97 | 0.24 | 0.97 | 0.36 | 0.00 | 0.45 |
| Table 5 funds with \|e\| > 1 | 2/15 | 0/15 | 0/15 | 7/15 | 0/15 | 5/15 | 2/15 | 7/15 |


**Reading.**
- **Without the interaction** (columns 2 and 2′), the new instrument gives a small fee coefficient, −1.24 to −1.28, with average elasticity −0.33. The fee barely matters for the typical fund.
- **With the interaction** (columns 3 and 3′), cheap funds' total coefficient is −28.8 or −24.0 against −6.1 or −3.8 for the rest; the interaction has t > 28. Fee sensitivity is concentrated among cheap funds.
- **Controls** are close to Table 2 (past return 0.43–0.50, log age 0.55–0.70). Tracking error becomes more negative once the interaction is in, as with the previous main spec.
- **The paper's instrument on the same rows** gives upward-sloping demand without the interaction (2p: +11.3, every fund-month) and an imprecise non-cheap slope with it (3p: −2.7, SE 2.8, F 13).
- Panel B (leveraged funds) is unchanged from Table 2. The new instrument is not needed there, and the leveraged interaction is not significant in the paper's A7.

## 3b. BLP with one random coefficient on the expense ratio (`code/explore/step26_blp_newiv.py`, `logs/explore_step26_*`, `logs/explore/step26_*.csv`)

**Setup.** This is the Table 2 column (3) analogue of column (3) above: one random coefficient (σ) on the expense ratio, with the cheap interaction in mean utility. Fund and month FE; Monte Carlo integration with 3000 draws, seed 623543; one-step GMM; SE clustered by month. The instruments are the new IV and new IV × cheap, plus one extra instrument to identify σ. That makes three excluded instruments for three parameters: price, price × cheap and σ. Three candidates were tried for the extra instrument:
- `BLP_IV_newproduct_1`, the paper's own Table 2 col (3) choice;
- the square of the new IV;
- a differentiation instrument: the sum over other funds in the same month and asset class of (Z_j − Z_k)².

**σ profiles** (GMM objective at fixed σ, with β concentrated out; the shares on the right are at the given σ):

| Extra instrument | σ ≈ 0 | 0.5 | 1 | 2 | 3 | 4 | 6 | Shape |
|---|---|---|---|---|---|---|---|---|
| `newproduct_1` (paper's) | 3.62 | 3.52 | 3.24 | 2.55 | 2.03 | 1.56 | 0.64 | falls toward large σ; 20% upward-sloping at σ = 6 |
| **Z² (new IV squared)** | 2.40 | 2.36 | 2.24 | **2.12** | 2.34 | 2.62 | 2.76 | **interior minimum near σ = 2** |
| Differentiation IV | 98.7 | | | | | | | conflicts with the new IV: non-cheap slope +0.64, 53% upward-sloping (stopped) |

**Estimate with Z² as the extra instrument** (BFGS from σ = 2, gtol 1e-7; converged in 4 iterations; projected gradient 3e-8; positive reduced Hessian):

| | (3) Logit IV × cheap | **(3B) BLP 1 RC × cheap** |
|---|---|---|
| Expense ratio (non-cheap mean) | −6.116 (0.845) | **−4.215 (0.591)** |
| Expense ratio × cheap | −22.655 (0.794) | **−22.048 (0.351)** |
| Cheap total (mean) | −28.77 | **−26.26** |
| σ, random coefficient on expense ratio | | **1.808 (0.239)** |
| Past 1-yr return | 0.432 (0.034) | 0.438 (0.036) |
| Age (log) | 0.549 (0.008) | 0.551 (0.008) |
| Tracking error | −1.044 (0.135) | −0.940 (0.110) |
| N | 97,429 | 97,429 |
| GMM objective at the optimum | | 2.11 |
| **Avg own-price elasticity** | **−2.68** | **−1.90** |
| Share \|e\| > 1 | 0.87 | 0.79 |
| Share e > 0 (upward-sloping) | 0 | 0.0002 |
| Share negative MC (firm Bertrand) | 0.24 | 0.35 |
| Table 5 funds with \|e\| > 1 | 7/15 | **7/15** |

**Reading.**
- **The random coefficient is estimated, and it is sizeable** (σ = 1.81, SE 0.24). With the paper's instrument, σ was either not identified (0.027 in Table 2 col 3) or ran off to values where demand slopes upward. Here a negative price coefficient for a cheap fund at its mean (−26.3) is far from zero relative to σ, while for non-cheap funds (mean −4.2, σ 1.8) a small share of simulated consumers have a positive coefficient. The realized share of upward-sloping fund-months is 0.02%.
- **The means barely move from the logit IV** (−4.2 against −6.1; cheap total −26.3 against −28.8), and so the 15 Table 5 funds hardly change (section 4). The average elasticity is lower (−1.90 against −2.68) and negative implied MC a bit higher (35%).
- **Two caveats.**
  - The model is exactly identified, but the three moment conditions cannot all be set to zero: the objective stops at 2.11 instead of 0, so the extra instrument and the two price instruments do not fully agree.
  - pyblp reports a covariance-matrix condition number of 1e17, the same near-singularity your coauthors found in the 3-RC model, so the standard errors should be treated as indicative.
- **The choice of extra instrument matters.** With the paper's `newproduct_1` the objective keeps falling toward large σ, as before. With the differentiation instrument the moments conflict outright. Only Z² gives an interior minimum.

## 4. The 15 Table 5 funds (own elasticity, Aug 2024)

| Fund | p (%) | cheap (20th)? | Table 5 (paper) | Table 2 logit IV | Previous main spec (paper IV, 20th) | **(3) new IV, fund + month** | **(3′) new IV, month × asset class** | new IV, 10th / 15th pct | **(3B) BLP 1 RC** |
|---|---|---|---|---|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | yes | −0.24 | −0.16 | −1.18 | **−0.84** | **−0.70** | −0.92 / −1.02 | **−0.77** |
| iShares Core MSCI EAFE ETF | 0.07 | yes | −0.58 | −0.39 | −2.83 | **−2.00** | **−1.67** | −2.20 / −2.44 | **−1.83** |
| iShares Core US Aggregate Bond ETF | 0.03 | yes | −0.25 | −0.17 | −1.21 | **−0.86** | **−0.72** | −0.19 / −1.05 | **−0.79** |
| iShares Russell 1000 Growth ETF | 0.18 | yes | −1.49 | −1.00 | −7.30 | **−5.15** | **−4.30** | −1.16 / −6.30 | **−4.66** |
| iShares Core S&P Mid-Cap ETF | 0.05 | yes | −0.41 | −0.28 | −2.03 | **−1.43** | **−1.20** | −0.32 / −1.75 | **−1.31** |
| SPDR S&P 500 ETF Trust | 0.09 | yes | −0.72 | −0.49 | −3.54 | **−2.50** | **−2.09** | −2.76 / −3.06 | **−2.28** |
| SPDR Gold Shares | 0.40 | no | −3.33 | −2.23 | −3.24 | **−2.44** | **−1.51** | −2.57 / −3.83 | **−1.33** |
| Technology Select Sector SPDR Fund | 0.08 | no | −0.67 | −0.45 | −0.65 | **−0.49** | **−0.30** | −0.51 / −0.77 | **−0.34** |
| Financial Select Sector SPDR Fund | 0.08 | no | −0.67 | −0.45 | −0.65 | **−0.49** | **−0.30** | −0.51 / −0.77 | **−0.34** |
| SPDR Portfolio S&P 500 ETF | 0.02 | yes | −0.17 | −0.11 | −0.81 | **−0.57** | **−0.48** | −0.13 / −0.19 | **−0.53** |
| Vanguard Total Stock Market Inst. Plus | 0.02 | yes | −0.16 | −0.11 | −0.78 | **−0.55** | **−0.46** | −0.61 / −0.67 | **−0.51** |
| Vanguard 500 Index Admiral | 0.04 | yes | −0.32 | −0.22 | −1.58 | **−1.11** | **−0.93** | −1.23 / −1.36 | **−1.02** |
| Vanguard 500 Index ETF | 0.03 | yes | −0.24 | −0.16 | −1.18 | **−0.84** | **−0.70** | −0.92 / −1.02 | **−0.77** |
| Vanguard Total Stock Market ETF | 0.03 | yes | −0.24 | −0.16 | −1.19 | **−0.84** | **−0.70** | −0.93 / −1.03 | **−0.77** |
| Vanguard Total Stock Market Admiral | 0.04 | yes | −0.33 | −0.22 | −1.59 | **−1.12** | **−0.94** | −1.24 / −1.37 | **−1.03** |
| **Funds with \|e\| > 1** | | | 2/15 | 2/15 | 11/15 | **7/15** | **5/15** | 6/15 / 11/15 | **7/15** |


The funds above 1 under column (3) are EAFE, Russell 1000 Growth, Mid-Cap, SPY, SPDR Gold, and the Vanguard 500 and Total Stock Market Admiral classes. The 2–3 basis point funds reach −0.55 to −0.86: much higher than Table 5 (−0.16 to −0.25) but still below 1.

## 5. Diagnostics

**Split sample** (each group with its own fixed effects; first-stage F of the instrument alone; reduced-form t is the weak-instrument-robust test of a zero slope):

| Fixed effects | Cutoff | Group | Funds | First-stage F, new / paper IV | Reduced-form t, new IV | IV slope (SE), new IV | IV slope, paper IV |
|---|---|---|---|---|---|---|---|
| fund + month | 20th | not cheap | 678 | **148.7** / 0.7 | −3.2 | **−2.42 (0.76)** | +93 (113) |
| fund + month | 20th | cheap | 486 | **47.8** / 55.0 | −19.0 | **−47.2 (5.3)** | −68.1 (9.1) |
| fund + month × asset class | 20th | not cheap | 678 | **202.4** / 28.1 | −2.6 | **−1.59 (0.63)** | +7.2 (2.3) |
| fund + month × asset class | 20th | cheap | 486 | **62.7** / 23.5 | −24.1 | **−40.7 (4.4)** | −105.6 (21.4) |
| fund + month | 15th | not cheap / cheap | 779 / 385 | 128.5 / 30.1 | −8.6 / −14.8 | −6.97 (0.94) / −62.8 (10.5) | |
| fund + month | 10th | not cheap / cheap | 906 / 258 | 120.9 / 107.3 | −3.8 / −15.9 | −3.75 (1.04) / −32.9 (3.1) | |

With the new instrument both groups have strong first stages and negative slopes. With the paper's instrument the non-cheap group has essentially no first stage under Table 2's fixed effects, and a positive slope under asset-class × month effects.

**Lead tests** (`code/explore/step27_lead_tests.py`, `logs/explore_step27_lead_tests.log`, `logs/explore/step27_lead_tests.csv`). The question is whether a fund's past demand shocks predict today's instrument. Under the exclusion restriction they should not. Procedure, for a given instrument Z, demand model and fixed-effect set:

1. Estimate the demand model by logit IV in pyblp: fund FE and the time FE absorbed (month, or month × asset class); controls tracking error, past 1-year return and log age; instruments Z, plus Z × cheap in the main model. Take ξ̂ = `res.xi`. With absorbed fixed effects this equals δ − Xβ̂ with the fund and time means removed (verified: correlation 1.0 with a manual two-way demeaning; δ = log share − log outside share).
2. Residualize the instrument: Z̃ is the residual of Z on fund FE, the same time FE and the three controls (Frisch–Waugh, with `pyhdfe`).
3. Index months by `month_key = round(12 × month_t)`. For each lag k = 12, 24, 36, pair each fund-month (j, t) with the same fund's residual k months earlier, giving (Z̃_{j,t}, ξ̂_{j,t−k}). Keep pairs where both exist: 79,728 pairs at k = 12 and 58,217 at k = 36 on the 97,429-row sample.
4. Demean both variables within fund over the paired sample.
5. Regress ξ̂_{j,t−k} on Z̃_{j,t} by OLS without a constant. Cluster the standard error by the calendar month t of the instrument observation, with no small-sample correction, and report t = b / SE.

| Sample | Instrument | Residual from | Fixed effects | Price coef. | t, k = 12 | t, k = 24 | t, k = 36 |
|---|---|---|---|---|---|---|---|
| Table 2 (108,300) | paper's | one slope (Table 2 col 2) | fund + month | −5.61 | −3.3 | −1.5 | 2.1 |
| Table 2 (108,300) | paper's | main (× cheap) | fund + month | −8.13 | −3.4 | −5.3 | −1.7 |
| 97,429 rows | paper's | one slope | fund + month | +11.26 | 6.7 | 10.7 | 20.3 |
| 97,429 rows | paper's | main | fund + month | −2.72 | −1.9 | −0.4 | 2.2 |
| 97,429 rows | paper's | one slope | fund + month × asset class | −1.33 | 2.1 | 8.4 | 18.2 |
| 97,429 rows | paper's | main | fund + month × asset class | −9.94 | −4.1 | −4.0 | −3.3 |
| 97,429 rows | **share-class** | one slope | fund + month | −1.24 | 2.1 | 2.6 | 5.2 |
| 97,429 rows | **share-class** | **main** | **fund + month** | **−6.12** | **−1.7** | **−2.9** | **−1.9** |
| 97,429 rows | **share-class** | one slope | fund + month × asset class | −1.28 | 2.4 | 2.8 | 5.8 |
| 97,429 rows | **share-class** | **main** | **fund + month × asset class** | **−3.80** | **−0.1** | **−0.2** | **2.1** |

How to read it:
- **The test depends on the model whose residual is used.** A misspecified model leaves part of the omitted fee response in ξ̂. The one-slope residuals ignore the steep cheap-fund slope, and on the 97,429 rows the paper's one-slope model even slopes upward.
- **With the main model's residual and Table 2's fixed effects, the two instruments look similar** (|t| ≤ 2.9).
- **Under asset-class × month effects they separate.** The paper's instrument rejects at every lag (t −3.3 to −4.1); the new one does not (|t| ≤ 2.1).

**Placebo** (`step24c`): each family is mapped to a random one of the 30 broadest other families, and the same instrument is rebuilt from that family's funds (20 draws). Under asset-class × month effects:
- **First stage:** the placebo's median F is 27 for all funds and 18 for non-cheap funds (90th percentiles 156 and 59), on samples about 40% the size. The real instrument has F 303 and 202. Scaled for sample size, it sits near the top of the placebo range, so part, not all, of its variation is family-specific.
- **Slopes:** the placebo slopes centre on zero (pooled −0.8, non-cheap +1.0) with very wide dispersion.

## 6. Robustness

**Cutoff** (main model, column 3 and 3′ form):

| Cutoff | Funds cheap | Fixed effects | Non-cheap (SE) | Cheap total | min F | Avg e | Neg. MC | Table 5 > 1 |
|---|---|---|---|---|---|---|---|---|
| 10th | 22% | fund + month | −6.46 (0.85) | −31.7 | 171 | −2.20 | 0.37 | 6 |
| 15th | 33% | fund + month | −9.61 (1.02) | −35.2 | 173 | −3.41 | 0.18 | 11 |
| **20th** | **42%** | **fund + month** | **−6.12 (0.85)** | **−28.8** | **167** | **−2.68** | **0.24** | **7** |
| 10th | 22% | month × asset class | −4.90 (0.61) | −24.9 | 298 | −1.68 | 0.47 | 3 |
| 15th | 33% | month × asset class | −6.88 (0.77) | −29.2 | 291 | −2.57 | 0.27 | 7 |
| 20th | 42% | month × asset class | −3.80 (0.66) | −24.0 | 262 | −1.96 | 0.36 | 5 |

No cutoff produces upward-sloping demand. The gap between cheap and non-cheap funds is stable (−20 to −26 at every cutoff). The Table 5 count depends on the cutoff (3 to 11), because several large funds sit near the cheap/non-cheap boundary at their launch fee (`MAIN_SPEC_entry_cheap_tier.md`, section 1).

**Drop one large firm** (fund + month FE, 20th percentile):

| Dropped | N | Non-cheap (SE) | Cheap total | min F |
|---|---|---|---|---|
| none | 97,429 | −6.12 (0.85) | −28.8 | 167 |
| Vanguard | 71,780 | −2.22 (0.69) | −25.3 | 192 |
| BlackRock | 75,346 | −3.45 (0.65) | −26.1 | 180 |
| State Street | 88,924 | −5.18 (0.73) | −28.9 | 177 |

With the paper's instrument, dropping Vanguard turned the non-cheap slope positive (+6.2). With the new instrument it stays negative and significant.

## 7. Caveats

- **Sample.** The instrument is not defined for 10% of the Table 2 fund-months, mostly the insurance-channel funds without a family identifier. Results are for the remaining 90%.
- **Exclusion restriction.** It is the usual Hausman assumption, now with a cleaner leave-out: a family's fees on funds in other asset classes respond to family cost conditions, not to this fund's demand. The threat that remains is family-wide demand shocks, such as a brand gaining popularity, that also move family-wide fees. The lead tests and the placebo do not point to it, but they cannot rule it out.
- **Classification by name.** Share class and, for indices outside the mapped clusters, asset class are parsed from fund names and index codes. Spot checks are in `asset_class.py`'s docstring and the step24 log.
- **Elasticity levels.** The cheapest Table 5 ETFs (2–3 basis points) still have |e| < 1 (−0.55 to −0.86), so the model still implies Lerner > 1, that is, negative marginal cost, for those funds.

## 8. How to report it

- **Table 2 Panel A:** add columns (3) and (3′) as the alternative demand model, with the cutoff table as robustness and a sentence on the instrument.
- **Appendix:** report the instrument diagnostics (the family-identifier split, lead tests, placebo).
- **Table 5:** report the elasticities from column (3).
- **Footnote:** a random coefficient on the expense ratio is not identified once the interaction is included (`OTHER_SPECS_explored.md`, section 4).

## 9. Code and logs

| What | Where |
|---|---|
| BLP version (σ profiles, estimate) | `code/explore/step26_blp_newiv.py`, `new_iv.py`, `logs/explore_step26_*_final.log`, `logs/explore/step26_*.csv` |
| Lead tests | `code/explore/step27_lead_tests.py`, `logs/explore_step27_lead_tests.log`, `logs/explore/step27_lead_tests.csv` |
| This report's numbers | `code/explore/step25_new_iv_main.py`, `logs/explore_step25_new_iv_main.log`, `logs/explore/step25_*.csv` |
| Instrument construction (asset class) | `code/explore/asset_class.py` |
| Paper's Hausman IV reconstructed | `code/explore/step23_hausman_reconstruct.py`, `logs/explore_step23_hausman_reconstruct.log` |
| Family-identifier split | `code/explore/step24b_family_split.py`, `logs/explore_step24b_family_split.log` |
| All instrument variants; asset-class × month FE and placebo | `code/explore/step24_hausman_variants.py`, `step24c_class_month_fe.py`, `logs/explore_step24*`, `logs/explore/step24*_*.csv` |
| Cheap tier definition | `code/explore/tiers.py` |
