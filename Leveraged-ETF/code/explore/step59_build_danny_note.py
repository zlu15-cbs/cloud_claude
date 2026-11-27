"""Write NOTE_for_danny_passive_spec.md from the result CSVs. python3 step59_build_danny_note.py RESULTS_DIR OUT_MD"""
import os, sys
import pandas as pd
from scipy.stats import chi2
R, OUT = sys.argv[1], sys.argv[2]
def csv(n):
    p = os.path.join(R, n)
    return pd.read_csv(p).iloc[0] if os.path.exists(p) else None
def f(r, k, nd=2): return 'pending' if r is None else f'{float(r[k]):.{nd}f}'.replace('-', '−')
def est(r, b, s, nd=2): return 'pending' if r is None else f'{f(r, b, nd)} ({f(r, s, nd).replace("−", "")})'
def J(r):
    if r is None: return 'pending'
    pv = chi2.sf(float(r['J']), 3)
    return f'{float(r["J"]):.1f} ({"p < 0.001" if pv < 0.001 else f"p = {pv:.2f}"})'
a2, a2c, ae = csv('step58_lag_step2_robust.csv'), csv('step58_lag_step2_clustered.csv'), csv('step58_lag_pct10_step2_clustered.csv')
b2, b2c, be = csv('step58_age_step2_robust.csv'), csv('step58_age_step2_clustered.csv'), csv('step58_age_pct10_step2_clustered.csv')
_p = os.path.join(R, 'step57_lag_lognormal.csv')
ln = pd.read_csv(_p) if os.path.exists(_p) else None
lntab = ''
if ln is not None:
    lntab = '| Fee coefficient | Mean | SD | Criterion |\n|---|---|---|---|\n' + ''.join(
        f'| {("Normal, no dispersion" if r.sd_coef < 0.01 else "Normal") if r.label.startswith("normal") else "Lognormal (negative for everyone)"} | {r.mean_coef:.2f} | {r.sd_coef:.2f} | {r.objective:.3f} |\n'.replace('-', '−')
        for r in pd.concat([ln[ln.label.str.startswith('normal')], ln[ln.label.str.startswith('lognormal')].sort_values('objective')]).itertuples())
md = f'''# Passive (1x) demand: what we explored after your 24 and 25 November packages, and where we ended up

For Danny, from Gene. 27 November 2026. Written up with Claude from our runs.
This note is self-contained: definitions are in section 2 and every table we rely on is in the note or its appendix.

## 1. Summary

- We used your packages as data only: the prepared passive sample (98,110 fund-months, 1,063 share classes, 177
  months), your five instruments, your 3,000 draws per month and your instrument input panels. We did not run your
  code. Our code reproduces your Table 7 criterion (100.87), your IV1, IV2 and IV4 exactly, and your column (4)
  estimates.
- **Where we ended up.** For the main passive column we would use a static model with a random coefficient on log
  fund age and **none on the fee**. That is your column (4) with the fee random coefficient removed (your estimate
  of it is 0.05, SE 20.5).
- **Why.** The fee random coefficient in Table 7 changes sign under four changes that should not matter: dropping
  IV2, adding an ETF taste trend, adding the age term, and widening the IV1/IV4 fee band from 10 to 12 bp. The fee
  slope and the age coefficient hold under all of them.
- **With last month's share added** (partial adjustment), the fee random coefficient is positive with your
  instruments, but it disappears once rival repricing is taken out of IV1 and IV4. We treat that model as an
  extension only.
- **One instrument check we would like your view on.** Matching rivals in IV1 and IV4 on each fund's fee at entry
  instead of last month's fee, so the counts move with entry and exit and not with rival repricing. The fee slope
  and the age coefficient survive it; the fee random coefficient does not.
- Four questions for you are in section 6.

## 2. Terms used in this note

| Term | Meaning |
|---|---|
| One menu | Mutual-fund classes and ETFs compete in the same market each month with one fee coefficient. No slope, month effect or trend is specific to either vehicle. This is Gene's maintained assumption. |
| B | Static model; random coefficient on log fund age; none on the fee. |
| A | B's mean utility plus last month's log share ratio; random coefficient on the fee instead of age. |
| Log share ratio | log(fund share) − log(outside share), the logit dependent variable. |
| Linear screen | 2SLS of the log share ratio on the fee and K terms, with fund and month effects, your controls and instruments. It approximates the BLP to second order and runs in seconds. We used it for robustness checks only; headline numbers are from the full BLP. |
| K and σ² | K = p(p/2 − e), with p the fund's characteristic and e its share-weighted market average (Salanié and Wolak). Its coefficient in the linear screen estimates σ², the variance of the random coefficient on p. A negative estimate means a normal random coefficient cannot fit. |
| Robust weight | Second-step GMM weight that allows unequal variances but treats fund-months as independent. Your package uses it. |
| Month-clustered weight | Second-step weight that also allows correlation across all funds within a month, matching the clustered standard errors. We report it as the main one. |
| J | Hansen's over-identification statistic (two-step criterion). All J values here have 3 degrees of freedom unless stated. |
| Long-run (model A) | If each month closes a fraction 1 − ρ of the gap to a target, the target's fee coefficient is the monthly one divided by 1 − ρ, and its SD the monthly SD divided by √(1 − ρ). ρ is the lag coefficient. |
| Fee band | Your IV1 and IV4 count rivals whose fee last month was within 10 bp of the fund's own fee last month. |
| Fee at entry | The fund's expense ratio in its first month in our raw index-fund file (1994 to 2025). Fixed per fund; 51% of your funds entered before January 2010. |
| Cheap | Our earlier classification: fee at entry at or below the 20th percentile of all index funds in that month. |

Fees are in percentage points. Standard errors, in parentheses, are clustered by month.

**Your instruments, as we understand them**

| IV | Definition | Incremental fee F (your Table 8) | Our note |
|---|---|---|---|
| IV0 | Same-family fee in other benchmarks and asset classes | 17.1 | The only one not built from rivals. Alone: fee slope −5.7 (1.1) static, −0.55 (0.19) per month in A |
| IV1 | Other-family rivals last month, same asset class and access, fee within 10 bp, tracking error within 0.02 | 348.3 | Moves when rivals reprice into or out of the band |
| IV2 | Other-family same-vehicle funds in other asset classes last month | 42.7 | Moves like an ETF-versus-mutual-fund trend |
| IV3 | Other-family share classes at most 12 months old, same asset class | 4.3 | Weak; dropping it changes little |
| IV4 | Certified rival liquidations over the previous 12 months, matched like IV1 | 88.9 | Same matching as IV1 |

## 3. The two specifications and their estimates

| | B: static (main) | A: partial adjustment (extension) |
|---|---|---|
| Random coefficient on | log fund age | fee |
| Mean utility | fee, tracking error, past return, log age | same, plus last month's log share ratio |
| Fixed effects | fund (share class), month | fund (share class), month |
| Instruments | your IV0 to IV4 | your IV0 to IV4 |
| Fund-months | 98,110 | 96,499 (each fund's first month has no lag) |
| Moments, parameters | 8, 5 | 9, 6 |

Full BLP, two-step GMM, your 3,000 draws per month.

| | B: static | A: partial adjustment |
|---|---|---|
| **Month-clustered weight (main)** | | |
| Mean fee coefficient | {est(b2c, 'b[prices]', 'se[prices]')} | {est(a2c, 'b[prices]', 'se[prices]')} per month |
| Random-coefficient SD | age {est(b2c, 'sigma_age', 'sigma_age_se')} | fee {est(a2c, 'sigma', 'sigma_se')} per month |
| Lag coefficient ρ | | {est(a2c, 'b[y_lag]', 'se[y_lag]', 3)} |
| Long-run mean fee coefficient, SD (at estimated ρ) | | {f(a2c, 'long_run_mean_fee_coef', 1)}, {f(a2c, 'long_run_sigma', 1)} |
| Own elasticity, equal-month mean | {f(b2c, 'mean_own_elasticity_equal_month')} | {f(a2c, 'mean_own_elasticity_equal_month')} per month |
| Own elasticity, AUM-weighted | {f(b2c, 'aum_weighted_elasticity')} | {f(a2c, 'aum_weighted_elasticity')} per month; {f(a2c, 'long_run_aum_weighted_elasticity')} long-run |
| Fund-months with upward-sloping demand | {100 * float(b2c['share_e_pos']):.1f}% | {100 * float(a2c['share_e_pos']):.1f}% |
| J on 3 df | {J(b2c)} | {J(a2c)} |
| **Robust weight (your convention)** | | |
| Mean fee coefficient | {est(b2, 'b[prices]', 'se[prices]')} | {est(a2, 'b[prices]', 'se[prices]')} per month |
| Random-coefficient SD | age {est(b2, 'sigma_age', 'sigma_age_se')} | fee {est(a2, 'sigma', 'sigma_se')} per month |
| J on 3 df | {J(b2)} | {J(a2)} |

- B with the robust weight is your column (4) to three decimals (fee −16.11, age SD 1.42, elasticity −3.90, J 102.3),
  because your fee SD there is 0.05.
- For reference, your column (3): fee −18.20 (0.92), fee SD 1.88 (0.37), elasticity −4.19, J 144.4.

## 4. How we got there

Each step is one question, what we ran, and what it ruled in or out.

**Step 1. Is the fee random coefficient in Table 7 stable?** No.

| Change to Table 7 | Fee σ² (linear screen; Table 7 itself: +3.1 (1.5)) |
|---|---|
| Drop IV2 | −17.1 (3.9) |
| Add an ETF taste trend | −15.3 (4.8) |
| Add the age term | −12.7 (3.0); in your BLP the fee SD goes to 0.05 (columns 4 and 6) |
| Widen the IV1/IV4 fee band from 10 bp to 12 bp | −1.6 (1.6); +1.3 at 11 bp, −3.1 at 15 bp (appendix A) |

Also: with IV0 plus one other instrument, σ² is −14.9 (3.8) with IV1, −57.4 (19.5) with IV3 and −12.8 (3.4) with
IV4. IV2 counts same-vehicle funds in other asset classes, so it moves like an ETF-versus-mutual-fund time trend.
The positive σ² rests on it.

**Step 2. Does a sign constraint help?** No. In Table 7 a lognormal with the same mean and SD gives the same
elasticities (largest gap 0.07 across the 15 Table 5 funds), because your normal coefficient is already eight SDs
below zero. Where the fee SD is at zero (columns 4 and 6) a lognormal has the same corner.

**Step 3. Where does the problem come from?** From the mutual-fund classes.

| Rows | Fee slope (logit, your five IVs) | Fee σ² when K is added |
|---|---|---|
| ETFs only | −13.6 (1.0) | +116 (23), weakly identified (first-stage F about 3) |
| Mutual-fund classes only | +4.4 (0.6) | −53 (7) |
| Pooled (Table 7) | −17.9 (0.9) | +3.1 (1.5) |

We tried separate fee slopes by access type, using a corrected, time-invariant CRSP flag (first record per class,
last value before 2019 for the 43 classes that flip, Admiral coded retail). The slopes were not stable: the
institutional slope is −28 when some first stages are pooled across segments and +13 when institutional classes
are estimated alone, and the BLP fee SD in that model is 2.3 (2.7). We dropped it. From here on mutual funds and
ETFs are one menu with one fee coefficient.

**Step 4. Can a static one-menu model carry a fee random coefficient?** We found none that does (appendix B).

**Step 5. What does hold in the static model?** The mean fee slope, and the age random coefficient.

| Check (linear screen: age K, no fee K) | Fee slope | Age σ² |
|---|---|---|
| Baseline | −15.7 (1.0) | +0.97 (0.14) |
| One instrument dropped: IV0, IV1, IV2, IV3, IV4 | −17.2, −11.2, −16.4, −15.4, −16.0 | +0.75, +1.21, +4.62, +0.95, +0.97 |
| Fee band 8, 12, 15 bp | −15.9, −18.6, −18.6 | +0.99, +0.83, +0.81 |
| ETF taste trend added | −13.6 (1.0) | +1.80 (0.30) |
| Before 2019; from 2019 | −14.8 (1.6); −5.9 (1.3) | +0.97 (0.15); +0.62 (0.45) |
| Fee slope, one instrument at a time (logit) | IV0 −5.7, IV1 −17.2, IV2 −28.2, IV4 −15.9 | |

That is specification B. We leave out the return random coefficient of your columns (5) and (6): its σ² turns
negative without IV3, and it makes the mean return coefficient negative, as your note points out.

**Step 6. Does inertia change the picture?** Yes, with your instruments. Adding last month's log share ratio
(coefficient 0.983) gives:

| Check (linear screen with the lag) | Fee slope, per month | Fee σ², per month |
|---|---|---|
| Baseline (J 7.1, month-clustered) | −0.47 (0.12) | +0.67 (0.26) |
| One instrument dropped: IV0, IV1, IV2, IV3, IV4 | −0.53, −0.64, −0.41, −0.47, −0.40 | +0.78, +0.43, +0.45, +0.63, +0.73 |
| Fee band 6 to 20 bp | −0.44 to −0.66 | +0.43 to +0.70 |
| ETF taste trend added | −0.41 (0.15) | +0.49 (0.34) |
| Age term added | −0.42 (0.11) | +0.49 (0.26) |
| Fee slope, one instrument at a time (logit) | IV0 −0.55, IV1 −0.20, IV2 −1.18, IV4 −0.79 | |
| Mutual-fund rows alone; ETF rows alone (logit) | −0.11 (0.08); −0.18 (0.11) | |
| Before 2019; from 2019 | −0.65 (0.22); +0.24 (0.32) | +1.35 (0.60); +3.3 (1.9) |

That is specification A. Two things it does that the static model does not: mutual-fund rows alone no longer give
upward-sloping demand, and J does not reject with the month-clustered weight. It is an extension and not the main
column because:
- The adjustment speed is not pinned down, so long-run magnitudes are not either (appendix C).
- Read literally, about 27% of investors get a positive fee coefficient. A lognormal coefficient fits better on a
  grid (appendix C); we have not run the full search.
- From 2019 the fee slope is positive but insignificant.
- Its fee random coefficient does not survive step 8.

**Step 7. Your 25 November package.** The passive sample, instruments and fits are identical to 24 November; the
new instruments are for the leveraged market. We applied the same redesign to the passive counts (no fee or
tracking matching, binary access). It does not carry over:

| Instrument set | Static fee slope | Static fee σ² | A: fee slope (with K) | A: fee σ² |
|---|---|---|---|---|
| Your five | −17.9 (0.9) | +3.1 (1.5) | −0.47 (0.12) | +0.67 (0.26) |
| Matching removed, three-way access | −14.2 (1.1) | −100 (31) | +0.64 (0.37) | +2.08 (0.69) |
| Matching removed, ETF / mutual-fund access | −7.5 (0.8) | −33 (14) | +0.26 (0.20) | +1.62 (0.44) |
| No access match | −3.0 (0.9) | −7.9 (1.3) | −0.04 (0.22) | +0.39 (0.24) |

| IV1 version, alone (static logit) | Fee slope | First-stage F |
|---|---|---|
| Yours (fee and tracking matching) | −15.4 (1.0) | 368 |
| Fee matching only | −16.1 (0.6) | 740 |
| Tracking matching only | −59 (15) | 15 |
| No matching | −140 (37) | 15 |

The fee band is what makes IV1 work in the passive market. IV1 is not a function of the fund's own lagged fee (a
cubic in it explains 1.5% of IV1 within fund and month); it moves when rivals' fees come within 10 bp.

**Step 8. The fee band uses rival fees. Can that be avoided?** Largely, but at a cost. Rivals reprice in response
to demand, so counts that move when rivals reprice can be correlated with the fund's own demand shock. Following
our "cheap" definition, we matched rivals on each fund's fee at entry, so the counts change only with entry and
exit. Everything else in IV1 and IV4 is as you built it. 74% of fund-months have a current fee within 10 bp of the
entry fee, and the entry-matched IV1 has a correlation of 0.85 with yours.

| IV1 and IV4 matched on | Static fee slope | Static fee σ² | B: age σ² | A: fee slope | A: fee σ² |
|---|---|---|---|---|---|
| Last month's fee, 10 bp (yours) | −17.9 (0.9) | +3.1 (1.5) | +0.97 (0.14) | −0.40 (0.11) | +0.67 (0.26) |
| Entry fee, 10 bp | −21.8 (1.5) | −28.4 (5.0) | +0.82 (0.18) | −0.74 (0.20) | +0.47 (0.50) |
| Entry-fee percentile, 10 points | −24.1 (1.7) | −28.4 (5.2) | +0.68 (0.21) | −0.79 (0.21) | +0.47 (0.53) |
| Same cheap tier | −21.4 (1.5) | −36.5 (8.9) | +1.03 (0.16) | −0.73 (0.22) | +0.60 (0.69) |

All eight versions are in appendix D. Full BLP with the entry-percentile version, month-clustered weight:

| | B: static | A: partial adjustment |
|---|---|---|
| Mean fee coefficient | {est(be, 'b[prices]', 'se[prices]')} | {est(ae, 'b[prices]', 'se[prices]')} per month |
| Random-coefficient SD | age {est(be, 'sigma_age', 'sigma_age_se')} | fee {est(ae, 'sigma', 'sigma_se')}: the lower end of the search range |
| Lag coefficient | | {est(ae, 'b[y_lag]', 'se[y_lag]', 3)} |
| Own elasticity, AUM-weighted | {f(be, 'aum_weighted_elasticity')} | {f(ae, 'aum_weighted_elasticity')} per month; {f(ae, 'long_run_aum_weighted_elasticity')} long-run |
| J on 3 df | {J(be)} | {J(ae)} |

- The mean fee slope does not depend on rival repricing.
- B survives in sign and significance under all eight entry-fee definitions (the BLP age SD falls from
  {f(b2c, 'sigma_age')} to {f(be, 'sigma_age')}).
- The static fee random coefficient is clearly negative once rival repricing is removed.
- A's fee random coefficient does not survive: in the screen its variance is positive but not distinguishable
  from zero, and in the full BLP the fee SD goes to the lower end of the search range. A reduces to a logit with
  inertia.
- Costs: the entry-matched IV1 is weaker on its own (first-stage F of 17 to 29, against 343); with these
  instruments B's age σ² turns negative if IV0 is also dropped; and B's J rises from {f(b2c, 'J', 1)} to {f(be, 'J', 1)}.
  Entry and exit respond to segment demand too. So we would keep your instruments in the reported column and use
  the entry-fee version as a robustness column.

## 5. What this leaves open

- **Over-identification.** J rejects for B under either weight. A passes only with the month-clustered weight.
- **Pooling.** Within mutual funds alone, static demand slopes up (+3.8 (1.3) with the age term), and within either
  vehicle alone the age σ² is negative (−4.0 and −0.6). B is right only if the two vehicles are one menu.
- **Inelastic large funds.** In B, 48% of assets are in funds with an own elasticity below 1 in absolute value
  (9 of the 15 largest), as in Table 7.
- **After 2019** the fee slope is smaller in both models.
- **Age coefficient in B.** Its SD and its mean are strongly correlated (the mean is 0.65 without the random
  coefficient and {f(b2c, 'b[log_product_fund_age]')} with it; smallest singular value {f(b2c, 'min_scaled_singular_value')}). The fee coefficient is unaffected.

## 6. Questions for you

1. Why did the fee and tracking matching stay in the passive IV1 and IV4 when you removed it from the leveraged
   ones? Our tests say the passive results need the band. Is there an exclusion argument for it that we are missing?
2. Could you rebuild IV1 and IV4 with entry-fee matching inside your pipeline, as a robustness column? You have the
   full roster and certification; we used our raw index file for the entry fees (all 1,063 classes and 151 of 153
   exits matched).
3. Are you comfortable with a month-clustered second-step weight as the reported one?
4. If A is reported, should the leveraged sample get the same lagged-share term?

## Appendix A. Fee band width (linear screens)

Your IV1 and IV4 rebuilt from your input panels at each width; tracking band and everything else unchanged.

| Fee band | Static fee σ² | A: fee σ² | A: fee slope | B: age σ² | B: fee slope |
|---|---|---|---|---|---|
| 6 bp | +4.4 (1.6) | +0.69 (0.26) | −0.44 (0.10) | | |
| 8 bp | +2.9 (1.6) | +0.70 (0.26) | −0.44 (0.11) | +0.99 (0.15) | −15.9 (0.9) |
| 9 bp | +3.3 (1.5) | +0.65 (0.26) | −0.47 (0.11) | | |
| 10 bp (yours) | +3.1 (1.5) | +0.67 (0.26) | −0.47 (0.12) | +0.97 (0.14) | −15.7 (1.0) |
| 11 bp | +1.3 (1.6) | +0.64 (0.26) | −0.48 (0.12) | | |
| 12 bp | −1.6 (1.6) | +0.59 (0.27) | −0.52 (0.13) | +0.83 (0.16) | −18.6 (1.2) |
| 15 bp | −3.1 (1.8) | +0.57 (0.27) | −0.54 (0.15) | +0.81 (0.17) | −18.6 (1.5) |
| 20 bp | −7.6 (2.1) | +0.43 (0.28) | −0.66 (0.17) | | |

99.5% of fees are on a whole basis point.

## Appendix B. Static one-menu alternatives for a fee random coefficient (linear screens)

| Alternative | Result |
|---|---|
| Month × asset class effects (your 8 classes) | Fee σ² +20.2 (1.3) with five IVs; −16.0 (2.9) without IV2 |
| Month × benchmark effects | +42.5 (4.6) with five IVs; −35.4 (6.0) without IV2 |
| Month effects + ETF taste trend | −15.3 (4.8) |
| Random coefficient on the vehicle (ETF dummy) | Its variance is negative: −4.6 (0.6); −9.6 (0.5) with month × asset class |
| Fee × broad-index fund | Interaction −0.8 (0.4); fee σ² +1.3 (1.8) |
| Fund-specific linear trends | Fee slope −5.7 (0.7); fee σ² −28.3 (8.4); mutual-fund rows alone +2.3 (0.4) |
| Fee × trend | Fee σ² +62.2 (5.5), but J 147.5 on 7 df, and +6.4 (2.1) once an ETF trend is added |

## Appendix C. Model A: adjustment speed and the sign of individual coefficients

| Estimate of the lag coefficient ρ | Value |
|---|---|
| Full sample | 0.983 (0.002) |
| Funds with at least 170 months | 0.987 (0.003) |
| Half-panel jackknife (Dhaene and Jochmans 2015), which removes the fixed-effect bias to first order | 1.000 |

| ρ imposed | Fee slope, per month | σ², per month | Long-run fee slope | Long-run SD |
|---|---|---|---|---|
| 0.95 | −1.02 (0.10) | +0.82 (0.27) | −20 | 4.0 |
| 0.98 | −0.51 (0.10) | +0.70 (0.26) | −25 | 5.9 |
| 0.99 | −0.34 (0.10) | +0.66 (0.26) | −34 | 8.1 |
| 1.00 | −0.17 (0.10) | +0.62 (0.26) | none | none |

- For ρ from 0.95 to 0.99 the long-run fee slope is the same order as the static −16 to −18. The data cannot rule
  out ρ = 1, where fees move the growth of a fund's share and there is no long-run level.
- The partial-adjustment model cannot be estimated directly at monthly frequency: at ρ = 0.983 the implied target
  shares put more than half the market in one fund in 159 of 176 months.

Sign-constrained fee coefficient in A (your instruments; one-step criterion, same weight, 500 draws per month; a
grid, not a search):

{lntab}
The lognormal fits better than the normal, and its criterion has an interior minimum near a mean of −0.5 and an SD
of 1.3 per month.

## Appendix D. Entry-fee matching, all versions (linear screens, month-clustered J)

| IV1 and IV4 matched on | Static fee slope | Static fee σ² | B: fee slope | B: age σ² | A: fee slope | A: fee σ² | A: J |
|---|---|---|---|---|---|---|---|
| Last month's fee, 10 bp (yours) | −17.9 (0.9) | +3.1 (1.5) | −15.7 (1.0) | +0.97 (0.14) | −0.40 (0.11) | +0.67 (0.26) | 7.1 |
| Entry fee, 5 bp | −22.4 (1.5) | −27.1 (5.0) | −15.5 (2.0) | +0.88 (0.19) | −0.76 (0.21) | +0.34 (0.55) | 11.3 |
| Entry fee, 10 bp | −21.8 (1.5) | −28.4 (5.0) | −15.7 (2.0) | +0.82 (0.18) | −0.74 (0.20) | +0.47 (0.50) | 10.3 |
| Entry fee, 15 bp | −21.9 (1.6) | −35.8 (6.8) | −15.5 (2.1) | +0.81 (0.19) | −0.76 (0.21) | +0.60 (0.58) | 10.1 |
| Entry fee, 20 bp | −21.6 (1.5) | −29.1 (5.9) | −15.3 (2.0) | +0.84 (0.18) | −0.77 (0.20) | +0.52 (0.53) | 10.3 |
| Entry percentile, 5 points | −22.6 (1.6) | −28.5 (5.6) | −16.3 (2.1) | +0.80 (0.19) | −0.77 (0.22) | +0.52 (0.60) | 9.0 |
| Entry percentile, 10 points | −24.1 (1.7) | −28.4 (5.2) | −19.0 (2.3) | +0.68 (0.21) | −0.79 (0.21) | +0.47 (0.53) | 8.8 |
| Entry percentile, 20 points | −23.3 (1.7) | −27.4 (5.7) | −17.0 (2.2) | +0.82 (0.19) | −0.84 (0.21) | +0.21 (0.55) | 9.3 |
| Same cheap tier (20th percentile) | −21.4 (1.5) | −36.5 (8.9) | −12.9 (1.9) | +1.03 (0.16) | −0.73 (0.22) | +0.60 (0.69) | 16.5 |

A's fee slope is from the logit with the lag; its σ² and J are from the version with K. The entry percentile is
the position of the entry fee among all index funds in the fund's entry month.

## Appendix E. How to reproduce

Branch `leveraged-etf-replication`, folder `Leveraged-ETF/`. Nothing below needs data beyond your package, except
the entry fees, which come from our raw index-fund file.

| Step | Script in `code/explore/` | What it does |
|---|---|---|
| Final BLP estimates of B and A | `step58_final_blp.py` | Resumable; both weights; `ENTRY=pct10` switches to the entry-fee instruments |
| Entry-fee instruments and their screens | `step60_entry_fee_band.py` | Rebuilds IV1 and IV4 from your input panels with entry-fee matching |
| Fee band width; lag-coefficient bias | `step54_band_and_rho.py` | |
| Period splits; static age-coefficient checks | `step55_final_checks.py` | |
| One-menu alternatives | `step51_one_menu.py`, `step52_one_menu_followup.py` | |
| Your leveraged redesign applied to passive | `step53_passive_iv_variants.py`, `step53b_own_lagged_fee.py` | Reproduces your IV1, IV2, IV4 exactly first |
| Sign-constrained coefficient in A | `step57_lag_lognormal.py` | |
| Access-type and vehicle splits | `step48` to `step50` | |

Output is in `logs/explore/` (coefficients and logs only; no data files). Longer write-ups:
`RESULTS_passive_final_specs.md`, `RESULTS_passive_one_menu.md`, `RESULTS_passive_access_spec.md`.
'''
open(OUT, 'w').write(md)
print('written;', md.count('pending'), 'pending;', len(md), 'chars')
