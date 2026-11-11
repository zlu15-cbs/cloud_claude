# Replication package: the recommended sample (section 2 of RESULTS_spec_summary.md)

Danny, this replicates the last table of section 2 of `RESULTS_spec_summary.md`: six demand specifications for the index market on the sample with both exclusions, with their supply-side results. It is meant as a starting point.

## 1. What it produces

Sample: Table 2 Panel A (108,300 fund-months) without the 112 variable-annuity funds and without the 50 funds with a real acquisition or transfer in 2010-2024. 1,140 funds, 97,315 fund-months.

| | T2, paper's exclusion | A5, paper's exclusion | T2, broad asset class | A5, broad asset class | V2, median | V2, weighted mean |
|---|---|---|---|---|---|---|
| Name in the code | `T2p` | `A5p` | `T2b` | `A5b` | `V2r` | `V2wr` |
| Base price coefficient (SE) | -7.49 (2.90) | -10.69 (3.40) | -12.73 (1.81) | -13.33 (1.87) | -10.350 (0.812) | -6.877 (0.564) |
| Interaction | - | -3.75 | - | -2.63 | -26.89 | -23.53 |
| First-stage F (min) | 17 | 33 | 94 | 140 | 302 | 557 |
| Scale eta under PC | 0.0126 | 0.0126 | 0.0126 | 0.0126 | 0.0127 | 0.0127 |
| Negative-MC share, own eta, B0-B65 | 0.23-0.36 | 0.010-0.144 | 0.008-0.151 | 0.000-0.062 | 0.000-0.001 | 0.006-0.031 |
| Conduct, main instrument, eta = 0.024 | PC, B50, B65 | PC, B50, B65 | PC, B50, B65 | PC, B50, B65 | PC, B65 | PC, B65 |

Our own output files are in `our_outputs/`, for comparison.

## 2. Data: all in your Dropbox folder `P16_LeverageMKT`

| File | Location | Passed as |
|---|---|---|
| Index-fund panel | `Code\python\nonLev_funds_product_month_level_v2_patched.csv` | inside `SC_DATA` |
| CRSP quarterly fund summary | `Data\source_intake\raw data\CRSP_fund_summary_2026_qtrly_combined.csv` | inside `SC_DATA` |
| Your source panel | `Data\source_intake\raw data\index_funds_preprocess_oct2026.csv` | `SC_SOURCE` (full path to the file) |
| Your handoff zip | `Data\v2_matched_comparison_handoff_20261110.zip`; the file used is `outputs/hausman-robustness-v1/passive/classified_donors.csv` | `SC_DANNY` (the folder holding it) |

- Put the first two files in one folder, or link them there, and point `SC_DATA` at it. The scripts create a `cache/` subfolder inside `SC_DATA` and write nothing else there.
- The source panel and `classified_donors.csv` are read by the instrument scripts. On this sample the donors are restricted to fund-months in the index CSV, and the category labels are not used for these six specifications.

## 3. How to run

```
pip install -r requirements.txt     # pyblp 1.3.0, pyRVtest 0.3.2, pyhdfe, pandas, numpy, scipy
SC_DATA=/path/to/folder SC_SOURCE=/path/to/index_funds_preprocess_oct2026.csv SC_DANNY=/path/to/passive sh run_section2.sh
SC_DATA=... SC_SOURCE=... SC_DANNY=... sh run_section2.sh conduct     # the same plus the conduct tests
```

- About 25 minutes without the conduct tests; each conduct test adds about 8 minutes. Memory: about 6 GB.
- Run the steps one at a time, as the script does.
- Results print to the screen and to `work/`: one line per specification from the demand scripts, then `work/down/sc_scale.csv`, `sc_mc.csv`, `sc_where.csv` and `sc_conduct_<name>.csv`.

## 4. Definitions

- **Variable-annuity funds:** the 112 funds with a blank `firm_f_old`. Dropped from the sample.
- **Refined family ID** (`code/sc_family_refined.py`): starts from your `firm_f`. (1) Two labels of one firm become one name. (2) A trustee, administrator or white-label platform listed in place of the firm that runs the fund is replaced by that firm. (3) Every other change is a real acquisition or transfer. All 121 transitions in `firm_f` and their classification are in `our_outputs/family_transitions.csv`. **The classification is our judgment from the firm names; please check it.**
- **Real switchers:** the 50 funds with a real change of family in 2010-2024 (`our_outputs/family_real_switches_table2.csv`). Dropped from the sample.
- **T2:** logit IV, one fee slope, fund and month effects, SE clustered by month. **A5:** adds fee x broad-based.
  - Paper's exclusion: instrument = lag-AUM-weighted mean fee of same-family funds tracking another index, share types pooled.
  - Broad-asset-class exclusion: the same, with donors in another of six broad asset classes (from CRSP's Lipper class).
- **V2:** fee and fee x cheap; instruments Z and Z x cheap; money market funds dropped. Z = fee of same-family, same-share-type funds in another broad asset class, aggregated by the median (`V2r`) or the lag-AUM-weighted mean (`V2wr`). Cheap = entry fee at or below the 20th percentile of that month's fees; entry month = the fund's first month in the index CSV on or after January 2005; ties are cheap.
- **Supply side:** candidates PC, B0, B25, B50, B65; MC = p + eta ln(TNA) - markup; eta by 2SLS with the rotator instrument; ownership by the refined family ID; conduct test with pyRVtest.

## 5. Things to know

- **The scale estimate is 0.013 on this sample,** against 0.021-0.024 on the paper's sample. The conduct row above uses eta = 0.024 and has not been re-run at 0.013.
- **V2's size depends on the cheap cutoff** (non-cheap slope -10.4 at the 20th percentile, -5.0 at the 25th, with the median). The 25th-percentile rows print from `sc_v2_robust.py`.
- **T2 and A5 with the paper's exclusion have a weak first stage** (F of 17 and 33).
- `RESULTS_spec_summary.md` has the full report; sections 1 and 2 explain the two exclusions.
- `code/replicate_V2.py` is the V2 script sent earlier; the other scripts import its functions.
