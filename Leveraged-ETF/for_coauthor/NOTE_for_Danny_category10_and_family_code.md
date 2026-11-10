# Two points on your 10 Nov note: the category10 labels, and the rows without a family code

Danny,

Two things came out of running your preferred specification next to V2. The first is a request. The second is a result on the Table 2 sample that I think we need to settle before choosing between specifications.

## 1. Where are the category10 labels and the rebuilt IV0 saved?

Your preferred specification is Table 2 unchanged except for IV0, which excludes donors on the target's exact benchmark and in its category10 class (pooled share types, lag-AUM weights, original IV0 where undefined). Your result is −5.713 (0.747).

I cannot reproduce it, because the category10 labels are not in the files I have. Could you tell me where these are saved, or send them?

- **The labels:** category10 and category20 per fund (`crsp_fundno`) or per tracked index.
- **The instrument:** the rebuilt IV0 per fund-month for category10 pooled, both the raw version and the hybrid with the fallback flag. Your note points to `results/hausman-robustness-v1/` and `results/table2-hausman-only-v1/continuation-20261109/`, but the donor panels and arrays are local and not in the repository.
- **The donor panel**, if it is easy to share: your source panel has 675,551 passive rows and my index CSV has 579,632.

**Why it matters.** I built a proxy with the Lipper 6 asset groups in place of category10. It does not match your number:

| IV0 construction (Table 2 specification, 108,300 rows) | Price coefficient (SE) | First-stage F | Rows on original IV0 |
|---|---|---|---|
| Original IV0 | −5.606 (1.310) | 33.6 | – |
| Yours: benchmark + category10, pooled | −5.713 (0.747) | | 2,502 |
| My proxy: benchmark + Lipper 6, pooled, blank families matched | −7.254 (0.456) | 231.0 | 2,492 |
| My proxy, original IV0 on the rows without a family code | −9.107 (0.912) | 86.6 | 10,263 |
| My rebuild of the original IV0 from my donor file (benchmark only) | −4.741 (1.192) | 36.1 | 7,793 |

- The last row shows that the donor file alone moves the coefficient by 0.9, so I cannot tell how much of the gap is the classification and how much is the donors.
- With your instrument values I can run your specification through the same downstream steps as V2 (scale, marginal costs, conduct) and compare them on equal terms.

## 2. The Table 2 results depend on the 7,771 fund-months without a family code

Your note says that blank family strings match one another in the original IV0, and that this affects 7,771 target observations. I split the Table 2 sample on that line. The instrument is the original IV0 throughout, and everything else is the notebook's specification.

| Specification | All 108,300 rows | 100,529 rows with a family code | 7,771 rows without one |
|---|---|---|---|
| **Table 2 col 2** (one slope) | **−5.606 (1.310)**; F 33.6 | **+7.244 (1.987)**; F 26.6 | **+2.322 (0.538)**; F 57.2 |
| Lead tests, t (12/24/36 months) | −3.3 / −1.5 / 2.1 | 6.7 / 11.6 / 18.9 | 0.1 / −0.3 / −0.2 |
| **Broad-based interaction** (Table A7 in my copy of the draft): specialized | **−7.503 (1.770)** | **+4.009 (1.588)** | +0.747 (0.293) |
| × broad-based | −5.278 (0.372) | −6.924 (0.428) | +4.884 (1.840) |
| First-stage F (min) | 53.0 | 49.0 | 11.3 |
| Share of fund-months with e > 0 | 0 | 0.49 | 1.00 |
| Lead tests, t (12/24/36 months) | −5.3 / −4.9 / −2.4 | 4.1 / 10.9 / 16.4 | −0.9 / −2.5 / −2.2 |

The first column reproduces the paper exactly (−5.606; −7.503 and −5.278).

**What the 7,771 rows are.**
- 112 mutual-fund share classes and no ETFs. Most are insurance and retirement-channel trusts: Voya, Allianz, John Hancock, Nationwide, American General, Principal, Mutual of America. Some are Vanguard classes.
- Their mean fee is 0.61%, against 0.29% for the sample.
- Their fees move four times as much within fund as the other funds' fees (standard deviation 0.133 against 0.034, after fund and month effects).
- Their IV0 is not a family instrument. Because blank families match one another, the donors are other firms' family-less funds. In a typical month there are 12 distinct IV0 values across 46 such rows.

**Why I think this is a problem.**
- **The sign is fragile.** Demand slopes upward on the rows with a family code and upward on the rows without one. It slopes downward only when the two are pooled. The negative coefficient therefore comes from comparing the two groups through the common month effects, not from fee variation within either group. That last sentence is my reading of the three columns; I have not decomposed it further.
- **It is hard to defend economically.** The paper's identification argument is that a family's fees on other products shift this product's fee. For these rows there is no family, and the instrument averages the fees of unrelated firms. Yet removing them reverses the result.
- **The broad-based table inherits it.** With a family code, specialized funds slope upward (+4.0) and 49% of fund-months have e > 0. Estimated on their own, specialized funds slope upward under every instrument I tried, including the original IV0 on all rows (+19.9, SE 5.3).
- **The stricter exclusions help, which supports your direction.** On the rows with a family code, the one-slope coefficient is +6 to +10 with the benchmark-only exclusion and −1.3 to −0.3 with an asset-class exclusion. The lead-test t-statistics fall from 10–17 to 3–7.

**The same split for the fee-based interactions** (original IV0):

| Specification | All 108,300 rows | 100,529 rows with a family code |
|---|---|---|
| Price × cheap (gene_idx): non-cheap; × cheap; F | −8.13 (4.32); −32.64 (4.20); 18.3 | −13.99 (7.07); −31.23 (4.55); 7.9 |
| Price × fee tercile at the first sample month: top; × low; × middle; F | −3.71 (6.13); −52.70; −11.99; 22.6 | −18.68 (8.94); −49.36; −10.61; 11.9 |

These keep their sign, but the base slope is not identified in either sample and the first stage weakens. The interaction coefficients are stable.

**What I am asking you to do.**

1. **Please rerun the split on your data and tell me whether you get the same signs.**
    - Take your Table 2 sample (108,300 fund-months) and drop the 7,771 fund-months where `firm_f_old` is blank. That leaves 100,529.
    - Re-estimate two models on those 100,529 rows, with nothing else changed: Table 2 col 2 (logit IV, original IV0), and the broad-based interaction (Table A7 col 2).
    - I get a price coefficient of **+7.244** for Table 2, and **+4.009** (specialized) with **−6.924** (× broad-based) for the interaction. Do you?
2. **Can you find out who manages the 112 funds with a blank `firm_f_old`?**
    - In the index CSV their family code is missing, so the original IV0 treats all of them as one family.
    - Does your source panel, or CRSP (`mgmt_cd`, `mgmt_name`), have a management company for them?
    - If it does, please send me the fund-to-family mapping, or rebuild IV0 for these funds with their true families. I will then rerun the table above.
3. **If their families cannot be recovered, which of these two options do you prefer?**
    - **(a) Keep them in the demand estimation as now.** Table 2 stays at −5.606, but the negative sign depends on rows whose instrument is built from unrelated firms.
    - **(b) Keep them in the market but not in the demand estimation.** They still count in the market shares, the outside good and the supply side; they are only left out when the price coefficient is estimated. This is what V2 does. With the original IV0, Table 2 then gives +7.244, so the paper would need a different instrument or specification.

Code: `code/spec_compare/sc_a5.py` and `sc_broad_ladder.py`. Logs: `logs/spec_compare/sc_a5_demand.csv`, `sc_broad_ladder.csv`.

Gene
