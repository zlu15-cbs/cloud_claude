# Index-market demand: two sample exclusions and a refined family ID give downward-sloping demand in every specification

**Caution.** "A5" is the broad-based interaction, which is Table A7 in our copy of the paper. No test here establishes that any instrument satisfies the exclusion restriction. Conduct tests use η = 0.024 throughout; on the recommended sample the estimated η is about 0.013, and the conduct test has not been re-run at that value.

✓ = desirable, ✗ = undesirable, – = not applicable. Negative-MC shares are the range over B0–B65 at each candidate's own η. Sources: `logs/spec_compare/`.

## Baseline: the paper's sample and definitions

108,300 fund-months (Table 2 Panel A). Family = CRSP management code, as in the paper's instrument.

| | T2 (paper) | A5 (paper) | V2 |
|---|---|---|---|
| Price interaction | none | broad-based | cheap |
| Donors exclude the target's | index | index | broad asset class, other share types |
| Donor aggregation | weighted mean | weighted mean | median |
| Base price coefficient (SE) | −5.606 (1.310) | −7.503 (1.770) | −3.385 (0.541) |
| Interaction (SE) | – | −5.278 (0.372) | −20.059 (0.784) |
| Share of fund-months with e > 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| First-stage F (min) | 34 | 53 | 177 |
| Table 5 funds with e < −1 | 2/15 | 2/15 | 5/15 |
| Scale η (PC–B65) | 0.0205–0.0213 | 0.0205–0.0208 | 0.0208–0.0223 |
| Negative-MC share | 0.21–0.36 | 0.005–0.088 | 0.067–0.087 |
| Share of fund-months below −0.20% | 0–0.089 | 0 | 0–0.001 |
| Vanguard fund-months negative at B0 | 0.81 | low | 0.15 |
| Conduct, main instrument | PC | PC, B65 | PC, B50, B65 |

- **Validation:** T2 and A5 reproduce the paper exactly.
- **V2** is defined in appendix A3.1. The full earlier scorecard is appendix A0.
- **On this sample all three look acceptable.** Sections 1 and 2 show that T2 and A5 owe this to two small groups of funds.

## 1. Drop the variable-annuity funds

**Who they are.** The 112 funds with a blank family code (7,771 fund-months, 1.7% of inside assets). All carry CRSP's variable-annuity flag and no other Table 2 fund does.

**Why they should go.**
- **Their fees are not observed.** CRSP has no expense ratio in 97% of their quarterly records. The build script fills each with the mean fee of funds whose names share the first five letters.
- **Their instrument is not a family instrument.** Blank family codes match one another, so their donors are other insurers' funds.
- **They are not bought in the open market.** They are chosen from an insurer's menu inside a contract.

**What happens** (paper's instrument and family code; same rows as the baseline table).

| | T2, all rows | T2, no VA | A5, all rows | A5, no VA | V2, all rows | V2, no VA |
|---|---|---|---|---|---|---|
| Rows | 108,300 | 100,529 | 108,300 | 100,529 | 96,069 est.; 107,863 supply | 96,069 est.; 100,092 supply |
| Base price coefficient (SE) | −5.606 (1.310) | **+7.244 (1.987)** | −7.503 (1.770) | **+4.009 (1.588)** | −3.385 (0.541) | −3.385 (0.541) |
| Interaction (SE) | – | – | −5.278 (0.372) | −6.924 (0.428) | −20.059 (0.784) | −20.059 (0.784) |
| Share of fund-months with e > 0 | ✓ 0 | ✗ 1.00 | ✓ 0 | ✗ 0.49 | ✓ 0 | ✓ 0 |
| First-stage F (min) | 34 | 27 | 53 | 49 | 177 | 177 |
| Table 5 funds with e < −1 | 2/15 | 0/15 | 2/15 | 0/15 | 5/15 | 5/15 |
| Scale η (PC–B65) | 0.0205–0.0213 | – | 0.0205–0.0208 | – | 0.0208–0.0223 | 0.0237–0.0253 |
| Negative-MC share | 0.21–0.36 | – | 0.005–0.088 | – | 0.067–0.087 | 0.054–0.081 |
| Share of fund-months below −0.20% | 0–0.089 | – | 0 | – | 0–0.001 | 0–0.0001 |
| Vanguard fund-months negative at B0 | 0.81 | – | low | – | 0.15 | 0.12 |
| Conduct, main instrument | PC | – | PC, B65 | – | PC, B50, B65 | PC, B65 |

Downstream rows are – where demand slopes upward: markups are then negative and the supply side is not defined.

- **T2 and A5 slope upward without these funds.** Each group alone slopes upward; only the pooled sample slopes downward.
- **V2's demand is unchanged** because these funds have no family donors and never entered its estimation. Only its supply side changes, and little.
- Details: appendix A1.

## 2. Drop funds with a real acquisition or transfer, using a refined family ID

**The problem.** The instrument is the fee of the family's other funds. When a fund changes family, its whole donor set changes overnight with no change in its own fee.
- **Example: Invesco DB Commodity Index Tracking Fund.** Its fee is 0.82–0.90% throughout. Its donors go from 9 sibling commodity funds (fees near 0.85%) to 176 Invesco funds led by QQQ (fee 0.20%), and its instrument falls from 0.84 to 0.25. Its market share falls over the same years because of the commodity bust.
- **That one fund moves T2 without VA funds from +7.2 to −1.5** (appendix A3.9, A8).
- **Why so few funds matter:** fees barely change within a fund, so the first stage is small, and a fund's weight depends on how much its instrument moves (appendix A9).

**The family ID.** The paper's instrument uses CRSP's management code, which changes for 1,049 of the 1,190 funds in 2010–2024, mostly from renamings. No CRSP field is a stable family ID (appendix A7). Danny's ownership ID (`firm_f`), already used for the supply side, changes for 42. We refine it with three rules (`sc_family_refined.py`, `family_transitions.csv`):

| Rule | What it does | Pairs | Example |
|---|---|---|---|
| Alias | two labels of one firm become one name | 40 | PDR Services → State Street; ProFunds → ProShares |
| Artifact | a trustee, administrator or white-label platform listed in place of the firm that runs the fund is replaced by that firm | 33 | Bank of New York → Invesco (QQQ); Exchange Traded Concepts → ROBO Global |
| Real | every other change is an acquisition or transfer | 48 | DB Commodity Services → Invesco; Guggenheim → Invesco |

- **Principle:** a fund's family is the firm that runs and markets it and earns most of its expense ratio.
- **The classification of each pair is our judgment from the firm names** and should be audited; all 121 pairs are in the CSV.

**The exclusion set.** Funds with a real change of family in 2010–2024: **50 of the 1,190 funds, 3,214 fund-months, 0.6% of assets** (`family_real_switches_table2.csv`).

| From → to | Funds |
|---|---|
| Guggenheim → Invesco | 13 |
| DB Commodity Services → Invesco | 11 |
| Morgan Stanley; OppenheimerFunds → Invesco | 4; 4 |
| USAA; Compass EMP → Victory Capital | 4; 3 |
| ETF Securities → abrdn | 3 |
| Evergreen → Allspring; U.S. Bancorp → Nuveen; GE Asset Management → State Street | 2; 2; 2 |
| Lattice → Hartford; Recon Capital → Global X | 1; 1 |

**What happens** (refined family ID; instrument donors and V2's cheap status from the index CSV; `sc_refined_family/`).

| | VA funds dropped | VA funds and real switchers dropped |
|---|---|---|
| T2, paper's exclusion | +17.92 (7.23) | **−7.49 (2.90)** |
| A5, paper's exclusion: specialized; × broad | +4.68 (2.42); −7.49 | **−10.69 (3.40)**; −3.75 |
| T2, broad-asset-class exclusion | −2.57 (0.69) | **−12.73 (1.81)** |
| A5, broad-asset-class exclusion: specialized; × broad | −3.03 (0.80); −5.42 | **−13.33 (1.87)**; −2.63 |
| V2, 20th percentile, median: non-cheap; × cheap | −7.776 (0.694); −25.85 | −10.350 (0.812); −26.89 |
| V2, 20th percentile, weighted mean: non-cheap; × cheap | −3.493 (0.589); −22.75 | −6.877 (0.564); −23.53 |
| V2, 25th percentile, median: non-cheap; × cheap | −2.963 (0.503); −16.31 | −4.969 (0.535); −15.74 |
| V2, 25th percentile, weighted mean: non-cheap; × cheap | **+1.008 (0.461)**; −16.00 | −2.058 (0.389); −14.99 |

- **With both exclusions, no fund-month slopes upward in any specification.**
- **The refined ID alone does not do it:** with only the VA funds dropped, T2, A5 and one V2 version still fail.

**The sample with both exclusions, in the baseline format** (1,140 funds, 97,315 fund-months; refined family ID for the instrument and for ownership; `sc_refined_family/rec_*`).

| | T2, paper's exclusion | A5, paper's exclusion | T2, broad-asset-class exclusion | A5, broad-asset-class exclusion | V2, median | V2, weighted mean |
|---|---|---|---|---|---|---|
| Base price coefficient (SE) | −7.49 (2.90) | −10.69 (3.40) | −12.73 (1.81) | −13.33 (1.87) | −10.350 (0.812) | −6.877 (0.564) |
| Interaction (SE) | – | −3.75 | – | −2.63 | −26.89 (1.26) | −23.53 (0.95) |
| Share of fund-months with e > 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| First-stage F (min) | 17 | 33 | 94 | 140 | 302 | 557 |
| Table 5 funds with e < −1 | 2/15 | 3/15 | 5/15 | 6/15 | 11/15 | 7/15 |
| Scale η (PC–B65) | 0.0126–0.0135 | 0.0126–0.0131 | 0.0126–0.0131 | 0.0126–0.0131 | 0.0127–0.0137 | 0.0127–0.0140 |
| Negative-MC share, own η | 0.23–0.36 | 0.010–0.144 | 0.008–0.151 | 0.000–0.062 | 0.000–0.001 | 0.006–0.031 |
| Negative-MC share, η = 0 | 0.48–0.57 | 0.35–0.44 | 0.36–0.43 | 0.31–0.40 | 0.12–0.23 | 0.20–0.32 |
| Share of fund-months below −0.20% | 0–0.006 | 0 | 0 | 0 | 0 | 0 |
| Min MC (% of assets) | −0.23 | −0.10 | −0.08 | −0.06 | −0.02 | −0.09 |
| Vanguard fund-months negative at B0; B65 | ✗ 0.76; 0.93 | 0.04; 0.43 | 0.03; 0.46 | 0.00; 0.18 | ✓ 0; 0 | ✓ 0.00; 0.07 |
| SPY negative at B65 | ✗ yes | ✓ no | ✓ no | ✓ no | ✓ no | ✓ no |
| Conduct, main instrument (η = 0.024) | PC, B50 (0.46), B65 (0.75) | PC, B50 (0.26), B65 | PC, B50 (0.33), B65 | PC, B50 (0.24), B65 | PC (0.84), B65; B50 rejected (0.03) | PC (0.95), B65; B50 rejected (0.02) |
| Conduct, min F | 136 | 149 | 148 | 149 | 151 | 149 |

V2 is at the 20th-percentile cutoff. Ownership uses the refined ID, so SPY counts as State Street in 2010–2012.

- **Marginal costs:** every specification except the paper-type T2 has almost no fund-month below −0.20%. V2 with the median has essentially no negative marginal costs.
- **Conduct:** B0 and B25 are rejected in every column and PC is never rejected. B65 cannot be separated from PC in any column. B50 is rejected only under V2.
- **The scale estimate changes with the sample.** η under PC is 0.0233 without the VA funds and 0.0126 once the 50 real switchers are also dropped. Dropping only the 11 DB funds leaves it at 0.0224; dropping the other 39 gives 0.0141. So the scale estimate is as sensitive to these funds as the demand slope was.
- **The conduct test here still uses η = 0.024,** as in the baseline. It has not been re-run at the sample's own η of about 0.013.

## 3. Recommendation: both exclusions, with the refined family ID

**Sample:** Table 2 Panel A without the 112 variable-annuity funds and without the 50 funds with a real acquisition or transfer. 1,140 funds, 97,315 fund-months.

The full results for this sample are the last table of section 2. V2 at the 25th-percentile cutoff on the same sample: non-cheap −4.969 (0.535) with the median and −2.058 (0.389) with the weighted mean, no fund-month sloping upward.

**Reading.**
- **Every specification has downward-sloping demand.**
- **T2 and A5 with the paper's exclusion remain weakly identified** (F of 17 and 33). T2 still has 23–36% negative marginal costs, at 76% of Vanguard's fund-months.
- **T2 and A5 with the broad-asset-class exclusion become usable:** first-stage F of 94 and 140, and 0–15% negative marginal costs, none large.
- **V2 has the strongest first stage and the fewest negative marginal costs,** and no longer needs the median for its sign.
- **V2's size still depends on the cutoff:** −10.4 and −6.9 at the 20th percentile, −5.0 and −2.1 at the 25th.
- **The base slope ranges from −2 to −13 across specifications.** The exclusions fix the sign; they do not pin down the magnitude.

**Does the top entry-fee quartile still matter?** It did before these exclusions (appendix A3.9). On the recommended sample, dropping it removes 46 more funds (2,290 fund-months):

| | Recommended sample | Top entry-fee quartile also dropped |
|---|---|---|
| T2, paper's exclusion | −7.49 (2.90) | −7.53 (2.81) |
| A5, paper's exclusion: specialized; × broad | −10.69; −3.75 | −10.73 (3.29); −3.63 |
| T2, broad-asset-class exclusion | −12.73 (1.81) | −12.56 (1.78) |
| A5, broad-asset-class exclusion: specialized; × broad | −13.33; −2.63 | −13.19 (1.84); −2.63 |
| V2, 20th percentile, median: non-cheap | −10.350 (0.812) | −9.719 (0.872) |
| V2, 20th percentile, weighted mean: non-cheap | −6.877 (0.564) | −7.807 (0.616) |
| V2, 25th percentile, median: non-cheap | −4.969 (0.535) | −4.378 (0.535) |
| V2, 25th percentile, weighted mean: non-cheap | −2.058 (0.389) | −2.892 (0.415) |

- **No.** T2 and A5 move by less than 0.2 and V2 by less than 1.
- **It does not reduce V2's sensitivity to the cutoff:** the gap between the 20th and 25th percentiles is the same with and without it.

**Do the high-fee funds still slope upward on their own?** Entry-fee quartiles 3 and 4 estimated alone, one fee slope (17,500 fund-months, 261 funds; `sc_refined_family/q34_*.log`).

| Instrument | Earlier sample and family code (appendix A3.6, A3.8) | Recommended sample | Min F |
|---|---|---|---|
| V2's: median of same-type family funds in another broad asset class | +1.34 (0.44) | **−2.32 (0.62)** | 72 |
| Broad-asset-class exclusion, pooled types, weighted mean | – | +13.7 (5.5) | 8 |
| Paper's exclusion, pooled types, weighted mean | −17.3 (3.0) | −44.8 (55.2) | 1 |

- **No, with V2's instrument.** The high-fee funds have a modest negative slope (−2.3). With a broad-based interaction on the same subsample: specialized −2.20 (0.93), broad-based −12.26.
- **The two weighted-mean instruments have no first stage on this subsample** (F of 1 and 8), so their signs carry no information.

- **So no further sample restriction is recommended.** The index-fund flag and Lipper-class restrictions we also tried are in appendix A6; they do not improve on this sample and turn the paper-type T2 and A5 upward again.

**Open decisions.**
- The cutoff for V2's cheap status (20th or 25th percentile) and the donor aggregation (median or weighted mean).
- Which η the conduct test should use, now that the estimate is 0.013 on this sample against 0.021–0.024 before.
- Whether T2 and A5 are reported with the paper's exclusion or the broad-asset-class exclusion.
- The alias and artifact tables of the refined family ID need a second pair of eyes.

**Not yet done on the recommended sample:** the conduct test at the sample's own η (about 0.013) and under the other scale schemes; the supply side for V2 at the 25th percentile.

---

# Appendix

Appendix sections A0–A5 were written before the refined family ID. They use the paper's family code (CRSP management code) and, for V2, the cheap status measured on Danny's source panel. Their numbers are not comparable with sections 2 and 3.

## A0. The earlier scorecard (paper family code; V2 cheap status from the source panel)

**Caution.** "A5" is the broad-based interaction, which is Table A7 in our copy of the paper. V2 and the two alternatives all rest on one identifying assumption: the instrument's donors exclude the target's whole broad asset class (appendix A3). No test here establishes that any instrument satisfies the exclusion restriction.

✓ = desirable, ~ = borderline, ✗ = undesirable, – = not applicable. "No VA" drops the 112 variable-annuity funds (7,771 fund-months) from the sample. Downstream rows give the range over B0–B65 at each candidate's own estimated η; conduct uses η = 0.024. Sources: `logs/spec_compare/`.

| | T2 (paper) | T2, no VA | **T2 alternative** | A5 (paper) | A5, no VA | **A5 alternative** | **V2**, VA funds on the supply side | **V2**, no VA | V2 with weighted-mean donors, VA funds on the supply side |
|---|---|---|---|---|---|---|---|---| --- |
| **Specification** | | | | | | | | | |
| Price interaction | none | none | none | broad-based | broad-based | broad-based | cheap | cheap | cheap |
| Donors exclude the target's | index | index | broad asset class | index | index | broad asset class | broad asset class, other share types | same | broad asset class, other share types |
| Donor aggregation | weighted mean | weighted mean | weighted mean | weighted mean | weighted mean | weighted mean | median | median | **weighted mean** |
| Estimation rows | 108,300 | 100,529 | 98,151 | 108,300 | 100,529 | 98,151 | 96,069 | 96,069 | 96,069 |
| **Demand** | | | | | | | | | |
| Base price coefficient (SE) | −5.606 (1.310) | **+7.244 (1.987)** | −4.123 (0.736) | −7.503 (1.770) | **+4.009 (1.588)** | −3.983 (0.749) | −3.385 (0.541) | −3.385 (0.541) | −1.943 (0.549) |
| Interaction (SE) | – | – | – | −5.278 (0.372) | −6.924 (0.428) | −4.413 (0.413) | −20.059 (0.784) | −20.059 (0.784) | −20.722 (0.886) |
| Goal A: share of fund-months with e > 0 | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✗ 0.49 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| First-stage F (min) | 34 | 27 | 124 | 53 | 49 | 162 | 177 | 177 | 249 |
| Average own elasticity | −1.61 | +1.91 | −1.09 | −2.86 | +0.31 | −1.52 | −1.91 | −1.91 | −1.56 |
| Table 5 funds with e < −1 | 2/15 | 0/15 | 1/15 | 2/15 | 0/15 | 1/15 | 5/15 | 5/15 | 4/15 |
| **Downstream** | | | | | | | | | |
| Scale η range (PC–B65) | 0.0205–0.0213 | – | 0.0233–0.0245 | 0.0205–0.0208 | – | 0.0229–0.0233 | 0.0208–0.0223 | 0.0237–0.0253 | not run |
| Goal B: negative-MC share | 0.21–0.36 | – | 0.32–0.48 | 0.005–0.088 | – | 0.14–0.39 | **0.067–0.087** | **0.054–0.081** | 0.23–0.30 |
| Share of fund-months below −0.20% | 0–0.089 | – | 0.02–0.29 | 0 | – | 0–0.06 | 0–0.001 | 0–0.0001 | not run |
| Min MC (% of assets) | −0.31 | – | −0.46 | −0.12 | – | −0.33 | −0.23 | −0.21 | −0.51 |
| Magnitude screen (≤ 2% below −0.20%) | ~ fails at B65 | – | ✗ | ✓ | – | ~ fails at B65 | ✓ | ✓ | not run |
| Location: Vanguard fund-months negative at B0 | ✗ 0.81 | – | ✗ 0.94 | ✓ low | – | ✗ 0.32 | ~ 0.15 | ~ 0.12 | ~ 0.19 |
| SPY negative at B65 | ✗ yes | – | ✗ yes | ✓ no | – | ✗ yes | ✓ no | ✓ no | not run |
| **Conduct, main instrument** | PC | – | PC, B50, B65 | PC, B65 | – | PC, B50, B65 | PC, B50, B65 | PC, B65 | not run |
| **Overall** | **valid only with the VA funds** | **demand slopes upward** | **fallback: valid sign, flat, MC fails** | **valid only with the VA funds** | **49% slope upward** | **fallback: valid sign, flat, MC fails at B50–B65** | **most sensible** | **most sensible** | **valid sign; flat non-cheap slope; MC fails** |

**What the scorecard says.**
1. **T2 and A5 depend on the variable-annuity funds.** Without those 112 funds, T2 slopes upward for every fund-month and A5 for 49% of them (appendix A1).
2. **T2 and A5 have a fallback.** Rebuilding their instrument to exclude the target's whole asset class restores downward-sloping demand without the variable-annuity funds. The slope is flat, 14 of the 15 Table 5 funds stay inelastic, and a third or more of marginal costs are negative under T2 (appendix A2).
3. **A handful of high-fee funds decide the sign.** Dropping one commodity fund turns T2 without the variable-annuity funds from +7.2 to −1.5; dropping the top entry-fee quartile (50 funds, 0.4% of assets) gives downward-sloping demand in every specification and removes V2's dependence on the median (appendix A3.9).
4. **V2's non-cheap slope depends on the median.** With the lag-AUM-weighted mean that T2 and A5 use, and nothing else changed, the non-cheap slope falls from −3.4 to −1.9 and negative marginal costs rise from 7–9% to 23–30%. The sign and the cheap interaction do not change (appendix A3.7).
5. **V2 gives the most sensible demand.** No fund-month slopes upward, the first stage is strong, 5 of the 15 Table 5 funds have e < −1, and 5–9% of marginal costs are negative, almost none below −0.20%. It does not use the variable-annuity funds to estimate demand, so excluding them changes only the supply side (appendix A3).

- **Code:** `code/spec_compare/`. Columns T2 and A5: `sc_demand.py`, `sc_a5.py`, `sc_exva.py`. Alternatives: `sc_t2a5_nova_grid.py`. V2: `sc_v2_robust.py`, `sc_v2_final.py`, `sc_v2_cheap_start.py`. Supply side: `sc_downstream.py`.
- **Validation:** T2 reproduces the paper's −5.606 (1.310) and A5 its −7.503 and −5.278 exactly. Danny's negative-MC share (0.516 at η = 0) and scale under PC (0.0205) are also reproduced.
- **Supply sample:** the estimation sample's universe in each column (108,300 with the variable-annuity funds, 100,529 without); V2 also drops the 4 money market funds (107,863 and 100,092).

## A1. T2 and A5 depend on the variable-annuity funds, and that is a problem

**The dependence** (`sc_a5_demand.csv`, `sc_va_checks.csv`). The instrument is the paper's own; only the sample changes.

| | All 108,300 rows | 100,529 rows without the VA funds | The 7,771 VA rows alone |
|---|---|---|---|
| T2: price coefficient (SE) | −5.606 (1.310) | **+7.244 (1.987)** | +2.322 (0.538) |
| A5: specialized (SE) | −7.503 (1.770) | **+4.009 (1.588)** | +0.747 (0.293) |
| A5: × broad-based (SE) | −5.278 (0.372) | −6.924 (0.428) | +4.884 (1.840) |
| A5: share of fund-months with e > 0 | 0 | 0.49 | 1.00 |

**Who these funds are.**
- They are the 112 funds with a blank family code (`firm_f_old`). All carry CRSP's variable-annuity flag (`vau_fund`), and none of the other 1,190 funds does. Examples: VALIC Company I Stock Index Fund, Voya US Stock Index Portfolio, Vanguard Variable Insurance Fund Equity Index Portfolio.
- They average 1.7% of inside-market assets.

**Why relying on them is a problem.**
- **Their prices are not observed.** CRSP has no expense ratio in 97% of their quarterly records (6% for other funds), and none at all for 99 of the 112. The build script fills a missing fee with the mean fee of funds whose names share the same first five letters (`5_fund_market_data_for_Matteo_v6_nonlev_etf.R`, lines 89–99). In 85% of firm-months, every variable-annuity fund of a firm has the same fee.
- **Their instrument is not a family instrument.** CRSP has no management code for them, so the family code is blank, and blank codes match one another. Their donors are other insurers' funds.
- **They are not bought in the open market.** They are chosen from an insurer's menu inside a contract, so the expense ratio is not the price the investor trades off against other index funds.
- **The negative coefficient does not come from within either group.** Each group alone slopes upward; only the pooled sample slopes downward. The sign therefore comes from comparing the two groups through the common month effects. This is my reading of the three columns, not a separate test.
- **Fixing their families does not rescue it.** With their true families the T2 coefficient is −0.2 to −0.3, and that instrument is nearly the imputed fee itself.

**Reading.**
- **Gene's proposal is to exclude the variable-annuity funds from the sample.** The paper's two demand tables then no longer deliver downward-sloping demand.
- **Danny's category10 version of T2 has the same problem.** It reproduces his −5.713 (0.747) with these funds and gives +1.485 (1.079) without them (`sc_danny_cat10_demand.csv`).

## A2. The fallback: T2 and A5 with a broad-asset-class exclusion

Without the variable-annuity funds, the instrument was rebuilt 16 ways from Danny's full source panel: four exclusions, pooled or same share type, weighted mean or median (`sc_t2a5_nova_grid.csv`). The alternative in the scorecard is the version closest to the paper's own construction that has downward-sloping demand.

| Exclusion | Share type | Aggregation | T2 price (SE) | T2 e > 0 | T2 negative MC | A5 specialized; × broad | A5 e > 0 | A5 negative MC |
|---|---|---|---|---|---|---|---|---|
| index (paper) | pooled | weighted (paper) | +7.24 (1.99) | 1.00 | – | +4.01; −6.92 | 0.49 | – |
| category20 | pooled | weighted | +4.82 (1.46) | 1.00 | – | +3.13; −6.63 | 0.49 | – |
| category10 (Danny) | pooled | weighted | +3.93 (1.46) | 1.00 | – | +2.62; −6.08 | 0.49 | – |
| category10 | same type | weighted | −0.15 (0.64) | 0 | 1.00 | −0.99; −5.56 | 0 | 0.65–0.73 |
| **broad asset class** | **pooled** | **weighted** | **−4.12 (0.74)** | 0 | **0.32–0.48** | **−3.98; −4.41** | 0 | **0.14–0.39** |
| broad asset class | same type | weighted | −2.55 (0.42) | 0 | 0.59–0.73 | −2.50; −5.43 | 0 | 0.29–0.53 |
| broad asset class | same type | median | −0.92 (0.43) | 0 | 0.98 | +0.57; −6.71 | 0.49 | – |
| broad asset class | pooled | median | +9.54 (6.41) | 1.00 | – | +9.13; −8.08 | 1.00 | – |

**What the alternative needs.**
- **Required: the broad-asset-class exclusion.** With the same-index, category20 or category10 exclusion and pooled share types, every version slopes upward.
- **Required: the lag-AUM-weighted mean.** With a median, the pooled version has no first stage (F of 6) and the same-type version is flat or positive.
- **Preferred but not required: pooled share types.** Same-type matching keeps the sign but halves the slope and raises the negative-MC share.
- **Not required: the money market funds.** Dropping the 4 money market funds gives −3.45 for T2 and −3.26 with −4.78 for A5.

**Reading.**
- **The alternatives are valid on goal A and weak on everything else.** One of the 15 Table 5 funds has e < −1. Under T2, 32–48% of marginal costs are negative, at almost every Vanguard fund-month and at SPY for B65. A5 is better at B0 (14%) and passes the magnitude screen up to B50.
- **Why they stay flat:** one slope, or a broad-based interaction, cannot give the low-fee funds a slope steep enough. A fund charging 0.03% needs about −33 for an elasticity of −1.
- **They are a fallback, not a replacement for V2.** They use the same exclusion as V2, so they are no easier to defend on the instrument.

## A3. V2: definition, results, what it is robust to, and what breaks it

### A3.1 Definition

    ln s_jt − ln s_0t = α p_jt + α_c (p_jt × cheap_j) + β1 |TE_jt| + β2 R_jt + β3 ln Age_jt + μ_j + τ_t + ξ_jt

| Element | V2 | How it differs from T2 |
|---|---|---|
| Price interaction | cheap, fixed per fund | T2 has none |
| Cheap | The fund's expense ratio in its entry month is at or below the 20th percentile of that month's expense ratios across all index funds. The entry month is the fund's first month on or after January 2005 with a fee that CRSP reports. Ties count as cheap. 49% of estimation fund-months | – |
| Data for cheap | Danny's source panel (`index_funds_preprocess_oct2026.csv`), observed fees only | – |
| Instrument | Z and Z × cheap. Z is the median expense ratio, in the same month, of funds in the same family and the same share type, in another broad asset class | T2: lag-AUM-weighted mean of same-family funds on another index, any share type |
| Broad asset classes | Six, from CRSP's Lipper class, one per tracked index: US equity, international equity, bond, allocation, real asset, other | T2 excludes only the same index |
| Share type | ETF, institutional or retail | T2 pools them |
| Donor pool | Every fund in the index CSV that month, money market funds removed | T2: every fund in the source panel |
| Sample | Table 2 Panel A minus the 4 money market funds; demand is estimated on the 96,069 fund-months where Z is defined | T2: all 108,300 |
| Controls, fixed effects, clustering | As in T2: tracking error, past one-year return, log age; fund and month effects; clustered by month | same |

Rows without Z are the variable-annuity funds (7,771) and funds with no same-family, same-type donor in another asset class that month. They stay in the market shares and on the supply side.

**Why January 2005.** The cheap status must be predetermined, so it is fixed five years before the estimation window opens in 2010. The source panel then has 925 funds in the cross-section, against 60 in its first month, January 1993.

### A3.2 Results and the cutoff check

| | Non-cheap α (SE) | × cheap (SE) | Min F | e > 0 | Table 5 e < −1 | Negative MC B0–B65 | Without VA funds |
|---|---|---|---|---|---|---|---|
| **V2: 20th percentile** | **−3.385 (0.541)** | **−20.059 (0.784)** | 177 | 0 | 5/15 | 0.067–0.087 | 0.054–0.081 |
| 15th percentile | −7.527 (0.880) | −29.120 (1.972) | 128 | 0 | 11/15 | 0.000–0.001 | 0.000 |
| 25th percentile | −3.967 (0.607) | −17.409 (0.840) | 144 | 0 | 7/15 | 0.018–0.026 | 0.010–0.021 |

**Reading.**
- **Demand slopes down for every fund-month at all three cutoffs,** and the negative-MC share stays below 9%.
- **The magnitudes move.** The 20th and 25th percentiles are close. The 15th gives steeper slopes for both groups and almost no negative marginal costs.
- **Why the 15th differs:** fees cluster at round numbers. In January 2005 the 20th-percentile cutoff is exactly 0.25%, so the block of funds charging 0.25% is cheap at the 20th percentile and not at the 15th.

### A3.3 What V2 is robust to

Each row changes one element of V2 (`sc_v2_robust.csv`, `sc_v2_cheap_start.log`).

| Variant | Non-cheap α (SE) | × cheap (SE) | e > 0 | Table 5 e < −1 | Negative MC B0–B65 |
|---|---|---|---|---|---|
| **V2** | −3.385 (0.541) | −20.059 (0.784) | 0 | 5/15 | 0.067–0.087 |
| Variable-annuity funds dropped from the supply side | unchanged | unchanged | 0 | 5/15 | 0.054–0.081 |
| Donors from the full source panel | −2.993 (0.544) | −19.031 (0.771) | 0 | 5/15 | 0.092–0.107 |
| Cheap from a fund's first month in the index CSV (the version first sent to Danny) | −3.642 (0.419) | −20.562 (0.646) | 0 | 5/15 | 0.053–0.082 |
| Cutoff at the 15th; 25th percentile | −7.5; −4.0 | −29.1; −17.4 | 0 | 11/15; 7/15 | 0–0.03 |

**One file for both the cheap status and the donors, at each cutoff** (2005 start; `sc_v2_filecheck.csv`).

| Cutoff | Source panel for both: non-cheap; × cheap | Index CSV for both: non-cheap; × cheap | Negative MC, source; CSV | January 2005 cutoff, source; CSV | Table 2 funds whose status differs |
|---|---|---|---|---|---|
| 15th | −7.369 (0.969); −28.473 | −13.495 (1.226); −39.669 | 0–0.002; 0 | 0.20%; 0.183% | 46 |
| 20th | −2.993 (0.544); −19.031 | −8.447 (0.921); −28.317 | 0.092–0.107; 0 | 0.25%; 0.23% | 45 |
| **25th** | **−3.625 (0.614); −16.504** | **−4.158 (0.625); −18.086** | 0.026–0.034; 0.012–0.022 | 0.27%; 0.26% | 23 |

**Reading.**
- **The sign of demand is robust to all of these.** No fund-month slopes upward in any row.
- **The cheap funds are always strongly fee-sensitive** (interaction of −16 to −40).
- **Where the donors come from does not matter** (−3.4 against −3.0 at the 20th percentile).
- **Where the cheap status is measured matters at the 15th and 20th percentiles and not at the 25th.** The index CSV drops each fund's first 12 months, so its January 2005 cross-section has 790 funds against 925 and its cutoffs are lower. At the 20th percentile the source cutoff is exactly 0.25%, a fee that 36 funds charge that month (Select Sector SPDRs and iShares Russell style ETFs among them); the CSV cutoff is 0.23% and leaves them out. At the 15th the source cutoff is exactly 0.20%, with 22 funds on it.
- **At the 25th percentile the two files agree:** −3.6 against −4.2, with 1–3% negative marginal costs in both. The cutoffs (0.27% and 0.26%) fall between the round-number fees, and half as many funds change status.
- **So at the 20th percentile the size of the non-cheap slope is known only within about −3 to −8,** and at the 25th within −3.6 to −4.2. The qualitative results hold at every cutoff. This is an argument for reporting the 25th percentile next to the 20th, or for making it the baseline; the choice is Gene's.

### A3.4 What breaks V2, and why we do not make those choices

| Variant | Non-cheap α (SE) | × cheap | e > 0 | Negative MC B0–B65 | What goes wrong |
|---|---|---|---|---|---|
| Exclusion by Danny's category10 classes | **+1.562 (0.751)** | −16.007 | 0.51 | – | half the fund-months slope upward |
| Cheap classified from January 1993, the source panel's first month | −2.010 (0.412) | −20.542 | 0 | 0.22–0.32 | flat non-cheap slope; many negative marginal costs |
| No cheap interaction (one slope, same Z) | −0.32 (0.29) | – | 0 | 1.00 | flat for everyone |

**The broad-asset-class exclusion.**
- **What the choice is.** Category10 splits equity and bonds into finer groups (US size and style, sector, developed, emerging; government, credit, municipal). V2 keeps all US equity together, all international equity together and all bonds together.
- **What happens with finer classes.** A family's sector funds become donors for its S&P 500 fund, and its credit fund for its government-bond fund. The non-cheap slope then turns positive. The same happened with 14 Lipper groups (−0.25) and with 783 index clusters (+0.40) in earlier runs, and in the T2 grid of appendix A2.
- **The argument for the broad classes.** The instrument is valid only if the donors' fees do not move with the target's demand shocks. Demand for index funds moves largely at the level of the asset class: flows into US equity, into international equity, into bonds. A family that sees strong demand for US equity can adjust fees on its S&P 500 fund and on its sector funds together. Excluding only the narrow category leaves those sector funds in the instrument.
- **The evidence is consistent with that argument but does not prove it.** The finer the exclusion, the more positive the slope, which is the direction of bias expected when donors share demand shocks with the target.
- **What a referee can still say.** Family-wide demand shocks cross asset classes too, and no exclusion removes them. V2 mitigates the problem; it does not eliminate it.

**The 2005 start.**
- A start in January 1993 classifies the oldest funds against a cross-section of 60 funds, and the non-cheap slope flattens to −2.0.
- A start inside the estimation window (2010) is not predetermined and is not considered.
- January 2005 is predetermined and based on a full cross-section.

**The cheap interaction.** With one slope and the same instrument, the estimate is −0.32 and every marginal cost is negative. The fee slope is heterogeneous, and a single slope cannot represent it.

**Reading.**
- **Three design choices carry V2: the broad-asset-class exclusion, the cheap interaction, and the median over donors (appendix A3.7).** Both have an economic argument, and both should be stated as assumptions in the paper.
- **One data choice matters: where and when the cheap status is measured.** The 2005 start on the source panel is defensible. The 25th percentile is the cutoff at which the result does not depend on the file (appendix A3.3).

### A3.5 Entry-fee rank in place of the cheap indicator

Gene's suggestion: interact the fee with the fund's entry-fee rank, so that no cutoff is needed. Rank is the percentile rank of the entry fee in the entry-month cross-section (2005 start), either continuous in (0, 1] or as a quartile 1–4 entering linearly. Instruments: Z and Z × rank (`sc_v2_rank.log`).

| Interaction | File for rank and donors | Fee slope at rank 0 (SE) | × rank (SE) | Min F | Implied slope: low; middle; high rank | Share of fund-months with e > 0 |
|---|---|---|---|---|---|---|
| Rank 0–1 | source rank, CSV donors (as V2) | −30.864 (1.240) | +53.748 (1.670) | 205 | −25.5; −4.0; +17.5 (at 0.1; 0.5; 0.9) | 0.111 |
| Rank 0–1 | source for both | −29.050 (1.278) | +51.547 (1.774) | 204 | −23.9; −3.3; +17.3 | 0.123 |
| Rank 0–1 | index CSV for both | −32.782 (1.367) | +54.506 (1.745) | 195 | −27.3; −5.5; +16.3 | 0.104 |
| Quartile 1–4 | source rank, CSV donors | −27.954 (1.148) | +10.394 (0.363) | 190 | −17.6; −7.2; +3.2; +13.6 (quartiles 1–4) | 0.177 |
| Quartile 1–4 | source for both | −26.090 (1.134) | +9.878 (0.370) | 197 | −16.2; −6.3; +3.6; +13.4 | 0.177 |
| Quartile 1–4 | index CSV for both | −33.894 (1.314) | +12.427 (0.372) | 199 | −21.5; −9.0; +3.4; +15.8 | 0.190 |

**Reading.**
- **The rank is stable across the two files.** The coefficients differ by about 10%, against a factor of almost three for the 20th-percentile indicator. The entry-fee ranks from the two files have a correlation of 0.99.
- **It fails goal A.** A linear interaction forces the slope to keep rising with the rank, so it crosses zero near the 57th percentile (between quartiles 2 and 3). 10–19% of fund-months slope upward.
- **What the data say is a step, not a line:** very elastic at the bottom and a flat, negative slope above. The indicator fits that shape; a linear rank does not.
- **Not used.** The marginal-cost numbers for these rows are not meaningful because of the positive slopes.

### A3.6 Who the high-fee funds are, and where the upward slope comes from

Gene's question: is the upward slope at high ranks an artifact of specialized funds? Funds are sorted into quartiles of the entry-fee rank (`sc_v2_highfee.log`; rank from the index CSV, V2's instrument).

| Entry-fee quartile | Fund-months | Funds | Mean fee (%) | Share of inside assets | Specialized | ETF | International equity or real asset | Fee slope, quartile dummies | Fee slope, estimated alone (SE; F) |
|---|---|---|---|---|---|---|---|---|---|
| 1 (lowest) | 49,509 | 531 | 0.11 | 0.809 | 0.40 | 0.44 | 0.15 | −23.9 | −47.4 (8.9; 21) |
| 2 | 28,340 | 340 | 0.30 | 0.144 | 0.50 | 0.69 | 0.29 | −6.8 | −0.04 (0.58; 131) |
| 3 | 15,683 | 229 | 0.56 | 0.043 | 0.74 | 0.81 | 0.51 | −0.9 | −1.18 (0.46; 205) |
| 4 (highest) | 2,537 | 48 | 0.93 | 0.004 | 0.54 | 0.43 | 0.60 | +30.6 | +76 (63; 2) |

**The top half (quartiles 3 and 4), estimated alone on subgroups.**

| Subgroup | Fund-months | Fee slope (SE) | First-stage F |
|---|---|---|---|
| Broad-based | 5,203 | −12.95 (1.78) | 36 |
| Specialized | 13,017 | **+5.66 (0.96)** | 181 |
| ETFs | 13,805 | **+7.15 (1.19)** | 238 |
| Mutual funds | 4,415 | −1.14 (0.27) | 150 |
| US equity | 7,276 | +0.96 (1.10) | 23 |
| Not US equity | 10,944 | **+3.96 (0.48)** | 218 |

**Reading.**
- **Gene's conjecture holds for the top half.** High-fee broad-based funds slope downward (−13). High-fee specialized funds slope upward (+5.7), and they are three quarters of the fund-months there.
- **Who they are.** Country ETFs (iShares MSCI Taiwan, Brazil, Japan, India, China Large-Cap), thematic ETFs (Global X robotics, cloud, electric vehicles; ROBO; KraneShares China Internet), and commodity funds (Invesco DB Commodity, iShares Silver, VanEck Gold Miners).
- **The top quartile is tiny and partly not index funds.** It has 48 funds and 0.4% of assets, no first stage on its own (F of 2), and includes PIMCO IndexPLUS and Russell Investment Company funds, which are actively managed against an index.
- **A possible reason, not tested:** for a country or theme fund the fee is not the margin of competition. Demand follows the theme, and there are few close substitutes on the same exposure.
- **The linear rank fails for a second reason too.** With specialized funds removed, the linear rank model still has 6% of fund-months sloping upward. The jump from quartile 1 (−24) to quartile 2 (−7) is too large for a line.
- **What it means for V2.** The non-cheap slope of −3.4 averages a clearly negative slope for mid-fee and broad-based funds with a zero or positive slope for high-fee specialized ETFs. Those funds are 4.7% of assets.
- **The broad/specialized label is not consistent within an index:** iShares MSCI Emerging Markets is broad-based, while the DFA and SPDR funds on the same index are specialized.

### A3.7 Donor aggregation and share-type matching in V2

The scorecard shows V2 with a median and the other models with a weighted mean. Each row below changes only how V2's donors are aggregated or matched (2005 start, same broad-asset-class exclusion, CSV donors; `sc_v2_agg.csv`).

| Cheap cutoff | Aggregation | Share types | N | Non-cheap α (SE) | × cheap (SE) | Min F | e > 0 | Table 5 e < −1 | Negative MC B0–B65 |
|---|---|---|---|---|---|---|---|---|---|
| 20th | **median (V2)** | same type (V2) | 96,069 | −3.385 (0.541) | −20.059 (0.784) | 177 | 0 | 5/15 | 0.067–0.087 |
| 20th | lag-AUM-weighted mean | same type | 96,069 | −1.943 (0.549) | −20.722 (0.886) | 249 | 0 | 4/15 | 0.228–0.303 |
| 20th | unweighted mean | same type | 96,069 | −0.687 (0.710) | −19.149 (0.971) | 141 | 0 | 3/15 | 0.575–0.830 |
| 20th | median | pooled | 97,559 | −2.627 (1.479) | −21.816 (1.305) | 51 | 0 | 5/15 | 0.118–0.132 |
| 20th | lag-AUM-weighted mean | pooled | 97,559 | −1.499 (1.105) | −22.891 (1.354) | 144 | 0 | 4/15 | 0.377–0.415 |
| 25th | median | same type | 96,069 | −3.967 (0.607) | −17.409 (0.840) | 144 | 0 | 7/15 | 0.018–0.026 |
| 25th | lag-AUM-weighted mean | same type | 96,069 | −0.016 (0.490) | −16.440 (0.615) | 309 | 0 | 5/15 | 0.84–0.98 |
| 25th | lag-AUM-weighted mean | pooled | 97,559 | −1.218 (1.097) | −19.471 (0.837) | 171 | 0 | 6/15 | 0.411–0.427 |

**Reading.**
- **Yes, the median drives the size of the non-cheap slope.** With a weighted mean it is −1.9 at the 20th percentile and zero at the 25th. With an unweighted mean it is −0.7. Negative marginal costs rise to 23% or more.
- **It does not drive the sign or the cheap interaction.** No fund-month slopes upward in any row, and the interaction stays between −16 and −23.
- **Same-type matching is not required for the sign, but it is needed for precision.** With pooled share types and a median the non-cheap slope is −2.6 with a standard error of 1.5 (F of 51, against 177), so it is no longer distinguishable from zero.
- **The defence of the median is robustness to outliers,** not a result: a family's one expensive fund in another asset class moves a mean and not a median, and asset weights make the instrument follow the family's largest fund. That argument is ours; the data do not choose between the two.
- **The opposite holds for T2 and A5 alternatives:** they need the weighted mean and fail with the median (appendix A2). So no aggregation works for every model.
- **Consequence.** V2's non-cheap slope now depends on three choices: the broad-asset-class exclusion, the cutoff and file for the cheap status, and the median. The robust results are the sign and the high elasticity of cheap funds.

### A3.8 Other instruments for the high-fee funds

Gene's question: can another instrument remove the upward slope for entry-fee quartiles 3 and 4? One fee slope, estimated on those funds alone (`sc_highfee_iv.log`). "Family" instruments use the same family's other funds; "rival" instruments count other families' funds.

| Instrument | All high-fee (SE; F) | Specialized | Broad-based | Big 3 families | Other families |
|---|---|---|---|---|---|
| V2's Z | +1.34 (0.44; 168) | +5.66 (0.96; 181) | −12.95 (1.78; 36) | −6.75 (0.87; 59) | +2.51 (0.59; 154) |
| Z, donors not cheap | +1.02 (0.46; 217) | +2.38 (0.65; 209) | −8.94 (2.64; 32) | −14.2 (4.4; 5) | +1.08 (0.57; 183) |
| Z, donors high-fee only | +1.27 (0.41; 250) | −0.17 (0.47; 280) | +5.59 (1.62; 64) | +18.0 (7.5; 10) | +2.14 (0.51; 202) |
| Z, donors specialized only | +5.64 (1.04; 55) | +11.27 (2.09; 61) | −9.60 (2.13; 20) | −7.70 (1.19; 25) | +2.73 (0.60; 83) |
| Z lagged 12 months | +0.18 (0.51; 220) | +6.96 (1.31; 184) | −28.8 (7.4; 12) | −9.83 (1.03; 54) | +2.62 (0.68; 150) |
| Paper's IV0 | −17.3 (3.0; 28) | +55 (30; 4) | −0.70 (0.65; 143) | −5.89 (1.69; 31) | −30.9 (10.4; 8) |
| Rivals on the same index | +5.05 (0.91; 145) | +0.45 (0.22; 421) | −9.11 (1.10; 88) | +0.52 (1.42; 19) | +6.11 (0.87; 143) |
| Rivals in the same index cluster | +3.06 (0.35; 412) | +0.78 (0.22; 343) | −17.7 (4.3; 21) | −3.27 (0.47; 35) | +4.55 (0.39; 267) |
| Z with asset class × month effects | +0.01 (0.42) | +5.34 (0.95) | −12.80 (1.74) | +27.1 (9.7) | +0.19 (0.48) |

**Reading.**
- **No instrument resolves it.** None gives a negative slope in every subgroup with a usable first stage. Restricting donors to high-fee funds brings the specialized slope to zero (−0.17) but turns the broad-based slope positive.
- **My earlier explanation was wrong.** I had suggested that fee cuts on the Big 3's core funds drive the positive slope. The Big 3's high-fee funds slope downward (−6.7); the positive slope is in the other families (+2.5).
- **The sign for these funds swings with the instrument and the subgroup,** from −17 to +55 under the paper's instrument. Their fee slope is not identified. Section 3.9 shows why: a few funds dominate.

### A3.9 A handful of funds decide the sign: top entry-fee quartile dropped, and the three most influential funds

**Scorecard specifications without the variable-annuity funds, re-estimated without the top entry-fee quartile** (50 funds, 2,656 fund-months, 0.4% of assets; `sc_q4_*.log`).

| | Base price coefficient (SE), as in the scorecard | Without quartile 4 | Interaction without quartile 4 | Min F | Table 5 e < −1 | Negative MC B0–B65 |
|---|---|---|---|---|---|---|
| T2, no VA | **+7.244 (1.987)** | **−5.24 (1.64)** | – | 30 | 1/15 | 0.27–0.49 |
| A5, no VA | **+4.009 (1.588)** | **−6.48 (1.90)** | −3.90 | 52 | 2/15 | 0.03–0.28 |
| T2 alternative | −4.123 (0.736) | −9.57 (0.94) | – | 131 | 2/15 | 0.01–0.20 |
| A5 alternative | −3.983 (0.749) | −9.40 (0.96) | −2.04 | 166 | 2/15 | 0.00–0.13 |
| V2 (median) | −3.385 (0.541) | −4.767 (0.514) | −19.511 | 175 | 5/15 | 0.019–0.053 |
| V2, weighted-mean donors | −1.943 (0.549) | −5.483 (0.563) | −20.426 | 236 | 7/15 | 0.002–0.031 |
| V2, unweighted-mean donors | −0.687 (0.710) | −3.929 (0.729) | −19.010 | 143 | 5/15 | 0.052–0.083 |
| V2, 25th percentile, median | −3.967 (0.607) | −5.316 (0.611) | −16.576 | 139 | 7/15 | 0.002–0.017 |
| V2, 25th percentile, weighted mean | −0.016 (0.490) | −3.576 (0.462) | −15.032 | 309 | 6/15 | 0.035–0.047 |

No fund-month slopes upward in any row without quartile 4.

**Which funds do it** (`sc_q4_influence.log`, `sc_q4_dropfunds.log`; exact re-estimation with the paper's instrument).

| Dropped | T2, all rows (paper) | T2, no VA | A5, no VA: specialized; × broad | V2: non-cheap; × cheap |
|---|---|---|---|---|
| Nothing | −5.606 (1.310) | +7.244 (1.987) | +4.009; −6.924 | −3.385 (0.541); −20.059 |
| Invesco DB Commodity Index Tracking Fund | −11.801 (2.054) | −1.462 (1.358) | −3.248; −4.817 | −4.642 (0.546); −20.085 |
| That fund, PIMCO 0-5 Year High Yield ETF, Invesco DB Agriculture Fund | −17.590 (2.689) | −9.876 (2.047) | −10.493; −2.755 | −5.253 (0.555); −20.124 |

**What happens in those funds.**
- **Invesco DB Commodity Index Tracking Fund.** Its fee is 0.82–0.90% throughout. Its family code changes from DB Commodity Services to Invesco, and the instrument falls from 0.78 in 2015–2017 to 0.37 in 2018 and 0.25 by 2024. Its assets fall over the same years. The instrument moves because the donor family changed, not because any fee changed.
- **PIMCO 0-5 Year High Yield ETF.** Fee constant at 0.55%. The instrument falls from 1.01 in 2013 to 0.30 in 2015 and 0.19 in 2016.
- **Invesco DB Agriculture Fund.** Same family change: the instrument falls from 0.86 in 2014 to 0.37 in 2015, fee 0.88–0.94%.

**Reading.**
- **Yes: without the top quartile, every specification has downward-sloping demand,** including T2 and A5 with the paper's instrument and no variable-annuity funds.
- **One fund is enough.** Dropping Invesco DB Commodity alone moves T2 without VA funds from +7.2 to −1.5, and the paper's own T2 from −5.6 to −11.8.
- **The cause is a jump in the instrument with no change in the fee.** For these funds the first stage is close to zero while the instrument and the fund's assets both trend, so they contribute a large reduced form and nothing to the first stage. This is my reading of the fund-level series; the reason for the PIMCO jump was not traced.
- **V2 is the least sensitive** (−3.4, −4.6, −5.3). T2 moves by 12 to 17 points.
- **Without the top quartile, V2 no longer depends on the median or the cutoff:** the non-cheap slope is −3.6 to −5.5 in all five versions, and negative marginal costs are at most 8%.
- **The upward slope at high fees (appendix A3.5 and A3.6) is this same handful of funds,** not a property of specialized funds in general.
- **What this means for the choice.** The sign of the paper's demand tables turns on single funds, in both directions. A sample rule is needed before specifications are compared: for example dropping commodity pools and funds that are not plain index funds, or the top entry-fee quartile. The rule should be set on economic grounds, not on the coefficient. That decision is Gene's.

## A4. Supply side in detail

**Scale η** (2SLS with the rotator instrument, under each candidate).

| | PC | B0 | B65 |
|---|---|---|---|
| T2 (paper) | 0.0205 (0.0051) | 0.0213 | 0.0209 |
| T2 alternative | 0.0233 | 0.0245 | 0.0244 |
| A5 (paper) | 0.0205 | 0.0208 | 0.0205 |
| A5 alternative | 0.0233 | 0.0230 | 0.0229 |
| V2, VA funds on the supply side | 0.0211 (0.0051) | 0.0208 | 0.0223 |
| V2, no VA | 0.0238 (0.0050) | 0.0237 | 0.0253 |

**Negative marginal costs** (monthly-mean share of fund-months with MC < 0, B0 → B65; PC is 0).

| | η = 0 | η = 0.024 | Own η | Share below −0.20% | Min MC |
|---|---|---|---|---|---|
| T2 (paper) | 0.52–0.58 | 0.17–0.34 | 0.21–0.36 | 0–0.089 | −0.31 |
| T2 alternative | 0.61–0.72 | 0.33–0.48 | 0.32–0.48 | 0.02–0.29 | −0.46 |
| A5 (paper) | – | – | 0.005–0.088 | 0 | −0.12 |
| A5 alternative | – | – | 0.14–0.39 | 0–0.058 | −0.33 |
| V2, VA funds on the supply side | 0.35–0.48 | 0.05–0.08 | 0.067–0.087 | 0–0.001 | −0.23 |
| V2, no VA | 0.36–0.50 | 0.05–0.09 | 0.054–0.081 | 0–0.0001 | −0.21 |

**Where the negatives are** (own η; share negative within the group).

| | Vanguard | SSGA | BlackRock | SPY | Cheap / non-cheap |
|---|---|---|---|---|---|
| T2 (paper), B0 | 0.81 | – | – | 0 | – |
| T2 alternative, B0 | 0.94 | – | – | 0 | – |
| A5 alternative, B0; B65 | 0.32; 0.89 | – | – | 0; negative | – |
| V2, B0 | 0.15 | 0.09 | 0.05 | 0 | 0 / 0.13 |
| V2, B65 | 0.18 | 0.22 | 0.07 | 0 | 0 / 0.16 |
| V2, no VA, B0 | 0.12 | 0.03 | – | 0 | – |

**Conduct test** (pyRVtest; selected if MCS p ≥ 0.05; η = 0.024; MCS p-values in brackets).

| | **Main instrument** (rival2 × csent_index) | rival2 × csent_income3 | Other four instruments | Min F |
|---|---|---|---|---|
| T2 (paper) | PC | – | – | – |
| T2 alternative | PC, B50 (0.17), B65 (0.18) | – | – | 69 |
| A5 (paper) | PC, B65 (0.08) | – | – | – |
| A5 alternative | PC, B50 (0.31), B65 (0.42) | – | – | 112 |
| V2, VA funds on the supply side | PC (1.00), B50 (0.11), B65 (0.74) | PC, B50, B65 | PC | 138 |
| V2, no VA | PC (0.55), B65 (1.00); B50 rejected (0.04) | PC, B50 (0.05), B65 | PC | 154 |

For the two alternatives the selection is the same under all four scale schemes. For V2 the table shows η = 0.024. With each candidate's own η the selection is PC, B50 (0.05), B65 with the variable-annuity funds on the supply side and PC, B65 without them. The runs with PC's η and with the capped η had not finished when this file was written. Cells marked – are in the logs (`sc_conduct_*.csv`, `sc_mc.csv`, `sc_where.csv`) and are not repeated here.

**Reading.**
- **η does not depend on the demand model:** about 0.021 with the variable-annuity funds and 0.024 without.
- **V2 has the fewest negative marginal costs of the specifications that are valid without the variable-annuity funds,** and almost none below −0.20%. All are on non-cheap funds. Vanguard has 12–18% of its fund-months negative, which securities lending cannot explain.
- **B0 and B25 are rejected and PC is never rejected, in every row.** Under V2 and the two alternatives, B65 cannot be separated from PC.

## A5. Other checks

- **Danny's category10 specification** reproduces exactly (−5.713, SE 0.747) from the labels in his handoff zip. Downstream it is almost identical to T2 (negative MC 20–35%, Vanguard 79%, conduct PC alone), and it slopes upward without the variable-annuity funds (+1.485).
- **Danny's source panel and the index CSV.** The CSV (579,632 fund-months) is the source panel (675,551) after the estimation filter, which mostly drops a fund's first 12 months. The paper's instrument is built before the filter and rebuilds exactly from the source panel (`sc_source_panel_check.log`).
- **Earlier reports** (`RESULTS_spec_compare.md`, `RESULTS_broad_iv_ladder.md`, `RESULTS_other_interactions.md`, `for_coauthor/V2_replication/`) use V2 with the cheap indicator from the index CSV and are superseded by this file where they differ.

## A6. Index-fund flag and Lipper-class restrictions

Refined family ID; donors and cheap status from the index CSV; no VA funds (`sc_refined_family/`, `sc_rule_excluded_funds.csv`, `sc_q4_funds_bd.csv`).

- **B/D flag:** CRSP's `index_fund_flag` is B (index-based) or D (pure index) in most of the fund's quarters. It removes enhanced index funds and unflagged funds (all 39 Russell funds, PIMCO IndexPLUS, money market funds). 154 funds, 3.3% of assets.
- **Lipper exclusions:** long-short and other alternatives, leveraged, money market. After the B/D flag these remove 10 more funds. Adding target-date and extension funds to the exclusion set changes no coefficient by more than 0.3, so they are left in.

| | Recommended sample (section 3) | + B/D flag | + Lipper exclusions |
|---|---|---|---|
| Funds dropped (of 1,190) | 50 | 200 | 207 |
| T2, paper's exclusion | −7.49 (2.90) | **+6.74 (2.71)** | **+8.42 (3.97)** |
| A5, paper's exclusion: specialized; × broad | −10.69; −3.75 | +0.39 (2.14); −5.69 | +0.16 (2.77); −5.65 |
| T2, broad-asset-class exclusion | −12.73 (1.81) | −6.00 (0.93) | −7.59 (1.28) |
| A5, broad-asset-class exclusion: specialized; × broad | −13.33; −2.63 | −7.37; −4.83 | −8.99 (1.52); −4.39 |
| V2, 20th percentile, median: non-cheap | −10.350 | −9.191 (0.936) | −10.041 (1.047) |
| V2, 20th percentile, weighted mean: non-cheap | −6.877 | −7.485 (0.734) | −8.221 (0.832) |
| V2, 25th percentile, median: non-cheap | −4.969 | −3.444 (0.563) | −3.735 (0.609) |
| V2, 25th percentile, weighted mean: non-cheap | −2.058 | −1.815 (0.480) | −2.043 (0.534) |
| Negative MC, T2 broad-asset-class | 0.01–0.17 | 0.43–0.55 | 0.39–0.48 |
| Negative MC, V2 20th percentile, median | 0.000–0.002 | 0.009–0.027 | 0.009–0.020 |

- **V2 is stable across the three samples.**
- **The paper-type T2 and A5 turn upward again** with the B/D flag (first-stage F of 8 to 21). The reason was not traced.
- **The broad-asset-class versions keep their sign but halve,** and their negative marginal costs rise to 17–55%.

## A7. Family identifiers compared

Table 2 funds without VA, 2010–2024.

| Identifier | Distinct values | Funds whose value changes | Values within BlackRock | Within Vanguard | Within State Street |
|---|---|---|---|---|---|
| `mgmt_cd` (the paper's instrument) | 154 | 1,049 | 3 | 2 | 4 |
| `mgmt_name` | 231 | 1,068 | 7 | 19 | 7 |
| `adv_name` (adviser) | 140 | 603 | 4 | 2 | 5 |
| CUSIP issuer (first 6 digits) | 264 | 148 | 22 | 19 | 14 |
| Trust name (fund name before the colon) | 215 | 242 | 14 | 17 | 12 |
| Danny's `firm_f` | 77 | 42 | 1 | 1 | 2 |

- **For trusts such as SPY and QQQ, CRSP's management field alternates between the trustee and the sponsor.** SPY shows PDR Services (the licensing sponsor) in 2008–2012 and State Street otherwise.
- **Danny's ID without the refinement, by month, does not help:** T2 without VA funds is +18.5 (F 7), because real acquisitions still move the donor set.
- **Excluding every fund whose `firm_f` ever changes** would remove 111 funds and 7.1% of assets, including SPY and QQQ. The refined ID avoids that.
- A version with one fixed family per fund was tried and dropped: it assigns a fund to its final owner in the years before an acquisition.

## A8. Invesco DB Commodity Index Tracking Fund

| Years | Family code | Fee (%) | Instrument | Donor funds; largest donor | Share of inside market (%) |
|---|---|---|---|---|---|
| 2010–2014 | DBC | 0.87–0.88 | 0.84–0.85 | 9; sibling DB commodity funds | 0.13–0.25 |
| 2015–2017 | ICA | 0.86–0.90 | 0.72–0.78 | 2–4; Invesco DB US Dollar Index | 0.03–0.06 |
| 2018–2020 | ICA | 0.82–0.88 | 0.31–0.37 | 162–176; Invesco QQQ Trust (46% of weight) | 0.01–0.04 |
| 2021–2024 | ICA, AIM | 0.84–0.86 | 0.25–0.29 | 196; Invesco QQQ Trust (59%) | 0.01–0.03 |

- After fund and month effects, the fund's instrument and its market share have a correlation of 0.86; its instrument and its fee, −0.18.
- The instrument falls because the family label absorbs cheaper funds. The share falls because of the commodity bust and the growth of the index market.

## A9. Why a few funds can decide the sign

- **The IV slope is a ratio:** how the instrument moves with market shares, over how it moves with fees, both within fund.
- **The denominator is small.** Fees barely change within a fund (standard deviation 0.02–0.05 after fund and month effects). In the sample without VA funds it sums to 3.6 over 100,529 fund-months.
- **A fund's weight depends on how much its instrument moves.** For the top entry-fee quartile the instrument's standard deviation is 0.086, against 0.028 for the bottom quartile.
- **So a few funds supply most of the numerator and none of the denominator.** The top quartile contributes +45.6 to a numerator of +26.2 and −0.15 to the denominator; the DB Commodity fund contributes +31.6 by itself (`sc_q4_influence.log`).
