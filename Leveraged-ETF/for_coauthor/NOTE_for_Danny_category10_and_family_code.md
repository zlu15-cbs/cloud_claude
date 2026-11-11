# Three points on your 10 Nov notes: your category10 specification, the variable-annuity funds, and V2 as now defined

Danny,

Thank you for the handoff zip. It had what I needed, so the request I was going to make is gone. Two results came out of running your preferred specification next to V2, and I think we need to settle the second before choosing between specifications. Section 3 gives the current definition of V2.

## 1. Your category10 specification reproduces, and it behaves like Table 2

From `classified_donors.csv` and `classified_targets.csv` in your zip I rebuilt your preferred instrument: donors outside the target's exact benchmark and its category10 class, donors with an unknown category left out, pooled share types, lag-AUM weights, and the original IV0 on the 2,502 rows where it is undefined.

| Table 2 specification, 108,300 rows | Price coefficient (SE) | First-stage F | Negative-MC share (B0–B65, own scale) | Vanguard fund-months negative (B0) | Conduct, main instrument |
|---|---|---|---|---|---|
| Original IV0 | −5.606 (1.310) | 33.6 | 0.21–0.36 | 0.81 | PC |
| Yours: benchmark + category10, pooled | **−5.713 (0.747)** | 128.8 | 0.20–0.35 | 0.79 | PC |

- **The coefficient matches yours exactly** (−5.713, SE 0.747, 2,502 rows on the original IV0). The original IV0 also rebuilds exactly from your donor file.
- **Downstream, your specification is almost the same as Table 2.** The stricter exclusion raises the first-stage F but leaves the slope, the marginal costs and the conduct result where they were.
- **Your matched comparison and this note are about the same thing.** You report that the original IV gives +5.247 on the V2-supported rows. Section 2 shows which rows make that difference: the variable-annuity funds.

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

**Your category10 instrument on the same split.**

| | All 108,300 rows | 100,529 rows without the variable-annuity funds |
|---|---|---|
| Table 2 col 2 with your category10 instrument | −5.713 (0.747) | **+1.485 (1.079)** |

The stricter exclusion does not protect the result: without these funds the slope is positive, though not significantly different from zero.

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

## 3. V2 as now defined

The cheap indicator in V2 has changed since the replication note I sent you.

- **Cheap:** a fund is cheap if its expense ratio in its entry month is at or below the 20th percentile of that month's expense ratios across all index funds; ties count as cheap. The entry month is the fund's first month on or after January 2005 with a fee that CRSP reports. It is measured on your source panel (`index_funds_preprocess_oct2026.csv`), which has each fund's first year; the index CSV does not.
- **Why 2005:** the status is fixed five years before the estimation window opens, on a cross-section of 925 funds.
- **Everything else is unchanged:** Z is the median fee of same-family, same-share-type funds in another of the six broad asset classes; money market funds are dropped.

| | Non-cheap α (SE) | × cheap (SE) | Min F | Share e > 0 | Negative MC B0–B65 (own η) |
|---|---|---|---|---|---|
| **V2 now** (2005 start, source panel, 20th percentile) | −3.385 (0.541) | −20.059 (0.784) | 177 | 0 | 0.067–0.087 |
| 15th percentile | −7.527 (0.880) | −29.120 (1.972) | 128 | 0 | 0.000–0.001 |
| 25th percentile | −3.967 (0.607) | −17.409 (0.840) | 144 | 0 | 0.018–0.026 |
| V2 as first sent (cheap from a fund's first month in the index CSV) | −3.642 (0.419) | −20.562 (0.646) | 316 | 0 | 0.053–0.082 |

- **V2 does not use the variable-annuity funds to estimate demand** (they have no family donors), so excluding them changes only the supply side: negative MC 0.054–0.081.
- **With your category10 classes as the exclusion, V2's non-cheap slope turns positive** (+1.562, SE 0.751; 51% of fund-months slope upward). V2 therefore rests on excluding the whole broad asset class. The argument is that a family's funds in the same broad asset class share demand shocks; I would like your view on it.
- **The size of the non-cheap slope depends on round-number fees at the cutoff.** With the index CSV for both the cheap status and the donors it is −8.4 at the 20th percentile (−3.0 with the source panel for both), because the source cutoff in January 2005 is exactly 0.25%. At the 25th percentile the two files agree (−3.6 and −4.2).

Details: `RESULTS_spec_summary.md`, section 3.

Code: `code/spec_compare/sc_a5.py`, `sc_broad_ladder.py`, `sc_v2_robust.py`. Logs: `logs/spec_compare/sc_a5_demand.csv`, `sc_broad_ladder.csv`.

Gene
