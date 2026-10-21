# Table 2 replication: results

Branch `leveraged-etf-replication`. Format: **replicated** vs *(paper)*; clustered SE in parentheses.
Environment: `requirements.txt` installed as pinned (pyblp 1.3.0, pyRVtest 0.3.2, numpy 2.4.1, pandas 2.2.3, scipy 1.17.1; no package changed or failed). Python 3.11.17 here, 3.11.14 pinned. 4 cores, 15 GB RAM.
Data: the two CSVs from the Dropbox folder. SHA-256: LETF `67306b40…bf85`, non-leveraged `0c4f32ca…c22`. These were not compared with the coauthor's local hashes.
Method: notebook cells run unmodified, in order, in one namespace (cells 2-9, 12-18, 24-26 leveraged; 2-9, 12-18, 23-25 index), seed 623543, BFGS gtol 1e-7. Column (1) from `code/table2_logit_ols.py`. Conduct-test, export and counterfactual cells were not run. Cell numbers in the index notebook are one lower than the map in `EXPECTED_RESULTS.md` for BLP 3 RC (cell 24, not 25).

**Status: all 16 cells filled. Panel A column (4) was not produced by the unmodified notebook cell; see "Panel A column (4)" at the end.**

## Panel A: Passive index funds (N = 108,300 replicated; 166 markets)

| | (1) Logit OLS | (2) Logit IV | (3) BLP, 1 RC | (4) BLP, 3 RC |
|---|---|---|---|---|
| Expense ratio | -0.938 (0.045) *(-0.938 (0.046))* | -5.606 (1.310) *(-5.606 (0.131))* | -6.771 (0.837) *(-6.771 (0.736))* | -8.348 (1.567) *(-8.348 (1.563))* |
| Past 1-yr return | 0.413 (0.037) *(0.413 (0.037))* | 0.413 (0.034) *(0.413 (0.034))* | 0.414 (0.034) *(0.414 (0.014))* | 0.387 (0.037) *(0.387 (0.028))* |
| Age (log) | 0.546 (0.012) *(0.546 (0.012))* | 0.573 (0.011) *(0.573 (0.011))* | 0.580 (0.010) *(0.580 (0.011))* | 0.594 (0.039) *(0.594 (0.049))* |
| Tracking error | -0.231 (0.039) *(-0.231 (0.039))* | -0.451 (0.066) *(-0.451 (0.066))* | -0.505 (0.074) *(-0.505 (0.062))* | -0.544 (0.091) *(-0.544 (0.095))* |
| RC sd, expense ratio | | | 0.027 (0.013) *(0.027 (0.011))* | -0.006 (36.694) *(-0.008 (38.559))* |
| RC sd, past return | | | | 0.008 (4.575) *(-0.009 (4.872))* |
| RC sd, age | | | | 0.001 (34.587) *(0.001 (30.556))* |
| Avg own-price elasticity | -0.270 market mean / -0.268 obs. mean *(-0.268)* | -1.614 *(-1.614)* | -1.950 *(-1.950)* | -2.404 *(-2.404)* |

Runtime: logit IV, seconds; BLP 1 RC 44.6 min (optimizer converged, 4 iterations).

## Panel B: Passive leveraged funds (N = 15,401 replicated; 177 markets)

| | (1) Logit OLS | (2) Logit IV | (3) BLP, 1 RC | (4) BLP, 3 RC |
|---|---|---|---|---|
| Expense ratio | -2.024 (0.098) *(-2.024 (0.098))* | -3.712 (0.328) *(-3.712 (0.328))* | -6.484 (0.072) *(-6.484 (0.079))* | -6.141 (1.033) *(-6.141 (0.688))* |
| Past 1-yr return | 0.259 (0.036) *(0.259 (0.037))* | 0.255 (0.036) *(0.255 (0.040))* | 0.261 (0.037) *(0.261 (0.029))* | 0.244 (0.057) *(0.244 (0.041))* |
| Age (log) | 0.658 (0.038) *(0.658 (0.038))* | 0.706 (0.040) *(0.706 (0.040))* | 0.779 (0.045) *(0.779 (0.031))* | 0.785 (0.190) *(0.785 (0.100))* |
| Tracking error | -1.183 (0.223) *(-1.183 (0.224))* | -1.376 (0.247) *(-1.376 (0.247))* | -1.546 (0.264) *(-1.546 (0.239))* | -1.644 (0.294) *(-1.644 (0.252))* |
| RC sd, expense ratio | | | 2.084 (0.102) *(2.084 (0.112))* | 1.813 (0.476) *(1.813 (0.314))* |
| RC sd, past return | | | | -0.095 (0.127) *(-0.095 (0.077))* |
| RC sd, age | | | | -0.075 (1.318) *(-0.075 (0.717))* |
| Avg own-price elasticity | -2.667 market mean / -2.683 obs. mean *(-2.684)* | -4.892 *(-4.892)* | -5.911 *(-5.911)* | -5.953 *(-5.953)* |

Runtime: logit, under 1 s; BLP 1 RC 27.2 min (optimizer **not** converged by pyblp's flag: 5 iterations, gradient norm 1.9e-7 vs gtol 1e-7); BLP 3 RC 29.4 min (converged, 24 iterations).

## Cell by cell

**Matches (all coefficients and elasticities to the third decimal):** every point estimate in every finished column, and every average elasticity except as noted below. N matches in both panels (108,300 and 15,401), so the Bull-only filter in the leveraged notebook is what the table uses.

**Standard errors that do not match:**

| Cell | Replicated | Paper | Note |
|---|---|---|---|
| Panel A (2), expense ratio | 1.310 | 0.131 | exactly 10x; the other three SEs match. Looks like a decimal slip in the table; not checked against the LaTeX |
| Panel B (2), past return | 0.0359 | 0.040 | robust, unadjusted and product-clustered SEs do not reproduce 0.040 either (tested) |
| Panel A (3), past return | 0.0335 | 0.014 | |
| Panel A (3), tracking error | 0.0743 | 0.062 | |
| Panel A (3), expense ratio | 0.837 | 0.736 | |
| Panel B (3), all five | 0.072, 0.264, 0.037, 0.045, 0.102 | 0.079, 0.239, 0.029, 0.031, 0.112 | |
| Panel B (4), all seven | 1.033, 0.294, 0.057, 0.190, 0.476, 0.127, 1.318 | 0.688, 0.252, 0.041, 0.100, 0.314, 0.077, 0.717 | mine are 1.2x to 1.9x larger |

For the BLP columns the point estimates agree to three decimals but the SEs do not. The covariance matrix is close to singular in these runs (covariance condition numbers 1e17 to 1e18), so SEs are numerically fragile. I did **not** test whether that explains the differences, so treat it as a possibility, not a finding. BLP SEs are expected to differ more according to the task note.

**Average elasticity definition (column 1).** `extract_diagonal_means` returns one mean per market (177 values in Panel B, 166 in Panel A), which the notebooks average with equal weight per market. That definition reproduces the paper's columns (2) to (4). For column (1) it gives -2.667 (B) and -0.270 (A); averaging over all observations gives -2.683 (B) and -0.2675 (A), which matches the paper's -2.684 and -0.268. In Panel B the same observation-level average for logit IV would be -4.921, not the paper's -4.892. So column (1) in the paper appears to be averaged over observations while columns (2) to (4) are averaged over markets. I only checked which definition matches each number, not how the paper's table was built.

**Column (1) code.** `code/table2_logit_ols.py` (new). Two routes, pyblp with the price as its own instrument and `pyhdfe` plus `statsmodels`, agree on all coefficients. SEs differ in the fourth decimal (statsmodels applies a small-sample correction).

## Panel A column (4): how it was obtained, and a caveat

The unmodified notebook run of this cell (single process) was killed by a container restart after about 80 minutes, with no result. I then wrote `code/solve_rc3_resumable.py`: it runs the notebook's own data-prep cells unmodified and the same formulation, Monte Carlo integration (3000 draws, seed 623543), BFGS with gtol 1e-7 and clustered SE, but spreads the markets over worker processes (`pyblp.parallel`, which does not change the numbers) and writes every objective evaluation to a JSON checkpoint so a restart can resume.

*Limitation of the resume logic.* The checkpoint holds evaluations from both GMM steps, and resuming starts from the lowest objective regardless of step; this worked on the Panel B test but is not guaranteed in general.

*Validation.* On Panel B column (4) the script, killed after 12 evaluations and resumed from its checkpoint, reproduced the uninterrupted notebook run to about 10 digits: objective 90.288, price -6.1413 (1.0325), sigma(price) 1.8126, elasticity -5.953273832 in both.

*Panel A.* The BFGS run reached the point sigma = (-0.00575, 0.00117, 0.00817) with objective 89.98928 after 19 evaluations. The next 24 evaluations moved the parameters by about 1e-9 and the objective by about 1e-13 (floating-point noise), so the line search could not satisfy gtol 1e-7 and kept retrying. I stopped it after about 2 hours 8 minutes and computed the full results at that point with the optimizer set to return its starting value (`FINALIZE=1`).

**Caveat.** pyblp's two-step GMM optimizes twice. From the objective values the run appears to have stalled in step 1 (89.99 at the stall, 130.6 at the same point after the weighting matrix is updated), so step 2 was never reached, and the numbers above are the step-1 optimum with the step-2 weighting matrix applied and no second optimization (reported projected gradient norm 0.069, not below 1e-7). The coefficients and the elasticity agree with the paper to the third decimal, and the random-coefficient sds are near zero and not identified (SEs 4.6 to 36.7), so I expect a second optimization to change little. I did not run it. The sign of a random-coefficient sd is not identified, so the paper's -0.009 for past return versus my +0.008 is not a discrepancy; the magnitudes differ in the third decimal.

SEs against the paper: expense ratio 1.567 vs 1.563 (close); past return 0.037 vs 0.028, age 0.039 vs 0.049, tracking 0.091 vs 0.095. Runtime of the final step: 34.8 minutes on 4 processes; 43 optimizer evaluations over 2 h 8 min on 3 processes before it was stopped.

## Files
- `code/table2_logit_ols.py`, `code/solve_rc3_resumable.py` (written to run the notebook prep cells, then the 3-RC solve, in parallel and resumable), `logs/` (condensed notebook output, OLS output, Panel A column (4) final output and checkpoint, Panel B resume validation; wide data-frame prints removed).
- Notebooks and data were not modified.
