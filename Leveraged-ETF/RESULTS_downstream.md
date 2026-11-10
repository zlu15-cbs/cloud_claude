# Downstream results: how sensitive are the scale, negative MC and conduct to the demand model?

## Key takeaways

1. **The cheap definition decides whether demand is valid.**
    - Every definition that marks 59–88% of fund-months as cheap (Danny's CRSP and index versions, the all-CRSP reference) leaves the expensive remainder with upward-sloping demand, under every instrument tried.
    - Our entry-tier definition (index reference, 47% cheap) is the only one with valid demand across instruments.
2. **The scale η is not informative about demand or conduct.** It is 0.019–0.025 in every model and under every candidate, because logit markups are nearly a fund constant and the fund FE absorb them. It is set by fees and AUM alone; the estimation versus full supply sample moves it more (0.0205 → 0.0235).
3. **Negative MC is where demand matters, from 0 to 98% of fund-months.**
    - It falls as the non-cheap slope steepens.
    - The two valid steep-slope models have **zero** negative MC after the scale adjustment: ours (flag-Z, asset-class exclusion, −8.0) and the paper's IV on all rows (−8.1).
    - Flatter valid models (cluster −3.6, paper's IV on family rows −2.7) pass the magnitude bounds, but their negative MCs sit at Vanguard non-cheap funds, where lending cannot explain them.
    - Danny's exclusion rule (index, −1.3) fails outright.
4. **Danny's benchmark reaches zero negative MC mechanically.** A quarter of its markups are negative (upward-sloping demand). The bridge model (his definition with our instrument) shows the same.
5. **The conduct test is robust but only partly decisive.**
    - B0 (firm Bertrand) and B25 are rejected under every valid demand model, instrument, η scheme and cap.
    - PC is never rejected.
    - With the pre-specified instrument, PC, B50 and B65 cannot be separated under valid demand; most alternative instruments select PC alone.
    - "PC only" with the main instrument arises only with invalid or flat demand, which is how Danny's PDFs get it.
6. **The open demand choice is the instrument's exclusion level** (asset class −8.0 / cluster −3.6 / index −1.3).
    - The lead tests favour the narrower exclusions.
    - The MC criteria (magnitude and location) favour the asset-class exclusion.
    - The sample choice (family-id rows versus all 108,300) matters for the paper's IV (−2.7 versus −8.1) but not for the conduct conclusions.

## Scorecard: all 9 models

**Caution.** Every model here includes 4 money market funds (437 fund-months) that are in the Table 2 sample. Without them, models 2, 3 and 5 slope upward, and models 1 and 6 flatten to about −3 (`RESULTS_best_model1.md` §4).

✓ = desirable, ~ = borderline, ✗ = undesirable, – = not applicable. Downstream rows use all 108,300 fund-months, η scheme A for conduct, and the range over B0–B65 at each candidate's own estimated η. Sources: §1–§7 below; `logs/step32b|c|d.log`; `logs/step34_mc_m*.csv`.

| | 1 ours | 2 | 3 | 4 | 5 | 6 | 7 Danny | 8 | 9 bridge |
|---|---|---|---|---|---|---|---|---|---|
| **Specification** | | | | | | | | | |
| Instrument | Z_flag | Z_flag | Z_flag | Z_flag | paper IV | paper IV | paper IV | paper IV | Z_flag |
| Instrument excludes same | asset class | cluster | index | asset class | – | – | – | – | asset class |
| Cheap interaction | gene_idx | gene_idx | gene_idx | none | gene_idx | gene_idx | danny_crsp | danny_crsp | danny_crsp |
| Estimation rows | 97,294 | 97,399 | 97,399 | 97,294 | 97,429 | 108,300 | 108,300 | 97,429 | 97,294 |
| **Demand outcomes** | | | | | | | | | |
| Non-cheap α | −8.02 | −3.64 | −1.25 | −0.85 | −2.72 | −8.13 | +5.85 | +17.14 | +7.93 |
| Cheap total α | −32.7 | −25.9 | −21.5 | – | −26.8 | −40.8 | −14.9 | −0.7 | −7.2 |
| Table 5 funds with \|e\| > 1 | 7/15 | 7/15 | 4/15 | 0/15 | 7/15 | 11/15 | 5/15 | 1/15 | 2/15 |
| **Demand screens** | | | | | | | | | |
| No upward slope (e > 0 share) | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.25 | ✗ 0.20 | ✗ 0.20 |
| First-stage F (min) | ✓ 114 | ✓ 72 | ✓ 103 | ✓ 222 | ~ 13 | ~ 18 | ✓ 44 | ✓ 25 | ✓ 225 |
| Lead tests, max \|t\| (12/24/36) | ✗ 4.3 | ✓ 1.4 | ✓ 1.6 | ✗ 4.2 | ~ 2.2 | ✗ 5.3 | ✓ 1.8 | ✗ 18.5 | ✓ 1.0 |
| Fee heterogeneity (cheap vs non-cheap) | ✓ | ✓ | ✓ | ✗ none | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Downstream outcomes** | | | | | | | | | |
| Scale η range (PC–B65) | 0.0205–0.0212 | 0.0204–0.0215 | 0.0186–0.0227 | 0.0205–0.0253 | 0.0203–0.0219 | 0.0205–0.0212 | 0.0193–0.0205 | 0.0135–0.0205 | 0.0193–0.0205 |
| Negative-markup share | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.25 | ✗ 0.17 | ✗ 0.21–0.25 |
| Negative-MC share | 0 | 0.06–0.08 | 0.49–0.67 | 0.98 | 0.13–0.14 | 0 | 0 | 0.77–0.82 | 0.06–0.20 |
| Min MC (% of assets) | −0.02 | −0.21 | −0.88 | −3.05 | −0.33 | −0.01 | +0.03 | −3.74 | −0.15 |
| **MC screens** (`NOTE_seclending_MC_bounds.md`) | | | | | | | | | |
| Magnitude: ≤ 2% below −0.20%, none below −0.60% | ✓ | ✓ | ✗ | ✗ | ~ B0/B25 only | ✓ | ✓ mechanical | ✗ | ✓ mechanical |
| Location: not at Vanguard or SPY | – none | ✗ Vanguard | ✗ | ✗ | ✗ Vanguard | – none | – none | – (fails size) | ✗ all Vanguard |
| **Conduct** | | | | | | | | | |
| Main IV selected set | PC, B50, B65 | PC, B50, B65 | PC, B50, B65 | PC | PC, B50, B65 | PC, B50, B65 | PC | PC | PC |
| Alternative IVs (majority) | PC | PC | PC, B65 | PC | PC | PC | PC | PC | PC |
| B0 and B25 rejected | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Robust to η scheme and capping | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Overall** | **pass** (lead caveat) | MC location fails | MC fails | MC fails, no heterogeneity | MC fails at B50/B65 and location | **pass** (weak F, lead caveat) | demand fails | demand and MC fail | demand fails |

Index market, logit demand, 9 demand models (`RESULTS_demand_grid.md` §4a).
- **Code:** `code/explore/downstream.py`, `step34_downstream.py`; validation `step33_downstream_validate.py`.
- **Logs and CSVs:** `logs/step33.log`, `logs/step34_*`.
- **Supply sample:** all 108,300 fund-months, unless marked "est" (estimation rows only).

## 0. Validation (`logs/step33.log`)

| Check | Result |
|---|---|
| Our logit markups vs pyblp (Table 2 col 2; Danny's benchmark with heterogeneous α) | identical (< 1e-13; pyblp's `compute_markups` is the Lerner index) |
| Our markups vs pyRVtest's own, PC / B0 / B25 / B50 / B65 | identical (< 2e-15) |
| Negative-MC share, B0, Table 2 IV logit, scale 0 | **0.5156** = Danny's 0.5156 |
| Scale under PC | **0.0205 (0.0051)** = Danny's 0.0205 (0.0051) |
| Conduct test with supplied markups vs pyRVtest computing its own | identical RV statistics; MCS p-values differ in the 4th decimal (simulation) |

**Definitions.**
- B0 is firm-level Bertrand. B25 / B50 / B65 add a 0.25 / 0.50 / 0.65 profit weight among BlackRock, Vanguard and SSGA (notebook kappa specifications 2 / 3 / 6).
- MC(η) = p + η·log(TNA) − markup.
- η is estimated under each candidate by 2SLS: MC winsorized 1/99 within calendar year, regressed on log AUM instrumented by the rotator, plus |tracking error|, log age, fund and month FE; clustered by month.
- **Conduct test:** pyRVtest. "Selected" means the model is not rejected in the model confidence set at 5% (MCS p ≥ 0.05).
- **Pre-specified main conduct instrument:** rival funds × residualized sentiment. The five alternatives are those listed in the notebook (cell 41).

## 1. Demand models

| # | Model | N | Non-cheap α | Cheap total | Min F | e > 0 |
|---|---|---|---|---|---|---|
| 1 | Z_flag, exclude asset class × gene_idx (ours) | 97,294 | −8.02 | −32.7 | 114 | 0 |
| 2 | Z_flag, exclude cluster × gene_idx | 97,399 | −3.64 | −25.9 | 72 | 0 |
| 3 | Z_flag, exclude index × gene_idx | 97,399 | −1.25 | −21.5 | 103 | 0 |
| 4 | Z_flag, no interaction | 97,294 | −0.85 | | 222 | 0 |
| 5 | paper IV × gene_idx, family-id rows | 97,429 | −2.72 | −26.8 | 13 | 0 |
| 6 | paper IV × gene_idx, all rows | 108,300 | −8.13 | −40.8 | 18 | 0 |
| 7 | **Danny's benchmark** (paper IV × danny_crsp, all rows) | 108,300 | **+5.85** | −14.9 | 44 | **0.25** |
| 8 | paper IV × danny_crsp, family-id rows | 97,429 | +17.14 | −0.7 | 25 | 0.20 |
| 9 | bridge: Z_flag × danny_crsp | 97,294 | +7.93 | −7.2 | 225 | 0.20 |

## 2. Scale η by conduct candidate: insensitive

| # | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|
| 1 | 0.0205 (0.0051) | 0.0206 | 0.0209 | 0.0211 | 0.0212 |
| 2 | 0.0205 | 0.0204 | 0.0209 | 0.0213 | 0.0215 |
| 3 | 0.0205 | 0.0186 | 0.0202 | 0.0218 | 0.0227 |
| 4 | 0.0205 | 0.0253 | 0.0250 | 0.0239 | 0.0227 |
| 5 | 0.0205 | 0.0203 | 0.0210 | 0.0215 | 0.0219 |
| 6 | 0.0205 | 0.0206 | 0.0208 | 0.0211 | 0.0212 |
| 7 | 0.0205 | 0.0195 | 0.0195 | 0.0194 | 0.0193 |
| 8 | 0.0205 | 0.0173 | 0.0166 | 0.0150 | 0.0135 |
| 9 | 0.0205 | 0.0197 | 0.0196 | 0.0194 | 0.0193 |
| 1 est / 5 est | 0.0235 | 0.0235 / 0.0232 | 0.0238 / 0.0239 | 0.0241 / 0.0246 | 0.0242 / 0.0251 |

SEs are 0.0046–0.0057, except model 4 under B50/B65 and model 8 (0.009–0.022).

**Why η barely moves.** A logit markup is about 1/(|α_j|(1 − s_j)). Shares are tiny and α_j is fixed per fund, so the markup is almost a fund constant: fund and month FE absorb 99.8% of its variance in model 1. η is identified from within-fund variation driven by the rotator, so it collapses to the PC value. Only when |α| is small (model 4: markups about 1.5 pp) does the residual share-driven movement shift η, by +0.004 to +0.005. Scratch check: `logs/why_eta.py`.

**The supply sample matters more than demand or conduct.** On the estimation rows only, η is 0.0235 instead of 0.0205, because the family-less funds leave the scale regression.

## 3. Negative marginal costs: highly sensitive to demand

Monthly-mean share of fund-months with MC < 0. PC is 0 in every row. B0 → B65 shown.

| # | η = 0 | η = 0.024 | own estimated η | **Admissible?** (own η: ≤ 2% below −0.20%, none below −0.60%) |
|---|---|---|---|---|
| 1 | 0.16–0.26 | **0** | **0** | **yes** (min MC −0.01) |
| 2 | 0.32–0.45 | 0.04–0.07 | 0.06–0.08 | **yes** (0% below −0.20; min −0.13 to −0.21) |
| 3 | 0.76–0.86 | 0.48–0.65 | 0.49–0.67 | **no** (36–37% below −0.20; 4–9% below −0.60) |
| 4 | 0.99 | 0.98 | 0.98 | **no** (96% below −0.20; 79–82% below −0.60) |
| 5 | 0.42–0.57 | 0.11–0.13 | 0.13–0.14 | B0/B25 yes (0.1% / 0.6%); B50/B65 **no** (2.3% / 3.7% below −0.20) |
| 5 est | 0.44–0.61 | 0.11–0.14 | 0.12–0.13 | B0–B50 yes; B65 marginal (2.2%) |
| 6 | 0.13–0.23 | **0** | **0** | **yes** |
| 7 Danny | 0.24–0.26 | **0** | **0** | "yes", but **mechanically**: 25% of markups are **negative** (upward-sloping demand) |
| 8 | 0.77–0.82 | 0.77–0.82 | 0.77–0.82 | **no** (77–82% below −0.20; 76–81% below −0.60) |
| 9 bridge | 0.41–0.47 | 0.01–0.14 | 0.06–0.20 | "yes", but 21–25% of markups are negative |

**Reading.**
- **Demand drives this result.** The flatter the non-cheap slope, the larger the markups and the more negative the MCs: model 1 (α −8) has 0%, model 3 (α −1.25) about 50–67%, model 4 (α −0.85) 98%.
- **The scale adjustment matters too.** It takes the valid steep-slope models (1, 6) from 13–26% to 0.
- **Danny's benchmark reaches 0 for the wrong reason.** Its zero negative MCs come from negative markups on a quarter of fund-months, not from plausible demand. The bridge (model 9) shows the same mechanism with our instrument.

## 4. Conduct test: B0 and B25 rejected under valid heterogeneous demand; PC never rejected

Selected sets (MCS p ≥ 0.05). Supply on all rows, η scheme A (0.024). Schemes B (own η) and C (PC η, Danny's convention) give the **same sets** in every model, except model 1 with the csent_income3 instrument (B: PC, B65).

| # | **Main IV** (rival2 × csent_index) | rival2 × csent_income3 | rival3 × csent_index | rival2 × bab_usa / × fmax / × rotator |
|---|---|---|---|---|
| 1 | PC, B50, B65 | PC, B50, B65 | PC | PC |
| 2 | PC, B50, B65 | PC, B50, B65 | PC | PC |
| 3 | PC, B50, B65 | PC, B50, B65 | PC, B50, B65 | PC, B65 |
| 4 | PC | PC | PC | PC |
| 5 | PC, B50, B65 | PC, B50, B65 | PC, B65 (B, C: PC, B50, B65) | PC |
| 6 | PC, B50, B65 | PC, B50, B65 | PC | PC |
| 7 Danny | PC | PC | PC | PC |
| 8 | PC | PC | PC | PC |
| 9 bridge | PC | PC | PC | PC |
| 1 est / 5 est | PC, B65 | PC, B50, B65 / PC, B65 | PC | PC |

**Reading.**
1. **PC is never rejected**, in any model, instrument or η scheme.
2. **B0 and B25 are rejected everywhere.** In the valid heterogeneous-demand models (1, 2, 3, 5, 6), the main instrument cannot separate PC from B50/B65. The alternative instruments select PC alone in most cases.
3. **"PC only" with the main instrument comes from the invalid or flat demand models (4, 7, 8, 9).** It is the same pattern as in Danny's PDFs: PC is "selected" decisively where demand is invalid.
4. **The η scheme does not matter** (A, B and C agree), consistent with §2.

## 5. Answers to the round's question

| Downstream result | Sensitivity to demand (among valid models 1, 2, 3, 5, 6) | Sensitivity to conduct |
|---|---|---|
| Scale η | negligible (0.019–0.023) | negligible |
| Negative MC after the scale adjustment | **large**: 0 (models 1, 6), 6–8% (2), 13% (5), 49–67% (3) | moderate (rises B0 → B65) |
| Admissibility (sec-lending bounds) | models 1, 2, 6 pass; 5 passes for B0/B25 only; 3 fails | |
| Conduct selection | stable: {PC, B50, B65} with the main IV; B0 and B25 always rejected | |

**Which demand models survive both demand screens and the MC bounds:** 1 (ours), 6 (paper IV, all rows) and 2 (cluster exclusion), and 5 under B0/B25. Model 3 (Danny's exclusion rule with our share classes) has valid demand but fails the MC bounds.

## 6. Where the negative MCs are (rule 3 of `NOTE_seclending_MC_bounds.md`)

`step35_checks.py`, `logs/step35_where_m*.csv`. Fund-months with MC < 0 at the candidate's own estimated η, all 108,300 rows. Cells give the share negative within the group, with the group's share of all negative MCs in parentheses. Models 1, 6 and 7 have none.

| Model, conduct | Vanguard | SSGA | BlackRock | Other firms | SPY | Cheap / non-cheap | US eq. / intl eq. / bond | Small-micro vs other |
|---|---|---|---|---|---|---|---|---|
| 2, B0 | **0.13 (0.57)** | 0.05 (0.07) | 0.05 (0.18) | 0.02 (0.18) | 0 | 0 / 0.10 | 0.06 / 0.06 / 0.04 | 0.06 vs 0.06 |
| 2, B65 | 0.17 (0.50) | 0.25 (0.24) | 0.07 (0.16) | 0.02 (0.09) | 0 | 0 / 0.15 | 0.10 / 0.09 / 0.06 | 0.08 vs 0.09 |
| 5, B0 | 0.19 (0.36) | 0.28 (0.17) | 0.09 (0.14) | 0.09 (0.32) | 0 | 0 / 0.23 | 0.14 / 0.14 / 0.10 | 0.15 vs 0.13 |
| 3, B0 | 0.20 (0.10) | 0.69 (0.11) | 0.59 (0.25) | 0.56 (0.54) | 0 | 0 / 0.88 | 0.50 / 0.65 / 0.27 | 0.53 vs 0.49 |
| 9 bridge, B0 | 0.25 (1.00) | 0 | 0 | 0 | 0 | | 0.06 / 0.03 / 0.15 | |

**Reading.**
- **SPY never has a negative MC.**
- **Rule 3 fails for models 2 and 5.**
    - Negative MCs sit among **non-cheap** funds only, and disproportionately at **Vanguard**: 57% of model 2's negative MCs (B0), with 13% of Vanguard fund-months negative against 2% for non-Big-3 firms. Vanguard lends at cost, so securities lending cannot explain a negative MC there.
    - They are **not** concentrated in small-cap or international funds, where lending revenue is highest: small/micro 0.06 against other 0.06.
    - The mechanism is the demand model's. Non-cheap funds get the flatter slope, hence the larger markups, and Vanguard's non-cheap classes (older, higher-fee classes in a low-fee family) have markups above price.
- **Model 3 fails everywhere**, consistent with §3.
- **Implication:** on the MC criteria, only the steep-slope valid models (1 and 6) are clean. Models 2 and 5 pass the magnitude bound, but their negative MCs fall where securities lending cannot explain them.

## 7. Danny's conduct convention: markups capped 1/99 by year

`logs/step35_conduct_capped_m*.csv`. Markups winsorized at the 1st/99th percentiles within each calendar year before the test, as Danny does. pyRVtest stands in for his own RV/MCS code, which is not available. η = 0.024 (A) and the PC-estimated η (C).

| # | Main IV | csent_income3 | rival3 × csent | bab_usa / fmax / rotator |
|---|---|---|---|---|
| 1 | PC, B50, B65 | PC, B50, B65 | PC | PC |
| 2 | PC, B50, B65 | PC, B50, B65 | PC | PC |
| 3 | PC, B50, B65 | PC, B50, B65 | PC, B50, B65 | PC, B65 |
| 5 | PC, B50, B65 | PC, B50, B65 | PC, B65 | PC |
| 6 | PC, B50, B65 | PC, B50, B65 | PC | PC |
| 7 Danny | PC | PC | PC | PC |
| 9 bridge | PC | PC | PC | PC |

Capping changes **nothing**: the selected sets equal the uncapped ones in §4, for both η schemes.
