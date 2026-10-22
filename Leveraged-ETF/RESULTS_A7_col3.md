# Table A7 column (3): what the code is, and the re-run

Source: `code/main_Danny_March2026_testing_v3_nonLev_Apr2026_matchEgan_broadspecial.ipynb` (coauthor's 26-Sep-2026 version, commit `f2d8bff`). This file keeps two things apart: what was **read** from the notebook and its saved outputs, and what was **run** here.

## Correction to the earlier report

My earlier A7 statements (in `Table2_alt.md` and `FINDINGS_SUMMARY.md`) were based on the 25-May copy of the notebook, in which cell 11 put both `prices` and `prices × broad` into X2 (two random coefficients) and renamed both `BLP_IV_newproduct_1` and its × broad version to instrument columns. That copy's saved output (−32.53 / +10.84) did not match the published table, and I concluded the published columns came from an unsaved run. **That conclusion is withdrawn.** The 26-Sep notebook contains the published column (3), and its saved output matches the table.

## Read from the notebook

**Specification (cells 11–15).**
- X1: `prices + I(prices*broad_specialized_ind) + product_tracking_err + product_past_1yr_ret + log_product_fund_age`, with `C(product_ids) + C(market_ids)` absorbed.
- X2: `0 + prices` — **one random coefficient, on the expense ratio** (K2 = 1 in the cell 13 output).
- Integration: Monte Carlo, 3000 draws, seed 623543. Optimizer: BFGS, gtol 1e-7, start `np.identity(1)`.
- `solve()` has no `se_type`, so the SEs are pyblp's default robust ones (not clustered).

**Excluded instruments (cell 4 and cell 11; confirmed by MD = 6 in the cell 13 output = 3 exogenous X1 columns + 3 excluded).**
1. `demand_instruments0` = `BLP_IV_hausman_exp_ratio` (Hausman fee IV).
2. `demand_instruments1` = `BLP_IV_hausman_exp_ratio_x_broad`.
3. `demand_instruments2` = `BLP_IV_newproduct_1`, **uninteracted**.

Cell 11 builds `BLP_IV_newproduct_1_x_broad` but never renames it to a `demand_instruments` column, so **it does not enter the problem**. With three parameters (β on price, β on price × broad, σ) and three excluded instruments the model is exactly identified, which is why the saved objective is 3.2e-18.

**Saved output (cell 15).** Converged, 5 iterations, 10 objective evaluations, 46 min.

| | Saved in notebook | Published Table A7, Panel A, col (3) |
|---|---|---|
| Expense ratio | −6.934 (1.295) | −6.934 (1.295) |
| Expense ratio × broad-based | −6.186 (0.607) | −6.186 (0.607) |
| RC sd, expense ratio | 2.2525 (0.680) | |
| Tracking error / past return / age | −0.520 / 0.410 / 0.516 | |

**Panel B (leveraged notebook, cells 11–15, read only):** same structure; the third instrument is `BLP_IV_rival_funds1`; saved β −6.780, × broad 0.512, σ 2.2465, 9 iterations, 20 min. Not re-run here (the leveraged interaction is not significant).

## Run here: `code/explore/a7_col3.py` (log `logs/explore_a7_col3.log`)

Cells 2, 3, 4, 11, 12, 13, 14 and 15 executed verbatim in one namespace. The only substitution is the `bfgs` object from cell 14, replaced by the same SciPy BFGS wrapped to checkpoint each evaluation (parallel over markets with `pyblp.parallel`, which does not change the numbers).

{{A7_RERUN}}

## Why the same design works for the broad-based interaction and not for the cheap-fund interaction

The published column (3) design — one RC on the expense ratio, the interaction in the mean utility, and one extra instrument entered **without** the interaction — is the design I applied to the cheap-fund tier (`Table2_alt.md`, columns (3‴) with `newproduct_3` and the run with `newproduct_1` itself). The difference is what the extra instrument says about the non-interacted slope (logit IV, instrument entered alone; `logs/explore_step12*`):

| Interaction | `newproduct_1` alone implies | Hausman IV implies | Hansen J (H, H × z, `newproduct_1`) |
|---|---|---|---|
| broad-based | −7.7 (specialized), −6.5 (broad) | −7.5, −12.8 | 4.0, p = 0.045 |
| cheap, 10th / 15th / 20th pct | **+2.6 / −1.0 / +0.5** (non-cheap) | −6.2 / −16.0 / −8.1 | 21 / 39 / 24, p < 0.001 |

Under broad-based, both instruments put negative slopes on both groups, so the BLP's σ (2.25) is pinned by a third moment that agrees with the first two, and the elasticities stay sensible. Under the cheap split, the third moment wants a non-cheap slope near zero, and the one-RC BLP delivers it by inflating σ (section 6 of `FINDINGS_SUMMARY.md`; σ profile in `logs/explore_step13_sigma_profile_raw20.log`).

{{A7_DESIGN_CHEAP}}
