# Table 2_alt: demand with a price × "cheap fund" interaction

Same samples, controls, fund and month fixed effects, and SE clustered by month as Table 2. The only change to the model is one extra term, expense ratio × cheap. Code and logs are under `code/explore/` and `logs/`; the numbers below are generated from those logs by `code/explore/make_table2_alt.py`.

## Definition of "cheap"

For each month of the **full raw file** (index funds 1994–2025; leveraged funds 2007–2024), compute the q-th percentile of expense ratios across all funds with a recorded fee that month. A fund is **cheap** if its expense ratio in its **first raw month** is at or below that month's cutoff; ties count as cheap. Code: `code/explore/tiers.py`.
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
- **(3″) BLP 1 RC, Hausman² IV** (index only) is the same as (3′), but uses the squared Hausman IV (and × cheap) as the extra instruments.

Elasticities are own-price elasticities. "Avg" is the per-market mean, as in Table 2. "Share e > 0" is blank for the index BLP columns because it was not recorded there; the 15-fund table and the average show where it occurs.

#### Panel A: Passive index funds: cheap = fee at first raw month ≤ 10th percentile (20% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs | (3″) BLP 1 RC, Hausman² IV |
|---|---|---|---|---|---|---|---|
| Expense ratio | -0.938 (0.045) | -5.606 (1.310) | -6.771 (0.837) | -1.000 (0.039) | -6.183 (5.239) | 0.274 (1.644) | -1.893 (0.814) |
| Expense ratio × cheap |  |  |  | 0.211 (0.068) | -62.443 (22.487) | -49.255 (8.830) | -18.105 (1.692) |
| Past 1-yr return | 0.413 (0.037) | 0.413 (0.034) | 0.414 (0.034) | 0.413 (0.037) | 0.418 (0.042) | 0.409 (0.041) | 0.421 (0.045) |
| Age (log) | 0.546 (0.012) | 0.573 (0.011) | 0.580 (0.010) | 0.546 (0.012) | 0.829 (0.151) | 0.597 (0.024) | 0.532 (0.018) |
| Tracking error | -0.231 (0.039) | -0.451 (0.066) | -0.505 (0.074) | -0.231 (0.039) | -1.290 (0.516) | -0.799 (0.155) | -0.549 (0.093) |
| RC sd, expense ratio |  |  | 0.027 (0.013) |  |  | 4.552 (1.207) | 0.051 (62.256) |
| N | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 |
| Weakest first-stage F |  | 33.6 |  |  | 11.2 |  |  |
| **Avg own-price elasticity** | **-0.270** | **-1.614** | **-1.950** | **-0.283** | **-3.179** | **0.333** | **-0.950** |
| Share abs(e) > 1 | 0.01 | 0.53 |  | 0.02 | 0.76 | 0.59 | 0.30 |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 |  |  |
| Share negative MC (firm Bertrand) | 0.99 | 0.52 |  | 0.98 | 0.31 | 0.18 | 0.79 |

#### Panel A: Passive index funds: cheap = fee at first raw month ≤ 15th percentile (31% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs | (3″) BLP 1 RC, Hausman² IV |
|---|---|---|---|---|---|---|---|
| Expense ratio | -0.938 (0.045) | -5.606 (1.310) | -6.771 (0.837) | -0.670 (0.028) | -16.046 (8.151) | -4.298 (2.438) | -8.096 (1.471) |
| Expense ratio × cheap |  |  |  | -0.852 (0.149) | -45.018 (10.795) | -58.425 (10.755) | -22.015 (1.245) |
| Past 1-yr return | 0.413 (0.037) | 0.413 (0.034) | 0.414 (0.034) | 0.414 (0.037) | 0.461 (0.045) | 0.468 (0.047) | 0.445 (0.068) |
| Age (log) | 0.546 (0.012) | 0.573 (0.011) | 0.580 (0.010) | 0.547 (0.012) | 0.740 (0.097) | 0.520 (0.024) | 0.532 (0.027) |
| Tracking error | -0.231 (0.039) | -0.451 (0.066) | -0.505 (0.074) | -0.233 (0.040) | -1.711 (0.564) | -1.329 (0.260) | -0.991 (0.155) |
| RC sd, expense ratio |  |  | 0.027 (0.013) |  |  | 8.293 (1.958) | 0.022 (116.799) |
| N | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 |
| Weakest first-stage F |  | 33.6 |  |  | 10.9 |  |  |
| **Avg own-price elasticity** | **-0.270** | **-1.614** | **-1.950** | **-0.224** | **-6.272** | **-0.426** | **-3.139** |
| Share abs(e) > 1 | 0.01 | 0.53 |  | 0.01 | 0.97 | 0.72 | 0.88 |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 |  |  |
| Share negative MC (firm Bertrand) | 0.99 | 0.52 |  | 0.99 | 0.05 | 0.26 | 0.21 |

#### Panel A: Passive index funds: cheap = fee at first raw month ≤ 20th percentile (38% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs | (3″) BLP 1 RC, Hausman² IV |
|---|---|---|---|---|---|---|---|
| Expense ratio | -0.938 (0.045) | -5.606 (1.310) | -6.771 (0.837) | -0.459 (0.027) | -8.132 (4.315) | -1.012 (1.914) | -3.610 (0.732) |
| Expense ratio × cheap |  |  |  | -1.404 (0.198) | -32.641 (4.204) | -41.281 (5.686) | -20.707 (4.881) |
| Past 1-yr return | 0.413 (0.037) | 0.413 (0.034) | 0.414 (0.034) | 0.416 (0.037) | 0.471 (0.039) | 0.480 (0.043) | 0.455 (0.035) |
| Age (log) | 0.546 (0.012) | 0.573 (0.011) | 0.580 (0.010) | 0.546 (0.011) | 0.652 (0.050) | 0.512 (0.021) | 0.522 (0.081) |
| Tracking error | -0.231 (0.039) | -0.451 (0.066) | -0.505 (0.074) | -0.259 (0.043) | -1.755 (0.387) | -1.702 (0.295) | -1.174 (0.211) |
| RC sd, expense ratio |  |  | 0.027 (0.013) |  |  | n/a | 0.520 (10.554) |
| N | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 | 108,300 |
| Weakest first-stage F |  | 33.6 |  |  | 18.3 |  |  |
| **Avg own-price elasticity** | **-0.270** | **-1.614** | **-1.950** | **-0.201** | **-3.931** | **-0.466** | **-2.018** |
| Share abs(e) > 1 | 0.01 | 0.53 |  | 0.00 | 0.93 | 0.79 | 0.76 |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 |  |  |
| Share negative MC (firm Bertrand) | 0.99 | 0.52 |  | 1.00 | 0.13 | 0.24 | 0.34 |

#### Panel B: Passive leveraged funds: cheap = fee at first raw month ≤ 10th percentile (49% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs |
|---|---|---|---|---|---|---|
| Expense ratio | -2.024 (0.098) | -3.712 (0.328) | -6.484 (0.072) | -1.947 (0.079) | -1.893 (0.444) | -4.150 (0.424) |
| Expense ratio × cheap |  |  |  | -0.375 (0.370) | -8.710 (0.843) | -12.262 (1.034) |
| Past 1-yr return | 0.259 (0.036) | 0.255 (0.036) | 0.261 (0.037) | 0.260 (0.037) | 0.278 (0.043) | 0.294 (0.048) |
| Age (log) | 0.658 (0.038) | 0.706 (0.040) | 0.779 (0.045) | 0.649 (0.038) | 0.510 (0.048) | 0.503 (0.055) |
| Tracking error | -1.183 (0.223) | -1.376 (0.247) | -1.546 (0.264) | -1.197 (0.223) | -1.689 (0.265) | -2.017 (0.290) |
| RC sd, expense ratio |  |  | 2.084 (0.102) |  |  | 2.309 (0.265) |
| N | 15,401 | 15,401 | 15,401 | 15,401 | 15,401 | 15,401 |
| Weakest first-stage F |  | 658.5 |  |  | 881.7 |  |
| **Avg own-price elasticity** | **-2.667** | **-4.892** | **-5.911** | **-2.756** | **-6.907** | **-8.637** |
| Share abs(e) > 1 | 0.99 | 0.99 |  | 0.99 | 1.00 |  |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 | 0.112 |
| Share negative MC (firm Bertrand) | 0.36 | 0.01 |  | 0.28 | 0.00 | 0.02 |

#### Panel B: Passive leveraged funds: cheap = fee at first raw month ≤ 15th percentile (58% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs |
|---|---|---|---|---|---|---|
| Expense ratio | -2.024 (0.098) | -3.712 (0.328) | -6.484 (0.072) | -1.947 (0.079) | -1.912 (0.444) | -4.186 (0.425) |
| Expense ratio × cheap |  |  |  | -0.375 (0.370) | -8.617 (0.841) | -12.186 (1.029) |
| Past 1-yr return | 0.259 (0.036) | 0.255 (0.036) | 0.261 (0.037) | 0.260 (0.037) | 0.278 (0.043) | 0.293 (0.048) |
| Age (log) | 0.658 (0.038) | 0.706 (0.040) | 0.779 (0.045) | 0.649 (0.038) | 0.512 (0.048) | 0.506 (0.055) |
| Tracking error | -1.183 (0.223) | -1.376 (0.247) | -1.546 (0.264) | -1.197 (0.223) | -1.686 (0.264) | -2.016 (0.289) |
| RC sd, expense ratio |  |  | 2.084 (0.102) |  |  | 2.319 (0.270) |
| N | 15,401 | 15,401 | 15,401 | 15,401 | 15,401 | 15,401 |
| Weakest first-stage F |  | 658.5 |  |  | 877.9 |  |
| **Avg own-price elasticity** | **-2.667** | **-4.892** | **-5.911** | **-2.760** | **-6.980** | **-8.760** |
| Share abs(e) > 1 | 0.99 | 0.99 |  | 0.99 | 1.00 |  |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 | 0.111 |
| Share negative MC (firm Bertrand) | 0.36 | 0.01 |  | 0.28 | 0.00 | 0.02 |

#### Panel B: Passive leveraged funds: cheap = fee at first raw month ≤ 20th percentile (58% of funds)

| | (1) Logit OLS | (2) Logit IV | (3) BLP 1 RC | (1′) Logit OLS | (2′) Logit IV | (3′) BLP 1 RC, notebook IVs |
|---|---|---|---|---|---|---|
| Expense ratio | -2.024 (0.098) | -3.712 (0.328) | -6.484 (0.072) | -1.947 (0.079) | -1.912 (0.444) | -4.186 (0.425) |
| Expense ratio × cheap |  |  |  | -0.375 (0.370) | -8.617 (0.841) | -12.186 (1.029) |
| Past 1-yr return | 0.259 (0.036) | 0.255 (0.036) | 0.261 (0.037) | 0.260 (0.037) | 0.278 (0.043) | 0.293 (0.048) |
| Age (log) | 0.658 (0.038) | 0.706 (0.040) | 0.779 (0.045) | 0.649 (0.038) | 0.512 (0.048) | 0.506 (0.055) |
| Tracking error | -1.183 (0.223) | -1.376 (0.247) | -1.546 (0.264) | -1.197 (0.223) | -1.686 (0.264) | -2.016 (0.289) |
| RC sd, expense ratio |  |  | 2.084 (0.102) |  |  | 2.319 (0.270) |
| N | 15,401 | 15,401 | 15,401 | 15,401 | 15,401 | 15,401 |
| Weakest first-stage F |  | 658.5 |  |  | 877.9 |  |
| **Avg own-price elasticity** | **-2.667** | **-4.892** | **-5.911** | **-2.760** | **-6.980** | **-8.760** |
| Share abs(e) > 1 | 0.99 | 0.99 |  | 0.99 | 1.00 |  |
| Share e > 0 (upward-sloping) | 0.000 | 0.000 |  | 0.000 | 0.000 | 0.111 |
| Share negative MC (firm Bertrand) | 0.36 | 0.01 |  | 0.28 | 0.00 | 0.02 |

#### The 15 Table 5 funds: own elasticity in the last month (Panel A)

| Fund | p (%) | Table 5 | Logit IV (Table 2) | 10th: cheap? / logit IV / BLP notebook IVs / BLP Hausman² | 15th: cheap? / logit IV / BLP notebook IVs / BLP Hausman² | 20th: cheap? / logit IV / BLP notebook IVs / BLP Hausman² |
|---|---|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | -0.24 | -0.16 | yes / -1.99 / -1.45 / -0.58 | yes / -1.77 / -1.89 / -0.87 | yes / -1.18 / -1.27 / -0.71 |
| iShares Core MSCI EAFE ETF | 0.07 | -0.58 | -0.39 | yes / -4.77 / -3.42 / -1.39 | yes / -4.24 / -4.39 / -2.09 | yes / -2.83 / -2.96 / -1.69 |
| iShares Core US Aggregate Bond ETF | 0.03 | -0.25 | -0.17 | no / -0.18 / -0.02 / -0.06 | yes / -1.82 / -1.94 / -0.90 | yes / -1.21 / -1.30 / -0.73 |
| iShares Russell 1000 Growth ETF | 0.18 | -1.49 | -1.00 | no / -1.11 / 0.31 / -0.34 | yes / -10.93 / -10.41 / -5.39 | yes / -7.30 / -7.15 / -4.35 |
| iShares Core S&P Mid-Cap ETF | 0.05 | -0.41 | -0.28 | no / -0.31 / -0.02 / -0.09 | yes / -3.04 / -3.19 / -1.50 | yes / -2.03 / -2.15 / -1.21 |
| SPDR S&P 500 ETF Trust | 0.09 | -0.72 | -0.49 | yes / -5.96 / -4.25 / -1.74 | yes / -5.30 / -5.40 / -2.61 | yes / -3.54 / -3.66 / -2.11 |
| SPDR Gold Shares | 0.40 | -3.33 | -2.23 | no / -2.46 / 1.94 / -0.75 | no / -6.39 / 2.73 / -3.22 | no / -3.24 / 2.20 / -1.41 |
| Technology Select Sector SPDR Fund | 0.08 | -0.67 | -0.45 | no / -0.49 / 0.01 / -0.15 | no / -1.28 / -0.34 / -0.64 | no / -0.65 / -0.09 / -0.29 |
| Financial Select Sector SPDR Fund | 0.08 | -0.67 | -0.45 | no / -0.49 / 0.01 / -0.15 | no / -1.28 / -0.34 / -0.65 | no / -0.65 / -0.09 / -0.29 |
| SPDR Portfolio S&P 500 ETF | 0.02 | -0.17 | -0.11 | no / -0.12 / -0.02 / -0.04 | no / -0.32 / -0.15 / -0.16 | yes / -0.81 / -0.88 / -0.49 |
| Vanguard Total Stock Market Index Fund; Insti | 0.02 | -0.16 | -0.11 | yes / -1.31 / -0.96 / -0.38 | yes / -1.17 / -1.25 / -0.58 | yes / -0.78 / -0.84 / -0.47 |
| Vanguard 500 Index Fund; Admiral Shares | 0.04 | -0.32 | -0.22 | yes / -2.65 / -1.92 / -0.77 | yes / -2.36 / -2.49 / -1.16 | yes / -1.58 / -1.68 / -0.94 |
| Vanguard 500 Index Fund; ETF Shares | 0.03 | -0.24 | -0.16 | yes / -1.99 / -1.45 / -0.58 | yes / -1.77 / -1.89 / -0.87 | yes / -1.18 / -1.27 / -0.71 |
| Vanguard Total Stock Market Index Fund; ETF C | 0.03 | -0.24 | -0.16 | yes / -2.00 / -1.46 / -0.58 | yes / -1.78 / -1.90 / -0.88 | yes / -1.19 / -1.27 / -0.71 |
| Vanguard Total Stock Market Index Fund; Admir | 0.04 | -0.33 | -0.22 | yes / -2.68 / -1.94 / -0.78 | yes / -2.38 / -2.52 / -1.17 | yes / -1.59 / -1.69 / -0.95 |

## What the table shows

1. **Logit IV with the interaction, column (2′), is the usable alternative.**
   - Cheap funds' price coefficient is −41 to −69, against −6 to −16 for the rest. The interaction is significant at every cutoff, and the weakest first-stage F is 10.9–18.3.
   - No fund-month has upward-sloping demand.
   - **Average own elasticity:** −3.2 to −6.3, against −1.6 in Table 2.
   - **Negative implied MC:** 5–31% of fund-months, against 52%.
   - **Table 5 funds above |e| = 1:** 10, 14 and 11 of 15 at the 10th, 15th and 20th percentiles.
   - **The same 9 funds are above 1 at every cutoff:** four of the five Vanguard funds (both 500 Index classes, and VTI's ETF and Admiral classes), iShares S&P 500, iShares EAFE, iShares Russell 1000 Growth, SPY and SPDR Gold.
   - The others change with the cutoff, because their cheap status or price coefficient does. That includes Vanguard Total Stock Market Institutional Plus (fee 0.02%), at −0.78 at the 20th percentile.
   - SPDR Portfolio S&P 500 (0.02%) stays below 1 at every cutoff.
   - **Costs:** the non-cheap coefficient is imprecise (SE 4–8). The controls also move (age 0.57 → 0.65–0.83; tracking error −0.45 → −1.3 to −1.8).
2. **Logit OLS, column (1′), barely moves.** The interaction is small and its sign varies (+0.2 to −1.4). OLS is attenuated, as in Table 2 col 1, so this column says little.
3. **BLP with the notebook's instruments, column (3′), fails in the index panel.**
   - The non-cheap mean coefficient goes to about zero (+0.3 to −4.3) while σ becomes large (4.6–8.3).
   - Part of the market then gets **upward-sloping demand**: SPDR Gold's own elasticity is +1.9 to +2.7, and the average is +0.33 to −0.47.
   - Cheap funds look fine (−1 to −10).
   - **Why** (run: `logs/explore_step10_instrument_check.log`): with the interaction, `BLP_IV_newproduct_1` alone implies a **positive** non-cheap slope (+1.3 to +3.2), while the Hausman IV implies −6 to −16. Using both, Hansen J rejects at every cutoff (p < 0.001).
   - Without the interaction, the paper's own index spec, the two instruments agree (J = 0.58, p = 0.45).
4. **BLP with the squared Hausman instrument, column (3″), gets the signs right but collapses to logit.**
   - σ goes to about 0, and is not identified (SE 10–117).
   - The overidentifying restrictions are rejected (GMM objective 214–638).
   - The weights change, so cheap funds' coefficients shrink (−20 to −30). Only 2–7 of 15 funds are above 1, and this varies with the cutoff.
5. **Other one-RC variants also failed** (logs in `logs/explore_table2_alt_*`):
   - a lognormal RC on −price: the mean log-coefficient went to −16.7, i.e. a price coefficient of about 0;
   - the RC on price × cheap: σ = 0.07 (SE 39), with a positive non-cheap slope.
6. **Leveraged panel.**
   - Most leveraged funds charge exactly 0.95%, so the percentile rule barely discriminates. The 10th percentile already labels 49% of funds cheap, and the 15th and 20th give identical groups.
   - The interaction is still strong in logit IV: rest −1.9, cheap −10.5, F ≈ 880. The average elasticity rises from −4.9 to −6.9.
   - BLP with the notebook instrument gives an average of −8.6 to −8.8, with 11% of fund-months upward-sloping.
   - **Note for the published Table 2 Panel B col 3:** the leveraged notebook's two instruments already disagree **without** the interaction (Hausman −3.71, `BLP_IV_rival_funds1` −5.06; J = 14.2, p < 0.001; `logs/explore_step10b_instrument_check_baseline.log`).
   - The 15th-percentile leveraged BLP stalled and was evaluated at its best point; the 20th-percentile cell reuses it, because the tiers are identical.

## Recommendation

- **Report column (2′), logit IV with the interaction, as the alternative demand model.** Use the 15th or 20th percentile as the main cutoff, with the other cutoffs as robustness.
  - It moves the cheapest large funds above |e| = 1.
  - It cuts negative marginal costs sharply.
  - It keeps the linear-in-fee form.
- **Do not report a BLP version yet.** With the current instruments the random coefficient is either not identified (σ → 0) or forced by a conflicting instrument into upward-sloping demand.
  - A credible column (3′) needs an extra instrument that agrees with the Hausman IV once the interaction is included. Candidates: cost shifters with within-fund variation, or differentiation instruments built on characteristics.
- **Before any of this goes in the paper,** the leveraged instrument conflict in the published Table 2 Panel B col 3 deserves a look.
