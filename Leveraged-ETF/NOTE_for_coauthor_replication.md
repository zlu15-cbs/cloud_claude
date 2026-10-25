# Note for coauthor: recommended demand specification, how to replicate it, and data issues to clean

This note accompanies the code in this bundle (code and documents only; no data). It covers four things:

1. The demand specification we recommend for the index market (Table 2 Panel A), defined exactly.
2. How to reproduce every number on a local machine.
3. The diagnostics behind the change of instrument, with the exact procedures.
4. The data issues found along the way, and the scripts that list the affected rows.

The full write-up is `MAIN_REPORT_sharecl_hausman.md` (included). None of the paper's own numbers or notebooks were changed.

---

## 1. The recommended demand model

**Sample.** Start from the Table 2 Panel A estimation sample: notebook `main_Danny_Oct2026_index_market.ipynb`, cells 2–4, run unmodified. That gives 108,300 fund-months and 1,302 funds, Jan 2010 – Aug 2024, with markets = months. Keep the fund-months that have a family identifier (`firm_f_old` non-missing) and where the instrument below is defined. That leaves **97,429 fund-months and 1,164 funds**, including all 15 Table 5 funds.

**Dependent variable.** δ_jt = ln s_jt − ln s_0t (logit inversion; s_0t = 1 − Σ inside shares in month t).

**Mean utility.**

    δ_jt = α · p_jt + α_c · (p_jt × cheap_j) + β₁ · tracking error_jt + β₂ · past 1-yr return_jt + β₃ · log age_jt + fund FE + month FE + ξ_jt

- p is `prices` (the expense ratio, in percent).
- Variant: replace month FE with month × asset-class FE.

**Cheap.** cheap_j = 1 if fund j's expense ratio in its **first month in the full raw file** (1994–2025, before any sample filter) is at or below that month's **20th percentile** of expense ratios across all index funds with a recorded fee; ties count as cheap. It is fixed per fund. Code: `tiers.raw_entry_tiers`. The 10th and 15th percentiles are robustness checks.

**Instrument (replaces `BLP_IV_hausman_exp_ratio`).** For fund j in month t:

    Z_jt = median expense ratio of the funds k in the raw file with the same family (`firm_f_old`) as j, the same share class as j, a different asset class from j, and recorded in month t.

- *Share class* is parsed from the fund name. ETF if `ETF_ind == 1`. Otherwise *institutional* if the name contains "institutional", "inst", "class I/K/Y/Z/R6", "premier", "select" or "admiral". Otherwise *retail* if it contains "investor", "retail", "class A/C/R/T", "service" or "advisor". Otherwise *other mutual fund*. Code: `new_iv.share_class`.
- *Asset class* is assigned **per tracked index** (`market_m_index`), so every share class of a portfolio, and every fund tracking the same index, gets the same class. There are five classes: US equity, international equity, bonds, allocation, real assets.
    - The 18 large `market_m_cluster` codes are mapped directly.
    - Other indices are classified from keywords in fund names and index codes, using the most common fund-level class among the funds tracking the index.
    - Code: `asset_class.classify_by_index`.
- Coverage: the median value is computed from 35 funds; 2% of values come from a single fund. The correlation with the paper's Hausman IV is 0.83.

**Estimation.**

- Logit IV in pyblp 1.3.0: `pyblp.Problem(pyblp.Formulation('prices + I(prices*cheap) + product_tracking_err + product_past_1yr_ret + log_product_fund_age', absorb='C(product_ids) + C(market_ids)'), data).solve(se_type='clustered')`.
- Excluded instruments: `demand_instruments0 = Z` and `demand_instruments1 = Z × cheap`. That is exactly identified.
- SE clustered by month, using the notebook's `clustering_ids`.
- First-stage F is the cluster-robust Sanderson–Windmeijer F.
- The average elasticity is the per-market mean of own elasticities (`extract_diagonal_means`), as in Table 2.

**Results (20th percentile).**

| | Non-cheap α (SE) | Cheap α + α_c | First-stage F | Avg own elasticity | Table 5 funds with \|e\| > 1 |
|---|---|---|---|---|---|
| Fund + month FE | −6.12 (0.85) | −28.77 | 166.6 | −2.68 | 7 / 15 |
| Fund + month × asset class FE | −3.80 (0.66) | −24.04 | 262.1 | −1.96 | 5 / 15 |
| *Paper's Table 2 col 2 (all 108,300 rows)* | *−5.61 (1.31)* | | *33.6* | *−1.61* | *2 / 15* |

**BLP version (Table 2 col 3 analogue).**

- Model: X2 = `0 + prices` (one random coefficient on the expense ratio) with the same X1. Monte Carlo integration, 3000 draws, seed 623543. BFGS, gtol 1e-7. SE clustered by month.
- Instruments: Z, Z × cheap, and **Z²** as the extra instrument for σ.
- Why Z²: the paper's `BLP_IV_newproduct_1` sends σ toward large values with upward-sloping demand, and a differentiation instrument conflicts with Z.
- Baseline result: σ = 1.81 (0.24); non-cheap mean −4.22 (0.59); cheap total −26.26; average elasticity −1.90; 7 of 15 Table 5 funds above 1; 0.02% of fund-months upward-sloping.

**BLP robustness.** One warning first: σ is **not credibly identified**, so the BLP version is a sensitivity check and the logit IV is the recommended column.

| BLP variant (20th percentile unless noted) | σ (SE) | Non-cheap (SE) | Cheap total | Avg e | Share e > 0 | Neg. MC | Table 5 > 1 | Objective at optimum | Covariance matrix |
|---|---|---|---|---|---|---|---|---|---|
| **1-step, Z² (baseline)** | 1.81 (0.24*) | −4.22 (0.59) | −26.3 | −1.90 | 0.0002 | 0.35 | 7 | 2.11, no root | singular |
| 2-step (clustered efficient W), Z² | 1.81 (0.24*) | −4.75 (0.53) | −26.8 | −2.03 | 0 | 0.31 | 7 | 5.25, no root | singular |
| 1-step, Z², 10th percentile | 0.07 (0.04*) | −8.45 (0.49) | −35.7 | −2.76 | 0 | 0.29 | 9 | 2.21, no root | singular |
| 1-step, Z², 15th percentile | 1.82 (0.42*) | −8.74 (0.43) | −34.2 | −2.91 | 0 | 0.20 | 10 | 0.35, no root | singular |
| 1-step, Z², fund + month × asset class FE | 6.30 (3.77) | −5.62 (2.11) | −30.8 | −0.86 | **0.30** | 0.37 | 6 (1 positive) | 0, root | regular (4e5) |
| 2-step, Z² + `newproduct_1` (overidentified) | 11.22 (4.26) | −7.52 (1.52) | −46.7 | −0.12 | **0.39** | 0.20 | 12 (1 positive) | J = 1.11, p = 0.29 | regular (4e5) |
| 2-step, Z² + Z³ (overidentified) | −0.11 (14.9) | −5.07 (0.53) | −26.5 | −2.35 | 0 | 0.28 | 7 | J = 8.53, **p = 0.004** | regular; reduced Hessian 0 |

\* Not a valid standard error: the Jacobian of the moments is singular at the optimum (see below).

- **Why the covariance is singular.** The baseline is exactly identified (six moments, six parameters) but stops at a non-zero objective with a zero gradient. That can happen only where the Jacobian of the moments is singular. The covariance's smallest eigenvalue is 2.5e-12, in the direction of σ against the two price coefficients. So σ = 1.81 is not a root, and its SE is not valid.
- **The paper's Table 2 col (3) has the same issue.** It is exactly identified with the Hausman IV and `newproduct_1`, ends at objective 0.576 with a zero gradient, and pyblp reports a covariance condition number of 2.4e17. Its σ SE of 0.013 is affected the same way.
- **Overidentification does not rescue σ.** With one extra instrument the covariance is regular, but σ goes to 11 (39% upward-sloping, with `newproduct_1`) or to 0 (J p = 0.004, with Z³).
- **What is stable.** Across the variants with downward-sloping demand: non-cheap −4 to −9, cheap total −26 to −36, and 7–10 of 15 Table 5 funds above 1.
- **To reproduce:**
    - Baseline: `python step26_blp_newiv.py estimate 2 zsq 2.0`.
    - Two-step: prefix `METHOD=2s`.
    - Cutoffs: prefix `CUTOFF=10` or `CUTOFF=15`.
    - Asset-class × month FE: prefix `FE=ac`.
    - Overidentified: use `zsq+np1` or `zsq+z3` with `METHOD=2s`.
    - Each run writes `step26_estimate_<tag>.csv`, `_funds.csv` and the covariance diagnostics `step26_cov_<tag>.csv` / `step26_coveig_<tag>.csv`.

**Nested logit (sensitivity check).** Nests are the tracked index (`market_m_index`). The within-index share ln s_{j|g} is instrumented by the log number of funds tracking the same index (or that count 12 months earlier, or `BLP_IV_rival_funds1` and `BLP_IV_newproduct_1`); the price instruments are Z and Z × cheap.

- With the new IV the non-cheap slope stays negative and no demand curve slopes upward; with the paper's IV on the same rows it is +4.0 to +6.4, with 53% of fund-months upward-sloping.
- But ρ (0.35–0.60 under month FE) absorbs much of the fee response: non-cheap −0.5 to −2.5, cheap total −17 to −21, and 41–78% of fund-months imply negative marginal cost (24% without nests).
- ρ is 0 with one slope and among non-cheap funds alone (whose slope is then −4.3 (0.7)), and 0.94 among cheap funds alone.
- So it is reported as a sensitivity check, not as the main column. Details: `OTHER_SPECS_explored.md` section 5c (in the repository); code `step28_nested_newiv.py`.

---

## 2. Replicating on a local machine

**Environment.** Python 3.11 and `requirements.txt` (pyblp 1.3.0, pyhdfe 0.2.0, pandas, numpy, scipy).

**Layout.** The scripts expect this structure:

```
<project>/code/main_Danny_Oct2026_index_market.ipynb      # your notebook; common.py executes its cells 2-4
<project>/code/explore/*.py                               # the scripts in this bundle
<workdir>/nonLev_funds_product_month_level_v2_patched.csv # run every script FROM a folder holding the CSV
```

`common.load('index')` executes cells 2, 3 and 4 of the notebook unmodified and returns `product_data`. The scripts read the raw CSV by bare filename (`tiers.RAW`), as the notebook does.

**Commands** (from `<workdir>`; set `PYTHONPATH=<project>/code/explore`):

| Step | Command | What it produces | Check against | Time |
|---|---|---|---|---|
| 1 | `python step25_new_iv_main.py` | Panel A table, cutoffs, drop-firm, split sample, 15 funds (`step25_*.csv`) | column (3): −6.116 (0.845), × cheap −22.655 (0.794), F 166.6 | ~10 min |
| 2 | `python step26_blp_newiv.py profile 2 zsq` | σ profile with Z² | minimum near σ = 2 (objective 2.12) | ~40 min |
| 3 | `python step26_blp_newiv.py estimate 2 zsq 2.0` | BLP estimate (`step26_estimate_zsq.csv`) | σ 1.808 (0.239), non-cheap −4.215 | ~5–60 min |
| 4 | `python step27_lead_tests.py` | lead tests (`step27_lead_tests.csv`) | table in section 3 | ~10 min |
| 5 | `python step24b_family_split.py` | Table 2 col 2 with and without a family identifier | +7.24 / +2.32 / pooled −5.61 | ~3 min |
| 6 | `python step24c_class_month_fe.py` | asset-class × month FE and the other-family placebo | `step24c_*.csv` | ~30 min |
| 7 | `python step23_hausman_reconstruct.py` | reconstruction of the paper's Hausman IV | match within 0.0005 pp in 83% of rows | ~3 min |
| 8 | `python data_issues.py` and `python step8_raw20_robustness.py` | the data-issue lists in section 4 | | ~5 min |
| 9 | `python step28_nested_newiv.py` | nested logit with tracked-index nests (`step28_*.csv`) | new IV, month FE, rivals: ρ 0.479, non-cheap −1.14, cheap total −18.00 | ~40 min |

For BLP, the second argument is the number of worker processes (`pyblp.parallel`). Set `OPENBLAS_NUM_THREADS=1`. Options are set by environment variable: `CUTOFF=10|15|20`, `METHOD=1s|2s`, `FE=month|ac`. Each evaluation is checkpointed to `step26_<tag>_ckpt.json`, so rerunning the same command resumes. `FINALIZE=1` evaluates at the best checkpointed σ.

---

## 3. Why the instrument was changed (diagnostics, with procedures)

**(a) The paper's Hausman IV, reconstructed.** For fund j in month t, `BLP_IV_hausman_exp_ratio` equals the previous-month-AUM-weighted average expense ratio of the same `firm_f_old` family's funds that track **other indices** (`market_m_index` ≠ j's), over all funds in the raw file. It matches the data column exactly wherever `firm_f_old` exists (correlation 1.000). We could not reproduce it for the 7.2% of estimation fund-months without `firm_f_old` (section 4, item 4).

**(b) Table 2's −5.6 is driven by the rows without a family identifier** (`step24b_family_split.py`):

| Sample | Price coefficient (SE) |
|---|---|
| All 108,300 fund-months (Table 2 col 2) | −5.61 (1.31) |
| 100,529 with `firm_f_old` | +7.24 (1.99) |
| 7,771 without | +2.32 (0.54) |
| All, month FE interacted with the with/without indicator | +7.64 (2.20) |

**(c) Lead tests** (`step27_lead_tests.py`). For an instrument Z, a demand model and a fixed-effect set:

1. Estimate the logit IV; ξ̂ = `res.xi`. In pyblp this is δ − Xβ̂ with the absorbed fund and time means removed (verified against a manual two-way demeaning).
2. Residualize Z on fund FE, the same time FE and the three controls (Frisch–Waugh with `pyhdfe`).
3. Index months by `month_key = round(12 × month_t)`. For k = 12, 24, 36, pair each (j, t) with the same fund's ξ̂ from t − k.
4. Demean both variables within fund over the paired sample.
5. Regress ξ̂(j, t−k) on Z̃(j, t) by OLS without a constant. Cluster by the calendar month t (no small-sample correction) and report t = b / SE.

| Instrument (97,429 rows) | Residual from | FE | t, k = 12 / 24 / 36 |
|---|---|---|---|
| paper's | one slope (Table 2 col 2) | fund + month | 6.7 / 10.7 / 20.3 |
| paper's | main (× cheap) | fund + month | −1.9 / −0.4 / 2.2 |
| paper's | main | fund + month × asset class | −4.1 / −4.0 / −3.3 |
| new | main | fund + month | −1.7 / −2.9 / −1.9 |
| new | main | fund + month × asset class | −0.1 / −0.2 / 2.1 |
| paper's, all 108,300 rows | one slope | fund + month | −3.3 / −1.5 / 2.1 |

The result depends on which model's residual is used. With the main model's residual and Table 2's fixed effects, the two instruments look similar. Under asset-class × month effects only the new one passes.

**(d) Placebo** (`step24c_class_month_fe.py`). Each family is mapped, fixed over time, to a random one of the 30 broadest other families, and the instrument is rebuilt from that family's funds; 20 draws.

- The paper's instrument with fund + month FE: placebo median first-stage F 13, against 25 for the real one.
- The new instrument with asset-class × month FE: the real F is 303, against a placebo median of 27 on samples about 40% the size. So part, not all, of its variation is family-specific.

**(e) Split sample** (`step25_new_iv_main.py`). Table 2 col 2 is run separately on cheap and non-cheap funds, each with its own fixed effects. With the paper's instrument, the non-cheap first stage is F = 0.7; with the new one it is F = 149, with a non-cheap slope of −2.4 (0.8) and a cheap slope of −47 (5).

---

## 4. Data issues to clean before the final runs

The row lists named below are not included in this bundle, which holds no data. `data_issues.py` and `step8_raw20_robustness.py` write them to the working folder.

1. **SPY's expense ratio** is recorded as **0.04% from Oct 2022 to Sep 2023** (12 months, `month_t` 2022.75 – 2023.67). The actual fee was 0.0945% throughout. List: `data_issues_spy_fee.csv` (Oct 2021 – Jun 2024). Correcting it changes the earlier cheap-tier estimates only in the third decimal, but it should be fixed at the source.
2. **43 temporary fee episodes** in 39 funds: fee changes of at least 0.02 pp that revert to the exact prior fee within 12 months (42 last exactly 12 months, 1 lasts 5). List: `step8_fee_reversals.csv`. Likely typos:
    - SPDR Portfolio Intermediate Term Corporate Bond ETF: 0.15 → **0.55** → 0.15 (from 2012.5).
    - Vanguard Long-Term Bond Index Institutional: 0.04 → **0.40** → 0.04 (from 2017.0).
    - BNY Mellon Institutional S&P 500 Stock Index: 0.20 → **0.50** → 0.20 (from 2018.75).

    Most of the rest look like annual prospectus updates or temporary waivers (iShares country ETFs 0.49 → 0.47 → 0.49). All fee changes in the file occur in January, which suggests annual prospectus values rather than monthly fees.

3. **`broad_specialized` is inconsistent within the same portfolios.** Funds tracking `market_m_index == 'SPX'` carry both labels: 51 "specialized" and 168 "broad-based", so 22.6% of SPX fund-months are "specialized". That index code also covers S&P 100, Russell 1000/3000 and total-market funds, where "specialized" may be intended. The S&P 500 funds themselves disagree:
    - **SPDR S&P 500 ETF Trust (SPY): specialized**, while iShares Core S&P 500 and Vanguard 500 ETF and Admiral are broad-based.
    - SPDR Portfolio S&P 500 is specialized.
    - The **Vanguard Total Stock Market ETF** class is specialized while its Admiral and Institutional Plus classes are broad-based.

    30 tracked indices have funds with both labels. Lists: `data_issues_broad_label_spx.csv` (the 51 SPX-index funds labelled specialized) and `data_issues_broad_label_mixed.csv`. Table A7 is identified from this label.

4. **112 funds (7,771 fund-months, 7.2% of the Table 2 sample) have no `firm_f_old`.** These are mostly variable-annuity and insurance-channel funds (Voya 22, John Hancock 11, Allianz 9, MetLife 8, PGIM 6, Nationwide 6, Vanguard Variable Insurance 6). For these rows `BLP_IV_hausman_exp_ratio` does not follow the construction in 3(a), and it is not correlated with the fund's own fee (within-fund correlation −0.12). List: `data_issues_no_family_id.csv`. **Question: how was the Hausman IV built for these funds?** Table 2 col 2's sign depends on them (3b).
5. **Units of the management fee.** `product_mgmt_fee` is in **basis points** while `product_exp_ratio` is in percent: SPY 4.6 against 0.09, SPDR Gold 40.0 against 0.40 (`data_issues_mgmt_fee_units.csv`). As a result `BLP_IV_hausman_op_cost` = Hausman expense ratio (%) − Hausman management fee (bp) mixes units, and is essentially minus the management-fee variant. It is commented out in the notebook, but it should be rebuilt if it is ever used.
6. **Other sample notes.**
    - Zero-fee funds (for example Fidelity's) are dropped by the notebook's `prices > 0` filter and sit in the outside option.
    - The two panels end in different months (index Aug 2024, leveraged Sep 2024).
    - The leveraged notebook's Bull-only filter is what Table 2 Panel B uses; the paper's note does not say so.

## 5. Paper issues found during the replication (unchanged in the paper)

- **Table 5's elasticity column** is the Table 2 col (4) price coefficient (−8.348) × p × (1 − s) in each fund's **last** month (Aug 2024).
- **The "Bertrand / Cournot / Monopoly" columns** are pyRVtest markup **levels in percentage points** (p − mc) averaged over the sample, not Lerner indices.
- **Two Vanguard rows are swapped.** The 430,969 AUM fund is VTI's ETF class (p = 0.03) and the 395,578 fund is the Admiral class (p = 0.04).
- **Table 2 Panel A col 2's price SE** replicates as 1.310; the paper shows 0.131.
- **Averaging definitions differ across Table 2's columns.** Column (1) elasticities are observation-level means; columns (2)–(4) are per-market means.
- **pyblp's covariance-matrix condition numbers** are ~1e17 for the published BLP columns too (Panel A col 3: 2.4e17; Panel B col 3: 8.9e16). Section 1 has the diagnosis for the new specification.

## 6. Files in this bundle

| File | Role |
|---|---|
| `NOTE_for_coauthor_replication.md` | this note |
| `MAIN_REPORT_sharecl_hausman.md` | full report on the recommended specification |
| `requirements.txt` | package versions |
| `code/explore/common.py` | runs notebook cells 2–4 and returns `product_data` |
| `code/explore/tiers.py` | cheap tier (`raw_entry_tiers`) |
| `code/explore/asset_class.py` | asset class per tracked index |
| `code/explore/new_iv.py` | the new instrument and its estimation sample |
| `code/explore/step1_table5_elasticity.py`, `step2_logit_screen.py` | helpers: Table 5 fund list, variable construction, first-stage F, summary statistics |
| `code/explore/step25_new_iv_main.py` | recommended spec: Panel A table, cutoffs, drop-firm, split sample, 15 funds |
| `code/explore/step26_blp_newiv.py` | BLP version: σ profiles, estimates, two-step, cutoffs, FE variant, covariance diagnostics |
| `code/explore/step27_lead_tests.py` | lead tests |
| `code/explore/step28_nested_newiv.py` | nested logit with tracked-index nests (sensitivity check) |
| `code/explore/step23_hausman_reconstruct.py`, `step24b_family_split.py`, `step24c_class_month_fe.py`, `step24_hausman_variants.py` | diagnostics of the paper's instrument and of the alternatives |
| `code/explore/data_issues.py`, `step8_raw20_robustness.py` | data-issue lists |
