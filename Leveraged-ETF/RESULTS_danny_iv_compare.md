# Danny's share-class Hausman IV vs our instrument Z

Question (Gene): is Danny's uploaded `patch_hausman_share_class_exp_ratio_IV.csv` (31 Oct 2026, `Dropbox\P16_LeverageMKT\Data\source_intake\raw data\`) identical or almost identical to our share-class instrument Z?

**Answer: no.** The two are built with the same idea: the fees of same-family, same-share-class siblings. But Danny excludes only funds tracking the **same index**, while Z excludes the whole **asset class**. That one choice moves the benchmark's non-cheap price slope from −6.1 to −1.2.

Code: `code/explore/step30_compare_danny_iv.py`, `step30b_iv_decompose.py`. Logs: `logs/step30.log`, `logs/step30b.log`.

## 1. How Danny builds it

Source: `Dropbox\P16_LeverageMKT\Code\5_fund_market_data_for_Matteo_v6_nonlev_etf.R`, lines 208–310. That is the block that writes the patch file; it sits behind `if (FALSE)`, so it was run by hand. I reproduced his `IV3_exp_ratio_med` from this logic: **exact on all 540,570 rows** where both are defined (scratch script `repro_iv3.py`).

| | Ours: Z (`new_iv.py`) | Danny's: `IV3_*` |
|---|---|---|
| Donor universe | the raw index file (`nonLev_funds_product_month_level_v2_patched.csv`) | CRSP index-fund file `index_funds_preprocess_oct2026.csv` (1993–2025; 675,551 fund-months, the patch's exact key set) |
| Family | `firm_f_old` | `fund_family` |
| Share class | ETF; else name regex with word boundaries → inst / retail / other | ETF; else CRSP `inst_fund == "Y"` **or** name regex → inst; else CRSP `retail_fund == "Y"` or regex → retail; else other. The regex has no word boundaries, so e.g. "inst" and "class r" match more names. |
| **Excluded siblings** | **same asset class** (US eq., intl eq., bond, allocation, real assets) | **same tracked index** (`market_index`) |
| Donor filter | fee present | lagged TNA present (focal fee present) |
| Statistic | median | `_vw`: lagged-TNA weighted mean; `_med`: median |
| Funds with no family id | no value | **all pooled into one "family"**. 69,164 rows (10%) get a value from unrelated family-less funds (`fund_family` is missing and R reads it as ""). |

**Column problems in the patch file:**
- `IV3_exp_ratio_med`, `IV3_exp_ratio_adj_med` and `IV3_mgmt_fee_med` are **identical**. R lines 257–259 compute `median(other_exp_ratio)` three times, so only one median column exists.
- `IV3_exp_ratio_adj_vw = exp_ratio − mgmt_fee` mixes percent with basis points (the known unit pitfall; values down to −4,152). `IV3_mgmt_fee_vw` is in basis points.

## 2. How close the values are

| Rows | Pair | Both defined | Correlation | Exactly equal | Median \|diff\| (pp) |
|---|---|---|---|---|---|
| raw fund-months | Z vs `IV3_exp_ratio_med` | 462,341 | 0.921 | 23% | 0.030 |
| estimation sample (97,429) | Z vs `IV3_exp_ratio_med` | 97,402 | 0.895 | 26% | 0.020 |
| estimation sample | Z vs `IV3_exp_ratio_vw` | 97,402 | 0.860 | 1% | 0.044 |

## 3. Effect on the benchmark demand model

Price × cheap (raw-entry 20th percentile), fund + month FE, the same 97,402 rows; only the instrument changes.

| Instrument | corr with Z | Non-cheap (SE) | × cheap (SE) | Cheap total | F price / × cheap | Avg own e | e > 0 |
|---|---|---|---|---|---|---|---|
| **Z (ours)** | 1 | **−6.128 (0.842)** | −22.659 (0.796) | −28.79 | 168 / 197 | −2.69 | 0 |
| Z, but exclude same **index** only | 0.964 | −1.197 (0.704) | −19.498 (0.821) | −20.69 | 190 / 218 | −1.24 | 0 |
| Z, other asset class, **no share-class match** | 0.880 | +36.6 (10.5) | +1.0 | +37.6 | 9.9 / 12.7 | +9.66 | **100%** |
| Z, other index, no share-class match | 0.846 | +51.1 (27.7) | +12.4 | +63.5 | 2.9 / 3.2 | +14.0 | **100%** |
| **Danny `IV3_exp_ratio_med`** | 0.895 | **−0.006 (0.877)** | −18.119 (0.813) | −18.12 | 102 / 97 | −0.86 | 0 |
| Danny `IV3_exp_ratio_vw` | 0.860 | −1.067 (0.734) | −21.718 (0.768) | −22.78 | 185 / 333 | −1.31 | 0 |
| Danny `IV3_exp_ratio_adj_vw` / `IV3_mgmt_fee_vw` | | +6.5 / +6.3 | | | 18 / 19 | +0.6 | 53% |

**Reading.**
1. **The exclusion rule is the main driver.** Changing only "other asset class" to "other index" in our own construction takes the non-cheap slope from −6.1 to −1.2, close to Danny's −0.0 / −1.1. His other differences (CRSP universe, family id, share-class flags, the pooled family-less funds) account for the rest.
2. **The share-class match is essential.** Without it, demand slopes upward for every fund-month, under either exclusion rule.
3. **Why the asset-class exclusion matters (my inference).** Same-family siblings that track a different index in the same asset class compete for the same investors: an S&P 500 fund and a total-market fund, say, or two bond-index funds. A demand shock to the asset class can then move the sibling's fee and the focal fund's demand together, which violates exclusion and pushes the slope toward zero. Excluding the whole asset class removes those siblings. With Danny's rule, the non-cheap slope is near zero, and the fund-months the model treats as non-cheap (a cheap total of about −18 and the 47% of fund-months that are cheap) get almost no fee response.
    **Not supported by the lead tests** (`RESULTS_demand_grid.md` §3d). With CRSP share-class flags, the same-index and same-cluster versions have |lead t| ≤ 1.6, while the asset-class version reaches 4.3. Point 3 is a hypothesis the data do not confirm. The exclusion level is open.
4. **Test that would settle it (run in §3d of `RESULTS_demand_grid.md`; it does not settle it in Z's favour):** the lead tests (`step27`) and the split-sample first stage for the other-index variant. If its residual loads on future instrument values more than Z's does, that confirms the contamination story.

## 4. Danny's point: use CRSP's retail/institutional flags, not name keywords

Code `code/explore/step30d_shareclass_flags.py`, log `logs/step30d.log`. CRSP `inst_fund` / `retail_fund` were merged to the raw index file by (crsp_fundno, quarter).

**Coverage.** Every mutual-fund fund-month has a CRSP flag row, and in every year 1994–2025, 99–100% carry exactly one Y. Only 718 of 272,786 are N/N; none are Y/Y. So "flags first, keywords as fallback" is the same as flags only.

**Keywords disagree with the flags often** (mutual-fund rows):

| Keywords \ CRSP flags | inst | retail | other | All |
|---|---|---|---|---|
| inst | 86,605 | 18,068 | 95 | 104,768 |
| retail | 18,350 | 66,223 | 159 | 84,732 |
| other | 37,470 | 45,352 | 464 | 83,286 |

So 17% of keyword-institutional rows are CRSP-retail, 22% of keyword-retail rows are CRSP-institutional, and the 83,286 rows the keywords cannot place have a flag almost everywhere.

**Effect on Z and the benchmark** (asset-class exclusion unchanged; the 97,279 rows where every version is defined):

| Share-class rule in Z | corr with Z | Equal to Z | Non-cheap (SE) | × cheap (SE) | Cheap total | F price / × cheap | Avg e | e > 0 |
|---|---|---|---|---|---|---|---|---|
| Keywords (current Z) | 1 | 100% | −6.063 (0.858) | −22.628 (0.804) | −28.69 | 162 / 187 | −2.67 | 0 |
| **CRSP flags** | 0.926 | 68% | **−8.018 (1.306)** | −24.669 (1.263) | −32.69 | 121 / 114 | −3.28 | 0 |
| Danny's rule (flags or loose keywords) | 0.931 | 76% | −6.305 (1.333) | −23.145 (1.189) | −29.45 | 106 / 105 | −2.76 | 0 |

**Assessment.** Danny is right on measurement: the flags cover the whole sample and are the administrative classification, while the keywords misplace about a fifth of the rows they classify and leave 30% unclassified. The benchmark is robust to the switch: still downward-sloping everywhere, slightly steeper (−8.0 vs −6.1), first stage weaker but strong (F 114–121). The switch does not touch the real disagreement with his instrument, which is the exclusion rule (§3: same index vs same asset class).

**Web check: which classification matches reality?** Scratch script `sc_sample.py`; sample in `logs/sc_sample.csv`. It draws 32 mutual-fund classes, latest month ≥ 2015, from each keyword × flag cell, with the largest funds plus random ones. The ground truth is who may buy the class and its minimum, from prospectuses, SEC 497/497K filings and fund-data pages.

| Cell (keywords \| CRSP) | Funds checked | What they are (source) | Right |
|---|---|---|---|
| inst \| retail | 8 Vanguard **Admiral** classes (VFIAX, VTSAX, VBTLX, …) | $3,000 minimum since Nov 2018, sold to individuals (Vanguard 497 supplement, 2018) | **CRSP** |
| retail \| inst | Vanguard **Investor** classes VTSMX, VGTSX, VTBIX | closed to new investors from 2018–19; remaining shares held by Vanguard funds and certain institutions (same supplement). CRSP switches each from retail to inst at that date (VTSMX 2018, VTBIX 2019, VGTSX 2021). | **CRSP** (time-varying) |
| retail \| inst | Empower S&P 500 **Investor** (MXVIX) | sold only to insurance separate accounts, IRA custodians, plan sponsors and 529 programs (Empower 497K) | **CRSP** |
| retail \| inst | Principal **R-3 / R-2** (PMFMX, PINEX) | retirement-plan classes (Principal 497) | **CRSP**: keyword "class r" wrongly makes them retail |
| retail \| inst | TIAA-CREF **Advisor** (TELCX); Nationwide **Service** (NDMSX) | sold through intermediaries, 529s and insurance accounts (TIAA 485BPOS); Nationwide not verified | ambiguous |
| other \| inst | JPMorgan 100% Treasury MM **Capital** (CJTXX) | $50 million minimum | **CRSP** (also a money-market fund in the index sample; see below) |
| other \| inst | Fidelity **Series** index funds (FCFMX, FSGEX); PNC R4; Nuveen R3; Wells Fargo **Administrator** | Series funds are for Fidelity funds-of-funds (my knowledge; not confirmed by the search); R classes are retirement plans | **CRSP** (Wells Fargo not verified) |
| other \| retail | Fidelity 500 (FXAIX), Schwab S&P 500 (SWPPX), Fidelity Total Market (FSKAX), Fidelity Premium class | $0 minimum (FXAIX, SWPPX); Premium class $10,000 | **CRSP** |

**Verdict:**
- **CRSP flags are right in every case that could be verified.** They are also time-varying and track real events, such as Vanguard closing Investor shares.
- **Keywords fail systematically on two common names.** "Admiral" is retail, not institutional, and "Class R" is a retirement-plan class, not retail. They also leave the big single-class funds (FXAIX, SWPPX) unclassified.
- **Danny's "flags or keywords" rule inherits the Admiral error.** The institutional keyword test runs before the retail flag, so every Admiral class becomes institutional.
- **The best rule is CRSP flags.** With keyword fallback it is identical in this sample, since only 718 mutual-fund rows lack a Y flag.
- **Side finding:** CJTXX, a money-market fund, is in the index-fund sample (`product_j` 17310). That is worth flagging to Danny as a sample-construction question.

Sources: [Vanguard 2018 supplement (SEC)](https://sec.gov/Archives/edgar/data/225997/000093247119006422/ps_adm112018final.htm), [Empower 497K](https://www.sec.gov/Archives/edgar/data/356476/000119312525096015/d903050d497k.htm), [Principal 497K](https://www.sec.gov/Archives/edgar/data/898745/000089874524000496/sp20241211midcapsp400index.htm), [TIAA-CREF 485BPOS](https://www.sec.gov/Archives/edgar/data/1084380/000093041323000461/c105358_485bpos-ixbrl.htm), [CJTXX (StockAnalysis)](https://stockanalysis.com/quote/mutf/CJTXX/), [FXAIX (Zacks)](https://www.zacks.com/funds/mutual-fund/quote/FXAIX/class-info), [SWPPX (Zacks)](https://www.zacks.com/funds/mutual-fund/quote/SWPPX/class-info), [Fidelity Premium class (Investing.com)](https://investing.com/funds/fidelity-500-index-premium).

**Recommendation:** switch Z to CRSP flags (flags only) as the benchmark's share-class rule. The choice rests on data quality, not on the estimates. This changes the benchmark's numbers, so it is applied only on Gene's go. Until then the grid in `RESULTS_demand_grid.md` uses keyword Z.

## 5. Implications for the demand grid (`PLAN_demand_grid.md`)

- Danny's IV is a **third, distinct** instrument, not a copy of Z. The 12-model grid keeps Z and the paper's Hausman IV, as Gene asked.
- If Danny proposes his version as the share-class instrument, the conversation is about one choice: excluding same-index versus same-asset-class siblings. His version also needs a fix for the family-less funds pooled into one family.
