# Everything else that was explored, and why it was set aside

Companion to `MAIN_SPEC_entry_cheap_tier.md`, which holds the recommended specification. This file records the other routes to larger own-price elasticities for the big index funds: other interactions, time-varying fee classifiers, log price, the one-random-coefficient BLP with the interaction, and the paper's Table A7 column (3). An appendix lists the facts about Table 5 and the data found along the way. Statements marked *inference* are my reading; everything else was run (scripts in `code/explore/`, logs in `logs/`, result tables in `logs/explore/*.csv`). The paper's numbers were never changed.

Throughout, unless stated: logit IV on the Table 2 Panel A sample (N = 108,300, Jan 2010 – Aug 2024), notebook controls, fund and month FE, SE clustered by month; each p × z term is instrumented by Hausman IV × z; F is the Sanderson–Windmeijer first-stage F, minimum over the endogenous terms. "Table 5 > 1" counts the 15 Table 5 funds with |e| > 1 in their last month (Table 2 logit IV: 2 of 15).

**Why this is hard in a linear-in-fee model.** With shares this small the own elasticity is α·p. |e| = 1 at p = 0.03% needs α ≈ −33, and −25 to −52 across the 2–4 basis point funds; −5.6 for Russell 1000 Growth (0.18%), −2.5 for SPDR Gold (0.40%). The pooled estimate is −5.6 (logit IV) to −8.3 (3 RC). Any fix therefore either gives low-fee funds a much steeper slope (an interaction) or changes the functional form (log price).

---

## 1. Interactions with fixed fund characteristics (`logs/explore_step2_screen.log`, `explore_step2_A7_combos.log`, `explore_step2_shareclass_pastfee.log`)

| Spec | Price terms, coef (SE) | min F | Avg e | Table 5 > 1 | Share e > 0 | Neg. MC (firm Bertrand) | Verdict |
|---|---|---|---|---|---|---|---|
| Table 2 logit IV | −5.606 (1.310) | 33.6 | −1.61 | 2 | 0 | 0.52 | baseline |
| Broad-based (the paper's A7 col 2) | −7.503 (1.770); × broad −5.278 (0.372) | 53.0 | −2.86 | 2 | 0 | 0.40 | reproduces A7 exactly; too small |
| ETF vs mutual fund | −2.988 (1.205); × ETF −1.889 (0.220) | 28.6 | −1.15 | 1 | 0 | 0.60 | too small |
| Big 3 | −4.141 (1.261); × Big3 −4.397 (0.382) | 36.6 | −1.67 | 2 | 0 | 0.48 | too small |
| Firm dummies (Vanguard, BlackRock, SSGA) | −7.406; × Vanguard −6.453, × BlackRock −5.528, × SSGA −1.935 | 74.1 | −2.68 | 2 | 0 | 0.37 | too small |
| Share class (institutional/Admiral, retail, other MF, ETF; parsed from names) | institutional −11.2, ETF −9.2, retail −7.4 | | | 2 | 0 | | 12 of the 15 are ETFs; too small |
| Asset class (5 groups from `market_m_cluster`) | base **+2.271**; US large blend −10.7, other US equity −14.0, intl −4.6, bond −5.2 | 87.4 | −0.90 | 1 | **0.39** | 0.35 | "other" group (incl. SPDR Gold, e = +0.90) slopes upward |
| AUM tercile at first sample month | base **+8.133**; low −17.9, mid −8.0 | 55.9 | −0.42 | 2 | **0.67** | 0.02 | largest funds slope upward |
| Fee tercile at first **sample** month | −3.714 (6.133); low −52.7, mid −12.0 | 22.6 | −3.75 | 13 | 0 | 0.06 | works in logit IV, but see section 2 (definition) and section 4 (BLP: base turns +9.5) |
| Broad + fee tercile | −0.07; × broad **+5.46**; fee terciles −51.1 / −14.1 | 48.7 | −2.11 | 12 | 0.10 | 0.42 | broad effect flips sign once fee tier is in |
| Firms + fee tercile; broad + firms + fee tercile | base **+17.3**; × Vanguard +11.2 | 134–252 | +2.6 | 3 | **0.60–0.64** | | break the base slope |
| Broad-based, with the raw-entry 20th-pct tier included | × broad −0.02 (1.2) | | | | | | adds nothing: A7's broad effect looks like a fee-level proxy *(inference)* |
| Price squared | −26.39 (2.61); p² +21.13 (0.84) | 43.9 | −1.14 | 7 | 0.09 | 0.20 | slope positive above p = 0.62% |
| Market state (sentiment, VIX residuals) × price | interaction ≈ 0 (t < 0.5) | 34–36 | −1.6 | 2 | 0 | 0.52 | no effect |

What this shows: fixed characteristics other than the fee level either leave 13 of the 15 funds below 1 or buy the elasticities with upward-sloping demand for part of the market. The fee level itself is the characteristic that matters, and the first-sample-month tercile already shows it (13 of 15). The entry-based tier in the main file is the clean version of that spec.

### 1b. The cheap tier plus a second interaction (`code/explore/step19_cheap_plus_interactions.py`, `logs/explore_step19_cheap_plus_interactions.log`, `logs/explore/step19_*.csv`)

Logit IV with price × cheap (entry tier) plus one more price interaction. Each p × z is instrumented by Hausman IV × z, and every z is fixed per fund, so fund FE absorb the main effects. Share class is parsed from mutual-fund names. "Institutional" means Admiral, Institutional, Institutional Plus, class I/K/Y/Z/R6, Premier or Select; "retail" means Investor, class A/C/R/T, service or advisor; ETFs are the base group in the full share-class spec. Among sample funds, 50% are ETFs, 23% institutional classes, 9% retail classes, 19% other mutual-fund classes. Coefficient (SE, t); "total cheap" is price + price × cheap for the base group.

**20th percentile**

| Second interaction | Price (base) | × cheap | × second term | min F | Avg e | Share e > 0 | Neg. MC | Table 5 > 1 |
|---|---|---|---|---|---|---|---|---|
| none (main spec) | −8.13 (4.32) | −32.64 (4.20, t −7.8) | | 18.3 | −3.93 | 0 | 0.13 | 11 |
| ETF | −16.64 (9.86) | −37.66 (8.04) | **+5.86 (2.98, t 2.0)** | 10.3 | −5.73 | 0 | 0.07 | 12 |
| **Institutional class** | −11.83 (5.94) | −34.67 (5.40) | **−3.12 (0.77, t −4.1)** | 16.5 | −5.23 | 0 | 0.08 | 11 |
| ETF + institutional (base: non-institutional MF) | −20.97 (12.71) | −40.06 (10.02) | ETF +6.15 (3.53, t 1.7); inst **−3.29 (1.10, t −3.0)** | 10.1 | −7.19 | 0 | 0.03 | 15 |
| Full share class (base: ETF) | −16.77 (11.25) | −42.30 (12.19) | inst −9.07 (4.50, t −2.0); retail −3.42 (2.25); other MF −6.98 (4.33) | 9.3 | −7.82 | 0 | 0.02 | 15 |
| Broad-based | −8.14 (3.89) | −32.65 (3.70) | −0.01 (1.20, t 0.0) | 35.2 | −3.93 | 0 | 0.13 | 11 |
| Big 3 | −11.16 (5.98) | −36.22 (5.95) | **+8.27 (2.75, t 3.0)** | 14.5 | −4.08 | 0 | 0.24 | 11 |
| Firms (Vanguard, BlackRock, SSGA) | −1.83 (1.80) | −29.67 (2.29) | +10.54 / +6.54 / +4.38 (all t > 4) | 59.4 | −1.21 | **0.23** | 0.32 | 5 |
| ETF + inst + broad + Big 3 | −19.16 (12.03) | −39.20 (8.42) | ETF +4.64 (n.s.); inst **−3.04 (t −3.0)**; broad +6.17 (n.s.); Big 3 **+8.57 (t 2.9)** | 14.9 | −5.10 | 0.05 | 0.03 | 11 |
| *Without cheap: ETF alone* | −2.99 (1.20) | | −1.89 (0.22, t −8.6) | 28.6 | −1.15 | 0 | 0.60 | 1 |
| *Without cheap: institutional alone* | −10.34 (2.48) | | −4.17 (0.41, t −10.3) | 25.7 | −3.16 | 0 | 0.36 | 2 |

**The second term at the other cutoffs** (coefficient, t; the cheap coefficient barely moves in every row):

| Second interaction | 10th pct | 15th pct | 20th pct |
|---|---|---|---|
| Institutional class | −0.84 (t −1.1) | **−3.59 (t −3.0)** | **−3.12 (t −4.1)** |
| ETF | +2.63 (t 0.7) | +1.61 (t 0.6) | +5.86 (t 2.0) |
| Broad-based | +2.65 (t 1.2) | +3.82 (t 1.7) | −0.01 (t 0.0) |
| Big 3 | +4.65 (t 1.1) | +4.05 (t 1.2) | **+8.27 (t 3.0)** |
| Firms | Vanguard +5.9, SSGA +3.1 (t 2.7–2.8); base +2.8: **76% upward-sloping** | Vanguard +7.8 (t 4.8); **63% upward-sloping** | all positive; **23% upward-sloping** |

**Reading.**
- **The institutional share class is the one extra interaction that is significant, with a stable sign, alongside cheap.** Its coefficient is −3.1 to −3.6 (t −3.0 to −4.1) at the 15th and 20th percentiles and keeps its sign in the kitchen-sink spec. Institutional mutual-fund classes are somewhat more fee-sensitive than ETFs and retail classes, even after cheap is controlled. The term is small next to cheap (−33 to −45), and it is not significant at the 10th percentile (−0.8, t −1.1). The cheap coefficient is unchanged when it is added (−34.7 against −32.6 at the 20th).
- For the 15 Table 5 funds it matters only for the three Vanguard mutual-fund classes, since the other twelve are ETFs. At the 20th percentile the Vanguard 500 Admiral goes from −1.58 to −1.92, the TSM Admiral from −1.59 to −1.94, and the TSM Institutional Plus from −0.78 to −0.95. The count above 1 stays at 11.
- **ETF is not robust.** Alone it is significant (−1.89), but once cheap is in, its sign flips to positive and it is significant only at the 20th (t 2.0). The first stage also drops to F ≈ 10. The ETF effect alone was a proxy for low fees: ETFs are disproportionately cheap.
- **Broad-based adds nothing** at any cutoff once cheap is in. This confirms that the paper's A7 broad effect is a fee-level proxy.
- **Big 3 is positive** (Big 3 funds are less fee-sensitive, conditional on cheap) but significant only at the 20th. **Firm dummies break the model**: all three are positive, the base slope goes to zero or positive, and 23–76% of fund-months get upward-sloping demand.
- Adding ETF together with institutional lifts all 15 Table 5 funds above 1 at the 20th percentile. That rests on an ETF coefficient that is not significant (t 1.7) and on a weaker first stage (F 10.1), so I would not use it.

## 2. Time-varying fee and size classifiers (none passes the exogeneity checks)

Each of these makes "cheap" (or "large") depend on information inside the estimation window. Since the classifier varies within fund, its main effect is included as a control and three diagnostics are run: within-fund corr(z, ξ̂), **lead tests** (regress ξ̂ from 1, 3 and 12 months *earlier* on today's z, within fund; a significant coefficient means past demand shocks predict the classifier), and the within-fund AR(1) of ξ̂ (0.975–0.978 throughout, so a 12-month lag does not break the link between past shocks and today's ξ).

| Classifier | Price terms | min F | Table 5 > 1 | Lead-test t (1 / 3 / 12 months) | Verdict |
|---|---|---|---|---|---|
| AUM tercile 12 months earlier (within-month, sample funds) | base **+3.49**; low +0.33, mid +0.24 | 29.1 | 1 | **−58 / −61 / −81** | fails; 100% upward-sloping |
| Fee tercile 12 months earlier (within-month, sample funds) | rest −1.87 (1.68); low −18.1, mid −10.0 total | 28.2 | 3 | −8.3 / −8.4 / −14.2 | fails; −18 is too flat for 0.03% funds |
| Rolling cheap status (monthly raw percentile; 6- or 12-month entry and exit rules) | | | 3 | **−15 to −17** | fails; status responds to past demand shocks |
| **Percentile of the fee 12 months earlier** (raw-file cross-section; `explore_step16*`): | | | | | |
| (a) continuous, price × pct12 | −15.73 (1.44); × pct12 **+29.24** (1.25) | 190 | 2 | 1.1 / 2.8 / 8.3 | slope turns positive above the 54th pct; 46% upward-sloping |
| (b) price × 1[pct12 ≤ 0.10] | **+17.21** (6.95); × z +18.44 (13.2) | **11.1** | 0 | 2.2 / 0.9 / −4.9 | weak IVs; positive slopes |
| (c) price × 1[pct12 ≤ 0.15] | −34.39 (26.3); × z −24.78 (11.3) | **1.6** | 15 | −2.5 / −4.3 / −9.4 | weak IVs; not an estimate |
| (d) price × 1[pct12 ≤ 0.20] | −9.28 (1.70); × z −14.19 (0.49), total −23.5 | 48.0 | 7 | **−3.8 / −5.1 / −9.8** | works mechanically but fails lead tests; cheap slope flatter than the entry tier's −40.8 |
| **Fee 60 months earlier, entry fee if the history is shorter** (section 2c), 20th pct | −27.96 (6.15); × z −20.44 (2.14), total −48.4 | 23.1 | 13 | 4.2 / 3.5 / 1.8 | best of the time-varying classifiers; exogeneity still not established (section 2c) |
| *Entry tier, 20th pct (main file)* | −8.13 (4.32); × cheap −32.64 (4.20) | 18.3 | 11 | n/a (fixed by fund) | |

Notes on the lagged-fee percentile (N = 105,049 fund-months with a fee observed 12 months earlier; baseline logit IV on that sample −4.81, average e −1.39):
- The continuous version is well identified but has the wrong shape: pct12 is almost the rank of the fund's own current fee (correlation 0.92), so price × pct12 is a smooth version of the price-squared spec, and a line in the rank cannot represent "very steep for the cheapest funds, moderately steep for everyone else" without turning positive at the expensive end. Even at the bottom of the distribution its slope (−15.7) is too small for 2–4 bp funds. SPDR Gold (pct12 = 0.56) gets e = +0.21.
- With a time-varying indicator the interaction's within-fund variation comes from the 16–17% of funds that switch status (2.5–4 times each on average) plus the fund's own fee changes; Hausman IV × indicator predicts it poorly at the 10th and 15th cutoffs.
- The ≤ 20th indicator agrees with the entry tier in 84% of fund-months; the difference in the Table 5 count (7 vs 11) is the flatter cheap slope.
- 15-fund elasticities under (a) and (d), last month: iShares Core S&P 500 −0.43 / −0.68; EAFE −0.84 / −1.63; AGG −0.44 / −0.70; Russell 1000 Growth −1.16 / −1.66; Mid-Cap −0.67 / −1.17; SPY −1.22 / −2.04; SPDR Gold +0.21 / −3.70; Technology and Financial Select Sector −0.86 / −1.87; SPDR Portfolio S&P 500 −0.30 / −0.47; Vanguard TSM Inst. Plus −0.29 / −0.45; Vanguard 500 Admiral −0.54 / −0.91; Vanguard 500 ETF −0.43 / −0.68; Vanguard TSM ETF −0.43 / −0.69; Vanguard TSM Admiral −0.55 / −0.92 (`logs/explore/step16_funds.csv`).

Two fixed-at-entry variants that were also set aside, because of the definition rather than exogeneity:
- Fee tier at the first sample month by a **fixed fee cutoff** (0.05–0.25%): 4–15 of 15 depending on the cutoff, with the first stage collapsing at 0.15–0.18%. "First sample month" is also mostly not the launch: 43% of funds enter in Jan 2010 and 43% enter when they pass the share filter.
- Average fee over the fund's first 12 sample months instead of the first month: similar to the first-month version; superseded by the raw-entry percentile.

### 2b. Robustness checks of the entry tier, 20th percentile (`logs/explore_step8_raw20_robustness.log`, `logs/explore/step8_robustness.csv`)

The cutoff grid itself is in the main file. The checks below hold the 20th-percentile definition fixed and change the sample or the model.

| Check | Rest / cheap total | F | Result |
|---|---|---|---|
| Correct SPY's fee error (recorded 0.04% Oct 2022 – Sep 2023, actual 0.0945%) | unchanged to the 3rd decimal | | holds |
| Drop State Street | −6.3 / −41.1 | 18 | holds |
| Drop BlackRock | −12.9 / −69.8 | 12 | holds |
| Add the paper's broad-based interaction | broad × price = −0.02 (SE 1.2) | | holds; A7's broad effect looks like a fee-level proxy *(inference)* |
| Percentile cutoffs computed among **sample** funds only (instead of the full raw population) | | **4.5** | first stage collapses; the definition needs the raw population |
| **Drop Vanguard** | **+6.2 (1.2)** / −22.4 | 73 | **fails for the rest:** 67% of fund-months get positive own elasticities; the cheap total survives |

The last row is the main caveat of the specification. The non-cheap slope is identified mainly from Vanguard funds' fee changes (Vanguard is about a quarter of the sample's fund-months). The robust part of the result is the **gap**: cheap funds respond far more to fees than the rest, at every cutoff and in every subsample. The fragile part is the level and sign of the non-cheap slope. Most Table 5 funds are cheap, so their elasticities rest on the robust coefficient; the 60% of fund-months outside the cheap group rest on the fragile one. Worth checking which Vanguard funds changed fees and whether those changes are plausibly exogenous (Vanguard's at-cost structure passing through scale economies); a Vanguard-specific slope would make this explicit.

### 2c. Cheap status from the fee 60 months earlier, entry fee for young funds (`code/explore/step17_lag60_tier.py`, `step17b_lag60_decompose.py`; `logs/explore_step17*.log`, `logs/explore/step17_*.csv`)

**Idea.** Use a classification date far enough back that today's demand shock no longer carries information from it. cheap_jt = 1 if fund j's fee in month t − 60 was at or below that month's q-th percentile across all raw index funds; if the fund has no raw fee 60 months before t, use its first raw month (the entry tier). 76% of sample fund-months use the lagged fee, 24% the entry fallback. The status changes inside the sample for 15–16% of funds and differs from the entry tier in 10–11% of fund-months. Because it varies within fund, its main effect is a control. Logit IV, Hausman IV and Hausman IV × z, Table 2 Panel A sample (N = 108,300).

**How fast the demand shock decays** (within-fund correlation of the Table 2 logit IV residual ξ̂ with itself k months earlier): 0.98 at 1 month, 0.73 at 12, 0.35 at 36, **0.12 at 60**, 0.06 at 72. So a 60-month lag removes most of the persistence that sank the 12-month classifiers, but not all of it.

| | 10th pct | 15th pct | **20th pct** | 20th, lag 36 | 20th, lag 48 | 20th, lag 84 | *Entry tier, 20th (main file)* |
|---|---|---|---|---|---|---|---|
| Expense ratio (non-cheap) | −24.58 (10.89) | −29.83 (10.89) | **−27.96 (6.15)** | −18.25 (4.07) | −21.34 (4.01) | −27.83 (6.20) | −8.13 (4.32) |
| × cheap | −17.73 (6.27) | −20.15 (4.68) | **−20.44 (2.14)** | −17.24 (1.53) | −17.77 (1.21) | −15.54 (1.41) | −32.64 (4.20) |
| Cheap total | −42.3 | −50.0 | **−48.4** | −35.5 | −39.1 | −43.4 | −40.8 |
| Main effect of cheap (utility) | +1.64 (0.38) | +2.28 (0.36) | **+2.82 (0.19)** | +2.36 (0.13) | +2.43 (0.11) | +2.28 (0.15) | absorbed by fund FE |
| Weakest first-stage F | **8.4** | **8.8** | 23.1 | 32.0 | 31.6 | 24.0 | 18.3 |
| Avg own-price elasticity | −7.38 | −9.17 | **−8.92** | −5.95 | −6.88 | −8.71 | −3.93 |
| Share \|e\| > 1 | 0.98 | 0.98 | 0.98 | 0.98 | 0.98 | 0.98 | 0.93 |
| Share e > 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Share negative MC (firm Bertrand) | 0.06 | 0.03 | 0.03 | 0.08 | 0.06 | 0.05 | 0.13 |
| Table 5 funds with \|e\| > 1 | 13 | 13 | **13** | 13 | 13 | 13 | 11 |
| Lead-test t, baseline ξ̂ from 1 / 3 / 12 months earlier | **21.4 / 21.8 / 21.1** | 7.2 / 6.7 / 5.7 | 4.2 / 3.5 / 1.8 | 3.9 / 1.9 / −2.7 | 3.5 / 3.4 / 2.0 | 4.7 / 4.8 / 5.0 | n/a |
| Lead-test t, ξ̂ from the classification date (60 / 72 months earlier) | −2.9 / −4.7 | −14.0 / −6.7 | **−14.9 / −11.9** | | | | n/a |

**The 15 Table 5 funds, own elasticity in the last month.** "cheap?" is the lag-60 status in Aug 2024; an asterisk marks a fund whose lag-60 status differs from its entry tier at that cutoff.

| Fund | p (%) | Entry tier, 20th (main) | Lag 60, 10th: cheap? / e | Lag 60, 15th | **Lag 60, 20th** | 20th, lag 36 / 48 / 84 |
|---|---|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | −1.18 | yes / −1.23 | yes / −1.45 | **yes / −1.41** | −1.03 / −1.14 / −1.26 |
| iShares Core MSCI EAFE ETF | 0.07 | −2.83 | yes / −2.94 | yes / −3.47 | **yes / −3.36** | −2.47 / −2.72 / −3.01 |
| iShares Core US Aggregate Bond ETF | 0.03 | −1.21 | yes* / −1.26 | yes / −1.49 | **yes / −1.44** | −1.06 / −1.16 / −1.29 |
| iShares Russell 1000 Growth ETF | 0.18 | −7.30 | no / −4.40 | no* / −5.34 | **no* / −5.00** | −3.27 / −3.82 / −4.98 |
| iShares Core S&P Mid-Cap ETF | 0.05 | −2.03 | yes* / −2.10 | yes / −2.49 | **yes / −2.41** | −1.76 / −1.94 / −2.16 |
| SPDR S&P 500 ETF Trust | 0.09 | −3.54 | no* / −2.13 | yes / −4.34 | **yes / −4.20** | −3.08 / −3.40 / −3.77 |
| SPDR Gold Shares | 0.40 | −3.24 | no / −9.79 | no / −11.88 | **no / −11.14** | −7.27 / −8.50 / −11.08 |
| Technology Select Sector SPDR | 0.08 | −0.65 | no / −1.96 | no / −2.38 | **no / −2.23** | −1.45 / −1.70 / −2.22 |
| Financial Select Sector SPDR | 0.08 | −0.65 | no / −1.96 | no / −2.38 | **no / −2.23** | −1.46 / −1.70 / −2.22 |
| SPDR Portfolio S&P 500 ETF | 0.02 | −0.81 | yes* / −0.84 | yes* / −1.00 | **yes / −0.97** | −0.71 / −0.78 / −0.86 |
| Vanguard Total Stock Market Inst. Plus | 0.02 | −0.78 | yes / −0.81 | yes / −0.96 | **yes / −0.93** | −0.68 / −0.75 / −0.83 |
| Vanguard 500 Index Admiral | 0.04 | −1.58 | yes / −1.64 | yes / −1.93 | **yes / −1.87** | −1.37 / −1.51 / −1.68 |
| Vanguard 500 Index ETF | 0.03 | −1.18 | yes / −1.23 | yes / −1.45 | **yes / −1.41** | −1.03 / −1.14 / −1.26 |
| Vanguard Total Stock Market ETF | 0.03 | −1.19 | yes / −1.24 | yes / −1.46 | **yes / −1.41** | −1.04 / −1.14 / −1.27 |
| Vanguard Total Stock Market Admiral | 0.04 | −1.59 | yes / −1.65 | yes / −1.95 | **yes / −1.89** | −1.38 / −1.53 / −1.69 |

**Where the identification comes from** (`step17b`, three variants per cutoff):

| | 10th | 15th | 20th |
|---|---|---|---|
| **Frozen**: lag-60 status taken at the fund's first sample month and held fixed (predetermined; differs from the entry tier in 4–5% of fund-months). Rest / cheap total (F) | −5.1 (3.5) / −50.3 (F 19.5) | −36.5 (29.1) / −125.3 (**F 4.6**) | −16.8 (9.2) / −62.6 (F 10.9) |
| Frozen: avg e; Table 5 > 1 | −2.36; 8 | −13.3; not usable | −6.94; 14 |
| **No switchers**: drop the funds whose lag-60 status changes in the sample. Rest / cheap total (F) | +811 / +1,299 (**F 0.03**) | −419 / −589 (**F 0.14**) | −19.2 (5.2) / −53.8 (F 25.1) |
| **Full** time-varying (table above) | −24.6 / −42.3 (F 8.4) | −29.8 / −50.0 (F 8.8) | −28.0 / −48.4 (F 23.1) |

**Reading.**
1. **At the 20th percentile the 60-month lag gives the best elasticities of any specification so far.** 13 of 15 Table 5 funds above |e| = 1 (the two below are the 0.02% funds, −0.97 and −0.93), no upward-sloping demand, 3% negative marginal cost, F = 23. The result is stable across lags of 36 to 84 months (13 of 15 throughout; cheap total −35 to −48).
2. **The 10th and 15th cutoffs do not work.** Their first stages are weak (F 8.4 and 8.8), and dropping the 16% of funds that switch status collapses them entirely (F 0.03 and 0.14). They are identified from the switchers only. The 20th survives dropping the switchers (F 25), so its result is not driven by them.
3. **The non-cheap slope is three to four times the entry tier's** (−28 against −8). Average elasticity rises to −8.9 (Table 2: −1.6; entry tier: −3.9), and SPDR Gold reaches −11. A 0.40% index fund with |e| = 11 has a Lerner index of 0.09, i.e. a markup of about 0.04 percentage points. Whether that is plausible for the expensive end of the index market is a question for the authors *(inference)*.
4. **Exogeneity is better than with any 12-month classifier, but not established.**
   - The 60-month lag shrinks the persistence channel to a within-fund ξ̂ correlation of 0.12, but the status is strongly correlated with the demand shock at its own classification date (t = −14.9 at 60 months, −11.9 at 72). That is expected: fees are endogenous, which is why the paper instruments them. With the lag, that endogeneity reaches today's ξ only through the 0.12 autocorrelation. It is smaller, not zero.
   - The short-horizon lead tests with the baseline ξ̂ still reject at the 20th (t = 4.2, 3.5 at 1 and 3 months), fail badly at the 10th (t ≈ 21) and 15th (t ≈ 6–7), and do not improve as the lag lengthens (lag 84: 4.7 / 4.8 / 5.0). These tests are imperfect for this question *(inference)*: the baseline residual omits the steeper cheap slope, which pushes it up for cheap fund-months, so they are biased toward positive t. All lag-60 lead t-statistics are positive, while the 12-month classifiers' were negative. Repeating the tests with the interacted model's own residual is not informative either, since that residual is orthogonal to the status by construction (within-fund correlation exactly 0).
   - **The main effect of the status is large**: +2.8 (SE 0.19) at the 20th. Holding today's fee fixed, a fund whose fee ranked in the cheapest fifth five years ago has mean utility 2.8 higher, i.e. a market share about 16 times larger. This could be slow adjustment or reputation, or the status could be tracking growth trends in demand. Under the entry tier, this term is absorbed by the fund FE and the question does not arise.
5. **The frozen variant**, which is predetermined like the entry tier, is fragile. It differs from the entry tier in only 4–5% of fund-months, yet at the 20th it moves the non-cheap slope from −8 to −17 and the cheap total from −41 to −63, with a weaker first stage (F 10.9); at the 15th it is not identified.

**Verdict.** The 60-month lag at the 20th percentile is the most favourable time-varying definition tried. It is a useful robustness exhibit showing that the cheap-fund gap survives when status is allowed to change: the cheap slope is −35 to −48 at every lag from 36 to 84 months. It does not replace the entry tier as the main specification, for three reasons: the classifier still carries the classification-date demand shock through a 0.12 autocorrelation, it adds a large unexplained status main effect, and it triples the non-cheap slope. The 10th and 15th cutoffs are not identified apart from the switchers.

### 2d. Why the lag-60 slopes are so much steeper than Table 2's −5.6 (`code/explore/step18_lag60_why.py`, `step18b_lag60_collinearity.py`; `logs/explore_step18*.log`, `logs/explore/step18_*.csv`)

**Adding the lag-60 terms one at a time** (20th percentile; z = lag-60 status, e = entry tier; logit IV, fund and month FE):

| | Terms | Instruments | Price | × status | Status main effect | min F | Avg e |
|---|---|---|---|---|---|---|---|
| A | p (Table 2 col 2) | H | −5.61 (1.31) | | | 33.6 | −1.61 |
| B | p + z | H | −5.83 (1.19) | | +0.05 (0.03) | 41.9 | −1.68 |
| C | p + p·z | H, H·z | −6.43 (1.57) | −1.91 (0.30) | | 28.1 | −1.93 |
| **D** | **p + p·z + z** (section 2c) | H, H·z | **−27.96 (6.15)** | **−20.44 (2.14)** | **+2.82 (0.19)** | 23.1 | −8.92 |
| E | p + p·e (main spec) | H, H·e | −8.13 (4.32) | −32.64 (4.20) | absorbed by FE | 18.3 | −3.93 |
| F | p + p·e + z | H, H·e | −7.58 (3.55) | −31.13 (2.51) | −0.09 (0.10) | 32.3 | −3.70 |

Neither lag-60 term moves the price coefficient on its own: the main effect alone gives −5.8 (and is itself about zero), and the interaction alone gives −6.4 / −8.3. Adding the lag-60 main effect to the entry-tier model changes nothing either (F). The jump happens only when the interaction and the main effect enter **together**, and then the main effect jumps from +0.05 to +2.82.

**What the pair of terms does.**
- 199 of the 1,302 funds (15%; 22.5% of fund-months) switch lag-60 status inside the sample. These are mostly funds that were repriced across the 20th percentile, or funds whose fee stood still while the market got cheaper. For the other 1,103 funds the status is constant, so the fund FE absorb z and z·p only differs from z through within-fund fee changes.
- For the switchers, z and p·z move together (within-fund correlation 0.67 after FE and controls). With both in the model, the main effect and the extra slope offset each other at the fees the switchers actually charge. The net effect of z, 2.82 − 20.44·p, is −0.21 at the switchers' average cheap-regime fee of 0.148%. In effect, the main effect absorbs the switchers' move from one regime to the other. Their remaining variation cannot identify the model: estimated on the switchers alone, model D has F = 1.6.
- So model D's slopes are identified essentially from the **non-switching funds' within-fund fee changes**. On those funds any fixed tier gives steep slopes:

  | Sample | Model | Price (non-cheap) | Price × cheap | Cheap total | min F |
  |---|---|---|---|---|---|
  | 1,103 non-switchers | Table 2 logit IV (one slope) | **+14.06 (4.30)** | | | 17.2 |
  | 1,103 non-switchers | entry tier | −22.12 (5.72) | −35.40 (1.71) | −57.5 | 26.0 |
  | 1,103 non-switchers | lag-60 status (constant for them) | −19.18 (5.17) | −34.66 (1.64) | −53.8 | 25.1 |
  | 199 switchers | Table 2 logit IV (one slope) | −24.79 (6.33) | | | 14.7 |
  | All funds | Table 2 logit IV | −5.61 (1.31) | | | 33.6 |
  | All funds | entry tier (main spec) | −8.13 (4.32) | −32.64 (4.20) | −40.8 | 18.3 |
  | All funds | lag-60, model D | −27.96 (6.15) | −20.44 (2.14) | −48.4 | 23.1 |

**Answer.** Table 2's −5.6 averages very different sources of within-fund fee variation.
- The non-switching funds, fitted with one common slope, give an *upward-sloping* +14 (a positive fee coefficient: demand rising with the fee). Once the slope can differ by tier, the same funds give −19 to −22 for non-cheap and −54 to −57 for cheap.
- **Why one slope gives +14.** The split-sample diagnostic answers this most directly (main spec, section 4; `code/explore/step20_split_sample_iv.py`). Table 2 col 2 is run separately on each group of the 1,103 non-switching funds, with group-specific fund FE, month FE and controls:

  | Group | Funds | First stage (SE) | F | Reduced form (SE) | IV (SE) |
  |---|---|---|---|---|---|
  | Non-switchers, cheap | 382 | 0.085 (0.006) | 182.9 | −4.38 (0.16) | −51.4 (4.2) |
  | Non-switchers, not cheap | 721 | −0.003 (0.005) | **0.2** | −0.09 (0.03) | +35 (75), not identified |
  | Non-switchers, pooled, one slope, common FE | 1,103 | 0.019 (0.004) | 17.2 | +0.26 (0.04) | **+14.1 (4.3)** |
  | Switchers, one slope | 199 | 0.071 (0.018) | 14.7 | −1.75 (0.07) | −24.8 (6.3) |

  Within the cheap group the instrument works very well (F 183, IV −51). For the non-cheap non-switchers it has no first stage at all (F 0.2). Pooling the two with one slope and common month effects produces a positive reduced form (+0.26) that neither group shows on its own: the cheap and non-cheap funds' fees and shares trend differently over time, and a single month effect does not absorb both. Without a first stage of its own in the non-cheap group, the pooled estimate inherits that cross-group artefact and lands at +14. An earlier version of this bullet split the pooled residuals by group and read the non-cheap funds' positive contribution as a "wrong-signed reduced form". That positive sign came from the common month FE: with the group's own month FE, the non-cheap reduced form is about zero (−0.09).
- The 199 switchers alone give −24.8.

Pooling them gives −5.6. In the entry-tier model (main spec), the switchers' fee changes are still in the regression, and the non-cheap slope settles at −8. The repricings are part of this *(inference)*: iShares Core cut fees from about 0.20% to 0.03–0.05% in 2012, and those cuts are attributed to the non-cheap slope with a share response far smaller than a −22 slope implies. In the lag-60 model, the status main effect absorbs the switchers' cross-regime shift. That leaves the non-switchers' steeper within-regime slopes, hence −28 / −48.

So the steeper lag-60 slopes are not evidence that exogeneity improved. They come from which funds' fee changes identify the slope, and they are the same fragility as the "drop Vanguard" result (section 2b): the **non-cheap slope depends on whose fee changes identify it** (−8 with the switchers, −19 to −28 without them, +6 without Vanguard). The **cheap slope is the stable part**: −35 to −58 across all of these. The event study of the 28 funds with a single 0 → 1 switch shows their shares rising steadily from three years before the switch to three years after (+0.36 in log share relative to the pre-switch mean), with no jump at the switch month. The status switch itself carries no news; the +2.8 main effect is an artefact of fitting a level and a slope to the same switch.

## 3. Log price (functional form) (`logs/explore_step2_screen.log`, `explore_step4_blp_B1.log`, `explore_step5*`, `explore_step6*`)

Utility α·log(p + c) instead of α·p. This is the one form that lifts every fund above |e| = 1, but it leaves the paper's linear specification, which the authors want to keep. Recorded for completeness.

| | Index, logit IV | Index, BLP 1 RC | Leveraged, logit IV | Leveraged, BLP 1 RC |
|---|---|---|---|---|
| α on log(p + 0.01) | −2.694 (0.078) | −8.90 (21.4) | −8.366 (0.856) | −7.726 (0.587) |
| σ | | 5.89 (18.5), not identified | | ≈ 0 (collapses to logit) |
| First-stage F | 824 | | | |
| Avg own e | −2.49 | −6.26 | −8.20 (Table 2: −4.89) | −7.57 |
| Table 5 > 1 / share e > 0 / neg. MC | 15 of 15 (−1.7 to −2.6) / 0 / 3% | | | |

- Little sensitivity to c (0.005, 0.02). The exogeneity assumption is the paper's own (Hausman IV, now in logs).
- The BLP random coefficient on log price is not identified; differentiation instruments push σ to 0 in the leveraged market and fail overidentification (J = 219); optimal instruments then degenerate.
- It roughly doubles the leveraged-market elasticity, which would lower the paper's leveraged markups *(inference)*. Any functional-form change has to be made for both markets.

## 4. The one-random-coefficient BLP with the cheap interaction (`logs/explore_table2_alt_*`, `explore_step10*`–`step15*`)

Design: Table 2 col 3 (one RC on the expense ratio; Monte Carlo 3000 draws, seed 623543; BFGS gtol 1e-7; clustered SE) with price × cheap (raw-entry tier) in the mean utility. Instruments: Hausman IV, Hausman IV × cheap, plus one or more extra instruments for σ. Every variant was run at the 20th percentile, most also at the 10th and 15th.

### 4a. σ is not identified once the interaction is in

- **σ profile** (`logs/explore_step13_sigma_profile_raw20.log`; one-step GMM with β concentrated out; instruments H, H × cheap, `BLP_IV_newproduct_3`):

  | σ | objective | non-cheap slope | cheap slope | avg e | share e > 0 | SPDR Gold e |
  |---|---|---|---|---|---|---|
  | 0 – 1 | 3.77 – 3.50 | −4.7 | −35 | −2.8 | 0 | −1.9 |
  | 2 | 2.88 | −4.6 | −37 | −2.5 | 0.2% | −1.4 |
  | 3 | 1.99 | −4.0 | −38 | −2.1 | 5% | −0.7 |
  | 4 | 1.09 | −3.0 | −39 | −1.5 | 30% | +0.3 |
  | 6.5 (BFGS root) | 0.00 | **+0.9** | −42 | +0.4 | 54% | +3.5 |

  The objective is shallow and monotone; its only root is at σ = 6.5, where more than half the market has upward-sloping demand. The cheap slope and the Table 5 count (10–11 above 1) are stable at every σ; only the non-cheap slope moves, because a large σ forces the mean coefficient up to keep expensive funds' shares positive.
- **Hansen J at fixed σ, efficient weighting** (`logs/explore_step13_hansenJ_fixed_sigma_raw20.log`): at the paper's σ = 0.027, J = 2.92 on 1 df, p = 0.088. The instruments do not reject the model with σ held at the paper's value.
- **Why.** Entered alone in logit IV, every extra instrument in the data implies a non-cheap slope near zero or positive (`newproduct_1`: +2.6 / −1.0 / +0.5 at the 10th / 15th / 20th; `logs/explore_step12*`, `step14*`), while the Hausman IV implies −6 to −16. A floating σ reconciles them by inflating heterogeneity. Hansen J for (H, H × cheap, `newproduct_1`) is 21–39, p < 0.001.

### 4b. Every estimator that lets σ float breaks the non-cheap funds (20th percentile unless noted)

| Variant | Non-cheap slope (SE) | Cheap × price | σ (SE) | Avg e | Outcome |
|---|---|---|---|---|---|
| Notebook IVs (`newproduct_1`, also × cheap); 10th / 15th / 20th | +0.27 (1.6) / −4.30 (2.4) / −1.01 (1.9) | −49.3 / −58.4 / −41.3 | 4.55 / 8.29 / n.a. | +0.33 / −0.43 / −0.47 | upward-sloping; instruments conflict |
| Squared Hausman IV (and × cheap); 10th / 15th / 20th | −1.89 (0.8) / −8.10 (1.5) / −3.61 (0.7) | −18.1 / −22.0 / −20.7 | ≈ 0, n.s. (SE 10–117) | −0.95 / −3.14 / −2.02 | collapses to logit; restrictions rejected |
| `newproduct_3` uninteracted (exactly identified; chosen by an instrument screen); 10th / 15th / 20th | +9.89 (4.7) / −1.71 (7.1) / +0.91 (5.4) | −60.6 / −60.6 / −42.7 | 8.71 / 9.36 / 6.48 | +4.59 / +0.69 / +0.35 | upward-sloping (SPDR Gold +3.5 at the 20th) |
| A7 design: `newproduct_1` uninteracted (the published A7 col 3 design) | −1.32 (1.40) | −40.85 (5.68) | 5.58 (1.23) | −0.58 | converged; SPDR Gold +2.0; 11 of 15 above 1, 1 positive |
| Chamberlain optimal IVs from the Hausman IV (`explore_step15*`) | **+4.0 (0.9)** | | 0.32 (0.64) | | positive non-cheap slope |
| Lognormal RC on −price (sign-constrained), `newproduct_3` | −2.6 (median) | | 1.6 (1.3) | −1.99 | stalled, no root; no e > 0 but 67% negative MC |
| Lognormal, two groups, free σ for the non-cheap group (`explore_step7*`) | → 0 | | → 29 | | σ diverges; fixing it at 0 works but is then logit |
| Normal RC with the first-sample-month fee tercile (`explore_step4_blp_A5.log`) | **+9.52 (2.01)** | −50.8 / −17.3 | 2.85 (1.65) | +0.35 | converged; highest-fee tercile slopes upward |

Lessons for any heterogeneous-slope BLP here: a normal RC on price with a large σ gives many simulated consumers a positive price coefficient; the sign-constrained (lognormal) version cannot go positive, so it drives the non-cheap mean toward zero instead; two-step GMM runs often stall in step 1 and the step-2 optimum can move a lot (one run moved the cheap-group median coefficient from −92 to −24 before it was stopped), so both steps must be optimized before reporting.

### 4c. σ held at the paper's 0.027: a sensitivity exhibit, not an estimated BLP (`logs/explore/step13cal_raw{10,15,20}_s0.027_*.csv`)

Holding σ at the Table 2 col 3 estimate and estimating the two price coefficients with H and H × cheap gives non-cheap −6.18 / −16.05 / −8.13, cheap −62.4 / −45.0 / −32.6, average elasticity −3.18 / −6.27 / −3.93, 10 / 14 / 11 of 15 above 1, no upward-sloping demand at the 10th / 15th / 20th percentiles. These are the logit IV numbers to the third decimal. Fixing a nonlinear parameter at a value estimated from another specification on the same data is not standard practice (calibration from an independent source, or micro moments, would be); with σ this small the column adds a label, not information. What it documents, with the σ profile and the J test, is that the data cannot pin σ once the interaction enters and do not reject the paper's own value. If shown at all, label it as σ fixed and put it in a robustness position.

### 4d. Table A7 column (3), for comparison (`RESULTS_A7_col3.md`, `code/explore/a7_col3.py`)

The published A7 col (3) (26-Sep notebook, commit `f2d8bff`) is this same design: one RC on the expense ratio, price × broad in X1, instruments Hausman, Hausman × broad and `BLP_IV_newproduct_1` **uninteracted** (the × broad version is built but never enters), exactly identified. It re-runs exactly: β −6.934 (1.295), × broad −6.186 (0.607), σ 2.2525 (0.680), average elasticity −2.346 (clustered SEs 1.214 / 0.653 / 0.768). It lifts only 2 of the 15 Table 5 funds above |e| = 1 (Russell 1000 Growth −1.18, SPDR Gold −2.23; the S&P 500 funds −0.39 to −0.61). It works for broad because `newproduct_1` alone implies negative slopes for both groups there (−7.7 specialized, −6.5 broad; J p = 0.045); under the cheap split the same instrument implies a non-cheap slope near zero, which is why the identical design fails there. An earlier conclusion that the published column came from an unsaved two-RC run was based on the 25-May notebook and is withdrawn.

Data note from that run: `broad_specialized` is inconsistent for S&P 500 funds. SPY (all 166 months), SPDR Portfolio S&P 500 and VTI's ETF class are coded "specialized" while other share classes of the same portfolios are "broad-based"; 22.6% of SPX fund-months are "specialized". A7 is identified from this label.

### 4e. Leveraged market

No interaction (not significant in the paper's A7 logit, and not pursued). Separately, the leveraged notebook's two instruments already disagree in the published Table 2 Panel B col 3: the Hausman IV alone implies −3.71 and `BLP_IV_rival_funds1` alone −5.06; Hansen J = 14.2, p < 0.001 (`logs/explore_step10b_instrument_check_baseline.log`). Panel B col 3 is also flagged "not converged" by pyblp (gradient 1.9e-7 vs gtol 1e-7), though its estimates match the paper.

---

## 5. Instruments for the non-cheap slope (`code/explore/step21_noncheap_iv_screen.py`, `step21b_noncheap_iv_pooled.py`; `logs/explore_step21*.log`, `logs/explore/step21*_*.csv`)

**Why.** In the split-sample diagnostic (main spec, section 4), the Hausman IV has a first-stage F of only 2.6–6.2 for non-cheap funds, so their slope is weakly identified.

**Candidates.** Every instrument in the index data that the coauthor built or listed in the notebooks: 27 with full coverage and within-fund variation.
- Hausman operating-cost and management-fee variants. The notebook comments out the operating-cost one as "too correlated" with the Hausman IV. Note on units (`step23`): `product_mgmt_fee` is in basis points (SPY 4.7 against a 0.09% expense ratio), so the management-fee variant is the family-average management fee in basis points. The operating-cost variant is defined as Hausman expense ratio (percent) minus Hausman management fee (basis points), so it mixes units and is essentially minus the management-fee variant. That is why the two behave as mirror images below.
- Rival-fund counts, five variants.
- Rivals' log age and tracking error, five variants each, plus the two logged versions used in the 3-RC cell.
- New-product entry counts and new products' fees, five variants each.

The conduct-test shifters (sentiment, BAB, FMAX and the like) are left out: they are demand shocks by construction, so they cannot be excluded from demand. Each candidate is run within each group (entry tier; group-specific fund FE, month FE and controls), alone and together with the Hausman IV, with a Hansen J test of agreement.

**Results for non-cheap funds** (slope with the candidate alone; first-stage F in parentheses; Hansen J p-value with the Hausman IV):

| Candidate | 10th pct | 15th pct | 20th pct | Same instrument, cheap funds (20th) |
|---|---|---|---|---|
| Hausman IV (main spec) | −12.4 (F 2.6) | −12.9 (F 5.8) | +4.7 (F 6.2) | −47.3 (F 15.8) |
| Hausman mgmt fee (op-cost variant is its mirror image) | +3.2 (F 25); J p 0.00 | +2.8 (F 36); J p 0.00 | +6.8 (F 34); J p 0.53 | −5.8 (F 39); J p 0.00 |
| New products, count (1, 4, 5) | −8.2 to −10.9 (F 29–34); J p 0.56–0.87 | −7.7 to −9.0 (F 32–34); J p 0.34–0.51 | −6.6 to −8.3 (F 29–33); J p 0.00 | −4.7 to −6.8 (F 20–57); J p 0.00 |
| Rival-fund counts (1–5) | −17 to +2 | −13 to +4 | −16 to +2 | −29 to +9 |
| Rivals' log age (1–5) | −10 to +6 | | −11 to +5 | |

**Reading.**
1. **No candidate gives a credible, consistent non-cheap slope.**
   - The rival counts and rival characteristics have very strong first stages (F up to 600), but their implied slopes range from −17 to +6 depending on the variant. They cannot all be valid.
   - The family-average management fee (and its mirror-image op-cost variant) has a strong first stage and gives *positive* slopes, +3 to +7. They agree with the Hausman IV's +4.7 at the 20th.
2. **The new-product counts are the most stable** (−7 to −11 at every cutoff, F ≈ 30), but their sign pattern points to an exclusion violation *(inference)*.
   - More new products in the market go with slightly *higher* incumbent fees (positive first stage) and *lower* incumbent shares (negative reduced form). The slope comes from the share loss.
   - That share loss is business stealing by the new entrants. A plain logit with one market per month leaves this within-index substitution in the demand error, so a count of entrants is correlated with ξ.
   - For cheap funds the same instruments give −2 to −7, against −37 to −57 from the Hausman IV, and Hansen J rejects at every cutoff. The Hausman IV has the expected sign pattern there: a higher instrument raises the own fee and lowers the share, with a reduced-form t of −19 to −30.
3. **Using a new-product count for non-cheap funds inside the pooled model does not help** (`step21b`):

   | Instruments, pooled model, 20th pct | Non-cheap | Cheap total | min F | Hansen J p | Share e > 0 | Table 5 > 1 |
   |---|---|---|---|---|---|---|
   | H, H × cheap (main spec) | −8.13 (4.32) | −40.8 | 18.3 | | 0 | 11 |
   | H × cheap, new products × (1 − cheap) | +0.01 (3.54) | −28.0 | 30.0 | | **0.55** | 6 |
   | H, H × cheap, new products × (1 − cheap) | −4.05 (3.39) | −34.5 | 14.7 | **0.001** | 0 | 11 |

   At the 15th percentile the pattern is similar (non-cheap −3.5 to −8.2; J p ≤ 0.001). At the 10th the two families agree (J p 0.83–0.96), and the estimates barely differ from the main spec (non-cheap −5.2 to −6.4, cheap total −65 to −69). In the pooled model the non-cheap slope lands near zero instead of the split-sample −7 to −11, because month FE and control coefficients are shared across the groups.
4. **Bottom line.** With the instruments available, the non-cheap slope cannot be pinned down. Every cost-side instrument says it is close to zero or weakly positive at the 20th. The entry and competition instruments say it is negative but are likely invalid in a plain logit. The cheap slope, which drives the Table 5 question, is identified by the Hausman IV alone and is robust.
5. **What could help.** (Both were then examined: the nested logit is in section 5b and does not identify the non-cheap slope; no cost shifter exists in the data.)
   - A nested logit with nests by tracked index (`market_m_index`). It keeps the fee linear and models within-index business stealing, which is exactly what makes the rival and new-product counts textbook instruments (for the within-nest share term).
   - A genuine cost shifter with within-fund variation for higher-fee funds, for example sub-advisory or custody cost changes, or the expiry of fee waivers.

### 5b. Nested logit with tracked-index nests (`code/explore/step22_nested_logit.py`, `logs/explore_step22_nested_logit.log`, `logs/explore/step22_*.csv`)

**Model.** ln s_j − ln s_0 = α·p_j [+ α_c·p_j·cheap_j] + controls + ρ·ln s_{j|g} + fund FE + month FE + ξ_j, where the nest g is the tracked index (`market_m_index`). There are 461 nests; 27% of fund-months are alone in their nest, and the S&P 500 nest holds up to 130 funds. The fee stays linear. pyblp estimates ρ by GMM with ρ bounded to [0, 0.99], and elasticities and costs account for the nests.

**Instruments.** The price instruments are the Hausman IV (and × cheap). For the within-nest share, four sets, built from the full raw file so they do not depend on the sample's share filter:
- the log number of funds tracking the same index that month;
- the same count 12 months earlier;
- that count plus entrants in the last 12 months and rivals' mean log age;
- the coauthor's `rival_funds1` and `newproduct_1`.

**Results** (20th percentile unless noted; SE clustered by month):

| Model | Nest instruments | ρ (SE) | Non-cheap price (SE) | Cheap total | Hansen J p | Share e > 0 | Avg e | Table 5 > 1 |
|---|---|---|---|---|---|---|---|---|
| One slope | rivals | 0.00 (0.07) | −5.89 (0.56) | | | 0 | −1.70 | 2 |
| One slope | rivals + entrants + age | 0.19 (0.06) | −7.33 (0.74) | | 0.000 | 0 | −2.39 | 2 |
| Cheap tier | rivals | 0.49 (0.06) | **+1.35 (0.75)** | −18.0 | | **0.55** | −1.01 | 6 |
| Cheap tier | rivals, 12 months earlier | 0.55 (0.05) | **+2.68 (0.79)** | −14.8 | | **0.55** | −0.33 | 7 |
| Cheap tier | rivals + entrants + age | 0.78 (0.06) | −3.69 (0.81) | −21.0 | **0.000** | 0 | −6.11 | 13 |
| Cheap tier | coauthor's | 0.54 (0.08) | **+2.70 (0.49)** | −15.0 | 0.57 | **0.55** | −0.32 | 7 |
| Cheap tier, 15th | rivals | 0.46 (0.09) | −3.09 (0.95) | −26.6 | | 0 | −2.73 | 11 |
| Cheap tier, 10th | rivals | 0.37 (0.11) | +0.51 (0.96) | −33.8 | | 0.76 | −0.93 | 7 |
| Split sample, non-cheap only | rivals | 0.00 (0.85) | −7.02 (9.63) | | | 0 | −2.99 | |
| Split sample, non-cheap only | rivals, 12 months earlier | 0.00 (1.22) | −5.38 (11.56) | | | 0 | −2.29 | |
| Split sample, non-cheap only | rivals + entrants + age / coauthor's | 0.99 (bound) | −19.1 / −3.7 | | 0.000 / 0.04 | 0 | degenerate | |
| Split sample, cheap only | rivals / rivals 12 months earlier | 0.93 / 0.92 (0.06) | −12.7 / −13.4 (cheap) | | | 0 | −15.5 / −13.0 | 12 |

**Reading.**
1. **The nests do not identify the non-cheap slope.**
   - In the pooled model with the cheap tier, the clean exactly identified nest instruments make the non-cheap price coefficient *positive* at the 10th and 20th percentiles, and 55–76% of fund-months get upward-sloping demand. Only at the 15th percentile is it negative (−3.1).
   - The overidentified set gives negative slopes, but Hansen J rejects (p < 0.001), and at the 15th percentile ρ runs to the 0.99 bound.
   - On non-cheap funds alone, ρ is either not identified (0 with SE 0.85–1.2) or runs to the bound, and the price coefficient is as imprecise as with the Hausman IV alone (SE ≈ 10).
2. **The overidentification tests still reject.** The hope was that modelling within-index substitution would make the rival and entry counts valid alongside the Hausman IV. In every overidentified run except the coauthor's pair at the 20th (p = 0.57, which comes with 55% upward-sloping demand), Hansen J still rejects.
3. **One by-product is worth noting** *(inference)*.
   - Among cheap funds alone, the nest parameter is large and consistent across the two exactly identified instrument sets (ρ = 0.92–0.93, SE 0.06): cheap funds tracking the same index are close substitutes.
   - With ρ that high, own elasticities of the cheap Table 5 funds become very large: −3 to −28 (iShares Core S&P 500 −5.1, SPY −15.3, Vanguard 500 Admiral −6.8, SPDR Portfolio S&P 500 −3.8).
   - This points to the same conclusion as the cheap tier (cheap funds' demand is very fee-sensitive), through within-index substitution instead of a steeper slope. It would change the paper's markup calculations a lot and is a modelling choice for the authors, not a fix for the non-cheap slope.
4. **Bottom line.** Neither route identifies the non-cheap slope with the data available. Nested logit with tracked-index nests leaves it unidentified, and there is no cost shifter in the data (`product_mgmt_fee` is in basis points and is part of the fund's own price; `product_exp_ratio_bkpt` is a monthly market-wide value absorbed by the month FE).

**Cost shifters would need outside data** *(inference)*. Candidates with within-fund variation for higher-fee funds:
- index licensing costs (for example, Vanguard's 2012–13 switch of 22 funds from MSCI to CRSP and FTSE benchmarks, made to cut licensing fees);
- the expiry of fee waivers or expense caps, from prospectus gross versus net expense ratios;
- sub-advisory fee schedules from N-CEN or N-SAR filings.

### 5c. Nested logit re-estimated with the share-class-matched Hausman IV (`code/explore/step28_nested_newiv.py`, `logs/explore_step28_nested_newiv.log`, `logs/explore/step28_*.csv`)

Same model and nest instruments as 5b, but the price instruments are the new Z and Z × cheap (`MAIN_REPORT_sharecl_hausman.md`), on the 97,429 fund-months where Z is defined (453 nests; 30% of fund-months alone in their nest). The paper's instrument is re-run on the same rows for comparison. SE clustered by month; first-stage F (Sanderson–Windmeijer) partials out the same fixed effects as the model.

**Pooled model, 20th percentile:**

| Price IV | Time FE | Nest instruments | ρ (SE) | Non-cheap (SE) | Cheap total | J p | Share e > 0 | Neg. MC | Avg e | Table 5 > 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| *No nests (main model)* | *month* | | | *−6.12 (0.85)* | *−28.8* | | *0* | *0.24* | *−2.68* | *7* |
| new | month | rivals | 0.48 (0.04) | −1.14 (0.38) | −18.0 | | 0 | 0.67 | −1.76 | 6 |
| new | month | rivals, 12 months earlier | 0.54 (0.03) | −0.48 (0.33) | −16.6 | | 0 | 0.78 | −1.61 | 10 |
| new | month | rivals + entrants + age | 0.60 (0.04) | −1.58 (0.37) | −18.3 | **0.000** | 0 | 0.50 | −2.34 | 10 |
| new | month | coauthor's | 0.35 (0.08) | −2.49 (0.74) | −21.0 | 0.49 | 0 | 0.41 | −2.03 | 7 |
| paper's | month | rivals | 0.18 (0.05) | **+3.96 (0.99)** | −15.5 | | **0.53** | 0.19 | +0.08 | 4 |
| paper's | month | rivals, 12 months earlier | 0.25 (0.05) | **+6.43 (1.29)** | −11.2 | | **0.53** | 0.28 | +0.91 | 4 |
| paper's | month | coauthor's | 0.10 (0.07) | +0.13 (1.08) | −21.6 | 0.07 | **0.53** | 0.00 | −1.08 | 4 |
| *No nests (main model)* | *month × asset class* | | | *−3.80 (0.66)* | *−24.0* | | *0* | *0.36* | *−1.96* | *5* |
| new | month × asset class | rivals | 0.25 (0.05) | −1.98 (0.37) | −19.2 | | 0 | 0.58 | −1.62 | 4 |
| new | month × asset class | rivals, 12 months earlier | 0.39 (0.03) | −1.01 (0.32) | −16.6 | | 0 | 0.75 | −1.43 | 6 |
| new | month × asset class | coauthor's | 0.49 (0.06) | −0.39 (0.50) | −14.9 | 0.23 | 0 | 0.83 | −1.31 | 6 |

Three of the 32 fits stopped short of pyblp's convergence test: paper's IV with month FE and rivals; new IV with month × asset class and rivals; new IV at the 15th percentile with month FE and lagged rivals. Their values are close to the neighbouring rows.

**Other cutoffs and the split sample (new IV, rivals):**

| Run | Time FE | ρ (SE) | Non-cheap (SE) | Cheap total | Neg. MC | Table 5 > 1 |
|---|---|---|---|---|---|---|
| One slope | month | 0.00 (0.06) | −3.68 (0.50) | | 0.65 | 1 |
| 15th | month | 0.33 (0.05) | −5.12 (0.52) | −24.8 | 0.27 | 11 |
| 10th | month | 0.22 (0.05) | −4.00 (0.45) | −25.6 | 0.47 | 5 |
| 15th | month × asset class | 0.09 (0.05) | −6.00 (0.48) | −26.8 | 0.29 | 7 |
| 10th | month × asset class | 0.04 (0.05) | −4.59 (0.41) | −24.0 | 0.49 | 3 |
| Split, non-cheap only | month | 0.00 (0.10) | −4.29 (0.70) | | 0.26 | 1 |
| Split, cheap only | month | 0.94 (0.06) | −14.70 (0.75) (cheap) | | 0.09 | 12 |

**Reading.**
1. **The new IV fixes the sign problem of 5b.** With the paper's instrument, the nested model with the cheap tier still gives a positive non-cheap slope and 53% upward-sloping demand on the same rows. With the new instrument the non-cheap slope is negative in every run, and no fund-month has upward-sloping demand.
2. **It does not beat the plain logit IV.** Pooled, ρ = 0.25–0.60 absorbs much of the fee response. The non-cheap slope shrinks to −0.4 to −2.5, the cheap total to −15 to −21, and 41–83% of fund-months imply negative marginal cost, against 24% in the main model. Hansen J rejects the overidentified set (p < 0.001); the coauthor's pair passes (p = 0.49 / 0.23).
3. **ρ is not stable.** It moves with the cutoff (0.22–0.48 under month FE; 0.04–0.25 under month × asset class) and with the nest instrument. With one slope, or among non-cheap funds alone, it is 0. Only among cheap funds alone is it large (0.94, as in 5b), so the pooled ρ mostly picks up cheap funds' within-index substitution, which the cheap interaction already captures.
4. **Bottom line.** Nests by tracked index are a sensitivity check, not an improvement. Under the specification without nests (ρ = 0), the non-cheap slope is −4.3 (0.7) in the split sample and −6.1 (0.9) pooled; the nested model does not reject that. It does, however, imply negative margins for most fund-months.

## 6. The Hausman IV itself: definition, checks, and a better-behaved variant (`code/explore/step23_hausman_reconstruct.py`, `step24_hausman_variants.py`, `step24b_family_split.py`, `step24c_class_month_fe.py`, `asset_class.py`; `logs/explore_step23*`, `explore_step24*`; `logs/explore/step24*_*.csv`)

**Definition** (reverse-engineered; the column arrives precomputed). For fund j in month t, it is the previous-month-AUM-weighted average expense ratio of the same family's (`firm_f_old`) funds that track other indices. It matches the data exactly where the family identifier exists (correlation 1.000). The 7% of estimation-sample fund-months without a family identifier are 112 funds, mostly variable-annuity and insurance-channel funds (Voya, Directed Services, SunAmerica, Nationwide). Their instrument values have an unknown construction, and on those rows the instrument does not move with the fund's own fee (within-fund correlation −0.12).

**Table 2's −5.6 comes from those 7% of rows** (`step24b`):

| Sample | Price coefficient (SE) | First-stage F |
|---|---|---|
| All fund-months (Table 2 col 2) | −5.61 (1.31) | 33.6 |
| With a family identifier (93%; 1,190 funds) | **+7.24 (1.99)** | 26.6 |
| Without a family identifier (7%; 112 funds) | **+2.32 (0.54)** | 57.2 |
| Pooled, month FE separate for the two groups | **+7.64 (2.20)** | |

Both subsets give upward-sloping demand. The negative pooled estimate comes from a different time trend between the two groups under common month effects. For the 112 funds without a family identifier the instrument rises from 0.26 to 0.30 over 2016–2024 while their shares fall; for everyone else it falls from 0.35 to 0.15.

**Alternative constructions** (family-identifier rows only, so every instrument uses the same rows). The changes you suggested:
1. Leave out the fund's whole asset class, not just its index. Asset classes are assigned per tracked index (`asset_class.py`): US equity, international equity, bonds, allocation and real assets.
2. Use the median instead of the AUM-weighted mean, which also removes the AUM weights that depend on past demand.
3. Match on vehicle or on share class.

The share-class-matched version is the only one that behaves well (`step24`, `step24c`):

| Instrument | Fixed effects | One slope (SE), F | Main spec: non-cheap (SE) / cheap total, min F | Split: non-cheap IV (F) / cheap IV (F) | Lead t, ξ̂ 12 / 24 / 36 months earlier |
|---|---|---|---|---|---|
| Original Hausman IV | fund + month | **+11.26 (3.14)**, F 25 | −2.72 (2.75) / −26.8, F 13 | +93 (F 0.7) / −68 (F 55) | **6.7 / 10.7 / 20.3** |
| Original Hausman IV | fund + month × asset class | −1.33 (1.25), F 56 | −9.94 (2.46) / −37.6, F 33 | **+7.2** (F 28) / −106 (F 24) | 2.1 / **8.4 / 18.2** |
| **Median, outside asset class, same share class** | fund + month | **−1.24 (0.58), F 218** | **−6.12 (0.85) / −28.8, F 167** | −2.4 (F 149) / −47.2 (F 48) | 2.1 / 2.6 / 5.2 |
| **Median, outside asset class, same share class** | fund + month × asset class | **−1.28 (0.43), F 333** | **−3.80 (0.66) / −24.0, F 183** | −1.6 (F 202) / −40.7 (F 63) | 2.4 / 2.8 / 5.8 |

Other variants on the same rows, each with fund + month effects:
- Outside the asset class with AUM weights or the median, and the vehicle match: the main spec's non-cheap slope comes out positive in five of these six runs, or the first stage collapses.
- The median outside the own index only: one slope +36.7, F 2.5.
- The family's other-index funds within the same asset class: one slope +3.21.

Details in `logs/explore/step24_hausman_variants.csv`.

**Placebo** (each family mapped to a random one of the 30 broadest other families, 20 draws). The partner family's fees still have some first-stage power. For the share-class-matched construction with asset-class × month effects, the median F is 27 (10–90% range 0.1–156) on a placebo sample about 40% the size. The placebo slopes centre on zero (pooled −0.8, non-cheap +1.0, cheap −18) with very wide dispersion. Scaled for sample size, the real instrument's first stage (F 333) sits near the top of the placebo range. That means part, not all, of its variation is family-specific. For the original Hausman IV with fund + month effects, the placebo median F (13) is about half the real one (25).

**Reading.**
1. **The paper's Hausman IV does not pass these checks.**
   - On the 93% of fund-months where its construction is known, it implies upward-sloping demand.
   - The lead tests reject strongly: t up to 20, meaning past demand shocks predict today's instrument.
   - Another family's fees have about half its first-stage power.
2. **Share-class matching gives a usable instrument.** Its first stage is very strong (F 150–330), slopes are negative in every split, and the estimates survive asset-class × month effects. The lead tests are much weaker (t 2–3 at 12–24 months) but still reject at 36 months (t ≈ 5–6).
3. **Re-estimating the main spec with it changes the headline.**
   - The non-cheap slope is now precisely estimated: −6.1 (SE 0.85) with fund + month effects, −3.8 (0.66) with asset-class × month effects.
   - The cheap total is −29 or −24, against −41 with the original instrument.
   - The Table 5 funds above |e| = 1 fall from 11 to 7 or 5.
   - Average elasticity −2.7; negative implied MC 24%; no upward-sloping demand.
   - The cheap-versus-non-cheap gap survives, at 4–6 times the non-cheap slope.

   15 Table 5 funds with fund + month effects (Aug 2024): iShares Core S&P 500 −0.84, EAFE −2.00, AGG −0.86, Russell 1000 Growth −5.15, Mid-Cap −1.43, SPY −2.50, SPDR Gold −2.44, Technology and Financial Select Sector −0.49, SPDR Portfolio S&P 500 −0.57, Vanguard TSM Inst. Plus −0.55, Vanguard 500 Admiral −1.11, Vanguard 500 ETF −0.84, VTI ETF −0.84, VTSM Admiral −1.12.

## Appendix A. Facts about Table 5 and the data found along the way

**Table 5.**
- The "Elasticity" column equals −8.348 × p × (1 − s) in each fund's **last sample month** (Aug 2024), for all 15 funds to within 0.0005; −8.348 is the Table 2 col 4 (3 RC) price coefficient, and with σ ≈ 0 the 3-RC model is effectively logit. Logit IV (−5.606) and BLP 1 RC do not reproduce the column.
- The "Bertrand" (and Cournot, Monopoly) columns are **markup levels in percentage points** (p − mc), averaged over the sample; the coauthor's R averages pyRVtest's `markups`, which notebook cell 34 labels "Price minus Marginal Cost in Percentage Points per Annum" (Lerner is computed separately as markup / price in cell 33). A 0.22 markup on a fund charging 0.02–0.04% means marginal cost of about −0.19 pp. The two columns are therefore consistent with each other: both say Lerner > 1 and negative marginal cost for the cheapest funds.
- Two Vanguard rows are swapped: the 430,969 AUM fund is VTI's **ETF** class (p = 0.03, e −0.244) and the 395,578 fund is the **Admiral** class (p = 0.04, e −0.326).
- The note "averaged over the entire sample period" is true for the markups only.

**Table 2 replication** (`RESULTS_table2.md`): all 16 columns match the point estimates and average elasticities to three decimals. SEs that do not match: Panel A col 2 price SE is 1.310 here vs 0.131 in the paper (exactly 10×, likely a decimal slip); Panel B col 2 past-return SE 0.036 vs 0.040; BLP SEs 1.2–1.9× the paper's. Column (1) elasticities match the observation-level mean while columns (2)–(4) match the per-market mean. The leveraged notebook's Bull-only filter is what Table 2 uses.

**Data.**
- Sample periods: index raw Jan 1994 – Dec 2025, estimation Jan 2010 – Aug 2024; leveraged raw Jan 2007 – Sep 2024, estimation Jan 2010 – Sep 2024. The panels end a month apart.
- Index sample: median share 0.037%, max 4.97%; median fee 0.20%, 5th percentile 0.04%; only 3.75% of fee variance is within fund.
- Zero-fee funds (e.g. Fidelity's) are dropped by the `prices > 0` filter and sit in the outside option.
- **SPY's fee is recorded as 0.04% from Oct 2022 to Sep 2023**; it was 0.0945% throughout. Correcting it changes the tier estimates only in the third decimal, but it should be fixed at the source.
- **43 temporary fee changes in 39 funds** (≥ 0.02 pp, reverting to the exact prior fee within 12 months; `logs/explore/step8_fee_reversals.csv`). Likely typos: Vanguard Long-Term Bond Index Institutional (0.04 → 0.40 → 0.04) and BNY Mellon Institutional S&P 500 (0.20 → 0.50 → 0.20). Most others last exactly 12 months, suggesting annual prospectus values. All fee changes in the file occur in January.
- SPY's fee never changed (0.09%) but moved from the 6th–8th percentile of index-fund fees in 2010 to the 43rd–48th in 2024; VTI cut from 0.06% to 0.03% and stayed in the 2nd–10th percentile (`logs/explore/fee_percentiles_spy_vti.csv`).
- `market_m_cluster` is an index cluster (313 codes), not an asset class. `csent_index_resid` and `chg_VIX_resid` vary within a month.
- "First month in the sample" is mostly not the launch: 43% of funds enter in Jan 2010, 43% when they first pass the share ≥ 0.01% filter, 15% at their first raw month.

**Paper fixes regardless of the model:** relabel Table 5's markup columns as levels in pp and the elasticity as last-month; swap the two Vanguard rows; fix the Panel A col 2 price SE; use one averaging definition across Table 2's columns; state the Bull-only filter and the panels' end months; if the linear model stays as is, say that it implies Lerner > 1 for the cheapest funds and give a reason (securities-lending income is the natural candidate).

## Appendix B. Worth exploring next

- An instrument for the random coefficient that agrees with the Hausman IV under the cheap interaction: none of the 24 in the data does, nor differentiation or optimal instruments built from the Hausman IV. A cost shifter with within-fund variation is the natural candidate.
- Why Vanguard drives the non-cheap slope (which Vanguard funds changed fees, and whether those changes are exogenous); a Vanguard-specific slope.
- The `broad_specialized` label for S&P 500 funds.
- Data cleaning: SPY's fee, the 43 temporary fee episodes, how expense ratios are sourced.
- Zero-fee funds modelled explicitly rather than folded into the outside option.
- One demand model for both markets if the functional form changes.

## Appendix C. Code and logs

| What | Where |
|---|---|
| Logit IV screen (all interactions, diagnostics) | `code/explore/step2_logit_screen.py`, `step2b`–`step2d`, `logs/explore_step2_*.log`, `logs/explore/step2_*.csv` |
| Entry-tier robustness (SPY fix, drop firms, broad, sample-only cutoffs) | `code/explore/step8_raw20_robustness.py`, `logs/explore_step8_raw20_robustness.log`, `logs/explore/step8_robustness.csv` |
| First-sample-month fixed-fee-cutoff variants | `code/explore/step2e_cutoff_sweep.py`, `step2f_switcher_composition.py`, `logs/explore/step2e_cutoff_sweep_value.csv` |
| Lagged-fee percentile | `code/explore/step16_lagfee_pct.py`, `logs/explore_step16_lagfee_pct.log`, `logs/explore/step16_*.csv` |
| Why the lag-60 slopes are steeper (term-by-term, switchers vs non-switchers, event study, one-slope IV split by group) | `code/explore/step18_lag60_why.py`, `step18b_lag60_collinearity.py`, `step18c_pooled_iv_split.py`, `logs/explore_step18c_pooled_iv_split.log`, `step20_split_sample_iv.py`, `logs/explore_step20_split_sample_iv.log`, `logs/explore_step18_lag60_why.log`, `explore_step18b_lag60_collinearity.log`, `logs/explore/step18_*.csv` |
| Instruments for the non-cheap slope (screen of 27 candidates; pooled model with new-product counts) | `code/explore/step21_noncheap_iv_screen.py`, `step21b_noncheap_iv_pooled.py`, `logs/explore_step21_noncheap_iv_screen.log`, `explore_step21b_noncheap_iv_pooled.log`, `logs/explore/step21*_*.csv` |
| Hausman IV variants, family split, asset-class x month FE, placebo | `code/explore/step24_hausman_variants.py`, `step24b_family_split.py`, `step24c_class_month_fe.py`, `asset_class.py`, `logs/explore_step24*.log`, `logs/explore/step24*_*.csv` |
| Hausman IV reconstruction (definition, units of the variants) | `code/explore/step23_hausman_reconstruct.py`, `logs/explore_step23_hausman_reconstruct.log` |
| Nested logit, tracked-index nests | `code/explore/step22_nested_logit.py`, `logs/explore_step22_nested_logit.log`, `logs/explore/step22_*.csv` |
| Nested logit with the share-class Hausman IV | `code/explore/step28_nested_newiv.py`, `logs/explore_step28_nested_newiv.log`, `logs/explore/step28_*.csv` |
| Cheap tier plus a second interaction (ETF, share class, broad, Big 3, firms) | `code/explore/step19_cheap_plus_interactions.py`, `logs/explore_step19_cheap_plus_interactions.log`, `logs/explore/step19_*.csv` |
| Status from the fee 60 months earlier (and 36/48/84), with decomposition | `code/explore/step17_lag60_tier.py`, `step17b_lag60_decompose.py`, `logs/explore_step17_lag60_tier.log`, `explore_step17b_lag60_decompose.log`, `logs/explore/step17*_*.csv` |
| Log price | `step2_logit_screen.py` (B1), `step4_blp_shortlist.py`, `step5_*`, `step6_logp_blp_strong_iv.py` |
| BLP with the interaction | `step4_blp_shortlist.py` (env `EXTRA_IV`, `EXTRA_IV_NAME`, `EXTRA_NOINTERACT`), `step9_lognormal_1rc.py`, `step7_lognormal_two_group.py`, `logs/explore_table2_alt_*` |
| σ profile, Hansen J at fixed σ, σ-fixed exhibit | `step13_sigma_profile.py`, `logs/explore_step13_*`, `logs/explore/step13cal_*` |
| Instrument checks and screens, optimal IVs | `step10_instrument_check.py`, `step10b_*`, `step12_iv_screen.py`, `step12b_*`, `step14_diff_iv_screen.py`, `step15_optimal_iv.py` |
| Table A7 col 3 re-run | `RESULTS_A7_col3.md`, `code/explore/a7_col3.py`, `logs/explore_a7_col3.log` |
| Table 5 reconstruction | `step1_table5_elasticity.py`, `step1b_formula_check.py`, `logs/explore_step1*` |
| Table 2 replication | `RESULTS_table2.md`, `code/table2_logit_ols.py`, `code/solve_rc3_resumable.py` |
| Superseded working documents (kept for the record) | `docs/superseded/Table2_alt.md`, `FINDINGS_SUMMARY.md`, `EXPLORATION_price_heterogeneity.md` |
