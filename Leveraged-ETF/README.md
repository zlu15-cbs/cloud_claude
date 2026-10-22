# P16_LeverageMKT — demand estimation replication

What to reproduce and what to look for: see `EXPECTED_RESULTS.md` (Table 2 numbers, Table 5, Tables A3 and A7).

## Results of the cloud session (read these two)

| File | Content |
|---|---|
| `MAIN_SPEC_entry_cheap_tier.md` | The recommended alternative demand model: logit IV with expense ratio × cheap (fee at the fund's first raw month ≤ the 10th/15th/20th percentile), Table 2 with the interaction, the 15 Table 5 funds, robustness |
| `OTHER_SPECS_explored.md` | Everything else tried and why it was set aside: other interactions, time-varying classifiers, log price, the one-RC BLP with the interaction, Table A7 col 3; appendix on Table 5 and data issues |
| `RESULTS_table2.md`, `RESULTS_A7_col3.md` | Replication records for Table 2 and Table A7 column (3) |
| `docs/superseded/` | Earlier working documents, kept for the record; superseded by the two files above |

## Layout

| Path | Content |
|---|---|
| `code/main_Danny_Oct2026_leveraged_market.ipynb` | Leveraged-fund market (Table 2 Panel B): logit, BLP, elasticities, conduct tests, counterfactuals |
| `code/main_Danny_Oct2026_index_market.ipynb` | Index-fund market (Table 2 Panel A): same steps |
| `code/main_Danny_March2026_testing_v3_replicate_Hausman_exp_ratio_broadspecial.ipynb` | Leveraged market with expense ratio x broad-based interaction (Table A7 Panel B) |
| `code/main_Danny_March2026_testing_v3_nonLev_Apr2026_matchEgan_broadspecial.ipynb` | Index market with the same interaction (Table A7 Panel A) |
| `data/LETF_product_month_level_v4_patched.csv` | Leveraged-fund product-month panel (93 MB) |
| `data/nonLev_funds_product_month_level_v2_patched.csv` | Index-fund product-month panel (879 MB) |
| `requirements.txt` | Package versions |
| `EXPECTED_RESULTS.md` | Targets and the research question |

## Run

1. Install `requirements.txt` (Python 3.11). The notebooks' first cell says to run each `pip install` in a separate cell.
2. The notebooks read their CSV by bare filename. Run each notebook from a working directory that holds its CSV (copy or link the CSV next to the notebook). Use a separate working directory per notebook: they all write `elasticity_outputs/` and same-named PDFs/CSVs into it.
3. Run top to bottom. Randomness: pyblp Monte Carlo integration, size 3000, seed 623543. The BLP estimations (BFGS, gtol 1e-7) dominate the runtime; the per-market elasticity export at the end writes one CSV per market. Runtime not measured.

## Outputs written by the notebooks

PDF figures (elasticity and cost/markup histograms and densities, conduct plots), `elasticity_outputs/*.csv` (one file per market), and the product data with costs: `lev_product_data_w_costs_*.csv`, `nonlev_product_data_w_costs_*.csv`, plus `*_counterfactual(s).csv`.

## Not included

The coauthor's reported per-market elasticity outputs (9 GB), the LaTeX paper (`Apps\Overleaf\Leveraged ETF`), and older notebook versions. Notebooks reference the pyblp/pyRVtest packages only; no credentials are needed.
