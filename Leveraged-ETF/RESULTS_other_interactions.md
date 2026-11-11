# Can ETF, institutional-class or broad-based interactions do what the cheap interaction does in V2?

**Short answer: no.** As replacements for cheap they fail; as additions to cheap they change little. Only the cheap interaction separates the low-fee funds, and that separation is what both goals need.

**The two goals** (Gene's, from the spec-comparison brief):
- **Goal A:** no upward-sloping demand (share of fund-months with e > 0 equal to 0). The tables below also show the other demand criteria: first-stage F and the Table 5 funds.
- **Goal B:** fewer negative implied marginal costs.

**Code and outputs.** `code/explore/step43_other_interactions.py`; `logs/step43.log`, `logs/step43_{demand,table5,where}.csv`. The script calls V2's own functions (`replicate_V2.py`) and changes only the set of price interactions. Its `cheap` row reproduces V2 exactly (α −3.642, α_x −20.562, F 315.8, 5/15, negative MC 0.053–0.082). The conduct test was not run.

## 1. Setup

    δ_jt = α p_jt + Σ_k α_k (p_jt × z_kj) + controls + fund FE + month FE,   instruments: IV and IV × z_k

Everything else is V2: money market funds dropped, 107,863 supply rows, SE clustered by month.

| Indicator (fixed per fund) | Definition | Share of fund-months | Mean fee, in / out of group (%) |
|---|---|---|---|
| cheap | `gene_idx` (V2) | 0.45 | 0.11 / 0.43 |
| ETF | `ETF_ind` | 0.52 | 0.30 / 0.27 |
| institutional | mutual fund with CRSP `inst_fund` = Y in most of its months | 0.24 | 0.20 / 0.31 |
| broad | the paper's `broad_specialized` = "broad-based" (Table A7) | 0.53 | 0.25 / 0.33 |
| broad, consistent | the same label, made equal for all funds tracking one index (most common label). Changes 154 funds, 13,832 fund-months, including SPY, SPDR Portfolio S&P 500 and VTI's ETF class | 0.62 | 0.26 / 0.33 |

Two instruments: **Z** (V2's, 96,069 rows) and the **paper's** `BLP_IV_hausman_exp_ratio` (all 107,863 rows).

## 2. Replacing cheap: none of the three works

Negative-MC share is the range B0–B65 at each candidate's own η. "Up" is the share of fund-months with e > 0.

**Instrument Z (V2's)**

| Interactions | Base α (SE) | Interaction terms (SE) | Min F | Up | Table 5 \|e\| > 1 | Negative MC | Verdict |
|---|---|---|---|---|---|---|---|
| **cheap (V2)** | −3.64 (0.42) | −20.56 (0.65) | 316 | 0 | 5/15 | 0.05–0.08 | reference |
| none | −0.32 (0.29) | | 383 | 0 | 0/15 | 1.00 | flat |
| ETF | −0.42 (0.28) | +0.18 (0.26) | 398 | 0 | 0/15 | 1.00 | flat; no ETF effect |
| institutional | −0.38 (0.33) | −0.50 (0.90) | 269 | 0 | 0/15 | 1.00 | flat; no effect |
| broad | **+1.20** (0.30) | −5.71 (0.30) | 399 | **0.49** | 0/15 | 0.00–0.01 (47% negative markups) | invalid |
| broad, consistent | **+8.22** (0.69) | −10.64 (0.48) | 268 | **0.40** | 1/15 | 0.39–0.49 | invalid |
| ETF + institutional | −0.41 (0.27) | +0.06 (0.33); −0.46 (1.02) | 253 | 0 | 0/15 | 1.00 | flat |
| ETF + institutional + broad | **+2.73** (0.27) | −2.65; −0.97; −6.33 | 256 | **0.49** | 0/15 | 0 (72% negative markups) | invalid |

**The paper's instrument (all rows)**

| Interactions | Base α (SE) | Interaction terms (SE) | Min F | Up | Table 5 \|e\| > 1 | Negative MC | Verdict |
|---|---|---|---|---|---|---|---|
| cheap | −3.03 (1.85) | −25.88 (1.47) | 40 | 0 | 7/15 | 0.09–0.11 | valid, imprecise |
| none | −4.26 (0.99) | | 54 | 0 | 1/15 | 0.33–0.47 | goal A and B fail |
| ETF | −1.56 (0.83) | −2.25 (0.23) | 52 | 0 | 1/15 | 0.47–0.69 | worse than none |
| broad (= Table A7) | −5.86 (1.37) | −5.94 (0.30) | 73 | 0 | 2/15 | 0.03–0.16 | B partly; A fails |
| broad, consistent | **+0.76** (1.34) | −8.77 (0.63) | 77 | **0.38** | 1/15 | 0 (38% negative markups) | invalid |
| institutional | −14.97 (7.23) | −18.22 (8.61) | **5.3** | 0 | 6/15 | 0 | weak IV |
| ETF + institutional | −8.89 (5.78) | −8.76; −25.77 (11.39) | **5.7** | 0 | 6/15 | 0 | weak IV |
| ETF + institutional + broad | −7.57 (7.32) | −13.45; −30.06; −6.62 | **8.0** | 0 | 7/15 | 0 | weak IV |

**Reading.**
- **With V2's instrument, ETF and institutional have no price effect at all.** Both coefficients are within one standard error of zero. The slope stays near −0.4, no Table 5 fund reaches 1, and every marginal cost is negative.
- **Broad-based gives upward-sloping demand** for the specialized half of the market under V2's instrument, and under the paper's instrument too once the label is made consistent within an index.
- **The paper's instrument with institutional looks like it meets both goals (6–7 of 15, zero negative MC), but it is not usable.** The first-stage F is 5 to 8, and the base slope has a standard error of 6 to 7. This is the same trap as the earlier steep slopes: a weak instrument inflating the coefficient.
- **The best non-cheap row is the paper's Table A7** (paper IV × broad): valid slope, negative MC of 3% at B0 rising to 16% at B65. It gets part of goal B, leaves 13 of the 15 Table 5 funds inelastic, and depends on the inconsistent label.

**Why.** A fund at a fee of 0.03% needs α ≈ −33 for |e| = 1. An interaction helps only if its group isolates the low-fee funds. Cheap does (mean fee 0.11% against 0.43%). ETF does not separate fees at all (0.30% against 0.27%), and institutional and broad barely do, so each group's slope is an average over cheap and expensive funds.

## 3. Adding them to cheap (V2's instrument): small changes

| Interactions | Base α (SE) | × cheap | Added term (SE) | Min F | Table 5 \|e\| > 1 | Negative MC B0–B65 | Min MC | Vanguard fund-months negative (B0) |
|---|---|---|---|---|---|---|---|---|
| **cheap (V2)** | −3.64 (0.42) | −20.56 | | 316 | 5/15 | 0.053–0.082 | −0.21 | 0.13 |
| + ETF | −2.52 (0.33) | −20.13 | −1.89 (0.34) | 393 | 5/15 | 0.057–0.075 | −0.30 | 0.09 |
| + institutional | −4.36 (0.55) | −21.36 | **−4.83 (1.24)** | 234 | 6/15 | **0.018–0.047** | −0.15 | **0.05** |
| + broad | −2.95 (0.42) | −20.48 | −2.55 (0.31) | 344 | 7/15 | 0.050–0.065 | −0.27 | 0.09 |
| + broad, consistent | −5.69 (1.19) | −21.76 | **+2.31** (0.89) | 91 | 5/15 | 0.035–0.053 | −0.21 | 0.06 |
| + ETF + institutional | −2.46 (0.35) | −20.89 | −3.81; −7.27 | 210 | 5/15 | 0.040–0.045 | −0.28 | 0.08 |
| + ETF + institutional + broad | −0.74 (0.36) | −20.50 | −5.20; −7.41; −3.39 | 211 | 5/15 | 0.040–0.054 | −1.24 | 0.03 |

- **The cheap coefficient does not move** (−20.1 to −21.8), so goal A is unchanged. The counts of 6/15 and 7/15 are the two Vanguard Admiral classes moving from −0.94 to −1.00 and −1.01.
- **Institutional is the one addition that helps goal B.** Negative MC falls from 5–8% to 2–5%, the minimum from −0.21 to −0.15, and Vanguard's negative share from 13% to 5%.
- **Broad's effect depends on the label.** With the paper's label it is −2.55; with a consistent label it turns to +2.31.
- **Under the paper's instrument** the additions either do nothing (ETF, consistent broad) or break the first stage (institutional: F 7.5, 8% upward-sloping). Cheap + broad with the paper's label is the cleanest row there (negative MC 0.025–0.043, F 52), with the same label caveat.

## 4. Recommendation

Keep V2 as it is. If one robustness column is wanted, use **cheap + institutional**: it is the only addition with a significant, correctly signed coefficient under both the old run and this one, and it moves goal B in the right direction.
