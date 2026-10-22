# Exploration: heterogeneity in the loading on the expense ratio

Question: if the demand loading on the expense ratio can differ across funds, do the large index funds in Table 5 Panel A get own-price elasticities above 1 in absolute value?

Each statement is labelled **[run]**, with the log under `logs/` or the result table under `logs/explore/`, or **[inference]**. The paper's numbers are not changed. Code is in `code/explore/`. Every spec uses the Table 2 Panel A sample (N = 108,300; 166 months), produced by notebook cells 2-4 run unmodified, with the notebook controls, fund and month FE, and SE clustered by month.

## Short answer

- **Step 1 [run].** Table 5's elasticity column is the Table 2 col (4) price coefficient times p(1 − s) in each fund's last month. It matches all 15 funds to 0.0005.
- **Interactions with fixed characteristics [run].** They do not deliver |e| > 1 for the large funds without implausible side effects:
  - Broad-based (the paper's A7) and the firm dummies raise the elasticities but leave 13 of 15 funds below 1.
  - Everything that does push them above 1 either gives part of the sample upward-sloping demand (asset class, AUM tercile, the A7 combinations), or does so in BLP (fee tercile).
- **Utility in log(price) [run].** This is the one form that delivers |e| > 1 for all 15 funds:
  - In logit IV it has a strong first stage (F = 824), no upward-sloping demand, and negative implied marginal cost for only 3% of fund-months.
  - Its BLP random coefficient is not identified with the available instruments.
  - In the leveraged market it raises the average elasticity from −4.9 to −8.2 (logit IV).
- **Recommendation.** See section 5.

## Things found along the way

- **Table 5's "Bertrand" column is a markup level, not a Lerner index [run, source code].**
  - The R script (`code/R_table5/Get_passive_index_elasticities.txt`) averages `BLP_mu_bt`.
  - Notebook cell 33 fills `BLP_mu_*` from pyRVtest's `markups` and computes Lerner separately as `BLP_mu / prices`.
  - Cell 34 labels the same quantity "Price minus Marginal Cost in Percentage Points per Annum".
  - So 0.224 for a Vanguard fund priced at about 0.02 to 0.04 percent means an implied marginal cost of about −0.19 percentage points. The two columns of Table 5 do not contradict each other. Both say Lerner > 1 and negative marginal cost for these funds.
  - The numbers agree with this reading **[run]**. Under logit IV the firm-Bertrand markup level is 0.216 for every BlackRock fund (`logs/explore_step1_logit.log`). Scaled by the price coefficients, 0.216 × 5.606 / 8.348 = 0.145, which is Table 5's BlackRock value. Vanguard's 0.32 scales to 0.215, Table 5's Vanguard range.
  - This supersedes the "two periods" explanation in `EXPECTED_RESULTS.md`. The elasticity is indeed last-month only and the margins are sample means, but that is not what makes −0.16 sit next to 0.22.
- **Two Vanguard rows appear to be swapped in Table 5 [run].**
  - In the data, the 430,969 fund is the *ETF* class (p = 0.03) and the 395,578 fund is the *Admiral* class (p = 0.04).
  - Table 5 calls the first "(MF)" and the second "(ETF)". The elasticities confirm which is which: −0.244 needs p = 0.03 and −0.326 needs p = 0.04.
- **Re-verified facts [run, `logs/explore_step2_screen.log` and an inline check].**
  - Confirmed: median share 0.037%, max 4.97%, median price 0.20%, within-fund share of price variance 3.75%.
  - The 5th percentile of price is 0.040, not 0.035.
  - **No fund-month has p = 0.** Notebook cell 4 drops `prices > 0` failures into the outside option, so the Fidelity zero-fee fund is not in the estimation sample, and the "drop p = 0" variant of B1 changes nothing.
- **Data notes [run].**
  - `market_m_cluster` is an index cluster with 313 codes, not an asset class. A4 collapses the largest codes as follows (codes in `code/explore/step2_logit_screen.py`):
    - US large blend: 1 (S&P 500, total market)
    - Other US equity: 5, 6, 7, 10, 11, 12, 23 (small, growth, NDX, value, mid, dividend)
    - International equity: 3, 9, 46
    - Bonds: 2, 16, 25, 26, 52
    - Other (the base group): everything else, including target date (17), REIT (21) and gold.
  - `csent_index_resid` and `chg_VIX_resid` vary within a month, so month FE do not absorb them. C1 includes their main effects.

## 1. Step 1: which model produced Table 5's elasticity column

| Candidate | iShares Core S&P 500 (paper −0.242) | Matches all 15? | Log |
|---|---|---|---|
| Logit IV (Table 2 col 2, α = −5.606) | −0.163 | no (ratio 0.67 throughout) | `explore_step1_logit.log` |
| BLP 1 RC at the paper's σ = 0.027 (`return`) | −0.197 | no | `explore_step1_blp1.log` |
| BLP 3 RC: α = −8.348 × p × (1 − s) | −0.2423 | **yes, max abs. diff 0.0005** | `explore_step1b_formula_check.log` |

- **[run]** The BLP 3 RC model evaluated with `return` at the paper's σ reproduces β = −8.348 (`explore_step1_blp3.log`).
  - I stopped that run during its post-solve elasticity step, after the coauthors' note that 3 RC has a rank-deficient covariance and is being reworked.
  - The formula check uses the same α and the 15 funds' p and s in their last month. With the 3 RC σ near zero, the BLP own elasticity equals α·p·(1 − s) to this precision. **[inference, supported by the 0.0005 fit]**
- **Baseline for what follows.** The screen is in logit IV, so its baseline is Table 2 col (2). Table 5 itself corresponds to α = −8.348.
- **Needed loading [run, `logs/explore/step1_blp1.csv`, column `loading_for_e1`].** Under any α·p model, |e| = 1 requires a loading of −1/(p(1 − s)):
  - −25 to −52 for the funds charging 2 to 4 basis points;
  - −5.6 for Russell 1000 Growth (p = 0.18);
  - −2.5 for SPDR Gold (p = 0.40).

## 2. Logit IV screen (steps 2-3) [run]

Logs: `explore_step2_screen.log`, `explore_step2_A7_combos.log`. Tables: `logs/explore/step2_*.csv`, `step3_positive_loading.csv`.

How each spec is set up:
- Each `p × z` is instrumented by `BLP_IV_hausman_exp_ratio × z`. B1 uses log(Hausman IV + c); B2 uses the squared Hausman IV.
- Every spec is exactly identified, so Hansen J is not defined (none is overidentified).
- The first-stage F is Sanderson-Windmeijer, cluster-robust; the column shows the minimum over endogenous terms.

How each metric is defined:
- "Avg own e" is the per-market mean, as in Table 2.
- "share e>0 loading" is the share of fund-months whose loading on price is positive, i.e. upward-sloping demand.
- Negative marginal cost is shown two ways:
  - single-product: p − p/|e| < 0, which is exactly the share with |e| < 1;
  - multi-product Bertrand with `firm_ids` ownership, from pyblp `compute_costs`.

| Spec | Tier | N | Price terms: coef (clustered SE) | min first-stage F | Avg own e | share abs(e)>1: all / broad / Big 3 | 15 funds: n abs(e)>1 (last mkt), median e | share e>0 loading | neg. MC: single-product / firm Bertrand |
|---|---|---|---|---|---|---|---|---|---|
| baseline | - | 108,300 | prices: -5.606 (1.310) | 33.6 | -1.614 | 0.53 / 0.46 / 0.40 | 2/15, -0.22 | 0.000 | 0.47 / 0.52 |
| A1_broad | A | 108,300 | prices: -7.503 (1.770); broad*prices: -5.278 (0.372) | 53.0 | -2.858 | 0.71 / 0.73 / 0.65 | 2/15, -0.49 | 0.000 | 0.29 / 0.40 |
| A2_etf | A | 108,300 | prices: -2.988 (1.205); etf*prices: -1.889 (0.220) | 28.6 | -1.150 | 0.41 / 0.33 / 0.30 | 1/15, -0.15 | 0.000 | 0.59 / 0.60 |
| A3_big3 | A | 108,300 | prices: -4.141 (1.261); big3*prices: -4.397 (0.382) | 36.6 | -1.668 | 0.58 / 0.49 / 0.55 | 2/15, -0.33 | 0.000 | 0.42 / 0.48 |
| A3_firms | A | 108,300 | prices: -7.406 (1.175); prices*vanguard: -6.453 (0.795); blackrock*prices: -5.528 (0.422); prices*ssga: -1.935 (0.534) | 74.1 | -2.684 | 0.73 / 0.68 / 0.74 | 2/15, -0.54 | 0.000 | 0.27 / 0.37 |
| A4_asset_class | A | 108,300 | prices: 2.271 (1.261); ac_us_large_blend*prices: -10.722 (0.669); ac_us_other_equity*prices: -14.001 (0.538); ac_intl_equity*prices: -4.583 (0.728); ac_bond*prices: -5.183 (0.960) | 87.4 | -0.896 | 0.44 / 0.42 / 0.30 | 1/15, -0.25 | 0.389 | 0.56 / 0.35 |
| A5_fee_tercile | A | 108,300 | prices: -3.714 (6.133); fee_t1*prices: -52.700 (7.572); fee_t2*prices: -11.994 (0.983) | 22.6 | -3.750 | 0.98 / 0.98 / 0.97 | 13/15, -1.64 | 0.000 | 0.02 / 0.06 |
| A6_aum_tercile | A | 108,300 | prices: 8.133 (1.875); aum_t1*prices: -17.887 (0.842); aum_t2*prices: -8.046 (0.571) | 55.9 | -0.417 | 0.45 / 0.38 / 0.40 | 2/15, 0.31 | 0.669 | 0.55 / 0.02 |
| B1_logp_c0.01 | B | 108,300 | log(prices + 0.01): -2.694 (0.078) | 824.4 | -2.492 | 1.00 / 1.00 / 1.00 | 15/15, -2.10 | 0.000 | 0.00 / 0.03 |
| B1_logp_c0.005 | B | 108,300 | log(prices + 0.005): -2.538 (0.073) | 835.0 | -2.434 | 1.00 / 1.00 / 1.00 | 15/15, -2.20 | 0.000 | 0.00 / 0.03 |
| B1_logp_c0.02 | B | 108,300 | log(prices + 0.02): -2.988 (0.088) | 790.2 | -2.596 | 1.00 / 0.99 / 0.99 | 15/15, -1.94 | 0.000 | 0.00 / 0.04 |
| B2_p_sq | B | 108,300 | prices: -26.389 (2.608); prices**2: 21.127 (0.838) | 43.9 | -1.143 | 0.86 / 0.85 / 0.87 | 7/15, -0.96 | 0.087 | 0.14 / 0.20 |
| C1_csent | C | 108,300 | prices: -5.801 (1.317); csent_index_resid*prices: 0.001 (0.003) | 35.6 | -1.636 | 0.53 / 0.46 / 0.40 | 2/15, -0.22 | 0.000 | 0.47 / 0.52 |
| C1_vix | C | 108,300 | prices: -5.605 (1.311); chg_VIX_resid*prices: -0.003 (0.007) | 33.6 | -1.614 | 0.53 / 0.46 / 0.40 | 2/15, -0.22 | 0.000 | 0.47 / 0.52 |
| C2_lag12_aum | C | 88,645 | prices: 3.494 (1.650); laum_t1*prices: 0.331 (0.064); laum_t2*prices: 0.243 (0.035) | 29.1 | 1.035 | 0.39 / 0.32 / 0.25 | 1/15, 0.14 | 1.000 | 0.61 / 0.00 |
| C2_baseline_same_sample | C | 88,645 | prices: -2.864 (1.345) | 21.5 | -0.798 | 0.34 / 0.25 / 0.22 | 1/15, -0.11 | 0.000 | 0.66 / 0.70 |
| A7_broad_fee | A | 108,300 | prices: -0.072 (4.198); broad*prices: 5.455 (1.347); fee_t1*prices: -51.086 (5.803); fee_t2*prices: -14.135 (0.549) | 48.7 | -2.108 | 0.77 / 0.93 / 0.78 | 12/15, -1.33 | 0.101 | 0.23 / 0.42 |
| A7_firms_fee | A | 108,300 | prices: 17.333 (1.831); prices*vanguard: 11.151 (1.225); blackrock*prices: 0.758 (0.569); prices*ssga: 4.483 (0.698); fee_t1*prices: -40.961 (1.824); fee_t2*prices: -17.329 (0.803) | 133.8 | 2.645 | 0.58 / 0.48 / 0.55 | 3/15, -0.36 | 0.636 | 0.42 / 0.16 |
| A7_broad_firms_fee | A | 108,300 | prices: 17.242 (1.979); broad*prices: 0.470 (0.929); prices*vanguard: 11.161 (1.231); blackrock*prices: 0.939 (0.621); prices*ssga: 4.648 (0.907); fee_t1*prices: -41.074 (1.892); fee_t2*prices: -17.485 (0.654) | 252.4 | 2.679 | 0.58 / 0.48 / 0.55 | 3/15, -0.35 | 0.595 | 0.42 / 0.22 |

Checks:
- **A1** reproduces Table A7 Panel A col 2: −7.503, −5.278, average −2.858. **[run]**
- **Baseline** reproduces Table 2 col 2: −5.606 (1.310), average −1.614. **[run]**

What the screen shows, per spec:
- **Raise elasticities with no upward-sloping demand.** A1 broad, A3 firms, A5 fee tercile, B1 log price.
  - Only A5 and B1 move most of the 15 funds above 1.
  - A5 reaches 13 of 15, with a weak base coefficient (−3.7, SE 6.1) and F = 22.6.
  - B1 reaches 15 of 15, with F = 824.
- **A4 asset class.** The "other" group gets a positive coefficient (+2.27), so 39% of fund-months have upward-sloping demand. SPDR Gold, which falls in "other", gets e = +0.90.
- **A6 AUM tercile.** The largest-AUM tercile gets +8.13, so 67% of fund-months have upward-sloping demand.
- **A7 combinations.** They break the base coefficient: firms + fee and broad + firms + fee put 60 to 64% of fund-months on upward-sloping demand, and broad + fee 10%. That leaves A5 alone as the best tier A spec.
- **B2 price squared.** The loading turns positive above p = 0.62, which is 8.7% of fund-months.
- **A2 ETF and A3 Big 3.** Little change.
- **C1 state variables.** The interaction is about 0 (t < 0.5); nothing there.
- **C2 lagged AUM tercile [run].** It fails exogeneity:
  - The lowest-tercile indicator has a within-fund correlation of −0.37 with the baseline ξ̂.
  - The lead tests give t = −58 to −81.
  - ξ̂ is highly persistent (within-fund AR(1) = 0.98), so a 12-month lag does not break the link between past AUM and current demand shocks.
  - The baseline on the same sample also differs (−2.86 against −5.61), so the C2 sample is itself selected.

| Spec | z | within-fund corr(z, xi) | lead t-stat k=1 / 3 / 12 | within-fund AR(1) of xi |
|---|---|---|---|---|
| C1_csent | csent_index_resid | 0.000 | -0.57 / -0.70 / -2.18 | 0.972 |
| C1_vix | chg_VIX_resid | 0.001 | -2.20 / -1.40 / 0.09 | 0.972 |
| C2_lag12_aum | laum_t1 | -0.368 | -57.84 / -61.31 / -80.63 | 0.978 |
| C2_lag12_aum | laum_t2 | 0.010 | 1.11 / 0.29 / -1.96 | 0.978 |

## 3. BLP with 1 RC on the shortlist (step 4) [run]

Logs: `explore_step4_blp_{B1,A5,A1}.log`. Tables: `logs/explore/step4_*`.

Setup: X2 = the price term. Instruments are the spec's logit instruments plus `BLP_IV_newproduct_1` and its interactions with each z, as in the broadspecial notebook. Integration is Monte Carlo with 3000 draws, seed 623543. Optimization is BFGS with gtol 1e-7, clustered SE, using `code/explore/step4_blp_shortlist.py` (parallel, checkpointed). Each run converged.

| Spec | Price terms (SE) | σ (SE) | Avg own e | share abs(e)>1 | neg. MC (firm Bertrand) | Time |
|---|---|---|---|---|---|---|
| B1 log(p + 0.01) | −8.90 (21.44) | 5.89 (18.49) | −6.26 | 0.98 | 0.013 | 37 min |
| A5 fee tercile | p: **+9.52** (2.01); p×fee_t1: −50.83 (9.74); p×fee_t2: −17.34 (3.58) | 2.85 (1.65) | **+0.35** | 0.92 | 0.159 | 25 min |
| A1 broad | p: −8.87 (1.62); p×broad: −3.58 (0.55) | 0.64 (2.20) | −2.98 | 0.70 | 0.373 | 18 min |

- **B1.** The random coefficient is not identified: σ = 5.9 with SE 18.5, and the mean coefficient's SE is 21. The objective is about 0 because the model is exactly identified (one extra instrument for one σ).
  - The large elasticities (−3.6 to −10.9 for the 15 funds) come from this unidentified σ. **[inference]**
  - The logit IV version (−1.7 to −2.6) is the defensible number.
- **A5.** It fails in BLP. The base coefficient turns positive (+9.5), so the highest-fee-tercile funds face upward-sloping demand, and the average elasticity is positive.
- **A1.** This is the paper's A7, now in BLP. σ is not identified, and 13 of 15 funds remain below |e| = 1.

## 4. The 15 Table-5 funds [run]

Own elasticity in each fund's last month. The "Table 5" column is −8.348·p·(1 − s), which equals the paper's values to 0.0005.

| Fund | p (%) | Table 5 (= -8.348 p(1-s)) | logit IV baseline | A1 broad, logit IV | B1 log p, logit IV | A1 broad, BLP 1RC | B1 log p, BLP 1RC | A5 fee tercile, BLP 1RC |
|---|---|---|---|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | -0.24 | -0.16 | -0.37 | -1.95 | -0.36 | -9.59 | -1.21 |
| iShares Core MSCI EAFE ETF | 0.07 | -0.58 | -0.39 | -0.89 | -2.34 | -0.87 | -7.82 | -2.88 |
| iShares Core US Aggregate Bond ETF | 0.03 | -0.25 | -0.17 | -0.38 | -2.01 | -0.37 | -10.16 | -0.25 |
| iShares Russell 1000 Growth ETF | 0.18 | -1.49 | -1.00 | -1.34 | -2.54 | -1.58 | -5.36 | -1.29 |
| iShares Core S&P Mid-Cap ETF | 0.05 | -0.42 | -0.28 | -0.37 | -2.23 | -0.44 | -8.83 | -0.41 |
| SPDR S&P 500 ETF Trust | 0.09 | -0.72 | -0.49 | -0.65 | -2.34 | -0.77 | -6.71 | -3.59 |
| SPDR Gold Shares | 0.40 | -3.32 | -2.23 | -2.99 | -2.62 | -3.49 | -3.62 | -2.29 |
| Technology Select Sector SPDR Fund | 0.08 | -0.66 | -0.45 | -0.60 | -2.38 | -0.71 | -7.50 | -0.63 |
| Financial Select Sector SPDR Fund | 0.08 | -0.67 | -0.45 | -0.60 | -2.39 | -0.71 | -7.52 | -0.63 |
| SPDR Portfolio S&P 500 ETF | 0.02 | -0.17 | -0.11 | -0.15 | -1.79 | -0.18 | -10.90 | -0.83 |
| Vanguard Total Stock Market Index Fund; Institut | 0.02 | -0.16 | -0.11 | -0.24 | -1.72 | -0.24 | -9.16 | -0.80 |
| Vanguard 500 Index Fund; Admiral Shares | 0.04 | -0.32 | -0.22 | -0.49 | -2.08 | -0.48 | -8.97 | -1.61 |
| Vanguard 500 Index Fund; ETF Shares | 0.03 | -0.24 | -0.16 | -0.37 | -1.96 | -0.36 | -9.61 | -1.21 |
| Vanguard Total Stock Market Index Fund; ETF Clas | 0.03 | -0.24 | -0.16 | -0.22 | -1.97 | -0.26 | -9.72 | -1.22 |
| Vanguard Total Stock Market Index Fund; Admiral  | 0.04 | -0.33 | -0.22 | -0.50 | -2.10 | -0.49 | -9.13 | -1.63 |

Mean Bertrand markup level (p − mc, percentage points; firm ownership) in the BLP 1 RC specs. Compare Table 5: 0.145 BlackRock, 0.131 SSGA, 0.215 to 0.224 Vanguard.

| Fund | p (%) | A1 broad, BLP 1RC | B1 log p, BLP 1RC | A5 fee tercile, BLP 1RC |
|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | 0.101 | 0.007 | 0.036 |
| iShares Core MSCI EAFE ETF | 0.07 | 0.101 | 0.017 | 0.037 |
| iShares Core US Aggregate Bond ETF | 0.03 | 0.101 | 0.011 | 0.133 |
| iShares Russell 1000 Growth ETF | 0.18 | 0.134 | 0.051 | 0.148 |
| iShares Core S&P Mid-Cap ETF | 0.05 | 0.133 | 0.018 | 0.137 |
| SPDR S&P 500 ETF Trust | 0.09 | 0.122 | 0.012 | 0.030 |
| SPDR Gold Shares | 0.40 | 0.124 | 0.115 | 0.175 |
| Technology Select Sector SPDR Fund | 0.08 | 0.123 | 0.022 | 0.136 |
| Financial Select Sector SPDR Fund | 0.08 | 0.123 | 0.022 | 0.136 |
| SPDR Portfolio S&P 500 ETF | 0.02 | 0.122 | 0.003 | 0.030 |
| Vanguard Total Stock Market Index Fund; Institut | 0.02 | 0.156 | 0.010 | 0.064 |
| Vanguard 500 Index Fund; Admiral Shares | 0.04 | 0.149 | 0.016 | 0.064 |
| Vanguard 500 Index Fund; ETF Shares | 0.03 | 0.151 | 0.015 | 0.064 |
| Vanguard Total Stock Market Index Fund; ETF Clas | 0.03 | 0.181 | 0.015 | 0.064 |
| Vanguard Total Stock Market Index Fund; Admiral  | 0.04 | 0.149 | 0.016 | 0.064 |

## 5. Leveraged market (step 5) [run]

Logs: `explore_step5_lev_logit.log`, `explore_step5_lev_blp.log`.

| Model | Price coefficient (SE) | Avg own e | Table 2 Panel B counterpart |
|---|---|---|---|
| Logit IV, p (Table 2 col 2, reproduced) | −3.712 (0.328) | −4.892 | −3.712, −4.892 |
| Logit IV, log(p + 0.01) | −8.366 (0.856) | −8.201 | |
| Logit IV, log(p + 0.005) / log(p + 0.02) | −8.498 / −8.159 | −8.367 / −7.927 | |
| BLP 1 RC, log(p + 0.01), extra IV `BLP_IV_rival_funds1` | −7.726 (0.587); σ = −0.011 | −7.573 | col 3: −5.911 |

- In the leveraged market the BLP collapses to logit: σ is about 0, with zero gradient and Hessian, so σ's SE is not meaningful.
- With log price the elasticity no longer scales with the fee. Leveraged funds (median fee 0.95%) then get |e| of about 8, up from about 5, which would lower the paper's leveraged markups and Lerner indices. **[inference]**
- One demand model for both markets is feasible in form (log price everywhere). The coefficient differs a lot between markets: −2.7 for index and −8.4 for leveraged in logit IV.

## 6. Ranked recommendation

1. **B1, utility in log(p + c), estimated in logit IV.**
   - Every fund-month gets |e| > 1, with no upward-sloping demand, few negative marginal costs (3%), a strong first stage (F = 824), and little sensitivity to c (0.005 to 0.02).
   - *Exogeneity assumption:* the same as the paper's. The Hausman expense-ratio IV (other markets' fees) is uncorrelated with within-fund demand shocks, now in logs. The functional form adds no new instrument. **Credible to the same degree as Table 2.**
   - *Caveats:*
     - It is a change of functional form, not heterogeneity in a characteristic.
     - The BLP version does not identify σ with the current instruments (index) or collapses to logit (leveraged). A stronger instrument for the random coefficient would be needed before reporting BLP numbers from it.
     - It roughly doubles the leveraged-market elasticity.
2. **A1, broad-based interaction (the paper's A7).**
   - It keeps the current model and is already in the paper, but it does not answer the question: 13 of 15 funds stay below |e| = 1 in logit IV and in BLP.
   - *Exogeneity:* broad-based status is fixed per fund and its main effect is absorbed by fund FE; the interaction instrument is Hausman × broad (F = 186). **Credible.**
3. **A5, fee tercile at the fund's first month.**
   - In logit IV it moves 13 of 15 funds above 1.
   - *Exogeneity:* the first-month fee is predetermined relative to later demand shocks. But it is selected on the outcome-relevant variable (price itself), so the specification is close to a step-function version of B1 **[inference]**. Its base coefficient is imprecise (SE 6.1).
   - **Not usable in BLP**, where the base coefficient turns positive (+9.5).
4. **Not recommended:**
   - A4 asset class, A6 AUM tercile, the A7 combinations and B2 price squared: upward-sloping demand for 9 to 67% of fund-months.
   - C1: no effect.
   - C2: fails exogeneity, with a persistent ξ̂ and strong lead correlations.

Where the paper stands either way: under the paper's own model, Table 5's two columns are consistent with each other (Lerner > 1, negative marginal cost for the cheapest funds). The open issue is whether a linear-in-fee demand is credible for funds that charge 2 to 4 basis points, and that is what B1 addresses. **[inference]**
