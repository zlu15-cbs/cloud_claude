# Handoff: reconcile Danny's results with our recommended specification, then run the downstream analysis

Written 3 Nov 2026 at the end of the cloud session (repo `zlu15-cbs/cloud_claude`, branch `leveraged-etf-replication`, folder `Leveraged-ETF/`). From here on, work happens in a **local** Claude Code session started in this folder (`C:\Users\zlu15\Dropbox\ClaudeCode\global\Colab\P16_LeverageMKT\`). Read `handoff.md` (23 Oct, older) for the earlier workstreams: Table 2 replication, the A7 column, and the expense-ratio fee patch.

People:
- Zhongjin "Gene" Lu: the user.
- Danny: the coauthor who owns the paper's code and data.
- Matteo: the third coauthor.

## 1. Goal of this round

1. **Reconcile.** Line up Danny's final results with our recommended demand specification. Danny will send a note on how to replicate his results and the Dropbox path to his data.
2. **Decide the final demand specification** for the index market (Table 2 Panel A). Panel B (leveraged) keeps the original model with no interaction.
3. **Run the downstream analysis** for the final specification and the main alternatives:
    - markups and the share of negative implied marginal costs;
    - the economies-of-scale ("scale") parameter;
    - the conduct test (pyRVtest).

## 2. Our recommended specification (full detail: `NOTE_for_coauthor_replication.md` §1, `MAIN_REPORT_sharecl_hausman.md`)

- **Sample.**
    - Start from the Table 2 Panel A sample: notebook `code/main_Danny_Oct2026_index_market.ipynb`, cells 2–4 unmodified. That is 108,300 fund-months and 1,302 funds, Jan 2010 – Aug 2024; a market is a month.
    - Keep rows with a family identifier (`firm_f_old`) and a defined instrument: **97,429 fund-months, 1,164 funds**, all 15 Table 5 funds.
- **Demand.** Logit IV in pyblp 1.3.0:

      δ_jt = α·p + α_c·(p × cheap_j) + β·[tracking error, past 1-yr return, log age] + fund FE + month FE + ξ

  SE clustered by month. Variant: month × asset-class FE.
- **Cheap.** The fee in the fund's first month in the raw index file (1994–2025) is ≤ that month's 20th percentile across all index funds; ties count as cheap. It is fixed per fund. Code: `tiers.raw_entry_tiers`. The 10th and 15th percentiles are robustness checks.
- **Instrument Z** (replaces the paper's `BLP_IV_hausman_exp_ratio`). It is the median expense ratio of funds with:
    - the same family (`firm_f_old`);
    - the same share class (ETF / institutional / retail / other mutual fund, parsed from names);
    - a different asset class (per tracked index: US equity, international equity, bond, allocation, real assets);
    - the same month.

  Excluded instruments: Z and Z × cheap. Code: `new_iv.py`, `asset_class.py`.
- **Results (20th percentile):**

  | Specification | Non-cheap (SE) | Cheap total | First-stage F | Avg own e | Table 5 funds with \|e\| > 1 |
  |---|---|---|---|---|---|
  | Fund + month FE | −6.12 (0.85) | −28.8 | 167 | −2.68 | 7 of 15 |
  | Month × asset-class FE | −3.80 (0.66) | −24.0 | 262 | −1.96 | 5 of 15 |

  No fund-month has upward-sloping demand. Negative MC (firm Bertrand, **no scale adjustment**) is 24% and 36%.
- **BLP with one random coefficient on price** (`step26_blp_newiv.py`, extra instrument Z²): σ = 1.81, but **σ is not credibly identified**. The covariance is singular, and overidentified versions send σ to 0 or 11. Report it as a sensitivity check only.
- **Nested logit** (tracked-index nests, `step28_nested_newiv.py`): signs are fine with the new IV, but 41–83% of fund-months have negative MC. It is a sensitivity check, not an improvement.
- **Diagnostics behind the instrument change** (`NOTE_for_coauthor_replication.md` §3): family-identifier split, lead tests, placebo, split sample.

## 3. Danny's work so far (two PDFs; our review is in `COMPARE_coauthor_CRSP_cheap.md` §1–7)

- **Design.**
    - The same samples and Table 2 columns (OLS, IV logit, BLP 1 RC, BLP 3 RC), still with the **paper's Hausman IV**.
    - Twelve cheap definitions: 10th / 20th / 50th percentile × reference group (funds founded, or existing, in the prior 1 or 5 years).
    - The launch fee is the first CRSP `exp_ratio` dated on or after `first_offer_dt`. Cheap means strictly below the percentile. A missing fee or missing history counts as not cheap.
    - PDF 1 uses all CRSP share classes as the reference; PDF 2 (3 Nov) uses index funds only.
- **Downstream, as described in his PDFs (§3 there).**
    - Markups are winsorized 1/99 by calendar year.
    - Costs = price + scale × log(TNA) − markup.
    - The scale is estimated by IV regression of the winsorized MC on log(AUM), with |tracking error|, log age, and fund and month FE. The excluded instrument is `rotator` (built in notebook cells 2–4 from negative residualized index returns at 1, 2–5 and 6–12 months).
    - Conduct is assumed PC for index funds and B65 for leveraged funds when estimating the scale.
    - Conduct test: RV / MCS at 5% with rival count, residualized sentiment and their product as instruments. Candidates are PC, B0, B25, B50 and B65; "B65" means 0.65 profit internalization among the Big 3, or among ProShares/ProFunds and Direxion.
    - The fixed scale was 0.024 (index) and 0.040 (leveraged) before. The estimated scale is 0.0205 (index) and about 0.037 (leveraged).
- **His conclusions, and our corrections** (`COMPARE_coauthor_CRSP_cheap.md` §6–7):
    1. He favoured Gene's "founded in the prior 1 year, 20th percentile". In PDF 1 that definition has **upward-sloping demand for every non-cheap fund-month (25%)**, so its zero negative MC is partly mechanical. In PDF 2 the same definition gives 58–78% negative MC.
    2. The index scale under PC does not depend on demand: it is the same 0.0205 in every column. So it cannot discriminate between demand models.
    3. Among definitions with **valid demand**, the index-universe reference does better (IV logit: 0 negative MC at scale 0.024 in 6 of 7). The closest to our recommendation are **existing in the prior 1 or 5 years, 20th percentile**: IV logit non-cheap −11 to −13, cheap −32 to −37.
    4. With valid demand, the conduct test selects "all five" (no discrimination) or rejects PC. It selects PC only in the specifications with invalid demand.
- **Coming from Danny:** a version with the share-class IV, a broad-based-index interaction table in the same format, and a final replication note with the Dropbox path to his data.

## 4. Plan for this round

1. **Read Danny's note and locate his code and data.** They are read-only: never edit his folders (`C:\Users\zlu15\Dropbox\P16_LeverageMKT\…` and whatever path he sends). Work on copies.
2. **Check that the two pipelines agree** on his benchmark (original Table 2):

   | Quantity | Target |
   |---|---|
   | IV logit price coefficient | −5.606 (1.310) |
   | First-stage F | 33.61 |
   | BLP1 price / σ | −6.771 / 0.027 |
   | Index scale (PC) | 0.0205 (0.0051) |
   | Negative MC, B0, IV logit, scale 0 | 0.5156 |

   Our scripts reproduce the demand numbers (`RESULTS_table2.md`). The downstream numbers must come from his code, or from a re-implementation checked against these targets.
3. **One comparison grid, demand first.**
    - Rows: cheap definition × instrument × fixed effects.
        - Cheap definitions: ours (raw-entry, index-only, 20th) and his index-universe existing-1y-20th, existing-5y-20th, founded-5y-20th and founded-1y-20th.
        - Instruments: paper's Hausman and share-class Z.
        - Fixed effects: month, and month × asset class.
    - Report for each row:
        - non-cheap and cheap slopes;
        - Sanderson–Windmeijer F;
        - share of fund-months with e > 0 (must be 0);
        - average e;
        - the 15 Table 5 elasticities;
        - lead tests (`step27_lead_tests.py`).
    - **Choose the final specification on these demand criteria before looking at negative MC or conduct**, to avoid selecting the model on downstream outcomes.
4. **Downstream, for the final specification and two or three alternatives:**
    - Markups under PC, B0, B25, B50 and B65. The kappa functions are in the index notebook, cells 31/40; check their numbering against Danny's labels.
    - Negative-MC shares at scale 0, at 0.024, and at the estimated scale.
    - **The scale estimated under each conduct candidate**, not only PC. Under PC the markup is zero, so the scale ignores demand.
    - The pyRVtest conduct test.
        - Starting point: index notebook, cells 41 and 43. Cost formulation `0 + log_product_fund_age + product_tracking_err + product_past_1yr_ret` with fund and month FE. Instruments `BLP_IV_rival_funds2 * Conduct_IV_csent_index_resid`. `demand_adjustment=False`, `clustering_adjustment=True`.
        - Prices are adjusted by the scale before testing (cell 41).
        - The notebook's comments list several instrument choices that "support PC". Pre-specify the conduct instruments and report the alternatives, so the conclusion is not instrument-shopped.
        - `pyRVtest` takes the pyblp results object, so the logit IV with Z and Z × cheap plugs in directly. pyRVtest 0.3.2 is in `requirements.txt`.
5. **Leveraged market:** no interaction. Confirm a scale of about 0.037 and the B65 selection under the reconciled downstream code.
6. **Write results to a .md file in this folder**, one per step. Keep the code under `code/explore/`.

## 5. Running our code locally

- **Scripts:** `code/explore/*.py` (copied from `replication_bundle/code/explore/`). `common.load('index')` executes cells 2–4 of `code/main_Danny_Oct2026_index_market.ipynb`, the parent folder of `explore/`.
- **Working directory:** the scripts read the CSV by bare filename (`nonLev_funds_product_month_level_v2_patched.csv`, in `data/`). Run from a work folder holding that CSV. On Windows a hard link avoids copying 879 MB (`mklink /H`, same volume, no admin needed). Set `PYTHONPATH` to `code\explore`.
- **Environment:** Python 3.11 with `requirements.txt` (pyblp 1.3.0, pyhdfe 0.2.0, pyRVtest 0.3.2).
- **BLP runs:**
    - Set `OPENBLAS_NUM_THREADS=1`.
    - `pyblp.parallel` on Windows needs the `if __name__ == '__main__':` guard; `step26_blp_newiv.py` has it.
    - Run long jobs in the background with a log file and a single completion check. Do not poll.
- **Commands and expected numbers:** `NOTE_for_coauthor_replication.md` §2. For example, `python step25_new_iv_main.py` gives column (3): −6.116 (0.845), × cheap −22.655 (0.794), F 166.6.

## 6. Known pitfalls

- **Paper's Hausman IV.** Exact only where `firm_f_old` exists. Its construction is unknown for 112 mostly insurance-channel funds (7.2% of rows), and Table 2's −5.6 depends on those rows (on the other rows: +7.24).
- **Management fee units.** `product_mgmt_fee` is in basis points while `product_exp_ratio` is in percent. `BLP_IV_hausman_op_cost` mixes the two.
- **Fee errors.** SPY is recorded at 0.04% for Oct 2022 – Sep 2023 (truth 0.0945%). There is a verified fee patch in `data_patch/` (not yet applied to Danny's panel; see `handoff.md`). Decide with Gene whether the final runs use it.
- **σ identification.** σ is not identified once the cheap interaction is in. BLP3 has rank problems. A σ near 0.027 often just echoes the paper's starting value.
- **Zero negative MC is not evidence by itself.** Upward-sloping demand mechanically produces positive MCs. Always check the e > 0 share first.
- **Table 5.**
    - The elasticity column is the 3-RC coefficient × p × (1 − s) in the last month.
    - The Bertrand / Cournot / Monopoly columns are markup *levels* in pp, not Lerner indices.
    - Two Vanguard rows are swapped.
- **Securities lending.** The 2–3 bp funds can still imply negative MC. Gene considers securities-lending income an acceptable explanation.

## 7. Files in this folder

| File | What |
|---|---|
| `HANDOFF_final_spec.md` | this file |
| `CLAUDE.md` | short rules and pointers, loaded automatically by Claude Code |
| `NOTE_for_coauthor_replication.md` | exact recommended specification, replication commands, diagnostics, data issues |
| `MAIN_REPORT_sharecl_hausman.md` | full report on the recommended specification (BLP, nested logit, robustness) |
| `MAIN_SPEC_entry_cheap_tier.md` | the cheap tier with the paper's instrument (previous main spec) |
| `OTHER_SPECS_explored.md` | everything else that was tried, and why it was set aside |
| `COMPARE_coauthor_CRSP_cheap.md` | review of Danny's two PDFs and his emails |
| `RESULTS_table2.md` | Table 2 replication: what matches, what does not |
| `EXPECTED_RESULTS.md`, `README.md`, `handoff.md` | earlier targets, layout, and the 23 Oct handoff |
| `code/explore/` | our scripts (step25 main spec, step26 BLP, step27 lead tests, step28 nested logit, step23–24 instrument diagnostics, new_iv, asset_class, tiers, common) |
| `replication_bundle/` | the bundle sent to Danny (same code and documents) |
| `code/*.ipynb`, `data/`, `data_patch/`, `code/fee_fix/` | Danny's notebooks, the two panels, and the fee patch |

The cloud repo (`github.com/zlu15-cbs/cloud_claude`, branch `leveraged-etf-replication`, `Leveraged-ETF/`) has the same documents plus all logs and result CSVs (`logs/explore/`).
