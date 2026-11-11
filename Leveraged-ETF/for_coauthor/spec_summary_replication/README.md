# Replication package for RESULTS_spec_summary.md

Four demand specifications for the index market (Table 2 Panel A), each with and without the variable-annuity funds:
T2, the modified T2 (proxy for Danny's stricter Hausman exclusion), V2, and the broad-based interaction (A5; Table A7 in our copy of the paper).

## 1. Data: all in Danny's shared Dropbox folder `P16_LeverageMKT`

| File | Location | Size |
|---|---|---|
| Index-fund panel | `Dropbox\P16_LeverageMKT\Code\python\nonLev_funds_product_month_level_v2_patched.csv` | 879,112,698 bytes |
| CRSP quarterly fund summary | `Dropbox\P16_LeverageMKT\Data\source_intake\raw data\CRSP_fund_summary_2026_qtrly_combined.csv` | 1,631,999,597 bytes |

| Danny's source panel (sections 2 and 3) | `Dropbox\P16_LeverageMKT\Data\source_intake\raw data\index_funds_preprocess_oct2026.csv` | 227,997,612 bytes |
| Danny's handoff zip (column 2) | `Dropbox\P16_LeverageMKT\Data\v2_matched_comparison_handoff_20261110.zip`; the two files used are `outputs/hausman-robustness-v1/passive/classified_donors.csv` and `classified_targets.csv` | 3.4 GB zipped |

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

`SRC` stands for `SC_SOURCE=<path to index_funds_preprocess_oct2026.csv> SC_DANNY=<folder with the two classified files>`.

| Report part | Script | Output |
|---|---|---|
| Scorecard, columns T2 and A5 (paper); validation | `sc_build.py`, `sc_demand.py`, `sc_a5.py` | `sc_demand.csv` (row `1_T2`), `sc_a5_demand.csv` (row `A5`), `sc_table5.csv` |
| Columns "T2, no VA" and "A5, no VA" | `sc_exva.py` | `sc_exva_demand.csv` (rows `T2x`, `A5x`) |
| Section 1: the variable-annuity funds | `sc_va_checks.py`, `sc_a5.py` | `sc_va_checks.csv`, `sc_va_funds.csv`, `sc_a5_demand.csv` |
| Section 1 and 5: Danny's category10 specification | `SRC python sc_danny_cat10.py`, then `downstream` and `conduct D10` | `sc_danny_cat10_demand.csv` (rows `D10`, `D10x`) |
| Section 2: T2 and A5 without the variable-annuity funds, 16 versions of the instrument | `SRC python sc_t2a5_nova_grid.py` | `sc_t2a5_nova_grid.csv` |
| Alternative columns for T2 and A5 | `SRC SC_ONLY=lipper6,pooled,wavg python sc_t2a5_nova_grid.py`, then `SC_ALT=1 python sc_v2_final.py downstream` and `SC_ALT=1 python sc_v2_final.py conduct T2alt` (and `A5alt`) | `sc_t2a5_alt.csv`, `sc_alt_*.csv`, `sc_conduct_T2alt.csv`, `sc_conduct_A5alt.csv` |
| V2 columns, sections 3.2–3.4 | `SRC python sc_v2_robust.py`, then `python sc_v2_final.py downstream` and `python sc_v2_final.py conduct V2n` (and `V2nx`, without the variable-annuity funds) | `sc_v2_robust.csv`; `sc_v2final2005_scale.csv`, `sc_v2final2005_mc.csv`, `sc_v2final2005_where.csv`, `sc_conduct_V2n.csv`, `sc_conduct_V2nx.csv` |
| Section 3.3: one file for both cheap and donors, three cutoffs | `SRC SC_GRID=filecheck python sc_v2_robust.py` | `sc_v2_filecheck.csv` |
| Section 3.4: start year of the cheap classification | `SRC python sc_v2_cheap_start.py` | `sc_v2_cheap_start.log` |
| Section 4: scale, negative MC, location, conduct for T2 and A5 (paper) | `sc_downstream.py`; `sc_a5.py downstream`; the same with `conduct SPEC` | `sc_scale.csv`, `sc_mc.csv`, `sc_where.csv`, `sc_conduct_SPEC.csv` |

- `replicate_V2.py` is the V2 script sent earlier. The other scripts import its functions (sample filters, cheap indicator, V2 instrument, first-stage F, markups, scale, conduct test).
- `sc_broad_ladder.py` is included because `sc_a5.py` imports one function from it.
- The demand CSVs also contain lead-test columns. We no longer use that test; ignore them.

## 4. Definitions

- **Variable-annuity (VA) funds:** the 112 funds (7,771 fund-months) with a blank `firm_f_old`. All carry CRSP `vau_fund` = Y and none of the other 1,190 funds does. "No VA" drops their rows, so they leave the demand estimation and the supply side and their assets count in the outside good.
- **T2:** logit IV, paper's `BLP_IV_hausman_exp_ratio`, fund and month fixed effects, standard errors clustered by month.
- **A5:** price and price × broad-based, instruments IV0 and IV0 × broad-based.
- **T2 alternative, A5 alternative:** the same two models without the variable-annuity funds, with the instrument rebuilt from the source panel: lag-AUM-weighted mean fee of same-family funds in another of the six broad asset classes, share types pooled.
- **V2:** price and price × cheap, instruments Z and Z × cheap, money market funds dropped. Z is defined in `NOTE_V2_replication.md`. Cheap: entry fee at or below the 20th percentile of that month's fees, ties cheap, entry month = the fund's first month on or after January 2005 with a fee that CRSP reports, measured on the source panel.
- **Supply side:** candidates PC, B0, B25, B50, B65; MC = p + η ln(TNA) − markup; η by 2SLS with the rotator instrument under each candidate; conduct test with pyRVtest and the markups supplied directly.

## 5. Numbers to check (`our_outputs/` holds our CSVs)

| Specification | With VA | No VA |
|---|---|---|
| T2: price coefficient (SE) | −5.606 (1.310) | +7.244 (1.987) |
| A5: specialized; × broad-based | −7.503 (1.770); −5.278 (0.372) | +4.009 (1.588); −6.924 (0.428) |
| Danny's category10 version of T2 | −5.713 (0.747) | +1.485 (1.079) |
| T2 alternative | – | −4.123 (0.736) |
| A5 alternative: specialized; × broad-based | – | −3.983; −4.413 |
| V2: non-cheap; × cheap | −3.385 (0.541); −20.059 (0.784) | unchanged |
| V2, 15th; 25th percentile: non-cheap | −7.527; −3.967 | unchanged |
| V2 as first sent (cheap from the index CSV) | −3.642 (0.419); −20.562 (0.646) | unchanged |
| Negative-MC share at own η, B0–B65: V2 | 0.067–0.087 | 0.054–0.081 |

The run script `run_all.sh` covers the paper's T2 and A5 columns and V2 as first sent. The other rows need the two extra inputs and are run with the commands in the table in section 3.

## Sections 2 and 3 of the report (refined family ID and the recommended sample)

`sc_family_refined.py` builds the refined family ID from `firm_f` in the index CSV and writes `family_transitions.csv` (every transition and its rule) and `family_real_switches_table2.csv` (the 50 excluded funds).

All runs set `SC_FAMILY=refined SC_DONORS=csv SC_CHEAP=csv` plus the two extra inputs (`SC_SOURCE`, `SC_DANNY`). Sample switches: `SC_PURE=1 SC_RULE=all SC_NOSWITCH=1` drops the real switchers (the recommended sample); `SC_RULE=bd` adds the B/D flag; `SC_RULE=narrow` adds the Lipper exclusions; `SC_DROPQ4=1` drops the top entry-fee quartile.

- T2 and A5: `SC_ONLY=index,pooled,wavg python sc_t2a5_nova_grid.py` (paper's exclusion) and `SC_ONLY=lipper6,pooled,wavg` (broad-asset-class exclusion).
- V2: `SC_GRID=agg python sc_v2_robust.py`.

Our outputs are in `our_outputs/sc_refined_family/`, one set of files per sample: `all_noswitch0` (VA dropped), `all_noswitch1` (recommended), `B_noq4`, `bd_noswitch1`, `narrow_noswitch1`.
