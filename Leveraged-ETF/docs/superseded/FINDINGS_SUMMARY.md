# Leveraged ETF: replication and demand-specification findings

Cloud session working notes, branch `leveraged-etf-replication` (repo `zlu15-cbs/cloud_claude`, folder `Leveraged-ETF/`). Every number below comes from a script in `code/` or `code/explore/`, with its log in `logs/`. Statements marked *inference* are my reading, not something I ran. The paper's numbers were never changed.

Detailed companion files:
- `RESULTS_table2.md`: Table 2 replication.
- `EXPLORATION_price_heterogeneity.md`: the first exploration round.
- `logs/explore/*.csv`: every result table.

---

## 1. Summary

1. **Table 2 replicates.**
   - All 16 columns match the paper's point estimates and average elasticities to three decimals.
   - Many standard errors do not match. That includes one apparent decimal slip in the paper (Panel A col 2 price SE: 1.310 here, 0.131 in the paper).
2. **Table 5 is internally consistent, but its labels are wrong.**
   - The "Elasticity" column is the 3-RC price coefficient × p × (1 − s) in each fund's **last month**.
   - The "Bertrand" column is a **markup level in percentage points** (p − mc), averaged over the sample. It is not a Lerner index.
   - Together the two columns say the cheapest funds price **below marginal cost** (Lerner > 1). They do not contradict each other.
   - Two Vanguard rows are swapped.
3. **Interacting price with fund characteristics does not reliably lift the large index funds above |e| = 1.** That includes broad-based, ETF, Big 3, firm, share class, asset class, AUM and market state. Each one either leaves most of the 15 Table 5 funds below 1 or produces upward-sloping demand for part of the sample.
4. **What works best within the linear-in-fee model: a fee tier set at the fund's first month in the full raw data.**
   - A fund is "cheap" if its fee then was at or below that month's 20th percentile across all index funds.
   - In logit IV, the cheap group's price coefficient is about −41 against −8 for the rest (F = 18). 11 of the 15 Table 5 funds go above |e| = 1, and negative implied marginal costs fall from 52% to 13% of fund-months.
   - **Caveats.** The cheap group's coefficient is robust, to the cutoff and to dropping any one firm. The non-cheap slope is imprecise. The result depends on computing the percentile cutoffs over all raw funds.
   - **BLP:** no credible one-RC version exists with the available instruments. The notebook's extra index instrument conflicts with the Hausman IV once the interaction is added. See section 6 and `Table2_alt.md`.
5. **`Table2_alt.md`: Table 2 with the interaction.**
   - Logit IV at the 10th, 15th and 20th percentiles lifts 10, 14 and 11 of the 15 funds above 1.
   - One-RC BLP: σ is not identified once the interaction enters (flat objective; the paper's σ = 0.027 not rejected, J p = 0.088); every estimator that lets σ float gives upward-sloping demand for non-cheap funds. A column with σ fixed at the paper's 0.027 is reported as a sensitivity exhibit only; it is numerically the logit IV column (section 6).
   - Table A7 col (3) in the 26-Sep notebook is this same design and re-runs exactly (β −6.934, σ 2.25); my earlier "unsaved run" conclusion is withdrawn. It lifts only 2 of the 15 Table 5 funds above 1.
   - The published leveraged Table 2 col 3 instruments also fail an overidentification test (J = 14.2, p < 0.001).
6. **Log price is the most robust way to lift the elasticities, but it leaves the linear specification.**
   - Logit IV: every fund-month is above |e| = 1, with F = 824 and 3% negative marginal cost.
   - The BLP random coefficient on log price is not identified, even with stronger instruments.
7. **Data issues to fix.**
   - SPY's fee is recorded as 0.04% from Oct 2022 to Sep 2023 (actual 0.0945%).
   - 43 temporary fee changes in 39 funds, at least two of them likely typos.
   - Zero-fee funds are dropped by the sample filter.
   - The two panels end in different months.

---

## 2. Table 2 replication *(run; `RESULTS_table2.md`, `logs/panel*`)*

- **Environment.** `requirements.txt` installed exactly as pinned (pyblp 1.3.0, pyRVtest 0.3.2). Python 3.11.17 here, 3.11.14 pinned.
- **Samples.** N = 108,300 (index, 166 months) and 15,401 (leveraged, 177 months). The leveraged notebook's **Bull-only** filter is what Table 2 uses; the paper's note does not say so.
- **Point estimates and average elasticities.** All columns match to three decimals.
- **Standard errors that do not match:**

| Cell | Replicated | Paper | Note |
|---|---|---|---|
| Panel A col 2, expense ratio | 1.310 | 0.131 | exactly 10×; probably a decimal slip in the paper |
| Panel B col 2, past return | 0.0359 | 0.040 | not reproduced by robust, unadjusted or product-clustered SEs |
| BLP columns (A3, B3, B4) | mostly 1.2–1.9× the paper | | covariance matrices near singular; cause not established |

- **Column (1) elasticities.** The paper's column (1) values match the **observation-level** mean. Columns (2)–(4) match the **per-market** mean (pyblp's `extract_diagonal_means`). So column (1) uses a different definition from the rest.
- **Convergence.**
  - Panel B col 3 is flagged "not converged" (gradient 1.9e-7 against gtol 1e-7). Its estimates still match.
  - The coauthors report a rank-deficient covariance in the 3-RC model and are reworking it, so 3-RC was not explored further.
- **Panel A col 4.** A container restart killed the notebook run, so it was finished with a parallel, checkpointed script (`code/solve_rc3_resumable.py`). That script was validated against Panel B col 4 to about 10 digits. The final numbers are a step-1 optimum evaluated with step-2 weights; details in `RESULTS_table2.md`.

## 3. Table 5 *(run; `logs/explore_step1*`, coauthor R in `code/R_table5/`)*

- **Elasticity column.** It equals −8.348 × p × (1 − s) in each fund's last sample month (Aug 2024), for all 15 funds, to within 0.0005.
  - That is the Table 2 col 4 (3-RC) price coefficient. With σ ≈ 0, 3-RC is effectively logit.
  - Logit IV (−5.606) and BLP 1-RC do not reproduce it.
- **"Bertrand" (and Cournot, Monopoly) columns.** The R averages pyRVtest's `markups` over the sample. Those are levels in percentage points: notebook cell 34 labels them "Price minus Marginal Cost in Percentage Points per Annum", and cell 33 computes Lerner separately as markup / price.
  - So a 0.22 markup on a fund charging 0.02–0.04% means marginal cost of about −0.19 percentage points.
  - The two columns are consistent with each other. Both say Lerner > 1 for the cheapest funds.
- **Labels.**
  - In the data, the 430,969 AUM fund is VTI's **ETF** class (p = 0.03) and the 395,578 fund is the **Admiral** class (p = 0.04). Table 5 has them the other way round.
  - The note "averaged over the entire sample period" is true for the markups only. The elasticity is last-month only.

## 4. Data facts and issues *(run)*

- **Sample periods.**
  - Index: raw Jan 1994 – Dec 2025; estimation **Jan 2010 – Aug 2024**.
  - Leveraged: raw Jan 2007 – Sep 2024; estimation **Jan 2010 – Sep 2024**.
  - The panels end a month apart.
- **Index sample.**
  - Shares are tiny: median 0.037%, max 4.97%. So 1 − s ≥ 0.95, and the logit own elasticity is essentially α·p.
  - Median fee 0.20%, 5th percentile 0.04%.
  - Only 3.75% of fee variance is within fund, which is what identifies α once fund FE are absorbed.
- **Zero-fee funds** (e.g. Fidelity's) are dropped by the notebook's `prices > 0` filter, so they sit in the outside option.
- **SPY's fee** is recorded as **0.04% from Oct 2022 to Sep 2023**; it was 0.0945% throughout.
  - Correcting it changes the tier estimates only in the third decimal (`logs/explore_step8_raw20_robustness.log`).
  - It is still worth fixing at the source.
- **Temporary fee changes.** Fee changes of at least 0.02 pp that revert to the exact prior fee within 12 months: 43 episodes in 39 funds, 0.5% of fund-months (`logs/explore/step8_fee_reversals.csv`).
  - Likely typos: Vanguard Long-Term Bond Index Institutional (0.04 → 0.40 → 0.04) and BNY Mellon Institutional S&P 500 (0.20 → 0.50 → 0.20).
  - Most others last exactly 12 months (iShares country ETFs 0.49 → 0.47 → 0.49), which suggests annual prospectus updates or temporary waivers.
- **SPY's and VTI's fee percentile** in each month's index-fund cross-section (`logs/explore/fee_percentiles_spy_vti.csv`):
  - SPY's fee never changed (0.09%). It moved from the 6th–8th percentile in 2010 to the 43rd–48th in 2024 because the market got cheaper around it.
  - VTI cut from 0.06% to 0.03% and stayed in the 2nd–10th percentile.
- **Variable notes.**
  - `market_m_cluster` is an index cluster (313 codes), not an asset class.
  - `csent_index_resid` and `chg_VIX_resid` vary within a month, so month FE do not absorb them.
- **"First month" in the sample is mostly not the fund's launch.**
  - 43% of funds enter in Jan 2010 (the window start).
  - 43% enter later than their first raw month, mostly when they pass the share ≥ 0.01% filter.
  - 15% enter at their first raw month.

## 5. Heterogeneity in the price loading: what was tried

Throughout: logit IV, Table 2 Panel A sample, notebook controls, fund and month FE, SE clustered by month. Each p × z term is instrumented with Hausman IV × z. "Table 5 > 1" counts the 15 Table 5 funds with |e| > 1 in their last month.

Why this is hard in a linear-in-fee model: |e| = 1 at p = 0.03% needs a coefficient of about −33, and −25 to −52 across the 2–4 basis point funds. The pooled estimate is −5.6 (logit IV) to −8.3 (3-RC).

### 5a. Does not work

| Interaction | Result | Problem |
|---|---|---|
| Broad-based (the paper's A7) | reproduces A7 exactly (−7.50, −5.28); 2 of 15 | too small |
| Broad-based, with the raw-entry tier included | broad × price = −0.02 (SE 1.2) | adds nothing; A7's effect looks like a fee-level proxy *(inference)* |
| ETF vs mutual fund; Big 3; firm dummies | 1–2 of 15 | too small |
| Share class (institutional/Admiral, retail, other MF, ETF; parsed from names) | institutional −11.2, ETF −9.2, retail −7.4; 2 of 15 | 12 of the 15 are ETFs |
| Asset class (5 groups) | 1 of 15 | 39% of fund-months slope upward |
| AUM tercile at first sample month | 2 of 15 | 67% slope upward |
| Price squared | 7 of 15 | 9% slope upward |
| Market state (sentiment, VIX) | interaction ≈ 0 | no effect |
| AUM tercile lagged 12 months | 1 of 15 | fails exogeneity (lead-test t −58 to −81; ξ̂ AR(1) 0.98) |
| Rolling "cheap" status (monthly percentile, 6/12-month entry and exit) | 3 of 15 | lead tests fail (t −15 to −17); status responds to past demand shocks |
| Percentile of the fee 12 months earlier (raw-file cross-section; `explore_step16*`) | continuous: 2 of 15; ≤ 20th pct indicator: 7 of 15 | continuous version is ≈ price × rank(price) (corr 0.92): slope turns positive above the 54th percentile, 46% slope upward; ≤ 10th / 15th indicators have weak first stages (F 11 / 1.6); ≤ 20th gives cheap slope −23.5 vs −40.8 for the entry tier and fails lead tests (t −4 to −10). Details in `Table2_alt.md` |
| Fee tier at first **sample** month, by rank | looked good | ties: 67 funds at exactly 0.20% split arbitrarily by row order |
| Fee tier at first sample month, by fee cutoff (0.05–0.25%) | 4–15 of 15 | first stage collapses at 0.15–0.18%; very sensitive to the cutoff |
| BLP, normal random coefficient, with any fee-tier interaction | | mean price coefficient turns **positive** for the non-cheap group (+1.8 to +9.5) |

### 5b. Works best within the linear model: raw-entry fee tier *(run; `logs/explore_step2g*`, `logs/explore_step8*`)*

Definition: each month of the raw data (1994–2025), compute fee percentiles across all index funds with a recorded fee. A fund is cheap if its fee in its **first raw month** was at or below that month's q-th percentile.
- 54% of sample funds have a first raw month before 2010; the median is 2009.
- The tier is fixed per fund, so fund FE absorb its level.
- It does not depend on the sample's share filter.

| Cutoff | Funds cheap | Rest (SE) | Cheap | Weakest F | Table 5 > 1 | Avg e | Neg. MC |
|---|---|---|---|---|---|---|---|
| 10th pct | 20% | −6.2 (5.2) | −68.6 | 11.2 | 10 | −3.18 | 31% |
| 15th pct | 31% | −16.0 (8.2) | −61.1 | 10.9 | 14 | −6.27 | 5% |
| **20th pct** | **39%** | **−8.1 (4.3)** | **−40.8** | **18.3** | **11** | **−3.93** | **13%** |
| 25th pct | 45% | −6.5 (3.4) | −30.1 | 34.9 | 9 | −3.27 | 14% |
| 30th pct | 50% | −3.4 (2.6) | −22.3 | 39.6 | 7 | −2.29 | 24% |
| 40th / 50th pct | 62% / 73% | **+2.7 / +10.7** | −17.9 / −11.3 | ~40 | 6 / 2 | | demand slopes upward for the rest |
| *Paper's model (logit IV)* | | −5.6 (1.3) | | 33.6 | 2 | −1.61 | 52% |

Robustness of the 20th-percentile spec:
- **Holds.**
  - Correcting SPY's fee error: no change.
  - Dropping State Street (−6.3 / −41.1, F 18) or BlackRock (−12.9 / −69.8, F 12).
  - Adding the broad-based interaction: no change.
  - The **cheap** coefficient moves smoothly with the cutoff (−69, −61, −41, −30, −22 from the 10th to the 30th percentile), with F ≥ 10.9 throughout. This is much better than the sample-first-month versions.
  - The **non-cheap** coefficient is not smooth and is imprecise everywhere: −6.2, −16.0, −8.1, −6.5, −3.4 (SEs 2.6–8.2), then positive at the 40th and 50th percentiles.
- **Fails.**
  - **Dropping Vanguard:** the rest coefficient becomes **+6.2 (SE 1.2)** and 67% of fund-months get positive own elasticities. The non-cheap slope is identified mainly from Vanguard funds' fee changes; Vanguard is about a quarter of the sample's fund-months.
  - The cheap coefficient survives dropping Vanguard (total −22.4, F 73). So the robust part is the *gap*: cheap funds respond far more to fees than the rest. The fragile part is the level and sign of the non-cheap slope. Most Table 5 funds are cheap, so their elasticities rest on the robust coefficient. The 60% of fund-months outside the cheap group rest on the fragile one.
  - **Cutoffs computed among sample funds only:** F falls to 4.5. The definition needs the full raw population.
- **Interpretation** *(inference)*. The data consistently want a much steeper fee slope for low-fee funds: the cheap coefficient is 4–11 times the rest's at every cutoff. That is a feature of the demand curve's shape, which log price captures with one parameter. The tier is a linear approximation of it, and its exact size depends on the cutoff.

### 5c. Log price (functional form) *(run; `logs/explore_step2_screen.log`, `explore_step4_blp_B1.log`, `explore_step5*`, `explore_step6*`)*

- **Logit IV, utility α·log(p + 0.01):**
  - α = −2.69 (0.08), F = 824.
  - All 15 Table 5 funds between −1.7 and −2.6; no upward-sloping demand; 3% negative marginal cost.
  - Little change for c = 0.005 or 0.02.
- **BLP, normal random coefficient on log price:** σ = 5.9 (SE 18.5), not identified.
  - Differentiation instruments push σ to 0 in the leveraged market and fail overidentification (J = 219).
  - Optimal instruments then degenerate.
- **Leveraged market:** the average elasticity rises from −4.9 (Table 2) to −8.2 (logit IV, log price). Leveraged markups would fall *(inference)*.

### 5d. BLP experience (lessons for any heterogeneous-slope spec)

- **Normal random coefficient on price with a large σ:** many simulated consumers get a positive price coefficient. This sank every fee-tier BLP.
- **Lognormal price coefficient** (pyblp `rc_types='log'`, X2 = −price by group, means via an agent constant): keeps demand downward-sloping for everyone.
  - With a free σ for the non-cheap group, that σ diverges (to 29), and its mean coefficient goes to about 0.
  - Fixing that σ at 0 works.
- **Two-step GMM:** several runs stall in step 1 (the BFGS line search makes no progress at the optimum).
  - Evaluating step 2 at the step-1 point is not enough. In one fee-tier run the step-2 optimization moved the cheap-group median coefficient from −92 to about −24, and the non-cheap coefficient to about 0, before I stopped it (`logs/explore_step7_lognormal_fee12_b40_fixrest_step2_stopped.log`).
  - Always optimize both steps before reporting.
- **Practical:** each index-market BLP evaluation takes 1–11 minutes. The container restarted several times. All long runs now use parallel workers (`pyblp.parallel`, one BLAS thread each) and per-evaluation checkpoints.

## 6. Table2_alt, the one-RC BLP, and Table A7 col 3 *(run; `Table2_alt.md`, `RESULTS_A7_col3.md`, `logs/explore_table2_alt_*`, `explore_step10*`–`step15*`, `explore_a7_col3.log`)*

`Table2_alt.md` reports Table 2 with price × cheap added for index funds (raw-entry tier at the 10th, 15th and 20th percentiles). Leveraged funds have no interaction, per the paper's A7.

- **Logit IV with the interaction is the usable alternative:** cheap coefficient −41 to −69 against −6 to −16 for the rest, no upward-sloping demand, average elasticity −3.2 to −6.3, negative MC down to 5–31%, and 10 / 14 / 11 of the 15 Table 5 funds above |e| = 1.
- **One RC on the expense ratio: σ is not identified once the interaction is in.**
  - A profile of the GMM objective over σ (`explore_step13_sigma_profile_raw20.log`) is shallow and monotone: 3.77 at σ = 0 to 0 at σ = 6.5, with the economics breaking past σ ≈ 2 (54% upward-sloping demand at the root). The cheap slope and the Table 5 count (10–11 above 1) are stable at every σ; only the non-cheap slope moves.
  - Hansen J with efficient weighting at the paper's σ = 0.027: 2.92 on 1 df, p = 0.088. The paper's σ is not rejected.
  - Every estimator that lets σ float breaks the non-cheap funds: notebook instruments, squared Hausman, uninteracted `newproduct_3`, the A7 design (`newproduct_1` uninteracted: σ 5.6, SPDR Gold +2.0), Chamberlain optimal instruments from the Hausman IV (non-cheap +4.0), and a lognormal RC (stalls; no e > 0 but 67% negative MC). Entered alone, every extra instrument in the data implies a non-cheap slope near zero or positive, against −6 to −16 from the Hausman IV.
  - **Sensitivity exhibit, σ held at the paper's 0.027** (H, H × cheap; exactly identified): non-cheap −6.2 / −16.0 / −8.1, cheap −68.6 / −61.1 / −40.8, average elasticity −3.18 / −6.27 / −3.93, 10 / 14 / 11 of 15 above 1, no upward-sloping demand. Holding σ at a value estimated from another specification on the same data is not standard BLP practice, and with σ this small the column is numerically the logit IV column; it is shown only to document that the paper's own heterogeneity, carried over, leaves the interaction result unchanged.
- **Table A7 col 3 (26-Sep notebook, commit `f2d8bff`), corrected.** My earlier statement that the published A7 col (3) came from an unsaved two-RC run was based on the 25-May notebook and is withdrawn. The current notebook's col (3) is one RC on the expense ratio with the interaction in X1 and instruments Hausman, Hausman × broad and `BLP_IV_newproduct_1` **uninteracted** (the × broad version is built but never enters). It re-runs exactly: β −6.934 (1.295), × broad −6.186 (0.607), σ 2.2525 (0.680), average elasticity −2.346; clustered SEs 1.214 / 0.653 / 0.768. It lifts only 2 of the 15 Table 5 funds above |e| = 1. It works for broad because `newproduct_1` alone implies negative slopes for both groups there (J p = 0.045), whereas under the cheap split it implies a non-cheap slope of +2.6 / −1.0 / +0.5.
- **Data note from the A7 run.** `broad_specialized` is inconsistent for S&P 500 funds: 22.6% of SPX fund-months are "specialized", including SPY in all 166 months, SPDR Portfolio S&P 500 and VTI's ETF class, while other share classes of the same portfolios are "broad-based".
- **Leveraged instruments.** The leveraged notebook's two instruments already disagree in the published Table 2 Panel B col 3 (Hausman −3.71, `BLP_IV_rival_funds1` −5.06; J = 14.2, p < 0.001).

## 7. Recommendations and what is worth exploring next

1. **Paper fixes, whatever the model.**
   - Relabel Table 5: the markup columns are levels in percentage points, and the elasticity is last-month only.
   - Swap the two Vanguard rows.
   - Fix the Table 2 Panel A price SE (1.310).
   - Use one averaging definition across Table 2's columns.
   - State the Bull-only filter and the panels' end months.
2. **If the linear model stays as is,** say plainly that it implies Lerner > 1 (negative marginal cost) for the cheapest funds, and give a reason. Securities-lending income is the natural candidate, and could be modelled as a negative cost component.
3. **If you add fee-level heterogeneity in the linear model,** report the logit IV column from `Table2_alt.md` as the alternative model, with the 15th or 20th percentile as the main cutoff and the others as robustness, and a footnote saying a random coefficient on the expense ratio is not identified once the interaction is included (σ profile and J test). If a random-coefficient column is wanted, include the σ-fixed one only as a labelled sensitivity column. Do not report a column with σ estimated jointly with the interaction.
4. **Worth exploring:**
   - *An instrument for the random coefficient that agrees with the Hausman IV under the cheap interaction.* None of the 24 in the data does; differentiation instruments built from the Hausman IV and Chamberlain optimal instruments do not either. A cost shifter with within-fund variation is the natural candidate.
   - *The `broad_specialized` label for S&P 500 funds* (SPY coded specialized), since A7 is identified from it.
   - *Why Vanguard drives the non-cheap slope.* Which Vanguard funds changed fees, and are those changes plausibly exogenous (e.g. Vanguard's at-cost structure passing through scale economies)? A firm-specific slope for Vanguard is one way to make this explicit.
   - *Stronger instruments for any random coefficient on price* (index market): cost shifters with real within-fund variation, or the coauthors' 3-RC rework.
   - *Data cleaning:* fix SPY's fee, review the 43 temporary fee episodes, and check how expense ratios are sourced (annual prospectus values vs monthly).
   - *Zero-fee funds:* model them explicitly instead of folding them into the outside option.
   - *Leveraged market:* any functional-form change (log price) also moves the leveraged elasticities and markups, so decide on one demand model for both markets.

## 8. Files

| What | Where |
|---|---|
| Table 2 replication | `RESULTS_table2.md`, `code/table2_logit_ols.py`, `code/solve_rc3_resumable.py` |
| First exploration report | `EXPLORATION_price_heterogeneity.md` |
| Table 5 reconstruction | `code/explore/step1_table5_elasticity.py`, `step1b_formula_check.py` |
| Logit IV screen (all specs) | `code/explore/step2_logit_screen.py`, `logs/explore_step2_*.log`, `logs/explore/step2_*.csv` |
| Raw-entry tiers and robustness | `code/explore/tiers.py`, `step2g_raw_entry_tiers.py`, `step8_raw20_robustness.py` |
| Cutoff sweeps, ties, switchers | `code/explore/step2e_cutoff_sweep.py`, `step2f_switcher_composition.py` |
| BLP (normal and lognormal) | `code/explore/step4_blp_shortlist.py`, `step6_logp_blp_strong_iv.py`, `step7_lognormal_two_group.py` |
| Fee percentiles, SPY/VTI | `code/explore/fee_percentiles_spy_vti.py` |
| Table 2 with the interaction | `Table2_alt.md`, `code/explore/table2_alt_logit.py`, `step4_blp_shortlist.py`, `step9_lognormal_1rc.py`, `make_table2_alt.py` |
| Instrument conflict checks | `code/explore/step10_instrument_check.py`, `step10b_instrument_check_baseline.py` |
| σ identification (profile, J at fixed σ, calibrated σ) | `code/explore/step13_sigma_profile.py` |
| Instrument screens, differentiation and optimal IVs | `code/explore/step12_iv_screen.py`, `step12b_iv_screen_uninteracted.py`, `step14_diff_iv_screen.py`, `step15_optimal_iv.py` |
| Table A7 col 3 re-run | `RESULTS_A7_col3.md`, `code/explore/a7_col3.py` |
| Lagged-fee percentile interaction | `code/explore/step16_lagfee_pct.py`, `logs/explore_step16_lagfee_pct.log`, `logs/explore/step16_*.csv`; section in `Table2_alt.md` |
