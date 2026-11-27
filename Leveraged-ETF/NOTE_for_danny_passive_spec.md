# Passive (1x) demand: what we explored after your 24 and 25 November packages, and where we ended up

For Danny, from Gene. 27 November 2026.

## Summary

- We used your packages as data only: the prepared passive sample (98,110 fund-months), your five instruments, your
  3,000 draws and your instrument input panels. We did not run your code. Our code reproduces your Table 7
  criterion, your IV1, IV2 and IV4 exactly, and your column (4) estimates.
- **Where we ended up.** For the main passive column we would use a static model with a random coefficient on log
  fund age and **none on the fee** (your column 4 with the fee random coefficient removed). A model with last
  month's share added gives a positive fee random coefficient with your instruments, but it disappears once rival
  repricing is taken out of IV1 and IV4, so we treat it as an extension only.
- **Why.** The fee random coefficient in Table 7 changes sign under four changes that should not matter. The fee
  slope and the age coefficient do not.
- **One instrument check we would like your view on.** Matching rivals in IV1 and IV4 on each fund's fee at entry
  instead of last month's fee, so the counts move with entry and exit and not with rival repricing. The fee slope
  and the age coefficient survive it; the fee random coefficient does not.

Details and hover definitions are in Section 11 of the identification page
(https://claude.ai/artifact/L5oCqTHiS5zzx4UD4V7jWe; Gene needs to share it with you). Fees are in percentage
points; standard errors are clustered by month.

## 1. The two specifications

| | B: static (main) | A: partial adjustment (extension) |
|---|---|---|
| Random coefficient on | log fund age | fee |
| Mean utility | fee, tracking error, past return, log age | same, plus last month's log share ratio |
| Fixed effects | fund, month | fund, month |
| Instruments | your IV0 to IV4 | your IV0 to IV4 |
| Fund-months | 98,110 | 96,499 |

Full BLP, two-step GMM, your draws. We report a month-clustered second-step weight as the main results, because it
matches the clustered standard errors; your robust-weight convention is the last block.

| | B: static | A: partial adjustment |
|---|---|---|
| **Month-clustered weight** | | |
| Mean fee coefficient | −16.16 (0.94) | −0.40 (0.11) per month |
| Random-coefficient SD | age 1.23 (0.16) | fee 0.66 (0.16) per month |
| Lag coefficient | | 0.983 (0.002) |
| Own elasticity, equal-month mean | −3.91 | −0.07 per month |
| Own elasticity, AUM-weighted | −1.91 | −0.04 per month; −2.32 long-run |
| J on 3 df | 28.9 (p < 0.001) | 6.8 (p = 0.08) |
| **Robust weight (your convention)** | | |
| Mean fee coefficient | −16.11 (0.95) | −0.45 (0.11) per month |
| Random-coefficient SD | age 1.42 (0.19) | fee 0.77 (0.16) per month |
| J on 3 df | 102.3 (p < 0.001) | 31.7 (p < 0.001) |

B with the robust weight is your column (4) to three decimals (fee −16.11, age SD 1.42, elasticity −3.90, J 102.3),
because your fee SD there is 0.05.

## 2. How we got there

Each step below is one question, what we ran, and what it ruled in or out. "σ²" is the coefficient on the
Salanié–Wolak term K = p(p/2 − e) in a linear IV regression with fund and month effects; it estimates the variance
of the random coefficient and runs in seconds, so we used it for the checks. Headline numbers are from the full BLP.

**Step 1. Is the fee random coefficient in Table 7 stable?** No.

| Change to Table 7 | Fee σ² (linear screen; Table 7 itself: +3.1 (1.5)) |
|---|---|
| Drop IV2 | −17.1 (3.9) |
| Add an ETF taste trend | −15.3 (4.8) |
| Add the age term | −12.7 (3.0); in your BLP the fee SD goes to 0.05 (columns 4 and 6) |
| Widen the IV1/IV4 fee band from 10 bp to 12 bp | −1.6 (1.6); +1.3 at 11 bp, −3.1 at 15 bp |

IV2 counts same-vehicle funds in other asset classes, so it moves like an ETF-versus-mutual-fund time trend. The
positive σ² rests on it.

**Step 2. Does a sign constraint help?** No. In Table 7 a lognormal with the same mean and SD gives the same
elasticities, because your normal coefficient is already eight SDs below zero. Where the fee SD is at zero
(columns 4 and 6) a lognormal has the same corner.

**Step 3. Where does the problem come from?** From the mutual-fund classes.

| Rows | Fee slope (logit, your five IVs) | Fee σ² when K is added |
|---|---|---|
| ETFs only | −13.6 (1.0) | +116 (23), weakly identified |
| Mutual-fund classes only | +4.4 (0.6) | −53 (7) |
| Pooled (Table 7) | −17.9 (0.9) | +3.1 (1.5) |

We tried separate fee slopes by access type (using a corrected, time-invariant CRSP flag) and by vehicle. The
retail and institutional slopes were not stable. Gene's view is that mutual funds and ETFs are one menu, so
everything after this point pools them with one fee coefficient.

**Step 4. Can a static one-menu model carry a fee random coefficient?** We found none that does. Month × asset
class or month × benchmark effects, a random coefficient on the vehicle, fee × broad-index, fund-specific trends
and fee × trend each fail the checks of step 1 or give a negative variance.

**Step 5. What does hold in the static model?** The mean fee slope, and the age random coefficient.

| Check (linear screen: age K, no fee K) | Fee slope | Age σ² |
|---|---|---|
| Baseline | −15.7 (1.0) | +0.97 (0.14) |
| One instrument dropped: IV0, IV1, IV2, IV3, IV4 | −17.2, −11.2, −16.4, −15.4, −16.0 | +0.75, +1.21, +4.62, +0.95, +0.97 |
| Fee band 8, 12, 15 bp | −15.9, −18.6, −18.6 | +0.99, +0.83, +0.81 |
| ETF taste trend added | −13.6 (1.0) | +1.80 (0.30) |
| Before 2019; from 2019 | −14.8 (1.6); −5.9 (1.3) | +0.97 (0.15); +0.62 (0.45) |

That is specification B.

**Step 6. Does inertia change the picture?** Yes, for the fee random coefficient. Adding last month's log share
ratio (coefficient 0.983) gives:

| Check (linear screen with the lag) | Fee slope, per month | Fee σ², per month |
|---|---|---|
| Baseline | −0.47 (0.12) | +0.67 (0.26) |
| One instrument dropped: IV0, IV1, IV2, IV3, IV4 | −0.53, −0.64, −0.41, −0.47, −0.40 | +0.78, +0.43, +0.45, +0.63, +0.73 |
| Fee band 6 to 20 bp | −0.44 to −0.66 | +0.43 to +0.70 |
| Mutual-fund rows alone; ETF rows alone | −0.11 (0.08); −0.18 (0.11) | |

That is specification A. It is an extension and not the main column because:
- The adjustment speed is not pinned down. The lag coefficient is 0.983 raw, 0.987 for funds with at least 170
  months, and 1.00 after a half-panel jackknife. Long-run magnitudes divide by one minus it: the long-run fee slope
  is −20, −25 and −34 at 0.95, 0.98 and 0.99.
- Read literally, about 27% of investors get a positive fee coefficient. A lognormal coefficient fits better on a grid
  (one-step criterion 0.154 against 0.172); we have not run the full search.
- From 2019 the fee slope is positive but insignificant.

**Step 7. Your 25 November package.** The passive sample, instruments and fits are identical to 24 November; the
new instruments are for the leveraged market. We applied the same redesign to the passive counts (no fee or
tracking matching, binary access). It does not carry over: the rival count's first-stage F falls from 368 to about
15, the static fee σ² turns negative and A's fee slope goes to zero. IV1 with only the fee matching gives a fee
slope of −16.1 (F 740), so the fee band is what makes IV1 work in the passive market.

**Step 8. The fee band uses rival fees. Can that be avoided?** Largely, yes. IV1 and IV4 move when rivals reprice
into or out of the 10 bp band, and rivals reprice in response to demand. Following our earlier "cheap" definition,
we matched rivals on each fund's fee in its first month in the raw index file (fixed per fund; 51% of funds entered
before 2010), so the counts change only with entry and exit.

| IV1 and IV4 matched on | Static fee slope | Static fee σ² | B: age σ² | A: fee slope | A: fee σ² |
|---|---|---|---|---|---|
| Last month's fee, 10 bp (yours) | −17.9 (0.9) | +3.1 (1.5) | +0.97 (0.14) | −0.40 (0.11) | +0.67 (0.26) |
| Entry fee, 10 bp | −21.8 (1.5) | −28.4 (5.0) | +0.82 (0.18) | −0.74 (0.20) | +0.47 (0.50) |
| Entry-fee percentile, 10 points | −24.1 (1.7) | −28.4 (5.2) | +0.68 (0.21) | −0.79 (0.21) | +0.47 (0.53) |
| Same cheap tier (20th percentile at entry) | −21.4 (1.5) | −36.5 (8.9) | +1.03 (0.16) | −0.73 (0.22) | +0.60 (0.69) |

Full BLP with the entry-percentile version, month-clustered weight:

| | B: static | A: partial adjustment |
|---|---|---|
| Mean fee coefficient | −19.96 (2.09) | −0.62 (0.27) per month |
| Random-coefficient SD | age 0.61 (0.24) | fee 0.10 (1.69): the lower end of the search range |
| Lag coefficient | | 0.980 (0.004) |
| Own elasticity, AUM-weighted | −2.36 | −0.07 per month; −3.58 long-run |
| J on 3 df | 137.2 (p < 0.001) | 7.2 (p = 0.07) |

- The mean fee slope does not depend on rival repricing.
- B survives in sign and significance under all eight entry-fee definitions we tried (the BLP age SD falls from
  1.23 to 0.61).
- The static fee random coefficient is clearly negative once rival repricing is removed.
- A's fee random coefficient does not survive: in the screen its variance is positive but not distinguishable
  from zero, and in the full BLP the fee SD goes to the lower end of the search range. A reduces to a logit with
  inertia.
- Costs: the entry-matched IV1 is weaker on its own (first-stage F of 17 to 29, against 343); with these
  instruments B's age σ² turns negative if IV0 is also dropped; and B's J rises from 28.9 to 137.2.
  Entry and exit respond to segment demand too, so we would keep your instruments in the reported column and use
  the entry-fee version as a robustness column.

## 3. What this leaves open

- **Over-identification.** J rejects for B under either weight. A passes only with the month-clustered weight.
- **Pooling.** Within mutual funds alone, static demand slopes up, and within either vehicle alone the age σ² is
  negative. B is right only if the two vehicles are one menu.
- **Inelastic large funds.** In B, 48% of assets are in funds with an own elasticity below 1 in absolute value
  (9 of the 15 largest), as in Table 7.
- **After 2019** the fee slope is smaller in both models.

## 4. Questions for you

1. Why did the fee and tracking matching stay in the passive IV1 and IV4 when you removed it from the leveraged
   ones? Our tests say the passive results need the band; is there an exclusion argument for it that we are missing?
2. Could you rebuild IV1 and IV4 with entry-fee matching inside your pipeline, as a robustness column? You have the full roster and
   certification; we used our raw index file for the entry fees (all 1,063 classes and 151 of 153 exits matched).
3. Are you comfortable with a month-clustered second-step weight as the reported one?
4. If A is reported, should the leveraged sample get the same lagged-share term?

## 5. Where things are

Branch `leveraged-etf-replication`, folder `Leveraged-ETF/`.
- Reports: `RESULTS_passive_final_specs.md` (final), `RESULTS_passive_one_menu.md`, `RESULTS_passive_access_spec.md`.
- Code: `code/explore/step48` to `step60`. Final BLP runs: `step58_final_blp.py`; entry-fee instruments:
  `step60_entry_fee_band.py`.
- Output: `logs/explore/` (coefficients and logs only; no data files).
