# Five demand specifications for the index market: which survive the family-code check, the demand screens and the marginal-cost screens?

## Key takeaways

1. **The two specifications in the paper depend on 7,771 fund-months that have no family code.**
    - Table 2 (T2): −5.61 on all rows, **+7.24** on the 100,529 rows with a family code.
    - Broad-based interaction (A5): specialized slope −7.50 on all rows, **+4.01** with a family code, where 49% of fund-months have e > 0.
    - On those 7,771 rows the instrument averages the fees of unrelated firms, so it is not a family instrument.
2. **Goal A (no upward-sloping demand) holds for all five as specified, but only V2, A5d and the modified T2 keep it on the rows with a family code.**
    - V2 and A5d are estimated on those rows only. The modified T2 (proxy) gives −4.56 there.
3. **Goal B (fewer negative MCs): A5 and the modified T2 are lowest at B0, V2 and A5d are flattest across conduct, T2 is worst.**
    - Negative-MC share at own η, B0–B65: A5 0.005–0.088; modified T2 0.006–0.163; A5d 0.050–0.065; V2 0.053–0.082; T2 0.21–0.36.
    - The single-slope and broad-only models put their negatives on cheap Vanguard funds; V2 and A5d put them on non-cheap funds.
4. **Broad-based alone has no defensible version; it survives only next to the cheap interaction.**
    - On defensible rows with an asset-class exclusion, the specialized slope is −0.23 (SE 0.47) and 80% of marginal costs are negative.
    - Added to V2 (A5d), broad-based is −2.56 (SE 0.31), the cheap coefficient is unchanged (−20.5), and the lead tests stay at 2.2.
    - Its sign depends on the label: made consistent within an index, the coefficient is +2.31 (SE 0.89).
5. **Goal D: the scale η does not move (0.019–0.023); negative MC and the fate of B50 and B65 do.**
    - B0 and B25 are rejected in all five. PC is never rejected.
    - T2 selects PC alone. Modified T2 and A5 keep B65 at the margin (p 0.06 and 0.08). V2 and A5d cannot separate PC from B65.
6. **The open choice is V2 or A5d against Danny's modified T2, and it needs his category10 instrument.**
    - Our proxy does not reproduce his coefficient (−9.11 against −5.71).
    - Whether to keep the 7,771 family-less rows in the demand estimation has to be decided first, because T2 and A5 change sign with it.

## Scorecard: all 5 models

**Caution.** Column 2 is a proxy for Danny's specification: it uses the Lipper 6 asset groups in place of his category10 labels and our 579,632-row donor file in place of his 675,551-row panel. Columns 1, 2 and 4 use the paper's 108,300 rows, including 4 money market funds; columns 3 and 5 drop those funds and estimate demand on the 96,069 rows where V2's instrument is defined. "A5" is the broad-based interaction, which is Table A7 in our copy of the paper; the fee-tercile specification called A5 in `RESULTS_spec_compare.md` is a different model. No test here establishes that any instrument satisfies the exclusion restriction.

✓ = desirable, ~ = borderline, ✗ = undesirable, – = not applicable. Downstream rows give the range over B0–B65 at each candidate's own estimated η; conduct uses η scheme A (0.024). Sources: `logs/spec_compare/sc_demand.csv`, `sc_a5_demand.csv`, `sc_scale.csv`, `sc_a5_scale.csv`, `sc_mc.csv`, `sc_a5_mc.csv`, `sc_where.csv`, `sc_a5_where.csv`, `sc_conduct_*.csv`.

| | 1 T2 | 2 Modified T2 (Danny, proxy) | 3 V2 | 4 A5 (broad, paper) | 5 A5d (broad + cheap) |
|---|---|---|---|---|---|
| **Specification** | | | | | |
| Instrument | paper IV0 | IV0 rebuilt, stricter exclusion | Z (V2) | paper IV0 | Z (V2) |
| Donors exclude the target's | index | index and Lipper-6 asset class | Lipper-6 asset class, other share types | index | Lipper-6 asset class, other share types |
| Donor aggregation | lag-AUM-weighted mean | lag-AUM-weighted mean | median | lag-AUM-weighted mean | median |
| Price interactions | none | none | cheap | broad-based | cheap and broad-based |
| Estimation rows | 108,300 | 108,300 (10,263 on original IV0) | 96,069 | 108,300 | 96,069 |
| **Demand outcomes** | | | | | |
| Base price coefficient (SE) | −5.606 (1.310) | −9.107 (0.912) | −3.642 (0.419) | −7.503 (1.770) | −2.948 (0.418) |
| × cheap (SE) | – | – | −20.562 (0.646) | – | −20.484 (0.642) |
| × broad-based (SE) | – | – | – | −5.278 (0.372) | −2.555 (0.308) |
| Average own elasticity | −1.61 | −2.62 | −1.93 | −2.86 | −2.02 |
| Asset-weighted own elasticity | −0.72 | −1.17 | −1.61 | −1.31 | −1.67 |
| Table 5 funds with \|e\| > 1 | 2/15 | 2/15 | 5/15 | 2/15 | 7/15 |
| **Demand screens** | | | | | |
| Goal A: no upward slope (e > 0 share) | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| Same on rows with a family code | ✗ +7.24; all e > 0 | ✓ −4.56 (0.66) | ✓ (its own rows) | ✗ +4.01; 49% e > 0 | ✓ (its own rows) |
| First-stage F (min) | ✓ 34 | ✓ 87 | ✓ 316 | ✓ 53 | ✓ 344 |
| Lead tests, max \|t\| (12/24/36) | ✗ 3.3 (−3.3 / −1.5 / 2.1) | ✗ 3.5 (−3.5 / −3.1 / −2.5) | ~ 2.2 (−2.0 / −2.2 / −0.5) | ✗ 5.3 (−5.3 / −4.9 / −2.4) | ~ 2.2 (−2.2 / −2.2 / −0.4) |
| Robust to the definition of the interaction | – | – | ✓ cutoffs 10–20% | ✗ label inconsistent for 154 funds | ✗ broad flips to +2.31 with a consistent label |
| **Downstream outcomes** | | | | | |
| Scale η range (PC–B65; SE about 0.005) | 0.0205–0.0213 | 0.0205–0.0210 | 0.0210–0.0220 | 0.0205–0.0208 | 0.0211–0.0225 |
| Negative-markup share | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 |
| Negative-MC share, η = 0 | 0.52–0.58 | 0.40–0.49 | 0.33–0.46 | 0.39–0.47 | 0.30–0.44 |
| Negative-MC share, η = 0.024 | 0.17–0.34 | 0–0.09 | 0.04–0.07 | 0–0.04 | 0.04–0.06 |
| Goal B: negative-MC share, own η | 0.21–0.36 | 0.006–0.163 | 0.053–0.082 | 0.005–0.088 | 0.050–0.065 |
| Min MC (% of assets) | −0.31 | −0.12 | −0.21 | −0.12 | −0.27 |
| **MC screens** | | | | | |
| Magnitude: ≤ 2% below −0.20%, none below −0.60% | ~ B0–B50 pass; B65 8.9% | ✓ | ✓ | ✓ | ✓ (0.5% below −0.20% at B65) |
| Tight: ≤ 1% below −0.10%, none below −0.30% | ✗ 2.8–27% | ✓ | ~ B0, B25 only | ✓ | ✗ 1.9–3.8% |
| Location: not at Vanguard or SPY | ✗ Vanguard 81% (B0); SPY 85% (B65) | ~ Vanguard 2% (B0), 54% (B65) | ✗ Vanguard 13% (B0) | ~ Vanguard 2% (B0), 26% (B65) | ~ Vanguard 9%; SSGA 23% (B0) |
| **Conduct** | | | | | |
| Main IV selected set | PC | PC, B65 (p 0.06) | PC, B50 (0.19), B65 (0.79) | PC, B65 (p 0.08) | PC, B50 (0.11), B65 (0.87) |
| Alternative IVs (majority) | PC | PC | PC | PC | PC |
| B0 and B25 rejected | ✓ | ✓ | ✓ | ✓ | ✓ |
| Robust to η scheme and capping | ✓ | ✓ | ✓ | ✓ | ~ B50 drops out under own η (scheme B) |
| **Overall** | **fails the family-code check, leads and MC location** | **proxy only: good MC at B0/B25; fails leads; leaves large funds inelastic** | **passes demand screens; MC location caveat** | **fails the family-code check and leads** | **as V2 on demand; broad term depends on the label; fails the tight MC bound** |

- **Code:** `code/spec_compare/sc_build.py`, `sc_demand.py`, `sc_downstream.py` (columns 1 to 3), `sc_a5.py` (columns 4 and 5, and the family-code splits), `sc_broad_ladder.py` (instrument ladder).
- **Logs and CSVs:** `logs/spec_compare/`.
- **Supply sample:** all 108,300 fund-months for columns 1, 2 and 4; 107,863 (money market funds dropped) for columns 3 and 5. Rows outside the demand estimation stay in the shares and on the supply side.
- **Fuller reports:** `RESULTS_spec_compare.md` (columns 1 to 3, the fee-tercile model, V2 without cheap, the literature), `RESULTS_broad_iv_ladder.md` (why the broad-based slope changes sign), `RESULTS_other_interactions.md` (ETF and institutional interactions).

## 0. Validation

| Check | Result |
|---|---|
| T2: paper's −5.606 (1.310) | **−5.606 (1.310)**: exact |
| A5: paper's Table A7 Panel A col 2, −7.503 and −5.278 | **−7.503 (1.770) and −5.278 (0.372)**: exact |
| V2: −3.642 (0.419), −20.562 (0.646), F 315.8, N 96,069 | **exact**, with its downstream and conduct results |
| Danny's modified T2: −5.713 (0.747) | **not reproduced: proxy −9.107 (0.912)**; −7.254 (0.456) with blank families matched as in his construction |
| T2 negative-MC share, B0, η = 0: Danny's 0.5156 | **0.516** |
| Scale under PC: Danny's 0.0205 (0.0051) | **0.0205 (0.0051)** |

## 1. The family-code check: T2 and A5 change sign without the 7,771 family-less rows

Original IV0, paper sample (`sc_a5_demand.csv`, rows `x_T2_*`, `x_A5_*`).

| Specification | All 108,300 | 100,529 with a family code | 7,771 without |
|---|---|---|---|
| T2: one slope (SE); F | −5.606 (1.310); 34 | **+7.244 (1.987)**; 27 | +2.322 (0.538); 57 |
| T2: lead t (12/24/36) | −3.3 / −1.5 / 2.1 | 6.7 / 11.6 / 18.9 | 0.1 / −0.3 / −0.2 |
| A5: specialized (SE) | −7.503 (1.770) | **+4.009 (1.588)** | +0.747 (0.293) |
| A5: × broad-based (SE) | −5.278 (0.372) | −6.924 (0.428) | +4.884 (1.840) |
| A5: share with e > 0 | 0 | 0.49 | 1.00 |
| A5: lead t (12/24/36) | −5.3 / −4.9 / −2.4 | 4.1 / 10.9 / 16.4 | −0.9 / −2.5 / −2.2 |
| Modified T2 (proxy): one slope (SE) | −9.107 (0.912) | −4.555 (0.663) on V2's 96,069 rows; leads 3.4 / 6.2 / 7.8 | – |

**Reading.**
- **Each part slopes upward and the pooled sample slopes downward.** The negative T2 coefficient comes from comparing the family-less funds with the rest through the common month effects. This is my reading of the three columns, not a separate test.
- **The 7,771 rows are 112 mutual-fund classes of insurance and retirement-channel trusts** (Voya, Allianz, John Hancock, Nationwide), with a mean fee of 0.61%. Blank family codes match one another in IV0, so their donors are unrelated firms.
- **The stricter exclusion survives the check on sign.** The proxy for Danny's instrument stays negative on the rows with a family code, though its lead tests worsen to 7.8.
- **V2 and A5d do not face this check,** because rows without a family code have no Z and are not used to estimate demand.

## 2. Is there a defensible broad-based specification? Only with the cheap interaction

All rows below are on V2's 96,069 rows, money market funds dropped (`sc_a5_demand.csv`, `sc_broad_ladder.csv`, `sc_a5_mc.csv`).

| Specification | Base (SE) | × cheap | × broad (SE) | Min F | e > 0 | Lead t, max | Negative MC B0–B65 |
|---|---|---|---|---|---|---|---|
| Broad, paper IV0 | +3.43 (1.58) | | −6.65 (0.33) | 49 | 0.49 | 18.2 | – |
| Broad, V2's Z | +1.20 (0.30) | | −5.71 (0.30) | 399 | 0.49 | 2.9 | – |
| Broad, asset-class / same-type / weighted mean | −0.23 (0.47) | | −4.82 (0.31) | 425 | 0 | 2.7 | 0.80–0.82 |
| Same, label consistent within an index | +4.61 (0.85) | | −8.45 (0.51) | 414 | 0.40 | 5.1 | – |
| **A5d: cheap + broad, V2's Z** | **−2.95 (0.42)** | −20.48 (0.64) | **−2.56 (0.31)** | 344 | 0 | 2.2 | 0.050–0.065 |
| Cheap + broad, consistent label (`step43`) | −5.69 (1.19) | −21.76 | +2.31 (0.89) | 91 | 0 | 3.0 | 0.035–0.053 |
| V2 (cheap only) | −3.64 (0.42) | −20.56 (0.65) | | 316 | 0 | 2.2 | 0.053–0.082 |

**Reading.**
- **Broad-based on its own cannot be rescued.** The one instrument that keeps specialized funds from sloping upward gives them a slope of zero, hence markups of 2.5 to 3.3 percentage points and 80% negative marginal costs.
- **A5d is V2 with a broad-based term.** The cheap coefficient does not move (−20.5 against −20.6), the first stage and lead tests are the same, and two more Table 5 funds reach −1.00 and −1.01.
- **The broad-based term is not robust.** The paper's label is inconsistent for 154 funds (SPY and VTI's ETF class are "specialized"). With a consistent label the term changes sign.
- **So A5d adds a fragile coefficient to V2 and little else.** It lowers the negative-MC share slightly (0.050–0.065 against 0.053–0.082) but fails the tight magnitude bound that V2 passes at B0 and B25.

## 3. Scale η by conduct candidate: insensitive

| # | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|
| 1 T2 | 0.0205 (0.0051) | 0.0213 | 0.0212 | 0.0211 | 0.0209 |
| 2 Modified T2 (proxy) | 0.0205 | 0.0210 | 0.0210 | 0.0209 | 0.0208 |
| 3 V2 | 0.0211 (0.0051) | 0.0210 | 0.0215 | 0.0218 | 0.0220 |
| 4 A5 | 0.0205 | 0.0208 | 0.0208 | 0.0206 | 0.0205 |
| 5 A5d | 0.0211 | 0.0213 | 0.0218 | 0.0222 | 0.0225 |

SEs are 0.0048–0.0054 (`sc_scale.csv`, `sc_a5_scale.csv`).

**Reading.**
- **η is 0.0205 to 0.0225 in all five, under every candidate.** The spread is less than half a standard error.
- **It carries no information about demand or conduct,** as in `RESULTS_downstream.md` §2.

## 4. Negative marginal costs: highly sensitive to demand

Monthly-mean share of fund-months with MC < 0, B0 → B65. PC is 0 in every row.

| # | η = 0 | η = 0.024 | Own η | Share below −0.10% (own η) | Share below −0.20% (own η) | Min MC | Mean markup (%) |
|---|---|---|---|---|---|---|---|
| 1 T2 | 0.52–0.58 | 0.17–0.34 | 0.21–0.36 | 0.028–0.266 | 0–0.089 | −0.31 | 0.22–0.31 |
| 2 Modified T2 (proxy) | 0.40–0.49 | 0–0.09 | 0.006–0.163 | 0–0.001 | 0 | −0.12 | 0.14–0.19 |
| 3 V2 | 0.33–0.46 | 0.04–0.07 | 0.053–0.082 | 0.001–0.030 | 0–0.0002 | −0.21 | 0.19–0.23 |
| 4 A5 | 0.39–0.47 | 0–0.04 | 0.005–0.088 | 0–0.0004 | 0 | −0.12 | 0.13–0.17 |
| 5 A5d | 0.30–0.44 | 0.04–0.06 | 0.050–0.065 | 0.019–0.038 | 0–0.005 | −0.27 | 0.18–0.22 |

**Where the negatives are** (own η; share negative within the group).

| Specification, conduct | Vanguard | SSGA | BlackRock | Other firms | SPY | Cheap / non-cheap |
|---|---|---|---|---|---|---|
| 1 T2, B0 | **0.81** | 0.03 | 0.04 | 0.01 | 0 | 0.40 / 0.06 |
| 1 T2, B65 | **0.96** | 0.52 | 0.40 | 0.01 | **0.85** | 0.63 / 0.15 |
| 2 Modified T2, B0 | 0.02 | 0 | 0 | 0 | 0 | 0.01 / 0 |
| 2 Modified T2, B65 | **0.54** | 0.14 | 0.11 | 0 | 0 | 0.32 / 0.04 |
| 3 V2, B0 | 0.13 | 0.04 | 0.05 | 0.02 | 0 | 0 / 0.10 |
| 3 V2, B65 | 0.17 | 0.25 | 0.07 | 0.02 | 0 | 0 / 0.15 |
| 4 A5, B0 | 0.02 | 0 | 0 | 0 | 0 | 0.01 / 0 |
| 4 A5, B65 | 0.26 | 0.09 | 0.09 | 0 | 0 | 0.16 / 0.03 |
| 5 A5d, B0 | 0.09 | 0.23 | 0.03 | 0.01 | 0 | 0 / 0.09 |
| 5 A5d, B65 | 0.11 | 0.27 | 0.06 | 0.01 | 0 | 0 / 0.12 |

**Reading.**
- **T2 is the outlier.** A fifth to a third of its marginal costs are negative, at Vanguard and at SPY, where securities lending cannot explain them (`NOTE_seclending_MC_bounds.md`).
- **A5 and the modified T2 look best at B0, but their negatives are on cheap Vanguard funds and grow with the profit weight.** Both are less than 1% at B0 and 9% to 16% at B65.
- **V2 and A5d are stable across conduct (5% to 8%) and put the negatives on non-cheap funds.** A5d moves some of them from Vanguard to SSGA's specialized funds.
- **A5's good numbers rest on the sample in section 1.** Its demand is not valid on the rows with a family code.

## 5. Conduct test: B0 and B25 rejected, PC never rejected; B65 depends on demand

Selected sets (MCS p ≥ 0.05), η scheme A (0.024); MCS p-values in brackets.

| # | **Main IV** (rival2 × csent_index) | rival2 × csent_income3 | rival3 × csent_index | rival2 × bab_usa / × fmax / × rotator | Scheme B (own η), main IV |
|---|---|---|---|---|---|
| 1 T2 | PC (B50 0.02, B65 0.03 rejected) | PC | PC | PC | PC |
| 2 Modified T2 (proxy) | PC, B65 (0.06) | PC | PC | PC | PC, B65 (0.06) |
| 3 V2 | PC, B50 (0.19), B65 (0.79) | PC, B50, B65 | PC | PC | PC, B50 (0.14), B65 (0.70) |
| 4 A5 | PC, B65 (0.08) | PC, B65 (0.06) | PC | PC | PC, B65 (0.08) |
| 5 A5d | PC, B50 (0.11), B65 (0.87) | PC, B50, B65 | PC | PC | PC, B65 (0.69) |

Minimum pairwise F for the main instrument: T2 67, modified T2 92, V2 140, A5 103, A5d 136. Schemes C (PC η) and A with markups capped 1/99 by year give the same sets as scheme A in all five.

**Reading.**
- **B0 and B25 are rejected and PC is never rejected, in all five.**
- **B65 is the sensitive part.** It is rejected under T2 (p 0.03), marginal under the modified T2 and A5 (0.06 and 0.08), and not separable from PC under V2 and A5d (0.79 and 0.87).
- **The pattern follows the slope on the low-fee funds.** The steeper it is, the smaller the gap between the collusive candidates and PC.
- **This is reported, not used to choose.** The demand criteria come first.

## 6. Answers to the round's question

| Downstream result | Sensitivity to demand | Sensitivity to conduct |
|---|---|---|
| Scale η | negligible: 0.0205–0.0225 | negligible |
| Negative MC after the scale adjustment | **large**: 0.005–0.09 (A5), 0.006–0.16 (modified T2), 0.05–0.07 (A5d), 0.05–0.08 (V2), 0.21–0.36 (T2) | small for V2 and A5d; large for A5 and the modified T2 |
| Location of negative MCs | **large**: cheap Vanguard funds under one slope or broad-only; non-cheap funds under V2 and A5d | |
| Conduct: B0 and B25 rejected, PC not rejected | none | |
| Conduct: B50 and B65 | **sensitive**: rejected under T2; B65 marginal under the modified T2 and A5; kept under V2 and A5d | |

**Which specifications survive, in the order of the project rules:**

| Step | 1 T2 | 2 Modified T2 (proxy) | 3 V2 | 4 A5 | 5 A5d |
|---|---|---|---|---|---|
| Goal A as specified | ✓ | ✓ | ✓ | ✓ | ✓ |
| Goal A on rows with a family code | ✗ | ✓ | ✓ | ✗ | ✓ |
| Lead tests | ✗ | ✗ | ~ | ✗ | ~ |
| Robust interaction definition | – | – | ✓ | ✗ | ✗ |
| MC magnitude and location | ✗ | ~ | ~ | ~ | ~ |

**Open choices for Gene and Danny.**
1. Whether the 7,771 family-less fund-months stay in the demand estimation. T2 and A5 depend on them.
2. V2 against Danny's modified T2. This needs his category10 instrument values (`for_coauthor/NOTE_for_Danny_category10_and_family_code.md`).
3. Whether the paper keeps a broad-based table. If it does, A5d is the version that passes the demand screens, with the label caveat.
