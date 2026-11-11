# Replication package for RESULTS_spec_summary.md

Four demand specifications for the index market (Table 2 Panel A), each with and without the variable-annuity funds:
T2, the modified T2 (proxy for Danny's stricter Hausman exclusion), V2, and the broad-based interaction (A5; Table A7 in our copy of the paper).

## 1. Data: two files, both in Danny's shared Dropbox folder `P16_LeverageMKT`

| File | Location | Size |
|---|---|---|
| Index-fund panel | `Dropbox\P16_LeverageMKT\Code\python\nonLev_funds_product_month_level_v2_patched.csv` | 879,112,698 bytes |
| CRSP quarterly fund summary | `Dropbox\P16_LeverageMKT\Data\source_intake\raw data\CRSP_fund_summary_2026_qtrly_combined.csv` | 1,631,999,597 bytes |

- The panel is the CSV that `main_Danny_Oct2026_index_market.ipynb` reads in cell 3. The scripts apply that notebook's sample filters (cells 3 and 4) unchanged and get 108,300 fund-months.
- Put both files in one folder, or link them there, and point `SC_DATA` at it. Nothing is written to Danny's folders except a `cache/` subfolder inside `SC_DATA`, so use a copy or a folder of links.
- CRSP columns used: `crsp_fundno`, `quarter`, `fund_name`, `lipper_class`, `lipper_asset_cd`, `crsp_obj_cd`, `inst_fund`, `retail_fund`, `vau_fund`, `mgmt_cd`, `mgmt_name`.

## 2. How to run

```
pip install -r requirements.txt          # pyblp 1.3.0, pyRVtest 0.3.2, pyhdfe, pandas, numpy, scipy
SC_DATA=/path/to/data sh run_all.sh           # everything except the conduct tests (about 1 hour)
SC_DATA=/path/to/data sh run_all.sh conduct   # the same plus the conduct tests (about 30 minutes each)
```

Memory: about 6 GB for the build step, 2.5 GB per conduct run.

## 3. Which script produces which part of the report

| Report section | Script | Output |
|---|---|---|
| Scorecard and section 2, columns 1–3 "with VA" | `sc_build.py`, `sc_demand.py` | `sc_demand.csv` (rows `1_T2`, `4p`, `3_V2`), `sc_table5.csv` |
| Column 4 "with VA" (broad-based) | `sc_a5.py` | `sc_a5_demand.csv` (row `A5`) |
| All "no VA" columns | `sc_exva.py` | `sc_exva_demand.csv` (rows `T2x`, `4px`, `V2x`, `A5x`) |
| Sections 3 and 4: scale, negative MC, location | `sc_downstream.py`; `sc_a5.py downstream`; `sc_exva.py downstream` | `sc_scale.csv`, `sc_mc.csv`, `sc_where.csv` in each work folder |
| Section 5: conduct | the same three scripts with `conduct SPEC` | `sc_conduct_SPEC.csv` |
| Sections 1 and 6: the variable-annuity funds | `sc_va_checks.py` | `sc_va_checks.csv`, `sc_va_funds.csv`, printed log |

- `replicate_V2.py` is the V2 script sent earlier. The other scripts import its functions (sample filters, cheap indicator, V2 instrument, first-stage F, markups, scale, conduct test).
- `sc_broad_ladder.py` is included because `sc_a5.py` imports one function from it.
- The demand CSVs also contain lead-test columns. We no longer use that test; ignore them.

## 4. Definitions

- **Variable-annuity (VA) funds:** the 112 funds (7,771 fund-months) with a blank `firm_f_old`. All carry CRSP `vau_fund` = Y and none of the other 1,190 funds does. "No VA" drops their rows, so they leave the demand estimation and the supply side and their assets count in the outside good.
- **Column 1, T2:** logit IV, paper's `BLP_IV_hausman_exp_ratio`, fund and month fixed effects, standard errors clustered by month.
- **Column 2, modified T2 (proxy):** the same with the instrument rebuilt from the index CSV: lag-AUM-weighted mean fee of same-family funds in another Lipper-6 asset class (which also excludes the same index). The original instrument is used where the rebuilt one is undefined and for funds without a family code. This is a proxy for Danny's category10 exclusion, whose labels we do not have.
- **Column 3, V2:** price and price × cheap, instruments Z and Z × cheap, money market funds dropped. Definitions in `NOTE_V2_replication.md` (sent earlier).
- **Column 4, A5:** price and price × broad-based, instruments IV0 and IV0 × broad-based.
- **Supply side:** candidates PC, B0, B25, B50, B65; MC = p + η ln(TNA) − markup; η by 2SLS with the rotator instrument under each candidate; conduct test with pyRVtest and the markups supplied directly.

## 5. Numbers to check (`our_outputs/` holds our CSVs)

| Specification | With VA | No VA |
|---|---|---|
| T2: price coefficient (SE) | −5.606 (1.310) | +7.244 (1.987) |
| Modified T2 (proxy) | −9.107 (0.912) | −3.491 (0.644) |
| V2: non-cheap; × cheap | −3.642 (0.419); −20.562 (0.646) | unchanged |
| A5: specialized; × broad-based | −7.503 (1.770); −5.278 (0.372) | +4.009 (1.588); −6.924 (0.428) |
| Negative-MC share at own η, B0–B65: modified T2 | 0.006–0.163 | 0.42–0.59 |
| Negative-MC share at own η, B0–B65: V2 | 0.053–0.082 | 0.041–0.073 |
