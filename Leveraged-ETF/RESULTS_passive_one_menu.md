# Passive funds as one menu: options for the fee random coefficient

25 Nov 2026. Mutual-fund classes and ETFs pooled, **one fee coefficient**, no vehicle-specific slope or month
effect. Danny's Tables 7–10 package (98,110 passive fund-months), read without running his code. Linear
(Salanié–Wolak) screens: 2SLS with K = p(p/2 − e_t), whose coefficient is σ²; fund fixed effects, his controls,
his five instruments, standard errors clustered by month. Fees in percentage points. Not sent to Danny.

Code: `code/explore/step51_one_menu.py`, `step52_one_menu_followup.py`, `step49_access_blp.py` (spec `T7-lag`).
Output: `logs/explore/step51.log`, `step52.log` and the matching CSVs.
The split-sample results that led here are in `RESULTS_passive_access_spec.md`.

## 1. Summary

- **The pooled fee slope is not the problem.** It is negative under every structure tried and with every strong
  instrument alone.
- **The fee random coefficient is.** In the static model σ² is positive only because of IV2, which moves like an
  ETF-versus-mutual-fund time trend. Without IV2, or with an ETF taste trend, σ² is negative.
- **Candidate: Table 7 plus the lagged share in mean utility (inertia).** It is the only version where the
  instruments agree with each other (J 7.1 on 3 df, p = 0.07; every static version gives 23 or more), the fee
  slope is negative for each instrument, σ² is positive whichever instrument is dropped, and mutual-fund rows
  alone no longer give a positive slope.
- **Open issues with the candidate:** σ² is only marginally significant; the long-run magnitudes depend on a lag
  coefficient close to one; markups need a long-run elasticity. The BLP estimate is running.

## 2. The pooled fee slope (logit, static)

| Month effects | Fee slope |
|---|---|
| Month (Table 7) | −17.9 (0.9) |
| Month + ETF × trend | −11.7 (0.7) |
| Month × asset class (his 8 classes) | −13.0 (0.7) |
| Month × benchmark index | −15.0 (1.0) |

One instrument at a time, month effects: IV0 −5.7 (1.1); IV1 −17.2 (1.1); IV2 −28.2 (2.5); IV4 −15.9 (1.6);
IV3 has little power (F 5.7). For reference, rows split by vehicle give +4.4 (mutual funds) and −13.6 (ETFs).

## 3. σ² in the static model depends on IV2

IV2 is the count of other-family, same-vehicle funds in other asset classes.

| Month effects | σ², all five IVs | J | σ² without IV2 | J |
|---|---|---|---|---|
| Month (Table 7) | +3.1 (1.5) | 60.7 on 3 | −17.1 (3.9) | 23.0 on 2 |
| Month × asset class | +20.2 (1.3) | 144.9 on 3 | −16.0 (2.9) | 9.0 on 2 |
| Month × benchmark | +42.5 (4.6) | 143.6 on 3 | −35.4 (6.0) | 4.7 on 2 |
| Month + ETF × trend | −15.3 (4.8) | 116.0 on 3 | | |
| Month × asset class + ETF × year | −46.4 (5.6) | 49.5 on 3 | | |

IV0 with IV1, and IV0 with IV4, give a negative σ² under all three structures (−12 to −34).

## 4. Options that do not help

| Option | Result |
|---|---|
| Random coefficient on the vehicle (ETF dummy), with or without covariance with the fee | Its variance is negative: −4.6 (0.6) with month effects, −9.6 (0.5) with month × asset class. It picks up a trend. |
| Fee × broad-index fund | Interaction −0.8 (0.4); σ² +1.3 (1.8). |
| Fund-specific linear trends | Fee slope −5.7 (0.7); σ² −28.3 (8.4); mutual-fund rows alone +2.3 (0.4). |
| Fee × trend (fee sensitivity rising over time) | σ² +62.2 (5.5), positive whichever instrument is dropped (+18 to +125). But J is 147.5 on 7, σ² falls to +6.4 (2.1) with an ETF trend and to −13.4 (3.0) with month × asset class + ETF × year, and mutual-fund rows alone give a slope of +5.7 and σ² of −23.7. |

## 5. Candidate: inertia

y_t = ρ·y_{t−1} + fee terms + controls + fund and month effects, where y is the log share ratio. 96,499 fund-months.

| | Month effects | Month × asset class |
|---|---|---|
| Lag coefficient ρ | 0.983 (0.002) | 0.984 (0.002) |
| Fee slope, per month | −0.47 (0.12) | −0.42 (0.10) |
| σ², per month | +0.67 (0.26) | +0.88 (0.19) |
| Long-run fee slope, slope / (1 − ρ) | −27.0 | −26.5 |
| Long-run σ² | +38.6 | +55.7 |
| J | 7.1 on 3 (p = 0.07) | 25.4 on 3 |
| Logit (no K): slope; J | −0.40 (0.11); 11.0 on 4 | −0.26 (0.08); 39.7 on 4 |

Robustness, month effects:

| Check | Result |
|---|---|
| Fee slope, one instrument at a time | IV0 −0.55 (0.19); IV1 −0.20 (0.13); IV2 −1.18 (0.38); IV4 −0.79 (0.40). All negative. |
| σ², one instrument dropped | +0.78, +0.43, +0.45, +0.63, +0.73. All positive; t from 1.0 to 2.9. |
| σ², IV0 + one other | IV1 +0.43 (0.26); IV2 +1.38 (0.88); IV4 −0.30 (0.58). None significantly negative. |
| With the age term | σ² +0.49 (0.26); age +0.02 (0.02); J 5.3 on 2. |
| With an ETF trend | σ² +0.49 (0.34); the trend coefficient is zero. |
| K split | Own fee −0.59 (0.94); market position +0.32 (0.29). Neither is significant alone. |
| Lag instrumented with the second lag | ρ 0.981; slope −0.50 (0.11); σ² +0.68 (0.26). |
| Mutual-fund rows alone | −0.11 (0.08); with IV0 alone −0.24 (0.07). With month × asset class: −0.11 (0.05), J 6.8 on 4. |
| ETF rows alone | −0.18 (0.11). With month × asset class: −0.30 (0.11), J 0.8 on 4. |

ρ imposed, month effects:

| ρ | Fee slope | σ² | J on 3 | Long-run slope |
|---|---|---|---|---|
| 0.95 | −1.02 (0.10) | +0.82 (0.27) | 20.5 | −20 |
| 0.98 | −0.51 (0.10) | +0.70 (0.26) | 7.5 | −25 |
| 0.99 | −0.34 (0.10) | +0.66 (0.26) | 6.6 | −34 |
| 1.00 | −0.17 (0.10) | +0.62 (0.26) | 7.8 | not defined |

## 6. Caveats on the candidate

1. **Long-run magnitudes.** They divide by 1 − ρ ≈ 0.017. With fund effects and a lagged dependent variable, ρ is
   biased down by roughly 2/T, the same order. If ρ is one, the fee moves the growth of a fund's share and there
   is no long-run level. The sign results do not depend on this; the sizes do.
2. **σ² is modest.** t = 2.6 with all five instruments; 1.5 to 1.9 with the age term or an ETF trend. With month ×
   asset class effects it comes from the market-position part of K, not from own-fee curvature.
3. **Markups.** The monthly elasticity is about −0.1. A static pricing condition needs the long-run elasticity,
   which carries caveat 1.
4. **The model is no longer static.** Lagged share in mean utility is a reduced form for investors who re-optimise
   rarely (about 2% of assets a month).

## 7. Next steps

- BLP estimate of `T7-lag` (running): σ, its standard error, J, share of investors with a positive coefficient.
- A check on ρ that is free of the fixed-effect bias (first differences with lagged instruments).
- If the inertia version is adopted, the same change for the leveraged sample.
