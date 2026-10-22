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

**Result (`logs/explore/a7_col3_summary.csv`, `a7_col3_funds.csv`).** Converged, objective 0.0, 7 objective evaluations, 1408 s on two worker processes.

| | Re-run | Notebook / published | Clustered SE (added) |
|---|---|---|---|
| Expense ratio | −6.934 (1.2947) | −6.934 (1.2947) | (1.214) |
| Expense ratio × broad-based | −6.186 (0.6068) | −6.186 (0.6068) | (0.653) |
| RC sd, expense ratio | 2.2525 (0.680) | 2.2525 (0.680) | (0.768) |
| Tracking error | −0.5203 (0.0769) | −0.52035 (0.0769) | (0.067) |
| Past 1-yr return | 0.4098 (0.0152) | 0.40975 (0.0152) | (0.032) |
| Age (log) | 0.5158 (0.0163) | 0.51583 (0.0163) | (0.022) |
| Average own-price elasticity (per-market mean) | **−2.346** | A7 reports −2.346 | |

Every coefficient and SE matches the saved output to four decimals, and the average elasticity matches A7 to three. 0.02% of fund-months have a positive own elasticity; 70% have |e| > 1.

**The 15 Table 5 funds, own elasticity in the last month (Aug 2024), under A7 col (3):**

| Fund | p (%) | broad-based? | e |
|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | yes | −0.39 |
| iShares Core MSCI EAFE ETF | 0.07 | yes | −0.92 |
| iShares Core US Aggregate Bond ETF | 0.03 | yes | −0.40 |
| iShares Russell 1000 Growth ETF | 0.18 | no | −1.18 |
| iShares Core S&P Mid-Cap ETF | 0.05 | no | −0.36 |
| SPDR S&P 500 ETF Trust | 0.09 | **no** | −0.61 |
| SPDR Gold Shares | 0.40 | no | −2.23 |
| Technology Select Sector SPDR | 0.08 | no | −0.56 |
| Financial Select Sector SPDR | 0.08 | no | −0.56 |
| SPDR Portfolio S&P 500 ETF | 0.02 | no | −0.15 |
| Vanguard Total Stock Market Inst. Plus | 0.02 | yes | −0.26 |
| Vanguard 500 Index Admiral | 0.04 | yes | −0.52 |
| Vanguard 500 Index ETF | 0.03 | yes | −0.39 |
| Vanguard Total Stock Market ETF | 0.03 | **no** | −0.21 |
| Vanguard Total Stock Market Admiral | 0.04 | yes | −0.52 |

Two points follow:
- The published A7 col (3) model lifts only 2 of the 15 funds above |e| = 1 (Russell 1000 Growth and SPDR Gold). The broad-based interaction roughly doubles the Table 5 elasticities (Table 2 col 3 gives −0.16 to −0.33 for the S&P 500 funds; here −0.39 to −0.61) but does not change the picture.
- **The `broad_specialized` label looks inconsistent for some of these funds.** SPY, SPDR Portfolio S&P 500 and VTI's ETF share class are coded "specialized", while the S&P 500 and Total Stock Market mutual-fund classes of the same portfolios are "broad-based". If the label is meant to describe the index, these should agree. Across the estimation sample, 22.6% of fund-months tracking the S&P 500 (`market_m_index == 'SPX'`) are coded "specialized" (SPY in all 166 months). Since the A7 interaction is identified from this label, it is worth checking at the source.


## Why the same design works for the broad-based interaction and not for the cheap-fund interaction

The published column (3) design — one RC on the expense ratio, the interaction in the mean utility, and one extra instrument entered **without** the interaction — is the design I applied to the cheap-fund tier (`Table2_alt.md`, columns (3‴) with `newproduct_3` and the run with `newproduct_1` itself). The difference is what the extra instrument says about the non-interacted slope (logit IV, instrument entered alone; `logs/explore_step12*`):

| Interaction | `newproduct_1` alone implies | Hausman IV implies | Hansen J (H, H × z, `newproduct_1`) |
|---|---|---|---|
| broad-based | −7.7 (specialized), −6.5 (broad) | −7.5, −12.8 | 4.0, p = 0.045 |
| cheap, 10th / 15th / 20th pct | **+2.6 / −1.0 / +0.5** (non-cheap) | −6.2 / −16.0 / −8.1 | 21 / 39 / 24, p < 0.001 |

Under broad-based, both instruments put negative slopes on both groups, so the BLP's σ (2.25) is pinned by a third moment that agrees with the first two, and the elasticities stay sensible. Under the cheap split, the third moment wants a non-cheap slope near zero, and the one-RC BLP delivers it by inflating σ (section 6 of `FINDINGS_SUMMARY.md`; σ profile in `logs/explore_step13_sigma_profile_raw20.log`).

**The A7 column (3) design applied to the cheap-fund tier (run; `logs/explore_table2_alt_blp_index_raw20_a7design_newproduct1.log`).** One RC on the expense ratio, price × cheap (20th-percentile raw-entry tier) in X1, instruments Hausman, Hausman × cheap and `BLP_IV_newproduct_1` uninteracted; exactly identified, converged.

| | Estimate (clustered SE) |
|---|---|
| Expense ratio (non-cheap) | −1.32 (1.40) |
| Expense ratio × cheap | −40.85 (5.68) |
| RC sd, expense ratio | 5.58 (1.23) |
| Average own-price elasticity | −0.58 |
| SPDR Gold Shares, own elasticity | **+2.0** |
| Table 5 funds with \|e\| > 1 / with e > 0 | 11 / 1 |

Same design, opposite outcome: under the cheap split the third instrument pulls σ to 5.6 and the non-cheap slope to zero, and part of the market gets upward-sloping demand. The diagnosis and the usable alternative (σ held at the paper's Table 2 col 3 value) are in `Table2_alt.md`.

