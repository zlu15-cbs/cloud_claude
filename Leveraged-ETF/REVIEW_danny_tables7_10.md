# Review of Danny's Tables 7–10 package (24 Nov 2026)

Source: `P16_LeverageMKT/Data/tables7_10_replication_20261124.zip`, which contains the Section 3 PDF, the prepared samples, the five instruments, and the archived fits.

Our checks are in `code/explore/step46_danny_iv_checks.py`, with output in `logs/explore/step46_danny_iv_checks.log`. The lognormal runs (25 Nov) are in `step45_lognormal_danny.py` and `step47_lognormal_profile.py`, with output in `logs/explore/step45_*` and `step47_*`. The script reads only his prepared arrays and runs none of his code. The numbers below are his archived fits unless marked "our check".

## 1. What his Slack message means

| Message | Meaning |
|---|---|
| "Here is the replication of Tables 7 to 10" | A self-contained package. `replicate.py verify` regenerates all 1,014 printed cells from the archived fits. `replay` and `refit` re-run them. |
| "I harmonized the IVs a bit more" | Every BLP column in a market now uses the same five excluded instruments. They share one 8-class asset dictionary ("P8"), one historical family dictionary, and IV0 built from observed fees in both numerator and denominator. The passive estimates are reused from his earlier "v8" note; only the write-up of the instruments is new. |
| "Focus on Tables 7 to 10" | Tables 1–2 keep the old comparator specifications. Tables 7–10 are the new five-IV demand and conduct results. Table 10 is "the adopted observed-fee baseline". |
| "age and return RCs in passive, price and age RCs in leveraged" | In passive funds, investors differ in their taste for fund age (σ 1.21, SE 0.29) and past return (σ 3.79, SE 0.80), but not detectably in fee sensitivity (σ_fee 0.040, SE 24.3). In leveraged funds, fee sensitivity (2.08, SE 0.46) and age (0.51, SE 0.21) differ; return does not (0.82, SE 1.30). |

**The five passive instruments:**

- **IV0:** AUM-weighted fee of the same family's funds in other asset classes. This is close to our Z, which uses the median and matches share class.
- **IV1:** count of other-family rivals at t−1 in the same class and access type, with fee within 10 bp and tracking error within 0.02.
- **IV2:** count of other-family, same-vehicle funds in other asset classes at t−1.
- **IV3:** stock of young same-class rivals from other families.
- **IV4:** certified rival liquidations over t−12 to t−1, matched like IV1.

**Other results:**

- **Conduct:** perfect competition (PC) is the only conduct retained for passive funds in every column. Leveraged funds retain B65 under BLP.
- **Scale:** the passive scale slope is γ = −0.0095 (SE 0.004). It is the same in every column, because under PC costs equal fees whatever the demand model.

## 2. (a) Is the identification of the fee random coefficient (BLP RC1) solved?

**For leveraged funds, yes. For passive funds, no.**

| Passive fit | σ on fee (SE) | Smallest standardized Jacobian singular value | Step-2 criterion (J), df | p |
|---|---|---|---|---|
| Table 7: fee RC only | 1.875 (0.367) | 0.70 | 144.4, 3 | 4e−31 |
| Table 8: fee + age RCs | 0.049 (20.5) | **0.031** | 102.3, 2 | 6e−23 |
| Table 9: fee + return RCs | 2.354 (0.378) | 0.47 | 59.6, 2 | 1e−13 |
| Table 10: all three (preferred) | **0.040 (24.3)** | **0.032** | 37.0, 1 | 1e−9 |

- **Rank is no longer the problem.** With eight moments, the Jacobian has full rank in every column. In Table 7 the fee RC is locally well determined.
- **But the preferred spec does not identify it.** In Tables 8 and 10, σ_fee sits at about zero with an SE of 20–24. The weakest direction of the Jacobian is about 20 times weaker than the next one. This is the σ = 0 stationary point described in the explainer page (Section 4): rank "passes" only at the 1e−9 tolerance. His own text calls passive price dispersion "imprecise". In substance, his message concedes there is no fee heterogeneity in passive funds.
- **Table 7's σ = 1.875 is fragile.**
  - *Our check, 1:* the linear version of Table 7 on his data and his five IVs reproduces it: fee −18.33, σ² = +3.07 (1.53), so σ ≈ 1.75.
  - *Our check, 2:* each just-identified pair gives a negative σ² (IV0 + IV1: −14.9 (3.8); IV0 + IV3: −57 (19); IV0 + IV4: −12.8 (3.4)). The positive value exists only in the overidentified combination.
  - *Our check, 3:* the overidentification test rejects. Our month-clustered J is 60.7 on 3 df.
  - Once the age K enters, the fee σ² turns negative: −12.7 (3.0), with σ²_age = +1.43. A normal RC cannot go below zero, so it stops at σ ≈ 0. That is exactly Tables 8 and 10.
- **Every fit rejects the overidentifying restrictions, in both markets.** Leveraged J is 125–153, p < 1e−28. His J uses a robust but not month-clustered weight, so it overstates somewhat. Our clustered J for the plain five-IV logit is still 62.9 on 4 df.
- **The fee K is not collinear with the age K.** Their within correlation is 0.009. Adding the age RC changes how the five instruments are combined, not a near-duplicate regressor.

## 3. (b) Are the elasticities of large, cheap funds reasonable?

**No: the largest, cheapest funds are still inelastic.**

The 15 Table 5 funds are the top 5 of BlackRock, Vanguard and State Street in the last month. Elasticities are from his archived `responses.npz`.

| Fund | Fee (%) | IV logit | Table 7 BLP | Table 10 BLP |
|---|---|---|---|---|
| iShares Core S&P 500 ETF | 0.03 | −0.16 | −0.53 | −0.42 |
| iShares Core MSCI EAFE ETF | 0.07 | −0.39 | −1.27 | −1.01 |
| iShares Core US Aggregate Bond ETF | 0.03 | −0.17 | −0.55 | −0.43 |
| iShares Russell 1000 Growth ETF | 0.18 | −1.01 | −3.19 | −2.61 |
| iShares Core S&P Mid-Cap ETF | 0.05 | −0.28 | −0.91 | −0.72 |
| SPDR S&P 500 ETF Trust | 0.09 | −0.49 | −1.57 | −1.24 |
| SPDR Gold Shares | 0.40 | −2.26 | −6.77 | −5.81 |
| Technology Select Sector SPDR | 0.08 | −0.45 | −1.45 | −1.16 |
| SPDR Portfolio S&P 500 ETF | 0.02 | −0.11 | −0.37 | −0.29 |
| Financial Select Sector SPDR | 0.08 | −0.45 | −1.45 | −1.16 |
| Vanguard Total Stock Market, Institutional Plus | 0.02 | −0.11 | −0.35 | −0.27 |
| Vanguard 500 Index, Admiral | 0.04 | −0.22 | −0.71 | −0.56 |
| Vanguard 500 Index, ETF | 0.03 | −0.16 | −0.53 | −0.42 |
| Vanguard Total Stock Market, ETF | 0.03 | −0.17 | −0.54 | −0.42 |
| Vanguard Total Stock Market, Admiral | 0.04 | −0.22 | −0.71 | −0.57 |
| **Funds with \|e\| > 1** | | **2 of 15** | **6 of 15** | **6 of 15** |

- **Why the big funds stay inelastic.** In his fits the RC barely bends the fee slope. In Table 7 the semi-elasticity e/p runs from −18.3 at fees ≤ 3 bp to −16.6 above 50 bp; in Table 10 it is flat at −14.5. So e ≈ α·p, and every fund cheaper than 1/|α| is inelastic: 5.5 bp in Table 7, 6.8 bp in Table 10.
- **Share of inelastic fund-months, Table 7 / Table 10:**
  - all fund-months, equally weighted: 15% / 18%;
  - all fund-months, AUM-weighted: 44% / 48%;
  - the last month, AUM-weighted: 54% / 58%.
- **The mean elasticity hides this.** The headline −4.19 (Table 7) is an equal-weighted mean over many small, expensive funds. The AUM-weighted mean is −2.09.
- **The larger elasticities come from IV1, not from the RC.**
  - IV0 alone gives a fee slope of −5.67 (F 40).
  - IV1 alone gives −17.25 (F 343). IV1 is the count of rivals within 10 bp of the fund's own lagged fee.
  - The plain five-IV logit gives −17.9, the same as the Table 7 mean slope.
  - IV1 is built from the fund's own lagged fee. Its exclusion is the assumption the elasticity level rests on.
- **Our recommended spec does about as well.** It gives 7 of 15 funds with |e| > 1. The cheap slope of −28.8 moves the threshold down to 3.5 bp.

**Is |e| > 1 required?** Only under Bertrand-type pricing.

- For a single-product fund with constant marginal cost and fee revenue only, the first-order condition is the Lerner rule (p − mc)/p = 1/|e|. So |e| < 1 means mc < 0. A fund facing |e| < 1 would gain by raising its fee.
- **Multi-product families make the requirement stronger.** Vanguard sells the Admiral, ETF and Institutional classes of the same portfolio. Internalizing cannibalization raises the markup, so own elasticities must be even larger.
- **It does not bind under PC.** The markup is zero, so costs equal fees whatever the elasticity. That is why his negative-MC share is 0 under PC but 27% (Table 7) and 34% (Table 10) under Bertrand. The inelastic big funds are part of why Bertrand is rejected, so the PC result for passive funds is conditional on this demand curve.
- **Other revenue relaxes it.** Securities-lending income lowers effective cost (see `NOTE_seclending_MC_bounds.md`).
- **Static elasticities understate long-run ones.** Shares are AUM stocks, and most AUM does not re-optimize in a given month. A monthly static model therefore understates the elasticity relevant for pricing.

## 4. "One coefficient cannot fit both": what it means, and a correction

**The idea.** With one normal fee RC, BLP is approximately a linear IV regression of ln(s/s₀) on the fee and K = p(p/2 − e_t), where e_t is the share-weighted mean fee in month t and the coefficient on K is σ². Within a fund, K varies through two channels:

- **Own-fee channel, p̄·p̃:** a fee cut matters more for cheap funds. σ² > 0 predicts that cheap funds' demand is steeper.
- **Market-position channel, −p̄·ẽ:** as the market gets cheaper (e_t fell from 0.20 to 0.08), σ² > 0 predicts that expensive funds hold up better than logit says. Their remaining investors are the fee-insensitive ones.

The RC forces one σ² on both channels.

- **In our data:**
  - The own-fee channel alone gives σ² > 0: fee × launch fee +92.9 (20.0); p²/2 +99 (51).
  - The full K gives σ² < 0 with every instrument set: −51 to −266.
  - Expensive funds lost share faster than their own fees explain. The market-position channel reads that as a negative σ².
- **On Danny's data with his IVs:** both channels are negative but imprecise: p²/2 −56.8 (31.2) and −p·e_t −13.3 (8.3). The positive Table 7 σ² appears only in the overidentified five-IV combination.

A normal RC cannot have σ² < 0. When the data want a negative value, the estimator stops at σ ≈ 0 with a positive criterion: the "wrong-sign case" in Section 4 of the explainer.

**Correction to the explainer page.** It said "the 0.049 in Danny's five-instrument fit". That number is his fee + age fit (Table 8); Table 10 gives 0.040. His fee-only five-IV fit (Table 7) gives σ = 1.875 (0.367), which is away from zero but fragile, as shown in §2. The page is now corrected (25 Nov).

**How to solve it, and what does not work:**

| Approach | Result |
|---|---|
| Fund-specific linear trends, to remove the secular move to cheap funds | **Does not work.** σ² stays negative: −28.4 (8.4). The fee slope collapses to −1.3 (2.0) because fees trend within fund. |
| Month × cheap fixed effects | **Does not work.** σ² = −49.4 (15.4). |
| Month × launch-fee-quintile fixed effects | Absorbs the variation; nothing is identified. |
| Sign-constrained (lognormal) RC | **Does not work** (run 25 Nov; explainer Section 10). *Our data, Z and Z × cheap:* unconstrained logit gives fee coefficient +14.85 (criterion 354.8), and the normal RC stops at mean +14.85, σ 0.216 (354.7), so demand slopes up everywhere. With every coefficient forced negative, the fit improves as fee sensitivity goes to zero: logit criterion 891 at −10, 654 at −3.7, 546 at 0. All 15 lognormal points with σ > 0 are above 546, with a positive π gradient. The best path (σ up to 4, median coefficient → 0) falls 554 → 547 toward 546, never below; mean elasticity there is −0.02. *Danny's data, five IVs:* the constraint does not bind. His Table 7 coefficient N(−18.5, 2.24²) is negative for every investor; the matched lognormal (σ 0.120, π 2.912) gives 101.7 vs his 100.87, with the same 15-fund elasticities (largest gap 0.07). In Tables 8 and 10 the corner is zero dispersion, which a lognormal shares. |
| Drop the passive fee RC; keep age and return RCs | The honest reading of Danny's Tables 8 and 10. It removes the near-singular direction and costs nothing: the fit is the same. |
| Fee heterogeneity as product heterogeneity (our cheap × fee slope) | Fits the own-fee channel directly. It does not claim investor heterogeneity, which these data cannot separate from product differences. |
| Substitution evidence: diversion moments from certified liquidations | The real fix if investor-level fee heterogeneity is needed. When a fund exits, where does its AUM go: to near or far funds in fee? Danny already uses these exits as IV4; used as a moment, they measure substitution directly. Investor-type micro moments (institutional vs retail AUM by fee tier) would also work. |

## 5. Points worth raising with Danny

Ask Gene before sending.

1. Report J (or Hansen's test with a clustered weight) for Tables 7–10. Every column rejects.
2. Is Table 7's σ_fee = 1.875 robust to dropping any one instrument? In the linear version, every just-identified pair gives a negative σ².
3. The mean elasticity of −4 rests on IV1. It is built from the fund's own lagged fee; what is the argument for its exclusion?
4. For passive funds, fix σ_fee = 0 in Tables 8 and 10 rather than report 0.040 (24.3).
5. The largest funds (VOO, IVV, VTI, VFIAX) have |e| ≈ 0.4–0.7. PC conduct is consistent with that, but the Bertrand rejection partly reflects it.
6. A lognormal (sign-constrained) fee RC is not a fix. In Table 7 the constraint never binds: the lognormal matched to his coefficient gives criterion 101.7 vs 100.87 and the same elasticities. In Tables 8 and 10 the fee RC is at zero dispersion, which a lognormal shares.
