# Why does price × broad-based slope upward under V2's instrument but not under the paper's?

**Short answer: it is the rows, not the instrument design.** The paper's instrument gives a downward slope for specialized funds only when the 7,771 fund-months without a family code are in the sample. On the rows with a family code it slopes upward too (+4.1, 49% of fund-months). Every instrument between the paper's and V2's slopes upward for specialized funds, and V2's is among the least so.

**Code and outputs.** `code/spec_compare/sc_broad_ladder.py`; `logs/spec_compare/sc_broad_ladder.log`, `sc_broad_ladder.csv`, `sc_blank_family_check.log`. Money market funds are dropped throughout. Broad is the paper's label, fixed per fund.

## 1. The ladder: one construction choice at a time

Model: δ = α p + α_b (p × broad) + controls + fund FE + month FE; instruments IV and IV × broad. The 8 rebuilt instruments use our index CSV as the donor file. Common rows are the 96,069 where all 8 are defined (V2's rows).

| Exclusion | Share type | Aggregation | Specialized α (SE) | × broad (SE) | Min F | e > 0 | Lead t (12/24/36) | One common slope (SE) |
|---|---|---|---|---|---|---|---|---|
| **Original IV0, all 107,863 rows** | | | **−5.86 (1.37)** | −5.94 (0.30) | 73 | 0 | −4.9 / −4.5 / −1.5 | −4.26 (0.99) |
| **Original IV0, rows with a family code (100,092)** | | | **+4.07 (1.31)** | −6.91 (0.34) | 73 | 0.49 | 3.4 / 8.8 / 13.2 | +6.41 (1.43) |
| Original IV0, common rows | | | +3.43 (1.58) | −6.65 (0.33) | 49 | 0.49 | 5.2 / 12.4 / 18.2 | +7.83 (2.33) |
| index | pooled | weighted mean (paper's design, rebuilt) | +7.25 (1.35) | −6.55 (0.36) | 76 | 1.00 | 5.7 / 11.6 / 17.0 | +9.84 (2.00) |
| index | pooled | median | +7.78 (1.15) | −6.99 (0.35) | 177 | 1.00 | 5.5 / 8.6 / 10.4 | +5.61 (1.07) |
| index | same type | weighted mean | +5.26 (0.52) | −6.02 (0.28) | 264 | 0.49 | 5.9 / 10.3 / 10.1 | +6.14 (0.62) |
| index | same type | median | +5.29 (0.47) | −6.77 (0.31) | 361 | 0.49 | 5.2 / 7.8 / 8.3 | +4.11 (0.42) |
| asset class | pooled | weighted mean | −1.17 (0.78) | −4.23 (0.37) | 182 | 0 | 2.5 / 5.5 / 6.7 | −1.30 (0.75) |
| asset class | pooled | median | +1.07 (0.87) | −4.79 (0.38) | 206 | 0.49 | 1.3 / 1.0 / 3.6 | −0.79 (0.71) |
| asset class | same type | weighted mean | −0.23 (0.47) | −4.82 (0.31) | 425 | 0 | −0.1 / 2.3 / 2.7 | −0.49 (0.47) |
| **asset class** | **same type** | **median (V2's Z)** | **+1.20 (0.30)** | −5.71 (0.30) | 399 | 0.49 | 0.9 / 1.1 / 2.9 | −0.32 (0.29) |

Rows 4 to 11 are on the common rows. On each instrument's own rows the pattern is the same (`sc_broad_ladder.csv`).

**Reading.**
- **The exclusion level is the choice that matters.** With the index exclusion the specialized slope is +5 to +8 and the lead t-statistics are 8 to 17. With the asset-class exclusion it is −1.2 to +1.2 and the leads fall to 1 to 7.
- **Share type and aggregation matter little for the sign.** Same-type matching raises F (76 → 264) and the median lowers the lead tests.
- **The × broad coefficient is stable** at −4.2 to −7.0 in every row. Broad-based funds are always more fee-sensitive than specialized funds; what moves is the level of the specialized slope.
- **Moving from the paper's design toward V2's makes the specialized slope less positive, not more.** V2's instrument is the cleanest on the lead tests. Its +1.20 is small, but it is significantly positive.

## 2. The paper's instrument: negative only when the family-less rows are pooled in

| Rows | N | One common slope (SE) | F | Lead t (12/24/36) |
|---|---|---|---|---|
| All (Table 2 minus money market funds) | 107,863 | **−4.26 (0.99)** | 54 | −2.6 / −0.5 / 3.6 |
| With a family code | 100,092 | **+6.41 (1.43)** | 46 | 5.8 / 9.4 / 15.1 |
| Without a family code | 7,771 | **+2.32 (0.54)** | 57 | 0.1 / −0.3 / −0.2 |

- **Who the 7,771 rows are:** 112 mutual-fund classes, no ETFs. Mostly insurance and retirement-channel trusts (Voya, Allianz, John Hancock, Nationwide, American General, Principal) plus some Vanguard classes. Mean fee 0.61%, 15% cheap, 77% broad-based.
- **Their IV0 is not a family instrument.** Danny's note says blank family strings match one another, so their donors are other firms' family-less funds. A typical month has 12 distinct IV0 values across 46 such rows.
- **Their fees move four times as much within fund** (SD 0.133 against 0.034), so they carry 19% of the first-stage covariance with 7% of the rows.

**Reading.**
- **Each part slopes upward, and the pooled sample slopes downward.** The negative coefficient comes from comparing the family-less funds with the rest through the common month effects, not from within either group. This is my reading of the three rows; I have not decomposed it further.
- **This applies to Table 2 itself, not only to the broad interaction.** The same holds with the cheap interaction: the paper's IV gives −3.0 on all rows and +2.0 on the rows with a family code (`RESULTS_best_model1.md` §4).
- **So the instrument is not what makes the paper's broad specification valid.** The sample is.

## 3. Which group slopes upward: specialized funds, under every instrument

Slope estimated separately on each subsample (own fund and month effects), common rows.

| Instrument | Specialized only (SE; F) | Broad only (SE; F) |
|---|---|---|
| Original IV0, all rows | +19.95 (5.26; 16) | −24.67 (2.71; 84) |
| index / pooled / weighted | +25.18 (7.42; 16) | −7.92 (1.41; 145) |
| index / same type / median | +11.94 (1.33; 108) | −5.35 (0.83; 219) |
| asset class / pooled / weighted | +1.13 (1.53; 80) | −6.58 (0.80; 195) |
| asset class / same type / weighted | +2.17 (0.79; 275) | −6.76 (0.61; 297) |
| asset class / same type / median (Z) | +4.49 (0.67; 204) | −7.37 (0.77; 231) |

**Reading.**
- **Specialized funds have a positive fee slope under all of them,** including the paper's instrument on all rows (+20). Broad-based funds are negative under all of them.
- **Broad is the wrong split for this.** Specialized funds mix cheap and expensive products (sector, country, thematic), and their fee changes line up with demand in the wrong direction. The cheap split puts the upward-sloping part at zero: V2 has no e > 0.
- **Open question:** why specialized funds' fees and their family's other-asset-class fees co-move positively with demand. A family-wide demand shock would do it, which is the threat Danny's note and Brown et al. describe.
