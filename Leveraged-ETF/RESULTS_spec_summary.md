# Four demand specifications for the index market, with and without the variable-annuity funds: which results survive?

## Scorecard: all 4 models

**Caution.** Column 2 is a proxy for Danny's specification: it uses the Lipper 6 asset groups in place of his category10 labels and our 579,632-row donor file in place of his 675,551-row panel, and it does not reproduce his coefficient (−9.11 against −5.71). "A5" is the broad-based interaction, which is Table A7 in our copy of the paper. The lead tests are reported with two-way clustered standard errors, which differ from the month-clustered ones in our earlier files (section 3). No test here establishes that any instrument satisfies the exclusion restriction.

✓ = desirable, ~ = borderline, ✗ = undesirable, – = not applicable. "With VA" is each specification as written. "No VA" drops the 112 variable-annuity funds (7,771 fund-months) from the sample: they leave the demand estimation and the supply side, and their assets count in the outside good. Downstream rows give the range over B0–B65 at each candidate's own estimated η; conduct uses η scheme A (0.024). Sources: `logs/spec_compare/sc_demand.csv`, `sc_a5_demand.csv`, `sc_exva_demand.csv`, `sc_leadcheck.csv`, `sc_scale.csv`, `sc_mc.csv`, `sc_where.csv` and their `sc_a5_*` and `sc_exva_*` counterparts, `sc_conduct_*.csv`.

| | 1 T2, with VA | 1 T2, no VA | 2 Modified T2 (Danny, proxy), with VA | 2 Modified T2, no VA | 3 V2, with VA | 3 V2, no VA | 4 A5 (broad), with VA | 4 A5, no VA |
|---|---|---|---|---|---|---|---|---|
| **Specification** | | | | | | | | |
| Instrument | paper IV0 | paper IV0 | IV0 rebuilt, stricter exclusion | same | Z (V2) | Z (V2) | paper IV0 | paper IV0 |
| Donors exclude the target's | index | index | index and Lipper-6 asset class | same | Lipper-6 asset class, other share types | same | index | index |
| Price interaction | none | none | none | none | cheap | cheap | broad-based | broad-based |
| Estimation rows | 108,300 | 100,529 | 108,300 | 100,529 | 96,069 | 96,069 | 108,300 | 100,529 |
| Supply rows | 108,300 | 100,529 | 108,300 | 100,529 | 107,863 | 100,092 | 108,300 | 100,529 |
| **Demand outcomes** | | | | | | | | |
| Base price coefficient (SE) | −5.606 (1.310) | **+7.244 (1.987)** | −9.107 (0.912) | −3.491 (0.644) | −3.642 (0.419) | −3.642 (0.419) | −7.503 (1.770) | **+4.009 (1.588)** |
| Interaction (SE) | – | – | – | – | −20.562 (0.646) | −20.562 (0.646) | −5.278 (0.372) | −6.924 (0.428) |
| Average own elasticity | −1.61 | +1.91 | −2.62 | −0.92 | −1.93 | −1.93 | −2.86 | +0.31 |
| Asset-weighted own elasticity | −0.72 | +0.89 | −1.17 | −0.43 | −1.61 | −1.61 | −1.31 | +0.08 |
| Table 5 funds with e < −1 | 2/15 | 0/15 | 2/15 | 1/15 | 5/15 | 5/15 | 2/15 | 0/15 |
| **Demand screens** | | | | | | | | |
| Goal A: no upward slope (e > 0 share) | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.49 |
| First-stage F (min) | ✓ 34 | ✓ 27 | ✓ 87 | ✓ 117 | ✓ 316 | ✓ 316 | ✓ 53 | ✓ 49 |
| Lead tests, max \|t\|, two-way clustered | ✓ 0.4 | ✗ 2.7 | ✓ 0.5 | ✓ 0.8 | ✓ 0.4 | ✓ 0.4 | ✓ 0.8 | ~ 2.0 |
| **Downstream outcomes** | | | | | | | | |
| Scale η range (PC–B65; SE about 0.005) | 0.0205–0.0213 | 0.0228–0.0235 | 0.0205–0.0210 | 0.0233–0.0247 | 0.0210–0.0220 | 0.0238–0.0250 | 0.0205–0.0208 | 0.0233–0.0250 |
| Negative-markup share | ✓ 0 | ✗ 1.00 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✓ 0 | ✗ 0.49 |
| Negative-MC share, η = 0 | 0.52–0.58 | – | 0.40–0.49 | 0.65–0.77 | 0.33–0.46 | 0.35–0.48 | 0.39–0.47 | – |
| Negative-MC share, η = 0.024 | 0.17–0.34 | – | 0–0.09 | 0.43–0.60 | 0.04–0.07 | 0.04–0.08 | 0–0.04 | – |
| Goal B: negative-MC share, own η | 0.21–0.36 | – | 0.006–0.163 | **0.42–0.59** | 0.053–0.082 | **0.041–0.073** | 0.005–0.088 | – |
| Min MC (% of assets) | −0.31 | – | −0.12 | −0.58 | −0.21 | −0.19 | −0.12 | – |
| **MC screens** | | | | | | | | |
| Magnitude: ≤ 2% below −0.20%, none below −0.60% | ~ B65 8.9% | – | ✓ | ✗ 15–38% below −0.20% | ✓ | ✓ | ✓ | – |
| Location: not at Vanguard or SPY | ✗ Vanguard 81% (B0); SPY at B65 | – | ~ Vanguard 2% (B0), 54% (B65) | ✗ Vanguard 99% (B0); SPY at B65 | ✗ Vanguard 13% (B0) | ✗ Vanguard 10% (B0) | ~ Vanguard 2% (B0), 26% (B65) | – |
| **Conduct** | | | | | | | | |
| Main IV selected set | PC | – | PC, B65 (0.06) | PC, B50 (0.13), B65 (0.13) | PC, B50 (0.19), B65 (0.79) | PC (0.52), B50 (0.05), B65 (1.00) | PC, B65 (0.08) | – |
| Alternative IVs (majority) | PC | – | PC | PC | PC | PC | PC | – |
| B0 and B25 rejected | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| **Overall** | **passes only with the VA funds** | **demand slopes upward** | **good MC, but only with the VA funds** | **valid sign; flat slope; MC fails** | **passes demand screens; MC location caveat** | **unchanged; slightly fewer negative MCs** | **passes only with the VA funds** | **49% slope upward** |

**What the scorecard says.**
- **T2 and A5 are fragile.** Their downward-sloping demand, and everything downstream of it, depends on keeping the variable-annuity funds in the estimation. Without those funds T2 slopes upward for every fund-month and A5 for 49% of them.
- **The real choice is between column 2 and column 3.** Both keep downward-sloping demand without the variable-annuity funds.
- **Column 2 (proxy) loses its good marginal-cost results without them.** Its slope falls from −9.1 to −3.5, and the negative-MC share rises from 0.6–16% to 42–59%, with 99% of Vanguard's fund-months negative. It also leaves all but one of the Table 5 funds inelastic.
- **Column 3 (V2) does not change.** The variable-annuity funds were never in its demand estimation. Dropping them from the supply side lowers the negative-MC share slightly (4.1–7.3%) and moves the conduct result toward B65.
- **Column 2 is still a proxy.** Danny's own category10 instrument may behave differently, and this comparison should be rerun with it.

- **Code:** `code/spec_compare/sc_build.py`, `sc_demand.py`, `sc_downstream.py` (columns 1 to 3), `sc_a5.py` (column 4), `sc_exva.py` (the "no VA" columns), `sc_leadcheck.py` (lead tests).
- **Logs and CSVs:** `logs/spec_compare/`.
- **Money market funds:** the 4 in the sample (437 fund-months) stay in columns 1, 2 and 4 and are dropped in column 3, as in each specification's definition.
- **Not run:** downstream MC and conduct for the two "no VA" columns with upward-sloping demand, where markups are negative and the results have no meaning.

## 0. Validation

| Check | Result |
|---|---|
| T2: paper's −5.606 (1.310) | **−5.606 (1.310)**: exact |
| A5: paper's Table A7 Panel A col 2, −7.503 and −5.278 | **−7.503 (1.770) and −5.278 (0.372)**: exact |
| V2: −3.642 (0.419), −20.562 (0.646), F 315.8, N 96,069 | **exact**, with its downstream and conduct results |
| Danny's modified T2: −5.713 (0.747) | **not reproduced: proxy −9.107 (0.912)** |
| T2 negative-MC share, B0, η = 0: Danny's 0.5156 | **0.516** |
| Scale under PC: Danny's 0.0205 (0.0051) | **0.0205 (0.0051)** |

## 1. Gene's proposal: exclude the variable-annuity funds from the sample

**Who they are.**
- The 7,771 fund-months without a family code (`firm_f_old`) are all variable-annuity funds, and there are no other variable-annuity funds in the sample.
- The flag is CRSP's `vau_fund`. Of the 112 funds, 109 carry it in every quarter and 3 in some quarters. None of the other 1,190 funds ever carries it.
- Examples: VALIC Company I Stock Index Fund, Voya US Stock Index Portfolio, Prudential Series Fund Stock Index Portfolio, Vanguard Variable Insurance Fund Equity Index Portfolio, John Hancock Variable Insurance Trust 500 Index Trust. Full list: `logs/spec_compare/sc_blank_family_funds.csv`.
- They average 1.7% of inside-market assets (3.5% in 2010, 0.8% in 2024).

**Why exclude them.**
- **They are not bought in the open market.** These funds are chosen from an insurer's menu inside a contract, so the expense ratio is not the price the investor trades off against other index funds.
- **Their fee data are not reliable, which is the harder reason.** In 85% of firm-months every variable-annuity fund of a firm has the same expense ratio in the CSV. Neither the price nor any family instrument is reliable for them (section 7).
- **Their instrument in the paper is not a family instrument.** CRSP has no management code for them, so their family code is blank, and blank codes match one another in IV0. Their donors are other insurers' funds.

**What each treatment gives for Table 2 col 2** (`sc_blank_family_check.log`).

| Treatment of the variable-annuity funds | Price coefficient (SE) | First-stage F |
|---|---|---|
| As in the paper: pooled as one "family" | −5.606 (1.310) | 34 |
| Kept, with their true families (parent firm) | −0.340 (0.049) | 314 |
| **Excluded from the sample (proposal)** | **+7.244 (1.987)** | 27 |

**Reading.**
- **The paper's coefficient exists only under the first treatment.** Each of the two alternatives removes the negative slope.
- **Excluding them is the cleaner choice,** because the true-family version rests on the fee data described in section 7.

## 2. Demand with and without the variable-annuity funds: T2 and A5 change sign

| # | Specification | Sample | N | Price (SE) | Interaction (SE) | Min F | e > 0 | Avg e | Table 5 e < −1 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | T2 | with VA | 108,300 | −5.606 (1.310) | | 33.6 | 0 | −1.61 | 2/15 |
| 1 | T2 | no VA | 100,529 | **+7.244 (1.987)** | | 26.6 | 1.00 | +1.91 | 0/15 |
| 2 | Modified T2 (proxy) | with VA | 108,300 | −9.107 (0.912) | | 86.6 | 0 | −2.62 | 2/15 |
| 2 | Modified T2 (proxy) | no VA | 100,529 | −3.491 (0.644) | | 117.0 | 0 | −0.92 | 1/15 |
| 3 | V2 | with or without VA | 96,069 | −3.642 (0.419) | cheap −20.562 (0.646) | 315.8 | 0 | −1.93 | 5/15 |
| 4 | A5 | with VA | 108,300 | −7.503 (1.770) | broad −5.278 (0.372) | 53.0 | 0 | −2.86 | 2/15 |
| 4 | A5 | no VA | 100,529 | **+4.009 (1.588)** | broad −6.924 (0.428) | 49.0 | 0.49 | +0.31 | 0/15 |

**Reading.**
- **T2 and A5 change sign.** The variable-annuity rows alone also slope upward (+2.32), so the negative coefficient comes from pooling the two groups under common month effects, not from fee variation within either. This is my reading of the three numbers, not a separate test.
- **The stricter exclusion keeps its sign but loses 60% of its size** (−9.1 to −3.5).
- **V2 is unchanged by construction.** Rows without a family code have no Z, so they were never in its estimation. Dropping them changes only the outside share, which the month effects absorb.

## 3. The lead test: what it is, and why the earlier t-statistics were too large

**Definition.**
- Take the demand residual ξ_jt from the fitted model, and the instrument Z_jt after removing the controls, fund effects and month effects.
- Regress ξ_jt on the instrument k months later, Z_j,t+k, for k = 12, 24 and 36. Both are demeaned within fund on the matched sample.
- **What it asks:** do today's demand shocks predict the instrument one to three years ahead? If the instrument is a cost shifter that does not respond to demand, they should not.
- **What a rejection means:** the family's other fees respond to this fund's past demand, or share a persistent demand shock with it. The IV estimate sets the same-month covariance of Z and ξ to zero by construction, so a problem can show up only at leads and lags.
- **What a pass means:** less. It is a necessary condition. It does not show that the instrument satisfies the exclusion restriction.

**Is the inference valid? Not as we reported it.** Our earlier files clustered the standard error by month only. ξ and Z are both highly persistent within a fund, so the observations of one fund are not independent, and month clustering overstates the t-statistic. Clustering by fund, or by fund and month, is the valid version (`code/spec_compare/sc_leadcheck.py`, `sc_leadcheck.csv`).

| Specification | t, month-clustered (12/24/36) | t, two-way clustered (12/24/36) |
|---|---|---|
| 1 T2, with VA | −3.3 / −1.5 / 2.1 | −0.4 / −0.2 / 0.3 |
| 1 T2, no VA | 6.7 / 11.6 / 18.9 | 1.0 / 2.0 / **2.7** |
| 2 Modified T2 (proxy), with VA | −3.5 / −3.1 / −2.5 | −0.5 / −0.5 / −0.3 |
| 2 Modified T2 (proxy), no VA | 1.3 / 3.3 / 6.9 | 0.2 / 0.5 / 0.8 |
| 3 V2 | −2.0 / −2.2 / −0.5 | −0.4 / −0.4 / −0.1 |
| 4 A5, with VA | −5.3 / −4.9 / −2.4 | −0.8 / −0.7 / −0.3 |
| 4 A5, no VA | 4.1 / 10.9 / 16.4 | 0.5 / 1.3 / **2.0** |

**Reading.**
- **With valid standard errors the t-statistics are five to eight times smaller.** Fund clustering and two-way clustering give the same numbers.
- **The test now rejects only where demand slopes upward:** T2 and A5 without the variable-annuity funds.
- **It no longer separates V2 from the single-slope models.** Earlier statements that V2 has "the cleanest lead tests" or that other specifications "fail the lead tests" used the month-clustered numbers and should not be relied on. This affects `RESULTS_spec_compare.md`, `RESULTS_best_model1.md`, `RESULTS_downstream.md` and the V2 replication note.
- **The ranking by coefficient is unchanged:** the lead coefficient is smallest for V2 and largest for T2 and A5 without the variable-annuity funds.

## 4. Scale η by conduct candidate: insensitive to demand, slightly higher without the variable-annuity funds

| # | Sample | PC | B0 | B25 | B50 | B65 |
|---|---|---|---|---|---|---|
| 1 T2 | with VA | 0.0205 (0.0051) | 0.0213 | 0.0212 | 0.0211 | 0.0209 |
| 2 Modified T2 (proxy) | with VA | 0.0205 | 0.0210 | 0.0210 | 0.0209 | 0.0208 |
| 2 Modified T2 (proxy) | no VA | 0.0233 (0.0049) | 0.0247 | 0.0247 | 0.0246 | 0.0245 |
| 3 V2 | with VA | 0.0211 (0.0051) | 0.0210 | 0.0215 | 0.0218 | 0.0220 |
| 3 V2 | no VA | 0.0238 (0.0050) | 0.0238 | 0.0244 | 0.0247 | 0.0250 |
| 4 A5 | with VA | 0.0205 | 0.0208 | 0.0208 | 0.0206 | 0.0205 |

**Reading.**
- **η does not depend on the demand model or the conduct candidate.** Within a sample the spread is 0.001.
- **The sample moves it more:** 0.021 with the variable-annuity funds and 0.024 without. The difference is about half a standard error.

## 5. Negative marginal costs: the modified T2's good result depends on the variable-annuity funds; V2's does not

Monthly-mean share of fund-months with MC < 0, B0 → B65. PC is 0 in every row.

| # | Sample | η = 0 | η = 0.024 | Own η | Share below −0.10% (own η) | Share below −0.20% (own η) | Min MC | Mean markup (%) |
|---|---|---|---|---|---|---|---|---|
| 1 T2 | with VA | 0.52–0.58 | 0.17–0.34 | 0.21–0.36 | 0.028–0.266 | 0–0.089 | −0.31 | 0.22–0.31 |
| 2 Modified T2 (proxy) | with VA | 0.40–0.49 | 0–0.09 | 0.006–0.163 | 0–0.001 | 0 | −0.12 | 0.14–0.19 |
| 2 Modified T2 (proxy) | no VA | 0.65–0.77 | 0.43–0.60 | **0.42–0.59** | 0.25–0.43 | 0.15–0.38 | −0.58 | 0.36–0.50 |
| 3 V2 | with VA | 0.33–0.46 | 0.04–0.07 | 0.053–0.082 | 0.001–0.030 | 0–0.0002 | −0.21 | 0.19–0.23 |
| 3 V2 | no VA | 0.35–0.48 | 0.04–0.08 | **0.041–0.073** | 0.0001–0.016 | 0 | −0.19 | 0.19–0.23 |
| 4 A5 | with VA | 0.39–0.47 | 0–0.04 | 0.005–0.088 | 0–0.0004 | 0 | −0.12 | 0.13–0.17 |

**Where the negatives are** (own η; share negative within the group).

| Specification, sample, conduct | Vanguard | SSGA | BlackRock | Other firms | SPY | Cheap / non-cheap |
|---|---|---|---|---|---|---|
| 1 T2, with VA, B0 | **0.81** | 0.03 | 0.04 | 0.01 | 0 | 0.40 / 0.06 |
| 2 Modified T2, with VA, B0 | 0.02 | 0 | 0 | 0 | 0 | 0.01 / 0 |
| 2 Modified T2, with VA, B65 | **0.54** | 0.14 | 0.11 | 0 | 0 | 0.32 / 0.04 |
| 2 Modified T2, no VA, B0 | **0.99** | 0.19 | 0.22 | 0.25 | 0 | 0.75 / 0.14 |
| 2 Modified T2, no VA, B65 | **1.00** | 0.85 | 0.71 | 0.25 | **0.85** | 0.89 / 0.34 |
| 3 V2, with VA, B0 | 0.13 | 0.04 | 0.05 | 0.02 | 0 | 0 / 0.10 |
| 3 V2, no VA, B0 | 0.10 | 0.02 | 0.04 | 0.01 | 0 | 0 / 0.08 |
| 3 V2, no VA, B65 | 0.16 | 0.19 | 0.06 | 0.01 | 0 | 0 / 0.14 |
| 4 A5, with VA, B65 | 0.26 | 0.09 | 0.09 | 0 | 0 | 0.16 / 0.03 |

**Reading.**
- **Goal B separates columns 2 and 3 once the variable-annuity funds are out.** The proxy for the modified T2 has 42% to 59% of marginal costs negative and fails the magnitude screen. V2 has 4% to 7% and passes it.
- **The reason is the slope on the low-fee funds.** A single slope of −3.5 gives a fund charging 0.03% an elasticity of −0.1 and a markup several times its fee. V2 gives the cheap funds −24.2.
- **V2's negatives stay on non-cheap funds,** with Vanguard at 10% to 16%. Securities lending cannot explain those, so the location caveat remains.
- **T2 and A5 without the variable-annuity funds are not shown.** Their markups are negative for 100% and 49% of fund-months.

## 6. Conduct test: B0 and B25 are rejected throughout; the weight on B65 rises without the variable-annuity funds

Selected sets (MCS p ≥ 0.05), η scheme A (0.024); MCS p-values in brackets.

| # | Sample | **Main IV** (rival2 × csent_index) | rival2 × csent_income3 | rival3 × csent_index | rival2 × bab_usa / × fmax / × rotator | Min F, main IV |
|---|---|---|---|---|---|---|
| 1 T2 | with VA | PC (B50 0.02, B65 0.03 rejected) | PC | PC | PC | 67 |
| 2 Modified T2 (proxy) | with VA | PC, B65 (0.06) | PC | PC | PC | 92 |
| 2 Modified T2 (proxy) | no VA | PC, B50 (0.13), B65 (0.13) | PC, B50, B65 | PC | PC | 57 |
| 3 V2 | with VA | PC, B50 (0.19), B65 (0.79) | PC, B50, B65 | PC | PC | 140 |
| 3 V2 | no VA | PC (0.52), B50 (0.05), B65 (1.00) | PC, B50, B65 | PC | PC | 157 |
| 4 A5 | with VA | PC, B65 (0.08) | PC, B65 | PC | PC | 103 |

Schemes B (own η), C (PC η) and A with markups capped 1/99 by year give the same sets, with one exception: for V2 without the variable-annuity funds, B50 sits at the 5% line (p 0.05 to 0.07) and drops out under scheme C.

**Reading.**
- **B0 and B25 are rejected in every row.** PC is never rejected.
- **Without the variable-annuity funds, B65 becomes the best-fitting model under V2** (MCS p of 1.00, with PC at 0.52). With them, PC fits best. The two are not separable in either sample.
- **This is reported, not used to choose.** The demand criteria come first.

## 7. The fee data for the variable-annuity funds, and a question for Danny

**Why a result with their true families is not trustworthy either.** Rebuilding the instrument for these funds with their true families gives a Table 2 coefficient of about −0.3 (section 1). On those rows the rebuilt instrument tracks each fund's own fee almost one for one (first-stage F in the thousands). The cause is the fee data (`sc_blank_family_check.log`):

- In 85% of firm-months, every variable-annuity fund of a firm has the same expense ratio in the index CSV.
- Allianz's funds are all at 0.400% in 2010–2016, then all at 0.535% in 2018 and 0.458% in 2020.
- Mutual of America's funds, including its S&P 500 index fund, are all at 0.13% in 2010, 1.05% in 2012, 1.42% in 2014 and 1.93% in 2022.

That looks like one firm-level or trust-level number copied to every fund. A family instrument for these funds is then nearly the fund's own fee, so it cannot identify the slope. We have not checked whether this comes from CRSP itself or from a step in Danny's build.

**Question for Danny.** Where do the variable-annuity funds' expense ratios come from: an imputation in your build, or CRSP as reported?
