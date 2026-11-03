# Recommended demand specification: passive index funds (Table 2 Panel A)

Source documents: `NOTE_for_coauthor_replication.md` §1 and `MAIN_REPORT_sharecl_hausman.md`. The paper's own numbers and notebooks are unchanged.

## Sample

- **Base sample:** the Table 2 Panel A estimation sample from `code/main_Danny_Oct2026_index_market.ipynb`, cells 2–4, run unmodified: 108,300 fund-months and 1,302 funds, Jan 2010 – Aug 2024. Each month is a market.
- **Restriction:** keep fund-months that have a family identifier (`firm_f_old`) and where the instrument below is defined.
- **Estimation sample:** 97,429 fund-months and 1,164 funds, including all 15 Table 5 funds.

## Model: logit, linear in the fee

- **Dependent variable:** δ_jt = ln s_jt − ln s_0t, where s_0t = 1 − Σ inside shares in month t.
- **Mean utility:**

      δ_jt = α·p_jt + α_c·(p_jt × cheap_j) + β₁·tracking error_jt + β₂·past 1-yr return_jt + β₃·log age_jt + fund FE + month FE + ξ_jt

- **Price:** p is the expense ratio (`prices`, in percent).
- **No random coefficient** in the main specification.

## "Cheap" indicator (`code/explore/tiers.py`, `raw_entry_tiers`)

- **Definition:** cheap_j = 1 if fund j's expense ratio in its first month in the full raw index file (1994–2025, before any sample filter) is at or below that month's 20th percentile across all index funds with a recorded fee.
- **Ties** count as cheap.
- **Fixed per fund:** the fund FE absorb its level, so only the price slope differs between groups.
- **Robustness:** the 10th and 15th percentiles.

## Instrument Z (replaces the paper's `BLP_IV_hausman_exp_ratio`; `code/explore/new_iv.py`, `asset_class.py`)

- **Definition:** for fund j in month t, the median expense ratio, in the same month, of the funds in the raw file that
    - belong to the same family (`firm_f_old`) as j,
    - have the same share class as j,
    - are in a different asset class from j.
- **Share class** is parsed from the fund name.
    - ETF if `ETF_ind == 1`.
    - Otherwise *institutional* if the name contains "institutional", "inst", "class I/K/Y/Z/R6", "premier", "select" or "admiral".
    - Otherwise *retail* if it contains "investor", "retail", "class A/C/R/T", "service" or "advisor".
    - Otherwise *other mutual fund*.
- **Asset class** is assigned per tracked index (`market_m_index`): US equity, international equity, bonds, allocation, real assets. Every share class of a portfolio, and every fund tracking the same index, gets the same class.
- **Coverage:** the median value is computed from 35 funds; 2% of values come from a single fund. Correlation with the paper's Hausman IV: 0.83.
- **Excluded instruments:** Z and Z × cheap. Two endogenous terms and two instruments, so the model is exactly identified.

## Estimation

- **Software:** logit IV in pyblp 1.3.0, with fund and month FE absorbed:

      pyblp.Problem(pyblp.Formulation('prices + I(prices*cheap) + product_tracking_err + product_past_1yr_ret + log_product_fund_age', absorb='C(product_ids) + C(market_ids)'), data).solve(se_type='clustered')

  with `demand_instruments0 = Z` and `demand_instruments1 = Z × cheap`.
- **Standard errors:** clustered by month.
- **First-stage strength:** the cluster-robust Sanderson–Windmeijer F.
- **Average elasticity:** the per-market mean of own elasticities (`extract_diagonal_means`), as in Table 2.
- **Variant:** replace month FE with month × asset-class FE.

## Results (20th percentile)

| | Fund + month FE (main) | Month × asset-class FE (variant) | *Paper's Table 2 col 2* |
|---|---|---|---|
| Non-cheap price coefficient (SE) | −6.116 (0.845) | −3.798 (0.660) | *−5.606 (1.310)* |
| Price × cheap (SE) | −22.655 (0.794) | −20.238 (0.643) | |
| Cheap total | −28.77 | −24.04 | |
| Past 1-yr return | 0.432 (0.034) | 0.496 (0.037) | *0.413 (0.034)* |
| Log age | 0.549 (0.008) | 0.644 (0.009) | *0.573 (0.011)* |
| Tracking error | −1.044 (0.135) | −0.942 (0.113) | *−0.451 (0.066)* |
| Weakest first-stage F | 166.6 | 262.1 | *33.6* |
| Average own-price elasticity | −2.68 | −1.96 | *−1.61* |
| Share of fund-months with e > 0 | 0 | 0 | *0* |
| Negative MC (firm Bertrand, no scale adjustment) | 24% | 36% | *52%* |
| Table 5 funds with \|e\| > 1 | 7 of 15 | 5 of 15 | *2 of 15* |
| N | 97,429 | 97,429 | *108,300* |

**Cutoff robustness** (fund + month FE):

| Cutoff | Non-cheap (SE) | Cheap total | Weakest F | Table 5 funds with \|e\| > 1 |
|---|---|---|---|---|
| 10th | −6.46 (0.85) | −31.7 | 171 | 6 |
| 15th | −9.61 (1.02) | −35.2 | 173 | 11 |

## Why this specification (details in `MAIN_REPORT_sharecl_hausman.md` §2 and §5)

- **The paper's Hausman IV is unreliable.** Table 2's −5.6 comes from the 7% of fund-months without a family identifier. On the other 93% the same instrument gives upward-sloping demand (+7.24).
- **The new instrument is strong for both groups.** Split-sample first-stage F is 149 for non-cheap funds and 48 for cheap funds. The paper's IV gives F = 0.7 for non-cheap funds.
- **Lead tests are small.** Using this model's residual, |t| ≤ 2.9. With month × asset-class FE, none rejects at the 1% level.
- **Robust:** to the cutoff, to month × asset-class FE, and to dropping Vanguard, BlackRock or State Street (non-cheap −2.2 to −5.2, always negative).

## Not part of the main specification

- **BLP with one random coefficient on the expense ratio** (extra instrument Z²): σ = 1.81, non-cheap −4.22, cheap total −26.3. σ is not credibly identified: the covariance is singular, and overidentified versions send σ to 0 or 11. Use it as a sensitivity check only.
- **Nested logit with tracked-index nests:** the signs are fine with Z, but 41–83% of fund-months have negative MC. Sensitivity check only.
- **Not yet run for this specification:** the downstream steps (scale parameter estimated under each conduct candidate, negative MC after scale adjustment, pyRVtest conduct test).

## Reproduce

From a folder holding `nonLev_funds_product_month_level_v2_patched.csv`, with `PYTHONPATH=code/explore`:

    python step25_new_iv_main.py

Column (3) should read −6.116 (0.845), × cheap −22.655 (0.794), F 166.6. It takes about 10 minutes.
