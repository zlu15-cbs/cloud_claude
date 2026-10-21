# EXPECTED_RESULTS.md — what the cloud session should reproduce and investigate

Paper: "Leveraged ETF" (Overleaf: `Apps\Overleaf\Leveraged ETF`; tables in `output/tables/*.tex`).
Table numbers below follow the order of `\begin{table}` in `main.tex` (body, then Online Appendix A1, A2, ...).
Statements marked **[source]** are copied from the paper's table files or the notebooks. Statements marked **[inference]** are mine and unchecked.

## Goal

1. **Validate Table 2** (demand parameters; `demand_parameters_v1.tex`): rerun both notebooks and compare every number below.
2. **Find what changes make own-price elasticities of large funds in Table 5 (`lerner_Index_examples.tex`) exceed 1 in absolute value**, using Tables A3 and A7 as the related evidence.

## Files

| Item | Path (relative to this folder) |
|---|---|
| Leveraged (Panel B) | `code/main_Danny_Oct2026_leveraged_market.ipynb`, reads `data/LETF_product_month_level_v4_patched.csv` |
| Index (Panel A) | `code/main_Danny_Oct2026_index_market.ipynb`, reads `data/nonLev_funds_product_month_level_v2_patched.csv` |
| A7 index (broad-based interaction) | `code/main_Danny_March2026_testing_v3_nonLev_Apr2026_matchEgan_broadspecial.ipynb`, same index CSV; formulation `prices + I(prices*broad_specialized_ind) + ...`, `broad_specialized_ind = (broad_specialized == "broad-based")`, IVs `BLP_IV_hausman_exp_ratio_x_broad`, `BLP_IV_newproduct_1_x_broad` |
| A7 leveraged | `code/main_Danny_March2026_testing_v3_replicate_Hausman_exp_ratio_broadspecial.ipynb`, same LETF CSV; IVs `BLP_IV_hausman_exp_ratio_x_broad`, `BLP_IV_rival_funds1_x_broad` |
| Env | `requirements.txt` (pyblp 1.3.0, pyRVtest 0.3.2, Python 3.11). Notebooks read the CSV by bare filename: run with the CSV in the working directory. |

Run each notebook top to bottom. pyblp Monte Carlo integration, size 3000, seed 623543. The first cell says to run each `pip install` in a separate cell.

## Map: Table 2 column to notebook cell **[source]**

Same cell numbers in both notebooks unless noted (index / leveraged).

| Col | Model | Cell | Specification |
|---|---|---|---|
| (1) Logit OLS | not in the notebooks | none | OLS counterpart of col (2); needs separate code (pyblp has no OLS switch; use `absorb` + OLS, or `pyblp.Problem` with the price as its own instrument) |
| (2) Logit IV | 8 | `prices + product_tracking_err + product_past_1yr_ret + log_product_fund_age`, absorb `C(product_ids) + C(market_ids)`, clustered SE; IV `demand_instruments0` = `BLP_IV_hausman_exp_ratio` |
| (3) BLP IV, 1 RC | 16 | X2 = `0 + prices`; extra IV `demand_instruments1` (index: `BLP_IV_newproduct_1`; leveraged: `BLP_IV_rival_funds1`) |
| (4) BLP IV, 3 RC | 24 / 25 | X2 = `0 + prices + log_product_fund_age + product_past_1yr_ret`; further IVs `demand_instruments2,3` (index: logs of `BLP_IV_rival_log_fund_age4`, `BLP_IV_rival_tracking_err4`; leveraged: `BLP_IV_rival_funds4`, `BLP_IV_newproduct_1`) |

Sample filters, both: `shares >= 0.0001`, 2010 <= month_t <= 2024+8/12. Market = month. Index: all rows. Leveraged: **only `market_m_bull_bear == "Bull"` rows, market = month x bull/bear** (cell 3). The paper note does not say Bull-only; Table 2 Panel B has N = 15,401. Confirm that N matches; if not, test whether Table 2 uses Bull only.
Elasticities: `compute_elasticities()` then `extract_diagonal_means`, averaged over all product-markets (cells 9, 18, 25/26).

## Expected numbers: Table 2 **[source]**

Standard errors in parentheses. Tolerance is yours to set; the BLP columns depend on the integration draws and the optimizer.

### Panel A: Passive index funds (N = 108,300)

| | (1) Logit OLS | (2) Logit IV | (3) BLP IV | (4) BLP IV |
|---|---|---|---|---|
| Expense ratio | -0.938 (0.046) | -5.606 (0.131) | -6.771 (0.736) | -8.348 (1.563) |
| Past 1-yr return | 0.413 (0.037) | 0.413 (0.034) | 0.414 (0.014) | 0.387 (0.028) |
| Age (log) | 0.546 (0.012) | 0.573 (0.011) | 0.580 (0.011) | 0.594 (0.049) |
| Tracking error | -0.231 (0.039) | -0.451 (0.066) | -0.505 (0.062) | -0.544 (0.095) |
| RC sd, expense ratio | | | 0.027 (0.011) | -0.008 (38.559) |
| RC sd, past return | | | | -0.009 (4.872) |
| RC sd, age | | | | 0.001 (30.556) |
| **Avg own-price elasticity** | **-0.268** | **-1.614** | **-1.950** | **-2.404** |

### Panel B: Passive leveraged funds (N = 15,401)

| | (1) Logit OLS | (2) Logit IV | (3) BLP IV | (4) BLP IV |
|---|---|---|---|---|
| Expense ratio | -2.024 (0.098) | -3.712 (0.328) | -6.484 (0.079) | -6.141 (0.688) |
| Past 1-yr return | 0.259 (0.037) | 0.255 (0.040) | 0.261 (0.029) | 0.244 (0.041) |
| Age (log) | 0.658 (0.038) | 0.706 (0.040) | 0.779 (0.031) | 0.785 (0.100) |
| Tracking error | -1.183 (0.224) | -1.376 (0.247) | -1.546 (0.239) | -1.644 (0.252) |
| RC sd, expense ratio | | | 2.084 (0.112) | 1.813 (0.314) |
| RC sd, past return | | | | -0.095 (0.077) |
| RC sd, age | | | | -0.075 (0.717) |
| **Avg own-price elasticity** | **-2.684** | **-4.892** | **-5.911** | **-5.953** |

All columns include fund FE and time FE. Text of the paper: Panel B IV coefficient "about 2 ... elasticity about 2.6", which does not match the table (-3.712 / -4.892 in col 2). Flag any such text/table mismatch; do not fix the paper.

## Table 5: the target of the investigation **[source: `lerner_Index_examples.tex`, `5_conducttesting.tex`]**

Averages over the sample period, top-5 funds of each Big-3 index sponsor (Panel A) and of ProShares / Direxion (Panel B). Elasticity, then Bertrand margin.

Panel A (index funds): **all but one have |elasticity| < 1.**

| Fund | AUM ($m) | Elasticity | Bertrand margin |
|---|---|---|---|
| Vanguard Total Stock Market Index Fund | 700,879 | -0.160 | 0.224 |
| Vanguard 500 Index Fund (MF) | 542,138 | -0.323 | 0.215 |
| Vanguard 500 Index Fund (ETF) | 508,722 | -0.243 | 0.217 |
| Vanguard Total Stock Market (MF) | 430,969 | -0.244 | 0.215 |
| Vanguard Total Stock Market (ETF) | 395,578 | -0.326 | 0.215 |
| SPDR S&P 500 ETF Trust | 566,342 | -0.725 | 0.131 |
| SPDR Gold Shares | 69,693 | -3.325 | 0.131 |
| Technology Select Sector SPDR | 69,366 | -0.665 | 0.131 |
| Financial Select Sector SPDR | 45,923 | -0.666 | 0.131 |
| SPDR Portfolio S&P 500 ETF | 44,366 | -0.167 | 0.130 |
| iShares Core S&P 500 ETF | 521,629 | -0.242 | 0.145 |
| iShares Core MSCI EAFE ETF | 124,057 | -0.580 | 0.145 |
| iShares Core US Aggregate Bond ETF | 116,890 | -0.249 | 0.145 |
| iShares Russell 1000 Growth ETF | 96,428 | -1.494 | 0.145 |
| iShares Core S&P Mid-Cap ETF | 89,662 | -0.415 | 0.145 |

Panel B (leveraged): already |elasticity| between 3.8 and 5.4 (ProShares UltraPro QQQ -3.839, Direxion Semiconductor Bull 3X -4.035, others -4.9 to -5.4). Nothing to fix; use as a reference for what the BLP gives when prices are high.

How the table is built **[source: coauthor's R, `code/R_table5/Get_passive_index_elasticities.txt` and `Get_passive_lev_elasticities.txt`]**:
- Funds: the top 5 by `product_mtna` in the last month, per firm.
- "Elasticity": the BLP own elasticity in the **last market only** (`tail(.SD,1)`).
- Bertrand / Bertrand_PW / Cournot / Monopoly: **sample means** of the fund-month margins.

The elasticity and the margins therefore come from different periods. That explains why a −0.16 elasticity sits next to a 0.22 margin. The table note's "averaged over the entire sample period" is accurate for the margins only.

In this sample 1 − s ≥ 0.95 (max share 5.0 percent), so a fund's own elasticity is about α·p.

## Hypotheses to test for why large funds have |e| < 1 **[inference — verify by running]**

1. **Mechanical price scaling.** In logit, own-price elasticity is alpha * p_j * (1 - s_j). Large index funds charge very low expense ratios (Vanguard roughly 0.03 to 0.04 percent; check the units in `product_exp_ratio`, as Table 2 Panel A has alpha about -5.6 with an average |e| of 1.6, which implies a typical p about 0.29 (if p is in percent)). With alpha near -8, p about 0.03 gives |e| about 0.24, matching the -0.16 to -0.33 above. So |e| < 1 for the largest funds follows from the functional form (the elasticity is proportional to price) and not necessarily from a flaw in the estimate. Test: print p, s, alpha*p*(1-s) for the Table 5 funds.
2. **Price coefficient too small for low-fee funds.** A3 and A7 are the related checks (below). Candidate changes: a price-by-fund-type interaction (A7 shows broad-based index funds are more price-sensitive, interaction -5.3 to -6.2 on top of the base); a random coefficient on price that varies with log price or fund size; a nonlinear price term (log price, or price in basis points with a fund-size interaction); a different outside-option definition (Panel A: shares below 0.01 percent plus index funds tracking with R^2 < 0.95; average outside share 12.15 percent); stronger instruments for the price (col 4 has RC standard errors of 38.6, 4.9, 30.6: the random coefficients are not identified, so col 4 is effectively logit-like).
3. **Fixed effects absorb the variation.** `absorb='C(product_ids) + C(market_ids)'` identifies alpha only from within-fund changes in the expense ratio, which for the large Vanguard / SPDR / iShares funds are tiny. Test: drop fund FE (the paper's A6 "Firm x Index FE" version does a related thing), or use firm-by-index FE, and see which funds' elasticities move.
4. **Market-share denominator.** The index notebook recomputes shares as `product_mtna / market_share_m_denom_alt1`. Large funds with big s have (1 - s) shrinking |e| further. Test sensitivity to the denominator.

For each variant, report: Table 2 Panel A col (2), (3), (4) coefficients and average own-price elasticity; the own-price elasticity of the 15 Table 5 funds; the share of fund-months with |e| > 1.

## Related appendix tables **[source]**

**A3 (`compare_cross_elas.tex`): Logit vs BLP average cross-elasticities, leveraged market** (x100), by issuer pair, split by "tracking a similar index (correlation > 0.99)" and "tracking a different index":

| k -> j | similar: Logit | similar: BLP | different: Logit | different: BLP |
|---|---|---|---|---|
| ProShares -> ProShares | 13.14 | 21.94 | 6.19 | 10.31 |
| ProShares -> ProFunds | 10.22 | 8.87 | 6.13 | 5.54 |
| ProShares -> Direxion | 14.98 | 22.20 | 6.25 | 9.92 |
| Direxion -> Direxion | 4.51 | 6.62 | 4.45 | 6.99 |
| Direxion -> ProFunds | 4.38 | 5.11 | 4.73 | 4.70 |
| Direxion -> ProShares | 4.34 | 6.91 | 4.67 | 7.60 |
| ProFunds -> ProFunds | 1.43 | 3.07 | 1.05 | 2.42 |
| ProFunds -> ProShares | 1.41 | 1.60 | 1.04 | 1.14 |
| ProFunds -> Direxion | 1.99 | 3.11 | 1.03 | 1.29 |

BLP is built on the BLP spec "random coefficients on price, fund age, and past 1-year return" (col 4 of Panel B, notebook cell 25/26). Definition in the note: epsilon_jk = (x_k / s_j) * d s_j / d x_k for k != j. The notebooks do not compute this table; the loop in cells 29+ saves per-market elasticity matrices to `elasticity_outputs/`, which can be aggregated by issuer and index-correlation pair.

**A7 (`demand_parameters_broad_vs_specialized.tex`): Table 2 with an expense-ratio x Broad-based-fund interaction.** Same columns and layout as Table 2.

| | Logit OLS | Logit IV | BLP IV | BLP IV |
|---|---|---|---|---|
| Panel A (index) Expense ratio | -1.317 | -7.503 | -6.934 | -5.343 |
| Panel A Expense ratio x Broad-based | 0.695 | -5.278 | -6.186 | -6.080 |
| Panel A avg own-price elasticity | -0.285 | -2.858 | -2.346 | -2.341 |
| Panel B (leveraged) Expense ratio | -2.019 | -3.737 | -6.780 | -6.279 |
| Panel B Expense ratio x Broad-based | -0.142 | 0.179 | 0.512 | 0.555 |
| Panel B avg own-price elasticity | -2.694 | -4.904 | -5.921 | -6.024 |

Panel A IV: the broad-based interaction is large and negative (the sum of the two terms is about -12.8 in logit IV), so broad-based funds (where the Vanguard / SPDR / iShares core funds sit) get a much larger price coefficient than in Table 2. That is the lever already found to raise their elasticities; the two Oct2026 notebooks do not contain the interaction, but the two `*_broadspecial.ipynb` notebooks in `code/` do (column `broad_specialized` in the data). A first task is to rerun the index one, confirm A7 Panel A, and then compute the Table 5 Panel A elasticities from it. These two notebooks are older (May 2026) than the Oct2026 ones, so check that their sample filters and IVs agree with Table 2 before comparing.

## Not available in this folder

- Table 5 and A3 are built in R from the per-market elasticity CSVs (`code/R_table5/`). Those CSVs and the R scripts that build the panel are not here.
- Table 2 col (1) Logit OLS code.
- The coauthor's reported per-market elasticity CSVs (`elasticity_outputs`, 6.0 GB; `elasticity_outputs_broad`, 3.0 GB) stay in Dropbox `P16_LeverageMKT\Code\python\`.
- The LaTeX sources are at `C:\Users\zlu15\Dropbox\Apps\Overleaf\Leveraged ETF\` (not copied).
