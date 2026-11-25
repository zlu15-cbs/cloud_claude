# Passive fee random coefficient: access-type specification and the mutual-fund fee slope

25 Nov 2026. Danny's Tables 7–10 package (98,110 passive fund-months, 1,063 share classes), read without running
his code. Linear screens are the Salanié–Wolak version: 2SLS with K = p(p/2 − e_t); the coefficient on K is σ².
Fund fixed effects and controls (tracking error, 1-year return, log age) throughout; standard errors clustered by month.
Fees are in percentage points. Nothing here has been sent to Danny.

Code: `code/explore/step48_access_spec_linear.py`, `step49_access_blp.py`, `step50*_*.py`.
Output: `logs/explore/step48_*`, `step49_*`, `step50*`.

## 1. Status

- **Specification B is withdrawn as the candidate preferred specification.** Its retail slope is zero, its
  institutional slope depends on a first-stage restriction, and in the BLP itself σ is not significant.
- **The problem is the mutual-fund classes, not the retail flag.** No cut of the mutual-fund classes gives a
  stable negative fee slope with Danny's instruments. ETFs do.
- **Next candidate: two segments (mutual fund, ETF), no retail / institutional flag.** Its BLP estimate is running.

## 2. Specification B and its BLP estimate

B = Table 7 + fee × institutional and fee × ETF slopes + month × access fixed effects (corrected flag);
instruments: Danny's five plus IV0 and IV1 × {institutional, ETF}.

| | Linear screen | BLP, one-step, 3,000 draws |
|---|---|---|
| σ² (linear) / σ (BLP) | +38.4 (7.2) | 2.24 (3.15) |
| Fee slope, retail | −8.6 (1.7) | −0.90 (2.50) |
| Fee slope, institutional | −15.7 | −27.0 |
| Fee slope, ETF | −36.1 | −19.7 |
| Criterion | J 111.4 on 5 df | 113.7 (two-step J ≈ 197.5 on 5 df) |

- BLP: 34% of investors have a positive fee coefficient for retail classes. AUM-weighted elasticity, last month:
  retail −0.05, institutional −1.07, ETF −2.21.
- The linear screen overstated σ. The BLP σ is within one standard error of zero.

## 3. Why the retail slope is zero

Logit version of B (no K): retail +0.12 (0.34), institutional −28.4, ETF −17.4.

| Possible cause | Check | Result |
|---|---|---|
| Too little fee variation in retail | Within-class SD of the fee; months with a fee change | Retail 3.4 bp, 2.5%; institutional 2.5 bp, 2.8%; ETF 3.7 bp, 3.0%. Not the cause. |
| Weak instruments | First-stage F, retail alone | 101. Not the cause. |
| Broker-sold classes (fee includes distribution) | Class type from the name | Broker-sold classes are 0.1% of retail AUM. Vanguard Admiral is 52%; nearly all the rest is no-load. Not the cause. |
| The Admiral recode | Logit B without it | Retail −0.03 (0.35). Not the cause. |
| Vanguard Investor classes closed and converted from 2019 | Drop those 611 class-months, or give them their own month effects | Retail +0.18 and +0.34. Not the cause. |
| Month × retail effects absorb the variation | Common month effects instead | Retail −5.2, institutional −12.3, ETF −13.2, but then σ² = −21.6 (3.7): the problem of point (1) returns. |
| **Instruments disagree within retail** | One instrument at a time | IV0 −1.9 (0.3); IV1 +9.7 (1.7); IV2 −18.0 (2.3); IV3, IV4 weak. |
| **Period** | Retail before / from 2019 | −1.8 (0.4) / +6.8 (0.9). With IV0 alone: −1.0 / +10.0. |
| **Family** | Retail, Vanguard / other | +6.2 (2.4) / +0.7 (0.4). Vanguard is 71% of retail AUM. |

## 4. The institutional slope is not robust either

| Institutional fee slope | Estimate |
|---|---|
| In B (IV2–IV4 first stages common across segments) | −28.4 (5.7) |
| Institutional classes alone, five IVs | **+13.0 (1.4)** |
| B with all five instruments × access (15 IVs) | +13.0 |
| Alone, by instrument | IV0 no first stage (F 1.0); IV1 −31.8; IV2 +12.8; IV3 +50.4; IV4 +12.4 |

The instruments do not work the same way in the three segments. First stage of IV0 (family fee in other asset
classes): retail +0.27 (t 16.5), institutional +0.005 (t 1.0), ETF −0.047 (t −3.6). Reduced form of IV1 (count of
near-fee rivals) on share: negative in retail, positive in institutional and ETF.

## 5. Mutual-fund classes against ETFs

| Sample (logit, fund + month FE, five IVs) | Fee slope | With K: σ² |
|---|---|---|
| ETFs only | −13.6 (1.0), F 76 | +116 (23), but F 2.5–3.4: weak |
| Mutual-fund classes only | **+4.4 (0.6)** | **−53.0 (7.3)** |
| Mutual-fund classes, before 2019 / from 2019 | −1.0 (0.5) / +5.4 (1.6) | |
| Mutual-fund classes aggregated to the fund (portfolio) | +1.3 (0.4); before 2019 −1.9 (0.4) | −94 (8) |

- ETFs, by instrument: IV0 −9.2, IV1 −20.6, IV2 −0.4, IV3 −35.6, IV4 −27.2. Negative throughout.
- The wrong-signed curvature (σ² < 0) of the pooled Table 7 analogue comes from the mutual-fund classes.
- Aggregating share classes to the fund level moves the mutual-fund slope toward zero but does not make it negative.
  The instruments were averaged across classes, not rebuilt, so this is a rough test.

## 6. Two-segment specification (S2)

Fee slope for mutual-fund classes (pooled) and for ETFs; fund and month × ETF fixed effects; instruments:
Danny's five plus IV0 and IV1 × ETF. It does not use the retail / institutional flag.

| Linear screen | Mutual-fund slope | ETF slope | σ² | J |
|---|---|---|---|---|
| Logit | −1.2 (0.6) | −15.5 | | 98.5 on 5 |
| With K | −8.5 (1.5) | −44.0 | +54.5 (7.6), F 11 | 40.7 on 4 |
| K split: own fee p²/2; market position −p·e_t | | | +38.7 (5.5); +2.8 (9.2) | 41.0 on 3 |
| + age K | | | +54.3 (7.5); age −0.08 (0.36) | 42.2 on 3 |
| All five IVs × segment (10) | +3.4 (1.0) | −20.9 | +13.7 (5.2) | 140.0 on 7 |
| IV0 and IV1 × segment | −6.1 (1.9) | −37.2 | +37.6 (9.8) | 1.8 on 1 |
| IV0 and IV2 × segment | +8.9 | +42.7 | −73.3 (9.6) | 14.1 on 1 |
| IV0 and IV3 × segment | +8.9 | +24.8 | −68.2 (22.5) | 34.1 on 1 |
| IV0 and IV4 × segment | −9.5 | −55.1 | +71.1 (43.6) | 13.7 on 1 |

- Logit elasticities, AUM-weighted, last month: mutual funds −0.06, ETFs −1.82.
- σ² is positive with the rival-count instruments matched on the fund's own lagged fee (IV1, IV4) and negative
  with IV2 and IV3. This is the instrument dependence already noted for Table 7.
- BLP estimate of S2: running (`step49_access_blp.py ... S2`).

## 7. Ways to address the mutual-fund slope

1. **Report it as a finding and confine the fee random coefficient and markups to ETFs.** Index mutual-fund
   demand that barely responds to monthly fee changes is consistent with platform lock-in and search frictions.
   The comparison group for leveraged ETFs is passive ETFs, where the slope is identified.
2. **Estimate the passive system on ETFs only**, with mutual-fund classes in the outside option. Needs Danny's
   market shares and instruments redefined; the logit slope is −13.6 either way.
3. **Rebuild the mutual-fund side at the fund level from CRSP** (portfolio identifier, instruments rebuilt at that
   level, lower frequency). This is a new sample, not a change to Tables 7–10.
4. Not recommended: keep B and present the retail zero as a retail effect. The data do not support a retail /
   institutional difference in either direction.
