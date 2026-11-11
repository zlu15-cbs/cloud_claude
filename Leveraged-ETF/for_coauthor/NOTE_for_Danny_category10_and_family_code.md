# Two points on your 10 Nov note: the category10 labels, and the rows without a family code

Danny,

Two things came out of running your preferred specification next to V2. The first is a request. The second is a result on the Table 2 sample that I think we need to settle before choosing between specifications.

## 1. Where are the category10 labels and the rebuilt IV0 saved?

Your preferred specification is Table 2 unchanged except for IV0, which excludes donors on the target's exact benchmark and in its category10 class (pooled share types, lag-AUM weights, original IV0 where undefined). Your result is −5.713 (0.747).

I cannot reproduce it, because the category10 labels are not in the files I have. Could you tell me where these are saved, or send them?

- **The labels:** category10 and category20 per fund (`crsp_fundno`) or per tracked index.
- **The instrument:** the rebuilt IV0 per fund-month for category10 pooled, both the raw version and the hybrid with the fallback flag. Your note points to `results/hausman-robustness-v1/` and `results/table2-hausman-only-v1/continuation-20261109/`, but the donor panels and arrays are local and not in the repository.

**Why it matters.** I built a proxy with the Lipper 6 asset groups in place of category10. It does not match your number:

| IV0 construction (Table 2 specification, 108,300 rows) | Price coefficient (SE) | First-stage F | Rows on original IV0 |
|---|---|---|---|
| Original IV0 | −5.606 (1.310) | 33.6 | – |
| Yours: benchmark + category10, pooled | −5.713 (0.747) | | 2,502 |
| My proxy: benchmark + Lipper 6, pooled, blank families matched | −7.254 (0.456) | 231.0 | 2,492 |
| My proxy, original IV0 on the rows without a family code | −9.107 (0.912) | 86.6 | 10,263 |
| My rebuild of the original IV0 from my donor file (benchmark only) | −4.741 (1.192) | 36.1 | 7,793 |

- The last row shows that the donor file alone moves the coefficient by 0.9. I have since found your source panel (`index_funds_preprocess_oct2026.csv`, 675,551 rows) in the shared Dropbox. The index CSV is that panel after the estimation filter, so 60,773 rows that are donors in IV0 are missing from my rebuild. I can redo the proxy on the full panel; what I still need from you are the category10 labels.
- With your instrument values I can run your specification through the same downstream steps as V2 (scale, marginal costs, conduct) and compare them on equal terms.

## 2. The Table 2 results depend on the 7,771 fund-months without a family code

Your note says that blank family strings match one another in the original IV0, and that this affects 7,771 target observations. I split the Table 2 sample on that line. The instrument is the original IV0 throughout, and everything else is the notebook's specification.

| Specification | All 108,300 rows | 100,529 rows with a family code | 7,771 rows without one |
|---|---|---|---|
| **Table 2 col 2** (one slope) | **−5.606 (1.310)**; F 33.6 | **+7.244 (1.987)**; F 26.6 | **+2.322 (0.538)**; F 57.2 |
| **Broad-based interaction** (Table A7 in my copy of the draft): specialized | **−7.503 (1.770)** | **+4.009 (1.588)** | +0.747 (0.293) |
| × broad-based | −5.278 (0.372) | −6.924 (0.428) | +4.884 (1.840) |
| First-stage F (min) | 53.0 | 49.0 | 11.3 |
| Share of fund-months with e > 0 | 0 | 0.49 | 1.00 |

The first column reproduces the paper exactly (−5.606; −7.503 and −5.278).

**What the 7,771 rows are: variable-annuity funds.**
- All 112 funds are flagged as variable-annuity underlying funds in CRSP (`vau_fund` = Y). None of the other 1,190 funds in the sample is.
- Examples: VALIC Company I Stock Index Fund, Voya US Stock Index Portfolio, Prudential Series Fund Stock Index Portfolio, Vanguard Variable Insurance Fund Equity Index Portfolio, John Hancock Variable Insurance Trust 500 Index Trust, Allianz AZL S&P 500 Index Fund, Nationwide NVIT Bond Index Fund. The list is in `logs/spec_compare/sc_blank_family_funds.csv`.
- **Why the family code is blank.** CRSP has no `mgmt_cd` for any of them, in any quarter, and `firm_f_old` is built from `mgmt_cd`. CRSP does have `mgmt_name` and `adv_name` for all 112, and the CSV has the parent firm (`firm_f`) for all of them. So the family can be recovered.
- They are sold only inside insurance contracts, with no ETFs among them. Their mean fee is 0.61%, against 0.29% for the sample. A few are not plain index funds (Russell Multi-Style Equity, Nationwide Investor Destinations, Transamerica JPMorgan Enhanced Index).
- Their fees move four times as much within fund as the other funds' fees (standard deviation 0.133 against 0.034, after fund and month effects).
- Their IV0 is not a family instrument. Because blank families match one another, the donors are other firms' variable-annuity funds. In a typical month there are 12 distinct IV0 values across 46 such rows.

**What happens when their families are recovered.** I rebuilt IV0 for these rows only (benchmark exclusion, lag-AUM weights), and kept your original IV0 for all other rows.

| IV0 for the variable-annuity rows | Table 2 col 2, all rows | First-stage F | Broad-based: specialized; × broad; share e > 0 |
|---|---|---|---|
| Original (all blank families pooled) | −5.606 (1.310) | 33.6 | −7.503; −5.278; 0 |
| Donors: the same parent firm's other variable-annuity funds | −0.217 (0.048) | 344.6 | +0.809; −1.460; 0.47 |
| Donors: all funds of the parent firm (`firm_f`) | −0.340 (0.049) | 313.5 | +0.791; −1.636; 0.47 |

- With a proper family instrument for these funds, the Table 2 coefficient falls from −5.6 to about −0.3.
- **This estimate is not credible either, because the fees of these funds are imputed.** In 85% of firm-months, every variable-annuity fund of a firm has the same expense ratio in the CSV. Allianz's funds are all at 0.400% in 2010–2016, 0.535% in 2018 and 0.458% in 2020.
- **CRSP does not report their fees.** It has no expense ratio in 97% of these funds' quarterly records (6% for the other funds), and none at all for 99 of the 112.
- **The build script fills them in** (`5_fund_market_data_for_Matteo_v6_nonlev_etf.R`, lines 89–99): a missing expense ratio becomes the mean fee of funds whose names share the same first five letters. The "price" of a variable-annuity fund is therefore close to the average fee of its firm's other funds, and a family instrument is nearly that same number.

**Why I think this is a problem.**
- **The sign is fragile.** Demand slopes upward on the rows with a family code and upward on the rows without one. It slopes downward only when the two are pooled. The negative coefficient therefore comes from comparing the two groups through the common month effects, not from fee variation within either group. That last sentence is my reading of the three columns; I have not decomposed it further.
- **It is hard to defend economically.** The paper's identification argument is that a family's fees on other products shift this product's fee. For these rows the instrument averages the fees of unrelated insurers' funds. Removing the rows reverses the result, and so does giving them their true families.
- **The broad-based table inherits it.** With a family code, specialized funds slope upward (+4.0) and 49% of fund-months have e > 0. Estimated on their own, specialized funds slope upward under every instrument I tried, including the original IV0 on all rows (+19.9, SE 5.3).
- **The stricter exclusions help, which supports your direction.** On the rows with a family code, the one-slope coefficient is +6 to +10 with the benchmark-only exclusion and −1.3 to −0.3 with an asset-class exclusion.

**The same split for the fee-based interactions** (original IV0):

| Specification | All 108,300 rows | 100,529 rows with a family code |
|---|---|---|
| Price × cheap (gene_idx): non-cheap; × cheap; F | −8.13 (4.32); −32.64 (4.20); 18.3 | −13.99 (7.07); −31.23 (4.55); 7.9 |
| Price × fee tercile at the first sample month: top; × low; × middle; F | −3.71 (6.13); −52.70; −11.99; 22.6 | −18.68 (8.94); −49.36; −10.61; 11.9 |

These keep their sign, but the base slope is not identified in either sample and the first stage weakens. The interaction coefficients are stable.

**What I am asking you.**

1. **Please confirm my reading of the fee imputation** (lines 89–99 of the build script), and tell me if the variable-annuity funds' fees were meant to be handled differently.
2. **How should the paper treat these 112 funds?** We know their families, so the choice is ours:
    - **(a) As now:** pooled as one "family". Table 2 is −5.606, but it rests on an instrument built from unrelated insurers' funds and on imputed prices.
    - **(b) With their true families:** Table 2 is about −0.3, which is close to regressing an imputed fee on itself.
    - **(c) Excluded from the sample.** Gene's proposal, and mine. They are sold inside insurance contracts and their prices are not observed. With the original IV0, Table 2 then gives +7.244, so the paper needs a different instrument or specification. `RESULTS_spec_summary.md` compares the candidates with and without these funds.

The split is easy to replicate: drop the 7,771 fund-months with a blank `firm_f_old` from the Table 2 sample and re-estimate, with nothing else changed.

Code: `code/spec_compare/sc_a5.py` and `sc_broad_ladder.py`. Logs: `logs/spec_compare/sc_a5_demand.csv`, `sc_broad_ladder.csv`.

Gene
