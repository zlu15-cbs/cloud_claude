# Which demand specification for the index market: Table 2, the fee-tercile interaction, V2, Danny's stricter Hausman exclusion, or V2 without the cheap interaction?

## Key takeaways

1. **Goal A (no upward-sloping demand) does not separate the five specifications: all have a zero share of e > 0.**
    - The other demand criteria do. First-stage F: V2 316, proxy 4p 87, T2 34, A5 23.
    - A5's top-tercile slope is −3.7 with an SE of 6.1, so its base slope is not identified.
2. **Goal B (fewer negative MCs) ranks them A5 < 4p ≈ V2 < T2 < V2 without cheap.**
    - Negative-MC share at each candidate's own η, B0–B65: A5 0.001; 4p 0.006–0.163; V2 0.053–0.082; T2 0.21–0.36; spec 5 1.00.
    - T2's negatives sit at Vanguard (81% of its fund-months at B0) and reach SPY at B65. Securities lending cannot explain either.
    - 4p is clean at B0 and B25, but at B65 54% of Vanguard fund-months are negative.
3. **Goal C (literature): V2 and T2 give average elasticities inside the 1.6–2.5 range of Brown, Egan, Jeon, Jin and Wu (2026); A5 is above it and spec 5 far below.**
    - Average own elasticity: T2 −1.61, V2 −1.93, 4p −2.62, A5 −3.75, spec 5 −0.08.
    - Weighted by assets the specifications separate: T2 −0.72, 4p −1.17, V2 −1.61, A5 −2.97. A single slope leaves the largest funds inelastic (S&P 500 ETFs at −0.16 to −0.26).
4. **Danny's fragility point shows that the fee slope is heterogeneous, not that V2's sign is fragile.**
    - One common slope on V2's rows is −0.32 (SE 0.29). Danny reports +0.002 (0.324). We agree.
    - Estimated separately with the same Z, both groups slope down: cheap −43.0 (4.8), non-cheap −1.42 (0.35).
    - The pooled slope sits near the non-cheap one because non-cheap funds carry 90% of the first-stage weight.
    - The magnitudes do depend on what is pooled: the non-cheap slope is −1.42 alone and −3.64 inside V2.
5. **Goal D: the scale η is insensitive to demand; negative MC is highly sensitive; the conduct test is partly sensitive.**
    - η is 0.019–0.022 in specifications 1 to 4 under every candidate (SE 0.005). Only the flat spec 5 moves it (0.030–0.034, SE 0.012–0.034).
    - B0 and B25 are rejected in every specification, under every instrument and η scheme.
    - Whether B50 and B65 survive depends on demand: T2 selects PC alone, 4p selects PC and B65 (p = 0.06), V2 cannot separate PC, B50 and B65.
    - PC is the best-fitting model everywhere except under A5, where B65 fits best, PC is kept at p = 0.06 and one alternative instrument rejects it.
6. **The open choice is between V2 and a single-slope model with a stricter exclusion (4p), and it turns on Danny's actual category10 instrument, which we do not have.**
    - Our proxy 4p gives −9.11 against his −5.71, so 4p's good MC results may not carry over to his instrument.
    - A5 has the best MC and Table 5 results but does not identify its base slope.

## Scorecard: all 5 models

**Caution.** Specification 4p is a proxy for Danny's preferred instrument: it uses the Lipper 6 asset groups in place of his category10 labels and our 579,632-row donor file in place of his 675,551-row panel, and it does not reproduce his coefficient (−9.11 against −5.71). Specifications 1, 2 and 4p keep the 4 money market funds (437 fund-months) that are in the Table 2 sample; 3 and 5 drop them. No test here establishes that any instrument satisfies the exclusion restriction.

✓ = desirable, ~ = borderline, ✗ = undesirable, – = not applicable. Downstream rows give the range over B0–B65 at each candidate's own estimated η; conduct uses η scheme A (0.024). Sources: `logs/spec_compare/sc_demand.csv`, `sc_table5.csv`, `sc_scale.csv`, `sc_mc.csv`, `sc_where.csv`, `sc_conduct_*.csv`.

| | 1 T2 | 2 A5 | 3 V2 | 4p Danny (proxy) | 5 V2 no-cheap |
|---|---|---|---|---|---|
| **Specification** | | | | | |
| Instrument | paper IV0 | paper IV0 | Z (V2) | IV0 rebuilt, stricter exclusion | Z (V2) |
| Donors exclude the target's | index | index | Lipper-6 asset class, other share types | index and Lipper-6 asset class | Lipper-6 asset class, other share types |
| Donor aggregation | lag-AUM-weighted mean | lag-AUM-weighted mean | median | lag-AUM-weighted mean | median |
| Price interaction | none | fee tercile at first sample month | cheap (gene_idx) | none | none |
| Estimation rows | 108,300 | 108,300 | 96,069 | 108,300 (10,263 on original IV0) | 96,069 |
| **Demand outcomes** | | | | | |
| Price coefficient (SE) | −5.606 (1.310) | −3.71 (6.13) top tercile | −3.642 (0.419) non-cheap | −9.107 (0.912) | −0.319 (0.289) |
| Interaction (SE) | – | −52.70 (7.57) low; −11.99 (0.98) middle | −20.562 (0.646) | – | – |
| Average own elasticity | −1.61 | −3.75 | −1.93 | −2.62 | −0.08 |
| Asset-weighted own elasticity | −0.72 | −2.97 | −1.61 | −1.17 | −0.04 |
| Table 5 funds with \|e\| > 1 | 2/15 | 13/15 | 5/15 | 2/15 | 0/15 |
| **Demand screens** | | | | | |
| Goal A: no upward slope (e > 0 share) | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| First-stage F (min) | ✓ 34 | ✓ 23 | ✓ 316 | ✓ 87 | ✓ 384 |
| Slope precisely estimated for every group | ✓ | ✗ top tercile SE 6.1 | ✓ | ✓ | ✗ zero |
| **Downstream outcomes** | | | | | |
| Scale η range (PC–B65; SE about 0.005) | 0.0205–0.0213 | 0.0189–0.0205 | 0.0210–0.0220 | 0.0205–0.0210 | 0.0211–0.0339 (SE up to 0.034) |
| Negative-markup share | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| Negative-MC share, η = 0 | 0.52–0.58 | 0.06–0.18 | 0.33–0.46 | 0.40–0.49 | 1.00 |
| Negative-MC share, η = 0.024 | 0.17–0.34 | 0–0.001 | 0.04–0.07 | 0–0.09 | 1.00 |
| Goal B: negative-MC share, own η | 0.21–0.36 | 0.001 | 0.053–0.082 | 0.006–0.163 | 1.00 |
| Min MC (% of assets) | −0.31 | −0.11 | −0.21 | −0.12 | −8.42 |
| **MC screens** | | | | | |
| Magnitude: ≤ 2% below −0.20%, none below −0.60% | ~ B0–B50 pass; B65 8.9% | ✓ | ✓ | ✓ | ✗ |
| Location: not at Vanguard or SPY | ✗ Vanguard 81% (B0); SPY 85% (B65) | ✓ almost none | ✗ Vanguard 13% (B0); SPY never | ~ Vanguard 2% (B0), 54% (B65); SPY never | ✗ everywhere |
| **Conduct** | | | | | |
| Main IV selected set | PC | PC (p 0.06), B50 (0.06), B65 | PC, B50, B65 | PC, B65 (p 0.06) | PC (test F = 1: uninformative) |
| Alternative IVs (majority) | PC | PC, B65 (rival3: B50, B65; PC rejected) | PC | PC | PC |
| B0 and B25 rejected | ✓ | ✓ | ✓ | ✓ | ✓ |
| Robust to η scheme and capping | ✓ | ~ B50 enters or leaves at p 0.05–0.10 | ✓ | ✓ | ✓ |
| **Overall** | **demand passes goal A; MC fails at Vanguard** | **best MC and Table 5; imprecise base slope** | **passes demand screens; MC location caveat** | **proxy only: good MC at B0/B25** | **flat demand; MC fails; not a usable model** |

- **Code:** `code/spec_compare/sc_build.py` (panel and instruments), `sc_demand.py` (demand fits), `sc_downstream.py` (scale, MC, location, conduct), `replicate_V2.py` (copy of the V2 script, whose functions the three scripts call).
- **Logs and CSVs:** `logs/spec_compare/`.
- **Supply sample:** all 108,300 fund-months for specifications 1, 2, 4p and 4q; 107,863 (money market funds dropped) for 3 and 5. Rows outside the demand estimation stay in the shares and on the supply side.
- **Proxy 4q** (exposure class = `market_m_cluster`, 785 clusters) is reported in the sections below and not in the scorecard.

## 0. Validation

| Check | Result |
|---|---|
| T2: paper's Table 2 col 2, −5.606 (1.310), F 33.6 | **−5.606 (1.310), F 33.6**: exact |
| A5: earlier run in `OTHER_SPECS_explored.md` §1, −3.714 (6.133); −52.7; −12.0; F 22.6; 13/15 | **−3.714 (6.133); −52.70; −11.99; F 22.6; 13/15**: exact. The paper has no Table A5 demand specification in `EXPECTED_RESULTS.md`, so A5 is the fee-tercile interaction of `CLOUD_PROMPT_explore_price_heterogeneity.md` |
| V2: N 96,069; −3.642 (0.419); −20.562 (0.646); F 315.8; 5/15 | **exact on every number** |
| V2 downstream: negative MC 0.053–0.082; min MC −0.212; conduct PC, B50 (0.19), B65 (0.79) | **exact** |
| Danny's preferred, category10 pooled: −5.713 (0.747), 2,502 fallback rows | **not reproduced: proxy 4p gives −9.107 (0.912)** with 10,263 fallback rows. With blank family codes matched to one another, as in his construction: −7.254 (0.456), 2,492 fallback rows |
| Our rebuilt IV0 with the paper's own exclusion (index only) against the original IV0 | equal within 0.0005 on 90% of the rows with a family code; T2 with it gives **−4.741 (1.192)** against −5.606. The donor-file gap alone moves the slope by 0.9 |
| Danny's pooled return-cluster exclusion: −5.206 (1.162) | proxy 4q (`market_m_cluster`): −4.516 (1.164). His clusters may not be `market_m_cluster` |
| Danny's V2 without interactions: +0.0020 (0.3240) on 96,047 rows | **−0.319 (0.289)** on 96,069 rows: both are zero within one SE |
| T2 negative-MC share, B0, η = 0: Danny's 0.5156 | **0.516** |
| Scale under PC: Danny's 0.0205 (0.0051) | **0.0205 (0.0051)** |

## 1. Demand: every specification slopes down; V2 has by far the strongest first stage

| # | Specification | N | Price (SE) | Interaction (SE) | Min F | e > 0 | Avg e | Table 5 \|e\| > 1 |
|---|---|---|---|---|---|---|---|---|
| 1 | T2 | 108,300 | −5.606 (1.310) | | 33.6 | 0 | −1.61 | 2/15 |
| 2 | A5 | 108,300 | −3.714 (6.133) | low −52.70 (7.57); middle −11.99 (0.98) | 22.6 | 0 | −3.75 | 13/15 |
| 3 | V2 | 96,069 | −3.642 (0.419) | cheap −20.562 (0.646) | 315.8 | 0 | −1.93 | 5/15 |
| 4p | Danny proxy, Lipper 6 | 108,300 | −9.107 (0.912) | | 86.6 | 0 | −2.62 | 2/15 |
| 4q | Danny proxy, cluster | 108,300 | −4.516 (1.164) | | 37.6 | 0 | −1.30 | 1/15 |
| 5 | V2 without cheap | 96,069 | −0.319 (0.289) | | 383.5 | 0 | −0.08 | 0/15 |

**Table 5 funds** (own elasticity in the fund's last market; `sc_table5.csv`).

| Fund | Fee (%) | 1 T2 | 2 A5 | 3 V2 | 4p | 5 |
|---|---|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | −0.16 | −1.64 | −0.70 | −0.26 | −0.01 |
| iShares Core MSCI EAFE ETF | 0.07 | −0.39 | −3.92 | −1.68 | −0.63 | −0.02 |
| iShares Core US Aggregate Bond ETF | 0.03 | −0.17 | −0.47 | −0.72 | −0.27 | −0.01 |
| iShares Russell 1000 Growth ETF | 0.18 | −1.00 | −2.81 | −4.33 | −1.63 | −0.06 |
| iShares Core S&P Mid-Cap ETF | 0.05 | −0.28 | −0.78 | −1.20 | −0.45 | −0.02 |
| SPDR S&P 500 ETF Trust | 0.09 | −0.49 | −4.90 | −2.10 | −0.79 | −0.03 |
| SPDR Gold Shares | 0.40 | −2.23 | −6.26 | −1.45 | −3.63 | −0.13 |
| Technology Select Sector SPDR | 0.08 | −0.45 | −1.25 | −0.29 | −0.73 | −0.03 |
| Financial Select Sector SPDR | 0.08 | −0.45 | −1.25 | −0.29 | −0.73 | −0.03 |
| SPDR Portfolio S&P 500 ETF | 0.02 | −0.11 | −1.13 | −0.48 | −0.18 | −0.01 |
| Vanguard Total Stock Market, Institutional Plus | 0.02 | −0.11 | −1.08 | −0.46 | −0.17 | −0.01 |
| Vanguard 500 Index, Admiral | 0.04 | −0.22 | −2.18 | −0.94 | −0.35 | −0.01 |
| Vanguard 500 Index, ETF | 0.03 | −0.16 | −1.64 | −0.70 | −0.26 | −0.01 |
| Vanguard Total Stock Market, ETF | 0.03 | −0.16 | −1.65 | −0.71 | −0.27 | −0.01 |
| Vanguard Total Stock Market, Admiral | 0.04 | −0.22 | −2.20 | −0.94 | −0.36 | −0.01 |

**Reading.**
- **Goal A is met by all of them.** No fund-month has e > 0 in any of the six fits.
- **V2 has the strongest first stage** (F 316, against 23 to 87 for the others).
- **A5 buys its elasticities with an unidentified base slope.** The top fee tercile (a third of the funds, mean fee 0.61%) has −3.7 with an SE of 6.1. The tercile is also set at the first sample month, which the earlier work flagged as endogenous to the sample window (`OTHER_SPECS_explored.md` §2).
- **A single slope cannot give the large funds |e| > 1.** T2 and 4p leave the S&P 500 funds at −0.11 to −0.26, whatever the instrument.

## 2. Danny's fragility claim: one common slope hides two negative slopes of very different size

Same rows (96,069), same Z, same controls and fixed effects as V2 (`sc_split.csv`, `sc_split_common_fe.csv`, `sc_demand.csv` rows `x_5_*`).

**What specification 5 is.** Cheap is fixed per fund, so its level is absorbed by the fund fixed effects. Removing "the cheap indicator" therefore means removing price × cheap and Z × cheap together. One slope is estimated for all funds.

| | All rows (spec 5) | Cheap funds only | Non-cheap funds only | V2 (interacted) |
|---|---|---|---|---|
| Fund-months (share) | 96,069 | 45,174 (47.0%) | 50,895 (53.0%) | 96,069 |
| Mean fee (%) | 0.26 | 0.10 | 0.40 | |
| Fee slope (SE) | **−0.319 (0.289)** | **−43.02 (4.81)** | **−1.418 (0.353)** | cheap −24.20; non-cheap −3.642 (0.419) |
| First-stage F | 383.5 | 56.7 | 315.7 | 315.8 |
| Average own elasticity | −0.08 | −4.48 | −0.57 | −1.93 |
| Within-fund SD of the fee (%) | 0.034 | 0.020 | 0.043 | |
| First-stage weight in a pooled slope (share of Σ Z·p) | 1 | 0.10 | 0.90 | |
| Contribution in the pooled regression's residuals: slope (weight) | −0.319 | −10.05 (0.15) | +1.38 (0.85) | |

**Reading.**
- **We confirm Danny's number.** One common slope is −0.32 (SE 0.29) against his +0.002 (0.324).
- **This shows heterogeneity, not a fragile sign.** With the same instrument, cheap funds have a slope of −43 and non-cheap funds −1.4. Both are negative and both are significant.
- **The pooled slope is near zero because it is a first-stage-weighted average.** Non-cheap funds have twice the within-fund fee variation and carry 90% of the weight, so the pooled slope sits close to their small slope and the cheap funds' steep slope is almost lost. Forcing common month effects on the two groups then moves it the rest of the way to zero (last row: the non-cheap contribution turns to +1.38). The last step is my inference from the two decompositions, not a separate test.
- **V2's magnitudes do depend on what is pooled.** The non-cheap slope is −1.42 on its own subsample and −3.64 inside V2, where the two groups share month effects and controls. The cheap slope is −43 alone and −24 inside V2. The sign and the ranking are stable; the size of the non-cheap slope is not.
- **Specification 5 is not a usable demand model.** It implies an average elasticity of −0.08 and markups of 4 to 5 percentage points (`sc_mc.csv`).

## 3. Danny's stricter exclusion: the proxy steepens the single slope and removes most negative MCs, but it is not his instrument

| Instrument (no interaction, 108,300 rows) | Price (SE) | Min F | Rows on original IV0 | Source |
|---|---|---|---|---|
| Original IV0 (T2) | −5.606 (1.310) | 33.6 | – | paper |
| Our rebuilt IV0, index exclusion | −4.741 (1.192) | 36.1 | 7,793 | validation |
| **4p: index + Lipper-6 exclusion** | **−9.107 (0.912)** | 86.6 | 10,263 | proxy |
| 4p with blank families matched | −7.254 (0.456) | 231.0 | 2,492 | proxy |
| 4q: index + cluster exclusion | −4.516 (1.164) | 37.6 | 7,814 | proxy |
| Danny: category10, pooled | −5.713 (0.747) | | 2,502 | his note |
| Danny: return cluster, pooled | −5.206 (1.162) | | | his note |
| Danny: category10, same type | −2.166 (0.297) | | 3,194 | his note |

**Reading.**
- **The direction matches Danny's finding.** A broader exposure exclusion keeps demand sloping down and strengthens the first stage (F 34 → 87).
- **The level does not.** Our proxy gives −9.1 or −7.3 against his −5.7. Two things differ: the exposure classes (Lipper 6 against his category10) and the donor file (579,632 rows against his 675,551).
- **Blank family codes matter.** On the 7,771 rows without `firm_f_old`, our rebuilt instrument is negatively correlated with the original IV0 (−0.21), so our file cannot reproduce his values there. In 4p those rows use the original IV0.
- **No sixth specification was added.** His category10 same-type result (−2.17) is flatter than the pooled one, so it would raise negative MCs; in our files the nearest construction is specification 5.

## 4. Money market funds and the estimation rows: the single-slope results depend on both

| Specification | As specified | Without the 4 money market funds | On V2's 96,069 rows |
|---|---|---|---|
| T2 | −5.606 (1.310) | −4.264 (0.993) | **+7.834 (2.333)** |
| A5 (top tercile; low; middle) | −3.71; −52.70; −11.99 | −4.70; −56.69; −10.64 | not run |
| 4p | −9.107 (0.912) | −7.931 (0.714) | −4.555 (0.663) |
| 4q | −4.516 (1.164) | −3.382 (0.918) | not run |
| V2 | – | −3.642 (0.419) | −3.642 (0.419) |

**Reading.**
- **The 437 money market fund-months steepen every single-slope model by 1.1 to 1.3.** They are not index funds.
- **The paper's instrument slopes upward on V2's rows.** T2's negative coefficient depends on the 12,231 fund-months that V2 does not use: the funds without a family code and the money market funds.
- **4p keeps its sign on V2's rows,** at half the size.

## 5. Scale η by conduct candidate: insensitive, except under flat demand

| # | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|
| 1 T2 | 0.0205 (0.0051) | 0.0213 | 0.0212 | 0.0211 | 0.0209 |
| 2 A5 | 0.0205 | 0.0189 | 0.0195 | 0.0201 | 0.0205 |
| 3 V2 | 0.0211 (0.0051) | 0.0210 | 0.0215 | 0.0218 | 0.0220 |
| 4p | 0.0205 | 0.0210 | 0.0210 | 0.0209 | 0.0208 |
| 4q | 0.0205 | 0.0214 | 0.0214 | 0.0212 | 0.0210 |
| 5 V2 no-cheap | 0.0211 | 0.0339 (0.0121) | 0.0339 (0.0142) | 0.0321 (0.0235) | 0.0301 (0.0335) |

SEs are 0.0047–0.0056 in specifications 1 to 4 (`sc_scale.csv`).

**Reading.**
- **η is 0.019–0.022 in every specification with a usable slope, under every candidate.** The spread across demand models (0.003) is smaller than one standard error.
- **Only specification 5 moves it,** to 0.030–0.034, and there it is not significant at B50 and B65. Its markups are 4 to 5 percentage points and swamp the fee.

## 6. Negative marginal costs: from 0.1% to 100% of fund-months, depending on demand

Monthly-mean share of fund-months with MC < 0, B0 → B65. PC is 0 in every row (`sc_mc.csv`).

| # | η = 0 | η = 0.024 | Own η | Share below −0.10% (own η) | Share below −0.20% (own η) | Min MC | Mean markup (%) |
|---|---|---|---|---|---|---|---|
| 1 T2 | 0.52–0.58 | 0.17–0.34 | 0.21–0.36 | 0.03–0.27 | 0–0.089 | −0.31 | 0.22–0.31 |
| 2 A5 | 0.06–0.18 | 0–0.001 | 0.001 | 0 | 0 | −0.11 | 0.11–0.14 |
| 3 V2 | 0.33–0.46 | 0.04–0.07 | 0.053–0.082 | 0.001–0.030 | 0–0.0002 | −0.21 | 0.19–0.23 |
| 4p | 0.40–0.49 | 0–0.09 | 0.006–0.163 | 0–0.001 | 0 | −0.12 | 0.14–0.19 |
| 4q | 0.57–0.66 | 0.27–0.41 | 0.31–0.45 | 0.17–0.36 | 0.008–0.260 | −0.42 | 0.28–0.38 |
| 5 V2 no-cheap | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | −8.42 | 3.9–5.4 |

**Where the negatives are** (B0 and B65, own η; share negative within the group; `sc_where.csv`).

| Specification, conduct | Vanguard | SSGA | BlackRock | Other firms | SPY | Cheap / non-cheap | Small-micro vs other |
|---|---|---|---|---|---|---|---|
| 1 T2, B0 | **0.81** | 0.03 | 0.04 | 0.01 | 0 | 0.40 / 0.06 | 0.27 vs 0.20 |
| 1 T2, B65 | **0.96** | 0.52 | 0.40 | 0.01 | **0.85** | 0.63 / 0.15 | 0.38 vs 0.36 |
| 2 A5, B0 and B65 | 0 | 0.01 | 0 | 0 | 0 | 0 / 0.002 | 0 vs 0 |
| 3 V2, B0 | 0.13 | 0.04 | 0.05 | 0.02 | 0 | 0 / 0.10 | 0.05 vs 0.06 |
| 3 V2, B65 | 0.17 | 0.25 | 0.07 | 0.02 | 0 | 0 / 0.15 | 0.08 vs 0.08 |
| 4p, B0 | 0.02 | 0 | 0 | 0 | 0 | 0.01 / 0 | 0 vs 0.01 |
| 4p, B65 | **0.54** | 0.14 | 0.11 | 0 | 0 | 0.32 / 0.04 | 0.21 vs 0.16 |
| 4q, B0 | **0.93** | 0.12 | 0.14 | 0.09 | 0 | 0.58 / 0.09 | 0.36 vs 0.30 |

**Reading.**
- **Goal B ranks the specifications A5, then 4p and V2, then T2.** The ranking follows the slope that each model gives the low-fee funds: the steeper it is, the smaller their markups.
- **The single-slope models put the negatives on cheap funds and on Vanguard.** T2 has 81% of Vanguard fund-months negative at B0, and SPY at B65. Vanguard lends at cost and SPY cannot lend, so lending revenue cannot explain either (`NOTE_seclending_MC_bounds.md`).
- **V2 puts them on non-cheap funds only,** with Vanguard at 13%. That is the known location caveat of V2.
- **4p passes the magnitude screen under every candidate and is nearly clean at B0 and B25** (0.6% and 2.1%). At B65 its negatives reach 16%, with more than half of Vanguard's fund-months.
- **The scale adjustment matters as much as demand.** It takes V2 from 33–46% to 5–8% and 4p from 40–49% to 1–16%.

## 7. Conduct test: B0 and B25 are always rejected and PC never is; B50 and B65 depend on demand

Selected sets (MCS p ≥ 0.05), η scheme A (0.024); main-instrument MCS p-values in brackets (`sc_conduct_*.csv`).

| # | **Main IV** (rival2 × csent_index) | rival2 × csent_income3 | rival3 × csent_index | rival2 × bab_usa / × fmax / × rotator | Same sets under schemes B, C and capped markups? |
|---|---|---|---|---|---|
| 1 T2 | PC (B50 0.02, B65 0.03 rejected) | PC | PC | PC | yes |
| 2 A5 | PC (0.06), B50 (0.06), B65 (1.00) | PC, B50, B65 | **B50, B65; PC rejected** | PC, B65; B50 also with bab_usa | B65 always best; B50 enters or leaves at p 0.05–0.10 |
| 3 V2 | PC, B50 (0.19), B65 (0.79) | PC, B50, B65 | PC | PC | yes |
| 4p | PC, B65 (0.06) | PC | PC | PC | yes |
| 4q | PC (B50 0.01, B65 0.02 rejected) | PC | PC | PC | yes |
| 5 V2 no-cheap | PC | PC | PC | PC | yes; but the test's F is 1 |

Minimum pairwise F for the main instrument: T2 67, A5 120, V2 140, 4p 92, 4q 55, specification 5: 1. With an F of 1 the test under specification 5 has no power, so its "PC" is not evidence.

**Reading.**
- **B0 and B25 are rejected in every specification.** This part of the conduct result does not depend on the demand model.
- **Whether partial coordination among the Big 3 survives does depend on it.** T2 and 4q reject B50 and B65. 4p keeps B65 at the margin (p = 0.06). V2 cannot separate them from PC.
- **A5 reverses the ranking.** B65 fits best (T^RV of PC against B65 = 1.9), PC is kept at p = 0.06 with the main instrument and rejected with rival3 × csent_index. The steeper the slope on the low-fee funds, the better the collusive candidates fit.
- **The η scheme and the capping change nothing in specifications 1, 3, 4p, 4q and 5,** consistent with section 5.
- **This is not a reason to prefer any specification.** The demand criteria come first.

## 8. Literature: V2 and T2 are inside the published range on average; they differ on the large low-fee funds

| Source | Estimate | Status |
|---|---|---|
| Brown, Egan, Jeon, Jin and Wu, "Why Do Index Funds Have Market Power?" (July 2026 draft), Table 2 | Fee coefficient −3.143 (retail), −4.929 (institutional), −6.506 (new 401(k) plans). Implied elasticity of demand 1.6, 2.5 and 3.3 | read from the paper's PDF |
| Same, Table A6 (broker-incentive specification) | Elasticity 1.8–2.0 retail, 2.6–2.7 institutional | read from the PDF |
| Same, section 4 | Mean (median) markup 53 (32) basis points; mean (median) marginal cost 35 (23) basis points; average expense ratio 77 basis points, load-adjusted | read from the PDF |
| Same, pp. 24–25 | Same-manager, other-market Hausman instrument; family advertising, reputation and demand spillovers would bias the fee coefficient toward zero | read from the PDF |
| Ben-David, Franzoni, Kim and Moussawi, "Competition for Attention in the ETF Space" (RFS 2023) | Broad-based ETFs compete on fees and their investors are fee-sensitive; specialized ETFs charge high fees to less fee-sensitive investors. No elasticity number | **unverified**: recalled from memory; a web search returned abstracts only |
| Egan, MacKay and Yang (index-fund demand papers) | No elasticity number recalled or retrieved | **unverified**; Danny's note cites them for the instrument argument only |

| | 1 T2 | 2 A5 | 3 V2 | 4p | 5 |
|---|---|---|---|---|---|
| Fee coefficient per percentage point | −5.6 | −3.7 to −56.4 | −3.6 to −24.2 | −9.1 | −0.3 |
| Average own elasticity | −1.61 | −3.75 | −1.93 | −2.62 | −0.08 |
| Median | −1.12 | −3.12 | −1.69 | −1.82 | −0.06 |
| Asset-weighted | −0.72 | −2.97 | −1.61 | −1.17 | −0.04 |
| Share of fund-months with \|e\| > 1 | 0.53 | 0.98 | 0.75 | 0.66 | 0 |
| Mean markup, B0–B65 (% of assets) | 0.22–0.31 | 0.11–0.14 | 0.19–0.23 | 0.14–0.19 | 3.9–5.4 |
| Mean markup relative to the mean fee (0.29%) | 0.8–1.1 | 0.4–0.5 | 0.7–0.8 | 0.5–0.7 | 14–19 |

**Reading.**
- **T2, V2 and 4p give average elasticities of 1.6 to 2.6, the range Brown et al. report (1.6 to 2.7).** A5 is above the range (3.75; close to their 401(k) figure of 3.3). Specification 5 is far outside it.
- **Weighted by assets, only V2 stays in the range (1.61).** T2 falls to 0.72 because a single slope makes elasticity proportional to the fee, and the assets sit in funds charging 0.02% to 0.09%.
- **Markups relative to fees:** Brown et al.'s mean markup is about 0.7 of their mean fee (53 of 77 basis points). V2 (0.7–0.8) and 4p (0.5–0.7) are close; T2 is higher and A5 lower. This is my comparison of ratios; their fees are load-adjusted and their sample is 2000–2020, so levels are not comparable.
- **Their instrument is the one whose exclusion Danny's note questions.** They name the same threats (family-wide demand shocks) and note that the bias would be toward zero.
- **Heterogeneity by investor type has the same sign as ours.** They find institutional demand more elastic than retail; our cheap + institutional variant has an institutional term of −4.83 (SE 1.24) (`RESULTS_other_interactions.md`).

## 9. Answers to the round's question

| Downstream result | Sensitivity to demand (specifications 1, 2, 3, 4p) | Sensitivity to conduct |
|---|---|---|
| Scale η | negligible: 0.019–0.022 | negligible |
| Negative MC after the scale adjustment | **large**: 0.001 (A5), 0.006–0.16 (4p), 0.05–0.08 (V2), 0.21–0.36 (T2) | moderate; large for 4p (0.006 at B0, 0.16 at B65) |
| Admissibility (magnitude) | A5, V2 and 4p pass; T2 passes for B0–B50 only | |
| Location of negative MCs | **large**: Vanguard and cheap funds under a single slope (T2, 4p at B65); non-cheap funds under V2; almost none under A5 | |
| Conduct: B0 and B25 rejected | none | |
| Conduct: PC | kept in all; marginal under A5 (p 0.06; rejected with one alternative instrument) | |
| Conduct: B50 and B65 | **sensitive**: rejected under T2, B65 marginal under 4p, kept under V2, B65 best under A5 | |

**Which specifications survive the demand criteria first, then the MC screens:**
- **V2** passes the demand screens and the magnitude screen; its negatives are at non-cheap Vanguard classes.
- **4p** has a strong first stage and the best MC results of the single-slope models, but leaves the Table 5 funds inelastic, and is a proxy.
- **T2** fails the location screen.
- **A5** does not identify its base slope.
- **Specification 5** is the flat pooled average of two negative slopes and is not a candidate.

**Open choice for Gene and Danny.** Whether the paper should carry a heterogeneous slope (V2) or a single slope with a stricter exclusion (Danny's category10 instrument). Deciding it needs Danny's actual category10 instrument values, so that his −5.71 specification can be run through the same downstream steps as V2.
