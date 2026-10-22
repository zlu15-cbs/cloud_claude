# Table 2_alt: demand with a price × "cheap fund" interaction

Same samples, controls, fund and month fixed effects, and SE clustered by month as Table 2. The only change to the model is one extra term, expense ratio × cheap. Code and logs are under `code/explore/` and `logs/`; the numbers below are generated from those logs by `code/explore/make_table2_alt.py`.

## Definition of "cheap"

For each month of the **full raw file** (index funds 1994–2025), compute the q-th percentile of expense ratios across all funds with a recorded fee that month. A fund is **cheap** if its expense ratio in its **first raw month** is at or below that month's cutoff; ties count as cheap. Code: `code/explore/tiers.py`.
- The status is fixed per fund, so fund FE absorb its level, and only the slope changes.
- For most funds it is set before the 2010–2024 estimation window (index: 54% of sample funds first appear in the raw data before 2010).
- It is measured relative to the market at the time, so it does not depend on the sample's share filter.
- Cutoffs reported: q = 10th, 15th and 20th percentiles.

## Columns

- **(1)–(3)** are Table 2 as published and replicated.
- **(1′) Logit OLS** and **(2′) Logit IV** add the interaction.
  - IV instruments: Hausman IV and Hausman IV × cheap, so the model is exactly identified.
  - "Weakest first-stage F" is the Sanderson–Windmeijer F, the minimum over the two endogenous terms.
- **(3′) BLP 1 RC, notebook IVs** is Table 2 col 3 (random coefficient on price; Monte Carlo 3000 draws, seed 623543; BFGS gtol 1e-7) with the interaction added. The extra instruments are the notebook's (index: `BLP_IV_newproduct_1`; leveraged: `BLP_IV_rival_funds1`), each also × cheap.
- **(3″) BLP 1 RC, Hausman² IV** is the same as (3′), but uses the squared Hausman IV (and × cheap) as the extra instruments.
- **(3‴) BLP 1 RC, newproduct_3** uses H, H × cheap and an uninteracted `BLP_IV_newproduct_3`: three instruments for three parameters (price, price × cheap, σ), exactly identified. `newproduct_3` was chosen by an instrument screen (`logs/explore_step12b_iv_screen_uninteracted.log`) as the candidate whose logit slopes agree best with the Hausman IV at all three cutoffs.
- **(3A7) BLP 1 RC, A7 design** is the published Table A7 column (3) design (`RESULTS_A7_col3.md`) applied to the cheap tier: H, H × cheap and an uninteracted `BLP_IV_newproduct_1`; exactly identified. Run at the 20th percentile.
- **(3σ) BLP 1 RC, σ fixed at 0.027** holds the random-coefficient sd at the paper's own Table 2 column (3) estimate (0.027, SE 0.013) and estimates the two price coefficients with H and H × cheap (exactly identified). This is the column we recommend reporting; the reason is in the notes.
- All BLP columns have **one random coefficient, on the expense ratio** (X2 = expense ratio); the interaction is in the mean utility only.
- **Panel B (leveraged funds) has no interaction.** In the paper's A7 the leveraged broad-based interaction is not significant, so Panel B is Table 2 as published.

Elasticities are own-price elasticities. "Avg" is the per-market mean, as in Table 2. "Share e > 0" is blank for the index BLP columns because it was not recorded there; the 15-fund table and the average show where it occurs.

#### Panel A: Passive index funds: cheap = fee at first raw month ≤ 10th percentile (20% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs | (3″) BLP 1 RC, Hausman² IV | (3‴) BLP 1 RC, newproduct_3 (exactly identified) | (3A7) BLP 1 RC, A7 design (newproduct_1 uninteracted) | (3σ) BLP 1 RC, σ fixed at 0.027 (Table 2 col 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| Expense ratio | -0.938 (0.045) | -5.606 (1.310) | -6.771 (0.837) | -1.000 (0.039) | -6.183 (5.239) | 0.274 (1.644) | -1.893 (0.814) | 9.886 (4.731) | n/a | -6.183 (5.211) |
| Expense ratio × cheap |  |  |  | 0.211 (0.068) | -62.443 (22.487) | -49.255 (8.830) | -18.105 (1.692) | -60.611 (9.324) | n/a | -62.441 (22.340) |
| Past 1-yr return | 0.413 (0.037) | 0.413 (0.034) | 0.414 (0.034) | 0.413 (0.037) | 0.418 (0.042) | 0.409 (0.041) | 0.421 (0.045) | 0.411 (0.057) | n/a | 0.418 (0.042) |
| Age (log) | 0.546 (0.012) | 0.573 (0.011) | 0.580 (0.010) | 0.546 (0.012) | 0.829 (0.151) | 0.597 (0.024) | 0.532 (0.018) | 0.538 (0.069) | n/a | 0.829 (0.150) |
| Tracking error | -0.231 (0.039) | -0.451 (0.066) | -0.505 (0.074) | -0.231 (0.039) | -1.290 (0.516) | -0.799 (0.155) | -0.549 (0.093) | -0.446 (0.256) | n/a | -1.290 (0.513) |
| RC sd, expense ratio |  |  | 0.027 (0.013) |  |  | 4.552 (1.207) | 0.051 (62.256) | 8.709 (2.175) | n/a | 0.027 (nan) |
| N | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | n/a | 108,300 |
| Weakest first-stage F |  | 33.6 |  |  | 11.2 |  |  |  | n/a |  |
| **Avg own-price elasticity** | **-0.270** | **-1.614** | **-1.950** | **-0.283** | **-3.179** | **0.333** | **-0.950** | **4.588** | n/a | **-3.179** |
| Share abs(e) > 1 | 0.01 | 0.53 |  | 0.02 | 0.76 | 0.59 | 0.30 | 0.87 | n/a | 0.76 |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 |  |  |  | n/a | 0.000 |
| Share negative MC (firm Bertrand) | 0.99 | 0.52 |  | 0.98 | 0.31 | 0.18 | 0.79 | 0.00 | n/a | 0.31 |

#### Panel A: Passive index funds: cheap = fee at first raw month ≤ 15th percentile (31% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs | (3″) BLP 1 RC, Hausman² IV | (3‴) BLP 1 RC, newproduct_3 (exactly identified) | (3A7) BLP 1 RC, A7 design (newproduct_1 uninteracted) | (3σ) BLP 1 RC, σ fixed at 0.027 (Table 2 col 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| Expense ratio | -0.938 (0.045) | -5.606 (1.310) | -6.771 (0.837) | -0.670 (0.028) | -16.046 (8.151) | -4.298 (2.438) | -8.096 (1.471) | -1.709 (7.135) | n/a | -16.045 (8.133) |
| Expense ratio × cheap |  |  |  | -0.852 (0.149) | -45.018 (10.795) | -58.425 (10.755) | -22.015 (1.245) | -60.576 (12.205) | n/a | -45.017 (10.763) |
| Past 1-yr return | 0.413 (0.037) | 0.413 (0.034) | 0.414 (0.034) | 0.414 (0.037) | 0.461 (0.045) | 0.468 (0.047) | 0.445 (0.068) | 0.470 (0.051) | n/a | 0.461 (0.045) |
| Age (log) | 0.546 (0.012) | 0.573 (0.011) | 0.580 (0.010) | 0.547 (0.012) | 0.740 (0.097) | 0.520 (0.024) | 0.532 (0.027) | 0.488 (0.099) | n/a | 0.740 (0.097) |
| Tracking error | -0.231 (0.039) | -0.451 (0.066) | -0.505 (0.074) | -0.233 (0.040) | -1.711 (0.564) | -1.329 (0.260) | -0.991 (0.155) | -1.230 (0.330) | n/a | -1.711 (0.563) |
| RC sd, expense ratio |  |  | 0.027 (0.013) |  |  | 8.293 (1.958) | 0.022 (116.799) | 9.364 (3.441) | n/a | 0.027 (nan) |
| N | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | n/a | 108,300 |
| Weakest first-stage F |  | 33.6 |  |  | 10.9 |  |  |  | n/a |  |
| **Avg own-price elasticity** | **-0.270** | **-1.614** | **-1.950** | **-0.224** | **-6.272** | **-0.426** | **-3.139** | **0.694** | n/a | **-6.272** |
| Share abs(e) > 1 | 0.01 | 0.53 |  | 0.01 | 0.97 | 0.72 | 0.88 | 0.79 | n/a | 0.97 |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 |  |  |  | n/a | 0.000 |
| Share negative MC (firm Bertrand) | 0.99 | 0.52 |  | 0.99 | 0.05 | 0.26 | 0.21 | 0.22 | n/a | 0.05 |

#### Panel A: Passive index funds: cheap = fee at first raw month ≤ 20th percentile (38% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs | (3″) BLP 1 RC, Hausman² IV | (3‴) BLP 1 RC, newproduct_3 (exactly identified) | (3A7) BLP 1 RC, A7 design (newproduct_1 uninteracted) | (3σ) BLP 1 RC, σ fixed at 0.027 (Table 2 col 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| Expense ratio | -0.938 (0.045) | -5.606 (1.310) | -6.771 (0.837) | -0.459 (0.027) | -8.132 (4.315) | -1.012 (1.914) | -3.610 (0.732) | 0.907 (5.445) | -1.317 (1.397) | -8.131 (4.312) |
| Expense ratio × cheap |  |  |  | -1.404 (0.198) | -32.641 (4.204) | -41.281 (5.686) | -20.707 (4.881) | -42.699 (7.618) | -40.852 (5.683) | -32.640 (4.198) |
| Past 1-yr return | 0.413 (0.037) | 0.413 (0.034) | 0.414 (0.034) | 0.416 (0.037) | 0.471 (0.039) | 0.480 (0.043) | 0.455 (0.035) | 0.482 (0.048) | 0.479 (0.042) | 0.471 (0.039) |
| Age (log) | 0.546 (0.012) | 0.573 (0.011) | 0.580 (0.010) | 0.546 (0.011) | 0.652 (0.050) | 0.512 (0.021) | 0.522 (0.081) | 0.480 (0.078) | 0.511 (0.020) | 0.652 (0.049) |
| Tracking error | -0.231 (0.039) | -0.451 (0.066) | -0.505 (0.074) | -0.259 (0.043) | -1.755 (0.387) | -1.702 (0.295) | -1.174 (0.211) | -1.656 (0.272) | -1.701 (0.295) | -1.755 (0.386) |
| RC sd, expense ratio |  |  | 0.027 (0.013) |  |  | n/a | 0.520 (10.554) | 6.481 (2.503) | 5.581 (1.230) | 0.027 (nan) |
| N | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 |
| Weakest first-stage F |  | 33.6 |  |  | 18.3 |  |  |  |  |  |
| **Avg own-price elasticity** | **-0.270** | **-1.614** | **-1.950** | **-0.201** | **-3.931** | **-0.466** | **-2.018** | **0.347** | **-0.580** | **-3.931** |
| Share abs(e) > 1 | 0.01 | 0.53 |  | 0.00 | 0.93 | 0.79 | 0.76 | 0.85 | 0.77 | 0.93 |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 |  |  |  |  | 0.000 |
| Share negative MC (firm Bertrand) | 0.99 | 0.52 |  | 1.00 | 0.13 | 0.24 | 0.34 | 0.07 | 0.25 | 0.13 |

#### Panel B: Passive leveraged funds: no interaction (Table 2 as published and replicated)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC |
|---|---|---|---|
| Expense ratio | -2.024 (0.098) | -3.712 (0.328) | -6.484 (0.072) |
| Expense ratio × cheap |  |  |  |
| Past 1-yr return | 0.259 (0.036) | 0.255 (0.036) | 0.261 (0.037) |
| Age (log) | 0.658 (0.038) | 0.706 (0.040) | 0.779 (0.045) |
| Tracking error | -1.183 (0.223) | -1.376 (0.247) | -1.546 (0.264) |
| RC sd, expense ratio |  |  | 2.084 (0.102) |
| N | 15,401 | 15,401 | 15,401 |
| Weakest first-stage F |  | 658.5 |  |
| **Avg own-price elasticity** | **-2.667** | **-4.892** | **-5.911** |
| Share abs(e) > 1 | 0.99 | 0.99 |  |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  |
| Share negative MC (firm Bertrand) | 0.36 | 0.01 |  |

#### The 15 Table 5 funds: own elasticity in the last month (Panel A)

| Fund | p (%) | Table 5 | Logit IV (Table 2) | 10th: cheap? / logit IV / BLP notebook IVs / BLP Hausman² / BLP newproduct_3 / BLP A7 design / BLP σ=0.027 | 15th: cheap? / logit IV / BLP notebook IVs / BLP Hausman² / BLP newproduct_3 / BLP A7 design / BLP σ=0.027 | 20th: cheap? / logit IV / BLP notebook IVs / BLP Hausman² / BLP newproduct_3 / BLP A7 design / BLP σ=0.027 |
|---|---|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | -0.24 | -0.16 | yes / -1.99 / -1.45 / -0.58 / -1.54 / n/a / -1.99 | yes / -1.77 / -1.89 / -0.87 / -1.89 / n/a / -1.77 | yes / -1.18 / -1.27 / -0.71 / -1.26 / -1.26 / -1.18 |
| iShares Core MSCI EAFE ETF | 0.07 | -0.58 | -0.39 | yes / -4.77 / -3.42 / -1.39 / -3.56 / n/a / -4.77 | yes / -4.24 / -4.39 / -2.09 / -4.36 / n/a / -4.24 | yes / -2.83 / -2.96 / -1.69 / -2.93 / -2.96 / -2.83 |
| iShares Core US Aggregate Bond ETF | 0.03 | -0.25 | -0.17 | no / -0.18 / -0.02 / -0.06 / 0.22 / n/a / -0.18 | yes / -1.82 / -1.94 / -0.90 / -1.94 / n/a / -1.82 | yes / -1.21 / -1.30 / -0.73 / -1.30 / -1.30 / -1.21 |
| iShares Russell 1000 Growth ETF | 0.18 | -1.49 | -1.00 | no / -1.11 / 0.31 / -0.34 / 2.62 / n/a / -1.11 | yes / -10.93 / -10.41 / -5.39 / -10.14 / n/a / -10.93 | yes / -7.30 / -7.15 / -4.35 / -6.95 / -7.15 / -7.29 |
| iShares Core S&P Mid-Cap ETF | 0.05 | -0.41 | -0.28 | no / -0.31 / -0.02 / -0.09 / 0.41 / n/a / -0.31 | yes / -3.04 / -3.19 / -1.50 / -3.18 / n/a / -3.04 | yes / -2.03 / -2.15 / -1.21 / -2.13 / -2.14 / -2.03 |
| SPDR S&P 500 ETF Trust | 0.09 | -0.72 | -0.49 | yes / -5.96 / -4.25 / -1.74 / -4.35 / n/a / -5.96 | yes / -5.30 / -5.40 / -2.61 / -5.34 / n/a / -5.30 | yes / -3.54 / -3.66 / -2.11 / -3.61 / -3.65 / -3.54 |
| SPDR Gold Shares | 0.40 | -3.33 | -2.23 | no / -2.46 / 1.94 / -0.75 / 8.58 / n/a / -2.46 | no / -6.39 / 2.73 / -3.22 / 4.50 / n/a / -6.39 | no / -3.24 / 2.20 / -1.41 / 3.50 / 2.00 / -3.24 |
| Technology Select Sector SPDR Fund | 0.08 | -0.67 | -0.45 | no / -0.49 / 0.01 / -0.15 / 0.79 / n/a / -0.49 | no / -1.28 / -0.34 / -0.64 / -0.13 / n/a / -1.28 | no / -0.65 / -0.09 / -0.29 / 0.06 / -0.12 / -0.65 |
| Financial Select Sector SPDR Fund | 0.08 | -0.67 | -0.45 | no / -0.49 / 0.01 / -0.15 / 0.79 / n/a / -0.49 | no / -1.28 / -0.34 / -0.65 / -0.13 / n/a / -1.28 | no / -0.65 / -0.09 / -0.29 / 0.06 / -0.12 / -0.65 |
| SPDR Portfolio S&P 500 ETF | 0.02 | -0.17 | -0.11 | no / -0.12 / -0.02 / -0.04 / 0.13 / n/a / -0.12 | no / -0.32 / -0.15 / -0.16 / -0.11 / n/a / -0.32 | yes / -0.81 / -0.88 / -0.49 / -0.87 / -0.87 / -0.81 |
| Vanguard Total Stock Market Index Fund; Insti | 0.02 | -0.16 | -0.11 | yes / -1.31 / -0.96 / -0.38 / -1.02 / n/a / -1.31 | yes / -1.17 / -1.25 / -0.58 / -1.25 / n/a / -1.17 | yes / -0.78 / -0.84 / -0.47 / -0.83 / -0.83 / -0.78 |
| Vanguard 500 Index Fund; Admiral Shares | 0.04 | -0.32 | -0.22 | yes / -2.65 / -1.92 / -0.77 / -2.04 / n/a / -2.65 | yes / -2.36 / -2.49 / -1.16 / -2.49 / n/a / -2.36 | yes / -1.58 / -1.68 / -0.94 / -1.67 / -1.67 / -1.58 |
| Vanguard 500 Index Fund; ETF Shares | 0.03 | -0.24 | -0.16 | yes / -1.99 / -1.45 / -0.58 / -1.55 / n/a / -1.99 | yes / -1.77 / -1.89 / -0.87 / -1.89 / n/a / -1.77 | yes / -1.18 / -1.27 / -0.71 / -1.26 / -1.26 / -1.18 |
| Vanguard Total Stock Market Index Fund; ETF C | 0.03 | -0.24 | -0.16 | yes / -2.00 / -1.46 / -0.58 / -1.55 / n/a / -2.00 | yes / -1.78 / -1.90 / -0.88 / -1.90 / n/a / -1.78 | yes / -1.19 / -1.27 / -0.71 / -1.27 / -1.27 / -1.19 |
| Vanguard Total Stock Market Index Fund; Admir | 0.04 | -0.33 | -0.22 | yes / -2.68 / -1.94 / -0.78 / -2.06 / n/a / -2.68 | yes / -2.38 / -2.52 / -1.17 / -2.52 / n/a / -2.38 | yes / -1.59 / -1.69 / -0.95 / -1.68 / -1.69 / -1.59 |

## What the table shows

1. **Logit IV with the interaction, column (2′), is the usable alternative.**
   - Cheap funds' price coefficient is −41 to −69, against −6 to −16 for the rest. The interaction is significant at every cutoff; the weakest first-stage F is 10.9–18.3.
   - No fund-month has upward-sloping demand. Average own elasticity −3.2 to −6.3 (Table 2: −1.6). Negative implied MC 5–31% of fund-months (Table 2: 52%).
   - **Table 5 funds above |e| = 1:** 10, 14 and 11 of 15 at the 10th, 15th and 20th percentiles. The same 9 are above 1 at every cutoff: four Vanguard funds (both 500 Index classes, VTI's ETF and Admiral classes), iShares S&P 500, EAFE and Russell 1000 Growth, SPY, SPDR Gold.
   - Costs: the non-cheap coefficient is imprecise (SE 4–8), and the controls move (age 0.57 → 0.65–0.83; tracking error −0.45 → −1.3 to −1.8).
2. **Logit OLS, column (1′), barely moves.** The interaction is small with varying sign; OLS is attenuated as in Table 2 col 1.
3. **The one-RC BLP: σ is not identified once the interaction is in, and every estimator that lets σ float breaks the non-cheap funds.**
   - **σ profile** (`logs/explore_step13_sigma_profile_raw20.log`; one-step GMM, β concentrated out, instruments H, H × cheap, `newproduct_3`, 20th pct):

     | σ | objective | non-cheap slope | cheap slope | avg e | share e > 0 | SPDR Gold e |
     |---|---|---|---|---|---|---|
     | 0 – 1 | 3.77 – 3.50 | −4.7 | −35 | −2.8 | 0 | −1.9 |
     | 2 | 2.88 | −4.6 | −37 | −2.5 | 0.2% | −1.4 |
     | 3 | 1.99 | −4.0 | −38 | −2.1 | 5% | −0.7 |
     | 4 | 1.09 | −3.0 | −39 | −1.5 | 30% | +0.3 |
     | 6.5 (BFGS root) | 0.00 | **+0.9** | −42 | +0.4 | 54% | +3.5 |

     The objective is shallow and monotone: its only root is at σ = 6.5, where more than half the market has upward-sloping demand. The cheap slope and the count of Table 5 funds above 1 (10–11) are stable at every σ; only the non-cheap slope moves, and it moves because a large σ forces the mean coefficient up to keep expensive funds' shares positive.
   - **Hansen J at fixed σ, efficient weighting** (`logs/explore_step13_hansenJ_fixed_sigma_raw20.log`): at the paper's σ = 0.027, J = 2.92 on 1 df, **p = 0.088**. The three instruments do not reject the model with σ held at the paper's value.
   - **Estimators that let σ float, all at the 20th percentile** (details in the logs named):

     | Column / variant | Non-cheap slope | σ | avg e | Outcome |
     |---|---|---|---|---|
     | (3′) notebook IVs (`newproduct_1`, also × cheap) | +0.3 to −4.3 | 4.6–8.3 | +0.3 to −0.5 | upward-sloping; instruments conflict (J p < 0.001) |
     | (3″) Hausman² IV | −1.9 to −8.1 | ≈ 0, n.s. | −1.0 to −3.1 | collapses to logit; restrictions rejected |
     | (3‴) `newproduct_3` uninteracted | +0.9 (5.4) | 6.5 (2.5) | +0.35 | upward-sloping (SPDR Gold +3.5) |
     | (3A7) A7 design, `newproduct_1` uninteracted | −1.3 (1.4) | 5.6 (1.2) | −0.58 | upward-sloping (SPDR Gold +2.0) |
     | Optimal IVs from the Hausman IV (`explore_step15*`) | **+4.0 (0.9)** | 0.32 (0.64) | | positive non-cheap slope |
     | Lognormal RC on −price, `newproduct_3` (`explore_table2_alt_lognormal_1rc_raw20_newproduct3.log`) | −2.6 median | 1.6 (1.3) | −1.99 | stalled, no root; no e > 0 but 67% negative MC |

   - **Why.** Entered alone, every extra instrument in the data implies a non-cheap slope near zero or positive (`logs/explore_step12*`, `step14*`), while the Hausman IV implies −6 to −16. A floating σ reconciles them by inflating heterogeneity. The sign-constrained (lognormal) version cannot go positive, so it drives the non-cheap slope toward zero instead.
4. **The reportable BLP column is (3σ): σ held at the paper's 0.027.**
   - The paper's own Table 2 col (3) finds essentially no price-coefficient heterogeneity in the index market (σ = 0.027, SE 0.013). Holding that value, and adding the interaction, gives non-cheap −6.2 / −16.0 / −8.1, cheap −68.6 / −61.1 / −40.8, average elasticity −3.18 / −6.27 / −3.93, 10 / 14 / 11 of 15 above 1, negative MC 31% / 5% / 13%, and no upward-sloping demand at the 10th / 15th / 20th percentiles.
   - With σ this small the column is numerically the logit IV column; its justification is the σ profile and the J test above, which say the data cannot pin σ once the interaction enters and do not reject the paper's value.
5. **Table A7 column (3), for comparison** (`RESULTS_A7_col3.md`): the published column is this same design (one RC, interaction in X1, `newproduct_1` uninteracted). It re-runs exactly (β −6.934, × broad −6.186, σ 2.25, average elasticity −2.346). It works for the broad-based split because `newproduct_1` alone implies negative slopes for both groups there; it lifts only 2 of the 15 Table 5 funds above |e| = 1.
6. **Leveraged funds.** No interaction, per the paper's A7. The notebook's two leveraged instruments already disagree in the published Table 2 Panel B col 3 (Hausman −3.71, `BLP_IV_rival_funds1` −5.06; J = 14.2, p < 0.001; `logs/explore_step10b_instrument_check_baseline.log`).

## Recommendation

- **Report (2′) logit IV with the interaction and (3σ) BLP with σ fixed at the Table 2 estimate**, with the 15th or 20th percentile as the main cutoff and the others as robustness, and a footnote giving the σ profile and the J test as the reason σ is held.
- **Do not report a column with σ estimated jointly with the interaction**: every instrument set in the data gives upward-sloping demand for the non-cheap funds, and the one sign-constrained version does not converge.
