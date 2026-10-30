# Coauthor's CRSP cheap-fund tables (`table2_cheap_crsp.pdf`, 30 Oct 2026) compared with our results

## 1. What the coauthor did

- **Same samples and specification as Table 2.** 108,300 index fund-months and 15,401 leveraged Bull fund-months. The paper's Hausman IV (and Hausman × cheap). Columns OLS, IV logit, BLP 1 RC, BLP 3 RC. SE clustered by month. The cheap indicator is fixed per fund.
- **Twelve cheap definitions from CRSP:** 10th, 20th and 50th percentiles × four reference groups (funds *founded* in the prior 1 or 5 years, funds *existing* in the prior 1 or 5 years).
    - The fund's launch fee is the first CRSP `exp_ratio` dated on or after `first_offer_dt`.
    - The fund is cheap if that fee is **strictly below** the reference group's percentile.
    - The reference universe is **all CRSP share classes, including active and delisted funds**, equally weighted.
    - Missing fee or missing history counts as not cheap (6,729 fund-months have a missing fee).
- **Additions we did not have:** conduct testing (PC, B0–B65) and negative-marginal-cost shares at estimated cost scales, plus detailed numerical diagnostics (rank, local-information gate, counts of upward-sloping responses).

## 2. Headline numbers (Panel A, IV logit, the paper's Hausman IV)

| Definition | Cheap share of fund-months | Non-cheap (SE) | Cheap total | Avg e | Demand signs valid |
|---|---|---|---|---|---|
| founded 1y, 10th | 0.58 | +1.09 (1.53) | −16.2 | −1.22 | no |
| founded 5y, 10th | 0.55 | −3.19 (2.03) | −22.1 | −2.35 | yes |
| existing 1y, 10th | 0.61 | −5.42 (2.65) | −24.2 | −3.24 | yes |
| existing 5y, 10th | 0.61 | −2.49 (2.34) | −22.0 | −2.53 | yes |
| founded 1y / 5y, 20th | 0.75 / 0.77 | **+5.85 / +21.6** | −14.9 / −6.3 | −1.35 / **+1.80** | no |
| existing 1y / 5y, 20th | 0.79 / 0.81 | **+13.0 / +9.2** | −13.4 / −14.1 | −0.50 / −1.39 | no |
| 50th (four groups) | 0.88–0.91 | −8.8 to −79 (very imprecise) | −6.8 to −29 | | interaction ≈ 0 or positive |
| *Ours: entry tier, 20th, new IV (97,429 rows)* | *about 42% of funds* | *−6.12 (0.85)* | *−28.8* | *−2.68* | *yes* |
| *Ours: entry tier, 30th, paper's IV* | *50% of funds* | *−3.4 (2.6)* | *−22.3* | *−2.29* | *yes* |
| *Ours: entry tier, 20th, paper's IV* | *38% of funds* | *−8.13 (4.32)* | *−40.8* | *−3.93* | *yes* |

**BLP 1 RC.**
- At the 10th percentile: σ ≈ 1.7–2.6, non-cheap −1.8 to −4.1, cheap total −22.7 to −26.4.
- Most BLP columns fail their local-information gate or show some upward-sloping responses.
- At the 20th percentile σ ≈ 0.026 and the non-cheap slope is positive (+2.4 to +5.5).

**Panel B (leveraged).**
- At the 10th and 20th percentiles there are 0–3 cheap funds, so the interaction cannot be estimated.
- At the 50th percentile the interaction is negative (IV logit cheap total −7.7 to −10.1).

## 3. Where it agrees with what we concluded

1. **The cheap-fund slope is steep and robust.** At every usable definition the cheap total is −14 to −24 in IV logit and −17 to −26 in BLP. That is the same order as ours with the new instrument (−24 to −29).
2. **The non-cheap slope is fragile with the paper's Hausman IV.** It turns positive at all four 20th-percentile definitions (+5.8 to +21.6), and in one 10th-percentile one. That matches our diagnosis: the paper's instrument barely moves non-cheap funds' fees (split-sample first-stage F 0.7–6). It also implies upward-sloping demand on the 93% of rows with a family identifier (+7.2).
3. **Their best rows match ours closely.** Their 10th-percentile definitions with valid demand signs make 55–61% of fund-months cheap. They give non-cheap −2.5 to −5.4 and cheap −22 to −24. Our entry tier at a comparable cheap share (30th percentile, 50% of funds) gives −3.4 / −22.3.
4. **When the cheap group is too broad, the rest slopes upward.** We found the same with our cutoffs: at the 40th and 50th percentiles the "rest" coefficient was +2.7 and +10.7. Their 20th-percentile definitions leave only the most expensive ~20% of fund-months as non-cheap.
5. **σ is not credibly identified.** Their BLP diagnostics flag local-information failures (including the benchmark Table 2 BLP columns), and the RC standard errors run into the hundreds in the 3-RC columns. We reached the same conclusion: a singular covariance in the exactly identified case, and σ going to 0 or 11 when overidentified.
6. **Leveraged funds: no interaction.** It is not estimable at the cutoffs we use, consistent with leaving Panel B unchanged.

## 4. Where it differs

1. **The percentile labels are not comparable.** Their reference universe is all CRSP share classes, including active funds, whose fees are much higher. So their "10th percentile" makes 55–61% of index fund-months cheap, against 20% under ours. Their 20th is about 75–81%. If the economic comparison is among index funds, the index-only reference (ours) is the natural one. Theirs measures "index-like fee" rather than "cheap among index funds".
2. **The instrument.** They use the paper's Hausman IV throughout. We showed that instrument is driven by the 7% of rows without a family identifier, and that the share-class-matched instrument (median fee of the family's same-share-class funds outside the fund's asset class) gives a precise negative non-cheap slope (first-stage F 167–262). Their positive non-cheap slopes are what we would expect from the paper's instrument. Re-running their definitions with the new instrument is the obvious next step: in `code/explore/new_iv.py`, swap in Z and Z × cheap as `demand_instruments0/1`.
3. **Launch-fee measurement.**
    - Their launch fee is the first CRSP fee record. That record lags the launch by more than a year for 9,573 fund-months, with a maximum of about 27 years. So for some funds the "launch fee" is a post-repricing fee, which biases the classification toward cheap.
    - Missing fees (6,729 fund-months) are coded not cheap, which puts unclassifiable funds in the non-cheap group.
    - Ours uses the fund's first month in the raw file (1994–2025). That is left-censored for funds launched before 1994, but it has no reporting-lag issue.
4. **Ties.** Their definition is strict (<); ours counts ties as cheap. This matters at fee points where many funds sit exactly at the percentile.
5. **What is reported.**
    - They add conduct tests and negative-MC shares at estimated cost scales. With a scale of 0.024, negative MC is close to 0 in the IV-logit columns, and PC is selected in most passive columns.
    - They do not report first-stage F, lead tests or the 15 Table 5 funds' elasticities. Those are our main checks of whether a specification answers the Table 5 question.

## 5. Suggested next steps for the two of you

- Re-run their four 10th-percentile definitions (and the 20th) with the share-class-matched Hausman IV. If the non-cheap slope turns negative and precise, as it did for us, the two approaches converge.
- Add an index-only reference universe to their CRSP construction (index funds founded or existing in the prior 1 or 5 years). That would make the percentiles comparable to ours.
- Run the definitions dropping the missing-fee rows instead of coding them not cheap, and flag funds whose first CRSP fee comes more than a year after launch.
- Report the first-stage F and the 15 Table 5 funds' elasticities for their preferred definition.
