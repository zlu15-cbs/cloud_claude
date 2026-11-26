# Passive (1x) funds: final recommended specifications

26 Nov 2026. Mutual-fund classes and ETFs in one menu, one fee coefficient. Danny's package of 25 Nov 2026
(98,110 passive fund-months, 1,063 share classes, 177 months; passive data and instruments identical to 24 Nov),
read without running his code. Standard errors clustered by month. Fees in percentage points. Not sent to Danny.

The same content, with hover definitions, is Section 11 of `docs/blp_rc_identification.html`.
Earlier steps: `RESULTS_passive_access_spec.md`, `RESULTS_passive_one_menu.md`.
Code: `code/explore/step54` to `step58`. Output: `logs/explore/step54*` to `step58*`.

## 1. Recommendation

- **B, without partial adjustment (main passive column).** Static demand; random coefficient on log fund age;
  **no random coefficient on the fee**. This is Danny's Table 7 column (4) with the fee random coefficient
  removed (his estimate of it is 0.05, SE 20.5).
- **A, with partial adjustment (dynamic extension).** Table 7 plus last month's log share ratio in mean utility;
  random coefficient on the fee.
- **Not recommended:** a fee random coefficient in the static model (Table 7 column 3). It fails four checks (§3).
- **Instruments in both:** Danny's IV0 to IV4, unchanged, with the 10 bp fee band.
- **Which to use for markups:** B. A's long-run magnitudes depend on an adjustment speed the data do not pin down.

## 2. Estimates (full BLP, two-step GMM, 3,000 draws per month)

| | B: static | A: partial adjustment |
|---|---|---|
| Random coefficient on | log fund age | fee |
| Mean utility | fee, tracking error, past return, log age | same, plus lagged log share ratio |
| Fixed effects | fund, month | fund, month |
| Fund-months | 98,110 | 96,499 |
| Mean fee coefficient | −16.11 (0.95) | −0.45 (0.11) per month |
| Random-coefficient SD | age 1.42 (0.19) | fee 0.77 (0.16) per month |
| Lag coefficient ρ | | 0.983 (0.002) |
| Long-run mean fee coefficient, SD (at estimated ρ) | | −26.1, 5.9 |
| Own elasticity, equal-month mean | −3.90 | −0.07 per month |
| Own elasticity, AUM-weighted | −1.90 | −0.04 per month; −2.45 long-run |
| Fund-months with upward-sloping demand | 0.0% | 0.4% |
| J, heteroskedasticity-robust weight (his convention) | 102.3 on 3 df (p < 0.001) | 31.7 on 3 df (p < 0.001) |
| J, month-clustered weight | 28.9 on 3 df (p < 0.001) | 6.8 on 3 df (p = 0.08) |
| Estimates with the clustered weight | fee −16.16 (0.94); age SD 1.23 (0.16) | fee −0.40 (0.11); fee SD 0.66 (0.16) |
| Smallest scaled singular value | 0.05 | 0.42 |

Danny's Table 7 for comparison. Column (3): fee −18.20 (0.92), fee SD 1.88 (0.37), elasticity −4.19, J 144.4 on 3 df.
Column (4): fee −16.11 (1.22), fee SD 0.05 (20.47), age SD 1.42 (0.27), elasticity −3.90, J 102.3 on 2 df.

## 3. Why no fee random coefficient in the static model

Linear screen (2SLS with the Salanié–Wolak K term; its coefficient is σ²). Table 7 analogue: fee σ² = +3.1 (1.5).

| Change to Table 7 | Static fee σ² |
|---|---|
| Fee band of IV1 and IV4 at 8, 10, 11, 12, 15 bp | +2.9, +3.1, +1.3, **−1.6, −3.1** (SE about 1.6) |
| Drop IV2 | **−17.1 (3.9)** |
| Add an ETF taste trend | **−15.3 (4.8)** |
| Add an age random coefficient | **−12.7 (3.0)**; in the BLP the fee SD goes to 0.05 (SE 20.5) |

## 4. Fee band (your question: 10 bp ± 2 bp)

| Fee band | Static fee σ² | A: fee σ² | A: fee slope | B: age σ² | B: fee slope |
|---|---|---|---|---|---|
| 6 bp | +4.4 (1.6) | +0.69 (0.26) | −0.44 (0.10) | | |
| 8 bp | +2.9 (1.6) | +0.70 (0.26) | −0.44 (0.11) | +0.99 (0.15) | −15.9 (0.9) |
| 9 bp | +3.3 (1.5) | +0.65 (0.26) | −0.47 (0.11) | | |
| 10 bp (his) | +3.1 (1.5) | +0.67 (0.26) | −0.47 (0.12) | +0.97 (0.14) | −15.7 (1.0) |
| 11 bp | +1.3 (1.6) | +0.64 (0.26) | −0.48 (0.12) | | |
| 12 bp | −1.6 (1.6) | +0.59 (0.27) | −0.52 (0.13) | +0.83 (0.16) | −18.6 (1.2) |
| 15 bp | −3.1 (1.8) | +0.57 (0.27) | −0.54 (0.15) | +0.81 (0.17) | −18.6 (1.5) |
| 20 bp | −7.6 (2.1) | +0.43 (0.28) | −0.66 (0.17) | | |

- A and B are robust to the band width. The static fee σ² is not.
- The band itself is needed: with the fee and tracking matching removed, the rival count's first-stage F falls from
  368 to about 15, the static fee σ² turns negative and A's fee slope goes to zero.

## 5. Support for B (linear screen: age K, no fee K)

| Check | Fee slope | Age σ² |
|---|---|---|
| Baseline | −15.7 (1.0) | +0.97 (0.14) |
| One instrument dropped: IV0, IV1, IV2, IV3, IV4 | −17.2, −11.2, −16.4, −15.4, −16.0 | +0.75, +1.21, +4.62, +0.95, +0.97 |
| ETF taste trend added | −13.6 (1.0) | +1.80 (0.30) |
| Before 2019; from 2019 | −14.8 (1.6); −5.9 (1.3) | +0.97 (0.15); +0.62 (0.45) |
| Fee slope, one instrument at a time (logit) | IV0 −5.7, IV1 −17.2, IV2 −28.2, IV4 −15.9 | |
| Mutual-fund rows alone; ETF rows alone | **+3.8 (1.3)**; −14.6 (0.9) | **−4.0 (0.7); −0.58 (0.21)** |

Weak points of B:
- It is a pooled result. Within mutual funds alone the fee slope is positive; within either vehicle alone the age
  σ² is negative.
- J rejects under both weights.
- The fee slope is smaller from 2019.
- The age SD and the mean age coefficient are strongly correlated (mean 0.65 without the random coefficient, 1.90
  with it; smallest singular value 0.05). The fee coefficient is unaffected.
- 48% of assets are in funds with an own elasticity below 1 in absolute value (9 of the 15 largest; Table 7 also 9).
- No fee heterogeneity: elasticities differ across funds only through fee level, share and age.
- A return random coefficient (his columns 5, 6) is left out: its σ² turns negative without IV3 and it makes the
  mean return coefficient negative.

## 6. Support for A (linear screen with the lagged log share ratio)

| Check | Fee slope, per month | Fee σ², per month |
|---|---|---|
| Baseline (J 7.1 on 3 df, clustered) | −0.47 (0.12) | +0.67 (0.26) |
| One instrument dropped: IV0, IV1, IV2, IV3, IV4 | −0.53, −0.64, −0.41, −0.47, −0.40 | +0.78, +0.43, +0.45, +0.63, +0.73 |
| ETF taste trend added | −0.41 (0.15) | +0.49 (0.34) |
| Age term added | −0.42 (0.11) | +0.49 (0.26) |
| Fee slope, one instrument at a time (logit) | IV0 −0.55, IV1 −0.20, IV2 −1.18, IV4 −0.79 | |
| Mutual-fund rows alone; ETF rows alone (logit) | −0.11 (0.08); −0.18 (0.11) | |
| Before 2019; from 2019 | −0.65 (0.22); **+0.24 (0.32)** | +1.35 (0.60); +3.3 (1.9) |

Weak points of A:

**Adjustment speed.**

| Estimate of ρ | Value |
|---|---|
| Full sample | 0.983 (0.002) |
| Funds with at least 170 months | 0.987 (0.003) |
| Half-panel jackknife (bias-corrected) | 1.000 |

| ρ imposed | Fee slope, per month | σ², per month | Long-run fee slope | Long-run SD |
|---|---|---|---|---|
| 0.95 | −1.02 (0.10) | +0.82 (0.27) | −20 | 4.0 |
| 0.98 | −0.51 (0.10) | +0.70 (0.26) | −25 | 5.9 |
| 0.99 | −0.34 (0.10) | +0.66 (0.26) | −34 | 8.1 |
| 1.00 | −0.17 (0.10) | +0.62 (0.26) | none | none |

- For ρ from 0.95 to 0.99 the long-run fee slope is −20 to −34. The data cannot rule out ρ = 1.
- If A is used for magnitudes, set ρ from outside evidence on index-fund asset turnover.
- The partial-adjustment model cannot be estimated directly at monthly frequency: at ρ = 0.983 the implied target
  shares put more than half the market in one fund in 159 of 176 months.

**Sign of individual coefficients.** Read literally, the estimate gives 28% of investors a positive fee
coefficient. Under the long-run reading almost none are. A coefficient constrained to be negative for everyone
(lognormal) was evaluated on a grid, one-step criterion, same weight and 500 draws:

| Fee coefficient | Mean | SD | Criterion |
|---|---|---|---|
| Normal, no dispersion | −0.39 | 0.00 | 0.234 |
| Normal | −0.45 | 0.78 | 0.172 |
| Lognormal (all negative) | −0.46 | 1.20 | 0.154 |
| Lognormal (all negative) | −0.70 | 1.50 | 0.157 |
| Lognormal (all negative) | −0.46 | 0.78 | 0.166 |
| Lognormal (all negative) | −0.46 | 0.40 | 0.197 |

The sign-constrained coefficient fits better than the normal one, and its criterion has an interior minimum near a
mean of −0.5 and an SD of 1.3 per month (the gradient changes sign between the last two grid points). It was not
searched for. Estimating A with a lognormal fee coefficient is the natural refinement if A is reported.

**Other.** σ² loses significance with an ETF trend or the age term; estimates are imprecise in sub-periods; J
rejects under the robust weight.

## 7. Instruments (both specifications)

| IV | Definition | Incremental fee F (his Table 8) | Note |
|---|---|---|---|
| IV0 | Same-family fee in other asset classes | 17.1 | Not built from rivals. Alone: fee slope −5.7 (1.1) static, −0.55 (0.19) per month in A |
| IV1 | Other-family rivals last month, same asset class and access, fee within 10 bp, tracking error within 0.02 | 348.3 | Built from rival fees |
| IV2 | Other-family same-vehicle funds in other asset classes last month | 42.7 | Moves like an ETF-versus-mutual-fund trend |
| IV3 | Other-family share classes at most 12 months old, same asset class | 4.3 | Weak |
| IV4 | Certified rival liquidations over the previous 12 months, matched like IV1 | 88.9 | Built from rival fees |

Exclusion of IV1 and IV4 needs rivals' fee changes to be unrelated to the fund's own demand shock.

## 8. Open questions

- For Danny: why the fee matching stayed in the passive IV1 and IV4 when he removed it from the leveraged ones.
- Whether to add the same lagged-share term to the leveraged sample if A is reported.
