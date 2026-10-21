# Prompt for the cloud session: heterogeneity in the loading on the expense ratio

Paste everything below the line into the cloud session (branch `leveraged-etf-replication`, folder `Leveraged-ETF/`).

---

Read `README.md`, `EXPECTED_RESULTS.md` and your own `RESULTS_table2.md` first.

**Question.** If the demand loading on the expense ratio is allowed to differ across funds (as Table A7 does with the broad-based indicator), do the large index funds in Table 5 Panel A get own-price elasticities above 1 in absolute value? Explore this. Do not change the paper's numbers.

**What is already known (checked on the Panel A estimation sample; treat as facts to re-verify, not assumptions):**
- Market shares are tiny: median 0.04 percent, max 5.0 percent, so 1 − s ≥ 0.95. The low elasticities come from the α·p term, not from 1 − s.
- `product_exp_ratio` is in percent: median 0.20, 5th percentile 0.035.
- With α = −8.35, a fund at p = 0.03 gets e ≈ −0.25. Reaching |e| = 1 there needs α ≈ −33, about 4x the pooled estimate. A7's broad-based interaction gives about −12.8 in logit IV.
- Only 3.5 percent of the expense-ratio variance is within fund, and fund FE absorbs the rest. Every interaction is identified from within-fund fee changes in its subgroup.
- Zero-fee funds exist (e.g. the Fidelity 500 Index Fund, 2nd largest by AUM). Their elasticity is 0 under any α·p model.
- Table 5's "Elasticity" column is the BLP own elasticity in the **last market only**. Its Bertrand/Cournot/Monopoly columns are **sample means** of fund-month margins (see `code/R_table5/Get_passive_index_elasticities.txt`, the coauthor's R). The fund list is the top 5 by `product_mtna` in the last month for BlackRock, Vanguard and State Street Global Advisors (`firm_ids`).

**Rules.**
- Do not edit the notebooks or the data. Reuse the notebook prep cells the way `code/solve_rc3_resumable.py` does.
- Put new code in `code/explore/`, logs in `logs/explore_*.log`.
- Screen everything in logit IV first; run BLP only on the shortlist.
- If any single BLP run passes 3 hours, stop it and report.
- Commit to this branch only.

## Step 1. Reproduce Table 5's elasticity column (Panel A)

Port the R logic to Python and compute the own elasticity in the last market for the 15 funds. Do this for:
- logit IV;
- BLP 1 RC;
- BLP 3 RC. Here, evaluate at the paper's estimates using the optimizer's `return` option with the published sigma as the start; do not re-optimize.

Report which one reproduces −0.160, −0.323, −0.243, …, −0.415 (`EXPECTED_RESULTS.md` lists all 15). Use that model as the baseline for everything below. If none reproduces them, say so and stop after step 1.

For each fund, print p, s, the loading, e, and the loading needed for |e| = 1.

## Step 2. Logit IV screen

Use the specification `α·p + Σ_k γ_k·(p × z_k)` plus the notebook controls, with the same fund and time FE, clustering and sample.
- Instrument each `p × z_k` with `BLP_IV_hausman_exp_ratio × z_k`. For broad-based, `BLP_IV_hausman_exp_ratio_x_broad` already exists.
- For every endogenous term, report the first-stage F (Sanderson–Windmeijer when there are several) and flag any F below 10.

**Tier A: time-invariant z.** Main effects are absorbed by the fund FE.
- A1 broad-based: `broad_specialized == "broad-based"`. This must reproduce A7 Panel A col 2 to three decimals (−7.503, −5.278, average elasticity −2.858); stop and report if it does not.
- A2 ETF vs mutual fund (`ETF_ind`).
- A3 `Big3`, and then separate Vanguard / BlackRock / SSGA dummies.
- A4 asset class: `market_m_cluster`. Use the main codes, collapse the rest to "other", and write down the mapping (look up what each code means in the data).
- A5 fee tercile at the fund's **first** month in the sample, fixed for the fund.
- A6 log-AUM tercile at the fund's **first** month in the sample. Never use the fund's average AUM, which contains later demand shocks.
- A7 combinations of the two or three strongest.

**Tier B: functional form.** A benchmark, not heterogeneity.
- B1: utility in α·log(p + c). Then e = α(1 − s), with no p factor.
  - Use c = 0.01, with sensitivity at c = 0.005 and 0.02, plus a run that drops p = 0.
  - Report how many fund-months have p = 0.
  - Instrument with log(Hausman IV + c).
- B2: α·p + α₂·p², with p² instrumented by the squared Hausman IV.

**Tier C: time-varying z.** Exploratory; label every result as such.
- C1: p × a market-level state variable (`csent_index_resid`, `chg_VIX_resid`). Their main effects are absorbed by the time FE.
- C2: p × log-AUM tercile lagged at least 12 months.
- For every C spec, report:
  - (i) the within-fund correlation of z with the baseline residual ξ̂;
  - (ii) a lead test: regress ξ̂ at t−k (k = 1, 3, 12) on z_t;
  - (iii) Hansen J when overidentified;
  - (iv) the within-fund AR(1) of ξ̂.
- A persistent ξ̂ makes C2 suspect; say so if it is.

## Step 3. For every spec, one row with

- coefficients, clustered SEs and first-stage F;
- average own elasticity (per-market mean, as in Table 2);
- share of fund-months with |e| > 1: overall, among broad-based funds and among the Big 3;
- for the 15 Table-5 funds: the last-market elasticity and the sample-mean elasticity;
- implied single-product Bertrand margin 1/|e| for those funds, and the share of all fund-months where p − p/|e| < 0. This is a negative implied marginal cost: an implausibility flag.

## Step 4. BLP on a shortlist of at most three

Choose specs that raise the Table-5 elasticities, have a first-stage F of 10 or more, and keep implied marginal costs mostly non-negative.
- Re-estimate each with 1 RC on price.
- Add interaction instruments in the style of the broadspecial notebook (`BLP_IV_newproduct_1 × z`).
- Report the step-3 row, and pyblp `compute_costs` / `compute_markups` under single-firm Bertrand ownership (`firm_ids`) for the 15 funds.

## Step 5. Leveraged market

Run the best spec once on the LETF panel (Panel B). Report how its coefficients and average elasticity compare with Table 2 Panel B, so the paper can keep one demand model for both markets.

## Deliverable

`EXPLORATION_price_heterogeneity.md` with:
1. Step 1 result.
2. The screen table.
3. The shortlist's BLP results.
4. A 15-fund table: baseline vs the best two specs.
5. A ranked recommendation. For each spec, give the exogeneity assumption it rests on and whether that is credible.

Mark every statement as **run** (with the log file) or **inference**. Commit the report, `code/explore/*.py` and the logs.
