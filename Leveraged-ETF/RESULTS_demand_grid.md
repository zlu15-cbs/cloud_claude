# Demand grid: 12 logit-IV models for the index market

Plan: `PLAN_demand_grid.md`. Code: `code/explore/step31_build_cheap.py` (indicators), `step32_demand_grid.py` (models), `ivtools.py`. Logs and CSVs: `logs/step31*`, `logs/step32*`.

**Setup.**
- **Rows:** the common 97,429 fund-months where Z is defined.
- **Model:** δ = α·p + α_x·(p × I) + tracking error + past 1-yr return + log age + fund FE + month FE.
- **Instruments:** z and z × I.
- **Inference:** SE clustered by month; F is the cluster-robust Sanderson–Windmeijer F.
- **Lead tests:** `step25`'s procedure, i.e. the residual at t − k on the residualized instrument at t, k = 12/24/36 months.

## 1. Validation: Danny's and the paper's numbers are reproduced

Paper Hausman IV, all 108,300 rows, our pipeline (pyblp 1.3.0) with our rebuilt indicators.

| Run | Ours: α (SE) / α_x | Published | F, ours | F, published |
|---|---|---|---|---|
| No interaction (Table 2.0) | −5.606 (1.310) | −5.606 (1.310) | 33.6 | 33.61 |
| Danny CRSP `founded_1y_p20` (CRSP report, Table 2.2) | +5.846 (1.710) / −20.786 | +5.846 / −20.786 | 44.3 / 1,289 | 28.08 / 1,128.15 |
| Danny index `founded_1y_p20` (index report, Table 2.2) | −0.613 (1.592) / −13.739 | −0.613 / −13.739 | 39.0 / 430 | 31.80 / 241.67 |
| Broad-based (paper Table A7, col 2) | −7.503 (1.770) / −5.278 | −7.503 / −5.278 | 53.0 / 186 | n/a |

- **Coefficients:** all match to three decimals, so the rebuilt indicators and the pipeline are right.
- **F with two endogenous regressors:** the values differ. Danny reports "SW conditional reduced-form rank Wald/df, CR0, no finite-sample correction"; ours is the cluster-robust SW F used throughout our reports. With one endogenous regressor, both give 33.6. The difference is in the statistic's definition, not the data.

## 2. The 12 models

Screens: e > 0 share = 0, min F ≥ 10, lead tests small.

| Instrument × interaction | Share I | Non-cheap α (SE) | α_x (SE) | Total for I = 1 | Min F | Avg own e | **e > 0** | Table 5 \|e\| > 1 | Lead t (12/24/36) | Passes |
|---|---|---|---|---|---|---|---|---|---|---|
| **Z × gene_idx** (benchmark) | 0.47 | **−6.116 (0.845)** | −22.655 (0.794) | −28.77 | 167 | −2.68 | **0** | 7/15 | −1.7 / −2.9 / −1.9 | **yes** |
| **Z × broad** | 0.50 | −0.449 (0.663) | −7.357 (0.262) | −7.81 | 235 | −0.88 | **0** | 0/15 | 0.2 / −0.4 / 1.6 | **yes** (but non-cheap slope ≈ 0) |
| Z × none | | −1.242 (0.582) | | | 217 | −0.33 | 0 | 0/15 | 2.1 / 2.6 / **5.2** | borderline (lead) |
| Z × gene_crsp | 0.88 | **+9.086** (1.058) | −13.614 | −4.53 | 183 | −0.05 | **0.12** | 1/15 | 2.7 / 2.4 / 3.9 | no |
| Z × danny_crsp | 0.80 | **+7.501** (0.728) | −13.318 | −5.82 | 201 | −0.11 | **0.20** | 2/15 | 2.4 / 2.3 / 4.2 | no |
| Z × danny_idx | 0.59 | **+5.151** (0.738) | −8.960 | −3.81 | 176 | +0.47 | **0.41** | 1/15 | 1.9 / 2.6 / 5.2 | no |
| **Z_paper × gene_idx** | 0.47 | −2.721 (2.752) | −24.089 (1.447) | −26.81 | 13.2 | −1.86 | **0** | 7/15 | −1.9 / −0.4 / 2.2 | **yes** (weak: F 13, α n.s.) |
| Z_paper × none | | **+11.263** (3.142) | | | 25.0 | +2.96 | **1.00** | 2/15 | 6.7 / 10.7 / 20.3 | no |
| Z_paper × gene_crsp | 0.88 | **+30.2** (6.7) | −26.9 | +3.29 | 22.4 | +3.11 | **1.00** | 1/15 | 6.5 / 12.6 / 20.8 | no |
| Z_paper × danny_crsp | 0.80 | **+17.1** (3.5) | −17.8 | −0.65 | 25.1 | +1.72 | **0.20** | 1/15 | 5.1 / 9.9 / 18.5 | no |
| Z_paper × danny_idx | 0.59 | **+13.5** (3.0) | −13.0 | +0.49 | 25.3 | +2.26 | **1.00** | 4/15 | 5.2 / 10.2 / 20.0 | no |
| Z_paper × broad | 0.50 | **+5.48** (1.97) | −7.61 | −2.13 | 46.2 | +0.65 | **0.50** | 1/15 | 5.2 / 13.0 / 19.3 | no |

## 3. Reading

1. **Only three of 12 pass the screens.** They are the benchmark (Z × gene_idx), Z × broad, and the benchmark interaction under the paper's IV. The third has F 13 and an insignificant non-cheap slope.
2. **Every CRSP-reference and Danny-definition model fails, under either instrument.** The non-cheap slope is positive: +5 to +9 with Z, +13 to +30 with the paper's IV. The cause is the size of the cheap group, 59–88% of fund-months. The non-cheap remainder is the most expensive funds, and their slope is not identified as negative. This is the pattern found before in Danny's CRSP PDF and in our own cutoff grid.
3. **Danny's index definition has valid signs only on the full sample.** On all 108,300 rows with the paper's IV it gives −0.61. On the 97,429 rows with a family id it gives +13.5. As with Table 2's −5.6, the valid sign comes from the 7% of rows without a family id, where the paper's IV construction is unknown.
4. **The paper's IV fails the lead tests** in every specification except the benchmark interaction: lead-36 t of 18–21. Past demand shocks predict today's instrument, the sign of a family-level demand response in the paper's Hausman IV. With Z, lead t's are 1.6–5.2, and the two passing Z models have |t| ≤ 2.9.
5. **Broad-based is a weak source of heterogeneity under Z.** It gives a near-zero slope for specialized funds and −7.8 for broad-based, average e −0.88, and no Table 5 fund above 1.

## 3b. Third instrument: Z with CRSP share-class flags (Z_flag)

`step32b_grid_zflag.py`. Rows: the 97,294 where Z_flag is defined. Keyword Z is re-run on the same rows for comparison. Why flags: `RESULTS_danny_iv_compare.md` §4.

| Interaction | Z_flag: non-cheap (SE) | Total | Min F | e > 0 | Leads t (12/24/36) | Z on the same rows: non-cheap / total / e > 0 |
|---|---|---|---|---|---|---|
| none | −0.852 (0.606) | | 222 | 0 | 1.3 / 1.0 / **4.2** | −1.070 / – / 0 |
| **gene_idx** | **−8.019 (1.306)** | −32.69 | 114 | **0** | −2.4 / **−4.3** / **−4.0** | −6.064 / −28.69 / 0 |
| gene_crsp | +7.781 | −6.27 | 201 | 0.12 | 1.0 / −0.8 / 0.0 | +9.183 / −4.39 / 0.12 |
| danny_crsp | +7.932 | −7.19 | 225 | 0.20 | 0.6 / −0.5 / 1.0 | +7.625 / −5.60 / 0.20 |
| danny_idx | +4.064 | −5.07 | 206 | 0.41 | 0.2 / −0.2 / 1.8 | +5.348 / −3.61 / 0.41 |
| broad | **+0.467** (0.667) | −6.09 | 261 | **0.50** | 0.2 / −0.8 / 2.0 | −0.328 / −7.72 / 0 |

- **The flags do not rescue any failing definition.** The CRSP-reference and Danny definitions still have upward-sloping demand for non-cheap funds.
- **Broad-based now fails.** Its specialized-fund slope turns slightly positive, so half the fund-months slope upward.
- **The benchmark interaction stays valid and gets steeper,** but its lead tests worsen (|t| up to 4.3 against 2.8 with keyword Z).

## 3c. Danny's benchmark (alternative benchmark)

His specification (clarified 3 Nov 2026): cheap = founded_1y_p20 with the all-CRSP reference; all 108,300 fund-months; IV logit. His PDFs use the paper's Hausman IV; the 284 cases he is now running use `IV3_exp_ratio_med` / `_vw`. Code `step32c_danny_benchmark.py`, log `logs/step32c.log`.

| Instrument | Interaction | N | Non-cheap (SE) | × cheap | Total | Min F | e > 0 | Leads t (12/24/36) |
|---|---|---|---|---|---|---|---|---|
| **Paper's Hausman (his PDFs)** | **danny_crsp** | 108,300 | **+5.846 (1.710)** | −20.786 | −14.94 | 44 | **0.254** | −1.1 / 0.8 / 1.8 |
| Paper's Hausman | none (Table 2.0) | 108,300 | −5.606 (1.310) | | | 34 | 0 | −3.3 / −1.5 / 2.1 |
| IV3_exp_ratio_med | danny_crsp | 107,870 | +6.882 (0.947) | −15.902 | −9.02 | 255 | 0.253 | −1.3 / −0.6 / 2.2 |
| IV3_exp_ratio_med | none | 107,870 | +0.758 (0.502) | | | 245 | **1.000** | 2.0 / 4.1 / 6.0 |
| IV3_exp_ratio_vw | danny_crsp | 107,870 | +4.718 (0.738) | −19.196 | −14.48 | 125 | 0.253 | 0.9 / 1.6 / 2.3 |
| IV3_exp_ratio_vw | none | 107,870 | −3.211 (0.359) | | | 124 | 0 | −0.7 / 2.7 / 4.9 |

**Danny's definition gives upward-sloping demand for the non-cheap quarter of fund-months under all three instruments** (+4.7 to +6.9). The failure is in the cheap definition, not the instrument: three quarters of fund-months are "cheap", and the remainder slopes up.

**Danny's sample argument.** He says that dropping rows "puts the other funds into the outside option". That is true of the shares: the mean outside share rises from 0.122 to 0.150 on the 97,429 rows. In logit, though, the outside share enters δ only as a month-level term, so month FE absorb it. On the same rows, the coefficients are identical either way. What the restriction does change is which rows identify α; Table 2's −5.6 depends on the 7,771 rows without a family id (`NOTE_for_coauthor_replication.md` §3). For the supply side (markups, conduct), all 108,300 products can stay in the market: logit markups need only α, the shares and ownership. This is how the downstream step will treat every model.

## 3d. Estimation sample and the "index" definition (benchmark cheap = gene_idx)

`step32d_sample_cluster.py`, log `logs/step32d.log`. Share classes from CRSP flags throughout. The reference row reproduces §3b's Z_flag × gene_idx exactly (−8.019).

| Variant | Rows | Non-cheap (SE) | × cheap | Total | Min F | Avg e | e > 0 | T5 \|e\|>1 | Leads t (12/24/36) |
|---|---|---|---|---|---|---|---|---|---|
| **Z_flag: exclude same asset class** (reference) | 97,294 | **−8.019 (1.306)** | −24.667 | −32.69 | 114 | −3.28 | 0 | 7 | −2.4 / **−4.3** / **−4.0** |
| Z_flag: exclude same **cluster** (`market_m_cluster`) | 97,399 | −3.636 (1.245) | −22.272 | −25.91 | 72 | −2.01 | 0 | 7 | −1.4 / −0.6 / −0.0 |
| Z_flag: exclude same **index** (`market_m_index`; Danny's rule) | 97,399 | −1.253 (0.832) | −20.295 | −21.55 | 103 | −1.30 | 0 | 4 | −0.1 / 0.8 / 1.6 |
| Z_flag, asset class mapped per cluster | 97,164 | −8.040 (1.351) | −25.626 | −33.67 | 93 | −3.33 | 0 | 8 | −2.2 / −3.3 / −4.3 |
| Paper IV, rows with family id | 97,429 | −2.721 (2.752) | −24.089 | −26.81 | 13 | −1.86 | 0 | 7 | −1.9 / −0.4 / 2.2 |
| **Paper IV, all 108,300 rows** | 108,300 | **−8.132 (4.315)** | −32.641 | −40.77 | 18 | −3.93 | 0 | 11 | −3.4 / **−5.3** / −1.7 |
| Z_flag with family-less rows pooled into one "family" | 105,687 | −30.3 (15.1) | −75.1 | −105.4 | **9.8** | −12.3 | 0 | 15 | 3.3 / 3.4 / −1.1 |

**Reading.**
1. **Exclusion ladder: index → cluster → asset class gives −1.3 → −3.6 → −8.0.** All three rungs have valid demand and strong instruments.
2. **The lead tests do not favour the asset-class rung.** The wider the exclusion, the larger the lead t's: |t| ≤ 1.6 for index, 1.4 for cluster, 4.3 for asset class. This contradicts my earlier inference (`RESULTS_danny_iv_compare.md` §3, point 3) that same-asset-class siblings contaminate the narrower instruments. On this evidence the exclusion level is **not settled**, and all three rungs go downstream.
3. **Asset class mapped per cluster** changes 3% of fund-months and the estimates by less than 0.1. It is redundant and dropped.
4. **The sample matters for the paper's IV:** −2.7 on the rows with a family id, −8.1 on all 108,300. The family-less 7% again moves the slope, now with a 24-month lead failure.
5. **Pooling family-less funds into one family fails.** F < 10, an average elasticity of −12 and all 15 Table 5 funds above 1. It is dropped.

## 3e. Rule, universe, or cheap share? Percentiles re-tuned to gene_idx's cheap share

`step37_cheap_share.py`, `logs/step37.log`, `logs/step37_{share,demand}.csv`. Z_flag × I, model 1's 97,294 rows (gene_idx share cheap 0.473). Each definition is re-run at several percentiles q; rows closest to 0.47 in bold.

| Definition (rule, universe) | q | Share cheap | Non-cheap α (SE) | Total cheap | Min F | e > 0 | T5 \|e\|>1 | Leads t (12/24/36) |
|---|---|---|---|---|---|---|---|---|
| gene_idx (Gene, index file) | 20 | 0.473 | −8.02 (1.31) | −32.7 | 114 | 0 | 7 | −2.4 / −4.3 / −4.0 |
| gene_crsp (Gene, all CRSP) | 4 | 0.419 | −3.60 (0.86) | −24.1 | 195 | 0 | 7 | −0.2 / −0.7 / 0.1 |
| **gene_crsp** | **5** | **0.480** | **−6.98 (1.21)** | −28.8 | 164 | **0** | 9 | −2.2 / −3.7 / −3.6 |
| gene_crsp | 7 | 0.569 | −4.63 (0.86) | −24.0 | 184 | 0 | 7 | −3.8 / −6.7 / −6.7 |
| gene_crsp | 10 | 0.678 | +1.55 | −13.4 | 245 | 0.32 | 5 | |
| gene_crsp | 20 | 0.877 | +7.78 | −6.3 | 201 | 0.12 | 2 | |
| danny_crsp (Danny, all CRSP) | 3 | 0.316 | −0.29 (0.69) | −17.8 | 213 | 0 | 2 | 1.5 / 2.1 / 5.0 |
| **danny_crsp** | **5** | **0.433** | **−0.01 (0.81)** | −16.0 | 250 | 0 | 2 | 0.0 / −0.3 / 0.8 |
| danny_crsp | 7 | 0.542 | −0.21 (0.68) | −15.4 | 226 | 0 | 2 | −1.9 / −3.0 / −2.5 |
| danny_crsp | 10–20 | 0.63–0.81 | +4.1 to +7.9 | | | 0.20–0.37 | 2 | |
| danny_idx (Danny, index universe) | 3–10 | 0.32–0.46 | +1.1 to +3.9 | | | 0.54–0.68 | 0–2 | |
| **danny_idx** | **12** | **0.481** | **+3.48 (0.65)** | −6.2 | 214 | **0.52** | 2 | 2.2 / 2.0 / 4.4 |
| danny_idx | 15–20 | 0.52–0.59 | +3.7 to +4.1 | | | 0.41–0.48 | 1 | |

**Reading.**
1. **Gene's rule: the universe does not matter once the cheap share is matched.** With the all-CRSP reference at q = 5 (48% cheap), the non-cheap slope is −7.0, against −8.0 with the index file; same F range, Table 5 count and lead pattern. Gene's rule is valid up to about 57% cheap and fails from 68%.
2. **Danny's rule: matching the share does not fix it.** With the all-CRSP reference, the non-cheap slope is flat (−0.3 to 0.0, not significant) at every share from 32% to 54%, and positive above. With the index universe it slopes **up** at every percentile, including the matched one (+3.5, 52% e > 0).
3. **So the rule matters, not only the share.** Danny's rule ranks a fund's launch fee against the classes launched in the prior year; Gene's ranks the entry fee against every fund alive in the entry month. A fund that was cheap for its launch cohort need not be cheap in the market it competes in. *(Inference: the recent-launch cohort is dominated by high-fee niche products, so Danny's "cheap" picks up funds that are mid-priced in the market and leaves a non-cheap group whose fee variation does not identify a downward slope.)*

## 4a. Downstream set (as of this round)

| # | Demand model | Estimation rows | Demand valid? | Role |
|---|---|---|---|---|
| 1 | Z_flag (exclude asset class) × gene_idx | 97,294 | yes | our preferred spec |
| 2 | Z_flag (exclude cluster) × gene_idx | 97,399 | yes | exclusion ladder |
| 3 | Z_flag (exclude index) × gene_idx | 97,399 | yes | exclusion ladder (Danny's rule) |
| 4 | Z_flag × none | 97,294 | yes (36-month lead t 4.2) | no heterogeneity |
| 5 | Paper IV × gene_idx | 97,429 | yes (F 13) | sample contrast |
| 6 | Paper IV × gene_idx | 108,300 | yes (F 18; 24-month lead t −5.3) | sample contrast |
| 7 | **Danny's benchmark**: paper IV × danny_crsp | 108,300 | no (25% e > 0) | anchor |
| 8 | Paper IV × danny_crsp | 97,429 | no | sample contrast for the anchor |
| 9 | Z_flag × danny_crsp | 97,294 | no (20% e > 0) | bridge: our spec with only the cheap definition changed |

The supply side (markups, MC, scale, conduct) uses all 108,300 fund-months in every model. For #1 and #5 it is also computed on the estimation rows only, to show the outside-option effect Danny raised.

## 4. Implication for the downstream sensitivity analysis (earlier draft, superseded by 4a)

The set of "sensible" demand models in this grid is small: the benchmark, Z × broad and, weakly, the benchmark interaction under the paper's IV. It is too small to show how the downstream results vary across sensible demand. Variants that stay within sensible demand and are already in our reports:

| Variant | Non-cheap | Cheap total | F | e > 0 |
|---|---|---|---|---|
| Benchmark, 10th percentile | −6.46 | −31.7 | 171 | 0 |
| Benchmark, 15th percentile | −9.61 | −35.2 | 173 | 0 |
| Benchmark, month × asset-class FE | −3.80 | −24.0 | 262 | 0 |
| Z × none (common slope) | −1.24 | | 217 | 0; lead-36 t 5.2 |
