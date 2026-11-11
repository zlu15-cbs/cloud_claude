# The refined family ID and how real switchers are identified

Code: `code/sc_family_refined.py` (in `section2_replication/code/` and `code/spec_compare/`).
Outputs: `family_transitions.csv` (every transition and its rule), `family_real_switches_table2.csv` (the 50 excluded funds).

## 1. Why it is needed

- **The instrument is the fee of the family's other funds.** When a fund's family label changes, its whole donor set changes in one month, with no change in its own fee.
- **The paper's instrument uses CRSP's management code** (`firm_f_old`). It changes for 1,049 of the 1,190 Table 2 funds in 2010–2024, mostly because management companies are renamed.
- **Danny's ownership ID** (`firm_f`) is far more stable: it changes for 42 of those funds. But some of its changes are not changes of owner, and they include the largest fund in the market.
- **We separate "false" switches from real ones** with rules, and drop only the funds with a real one.

## 2. The principle

A fund's family is the firm that runs and markets it and earns most of its expense ratio.

A trustee, an administrator, a licensing sponsor, a white-label ETF platform, or a second legal name of the same firm is not a separate family.

## 3. The three rules

They are applied in this order to each fund's history of `firm_f`.

| Rule | What it does | Pairs in the data | Funds affected |
|---|---|---|---|
| 1. Alias | two labels of one firm become one name, everywhere | 40 | 312 |
| 2. Artifact | a label change between two specific names that is not a change of the firm running the fund; the fund keeps the name of the firm that runs it | 33 | 69 |
| 3. Real | every remaining change is an acquisition or transfer | 48 | 299 |

- **Nothing is decided fund by fund.** The rules act on pairs of names.
- **A pair that is in neither table is real by default,** and it is listed in `family_transitions.csv`, so the tables can be audited and extended.
- **Result:** funds with more than one family in the index CSV fall from 586 to 282; distinct families from 257 to 217.

## 4. Examples of false switchers

**SPDR S&P 500 ETF Trust (SPY).** Alias.

| Period | CRSP management name | Danny's `firm_f` | Refined ID |
|---|---|---|---|
| 2001–2008 | State Street Bank & Trust | State Street Global Advisors | State Street Global Advisors |
| 2008–2012 | PDR Services LLC | **PDR Services** | State Street Global Advisors |
| 2012 on | State Street Bank and Trust; State Street Global Advisors | State Street Global Advisors | State Street Global Advisors |

- PDR Services is the sponsor of the SPDR trusts and holds the index licence. State Street is the trustee, runs the fund and earns most of the fee.
- Without the fix, SPY is not a State Street fund in 2010–2012, on the supply side as well.

**SPDR S&P MidCap 400 ETF.** Artifact, then alias.

| Period | CRSP management name | Danny's `firm_f` | Refined ID |
|---|---|---|---|
| 2001–2008 | Bank of New York | **BNY Mellon Investment Management** | State Street Global Advisors |
| 2008–2012 | PDR Services LLC | **PDR Services** | State Street Global Advisors |
| 2012 on | State Street | State Street Global Advisors | State Street Global Advisors |

- Bank of New York was the trustee.

**Invesco QQQ Trust.** Artifact.

| Period | CRSP management name | Danny's `firm_f` | Refined ID |
|---|---|---|---|
| 2001–2008 | Bank of New York; BNY Mellon Asset Management | **BNY Mellon Investment Management** | Invesco |
| 2008 on | Invesco PowerShares; Invesco Capital Management; Invesco | Invesco | Invesco |

- Bank of New York is the trustee of the QQQ trust; the sponsor runs and markets it.
- CRSP's management code also reverts to the trustee for two quarters in 2020.

**iShares Silver Trust.** Artifact.

| Period | CRSP management name | Danny's `firm_f` | Refined ID |
|---|---|---|---|
| first 3 months of 2007 | Bank of New York | **BNY Mellon Investment Management** | BlackRock |
| 2007 on | Barclays Global Fund Advisors; BlackRock | BlackRock | BlackRock |

**US Global Jets ETF.** Artifact, in both directions.

| Period | Danny's `firm_f` | Refined ID |
|---|---|---|
| to mid-2021 | U.S. Global Investors | U.S. Global Investors |
| mid-2021 to 2023 | **UBS Global Asset Management** | U.S. Global Investors |
| 2023 on | U.S. Global Investors | U.S. Global Investors |

- The sponsor's name is matched to UBS for some months.

**ROBO Global Robotics and Automation Index ETF.** Artifact.

| Period | Danny's `firm_f` | Refined ID |
|---|---|---|
| to mid-2021 | **Exchange Traded Concepts** | ROBO Global |
| mid-2021 on | ROBO Global | ROBO Global |

- Exchange Traded Concepts is a white-label platform that hosts funds for other sponsors.

**MassMutual S&P 500 Index Fund.** Alias, back and forth.

| Period | Danny's `firm_f` | Refined ID |
|---|---|---|
| to 2013–2018 | MassMutual | MassMutual |
| to mid-2021 | **MML Investment Advisers** | MassMutual |
| mid-2021 on | MassMutual | MassMutual |

## 5. The alias table

Label → canonical name. The number is the funds whose label changes this way somewhere in the index CSV.

| Label | Canonical name | Funds |
|---|---|---|
| Directed Services | Voya Investments | 54 |
| DBX Strategic Advisors | DWS | 32 |
| MML Investment Advisers; David L. Babson & Co. | MassMutual | 28; 3 |
| ProFunds | ProShares | 28 |
| GW Capital Management; Maxim Capital Management | Empower Funds | 14; 1 |
| Banc One Investment Advisors | One Group Mutual Funds | 12 |
| Crossmark Global Investments | Steward Funds | 11 |
| Krane Funds Advisors | KraneShares | 11 |
| Everence Capital Management | Praxis Mutual Funds | 8 |
| Nations Funds | Columbia Threadneedle Investments | 6 |
| Eclipse Funds | New York Life Investments | 6 |
| American General; SunAmerica Asset Management | AIG | 5; 1 |
| CWM Advisors | Inspire ETFs | 5 |
| Rafferty Asset Management | Direxion | 5 |
| Advantus Capital Management | Securian Asset Management | 4 |
| Empowered Funds | Alpha Architect | 4 |
| Northwestern Mutual Investment Services | Mason Street Advisors | 4 |
| Provident Institutional Management | BlackRock | 4 |
| SRN Advisors | Siren | 4 |
| Waddell & Reed | Ivy Investments | 4 |
| CCM Partners | Shelton Capital Management | 3 |
| FFCM | O'Shares Investment Advisers | 3 |
| PDR Services | State Street Global Advisors | 2 |
| Citizens Trust | Citizens Advisers | 2 |
| ETFis Capital | Virtus Investment Partners | 2 |
| Factor Advisors | ETF Managers Group | 2 |
| TortoiseEcofin | Tortoise | 2 |
| U.S. Trust Company of Boston | Boston Trust | 2 |
| KeyCorp | Victory Capital Management | 1 |
| Rational Advisors | Strategy Shares | 1 |
| Woodward Funds | First Chicago NBD | 1 |
| Federated Securities | Federated Hermes | 0 |
| Unknown | State Street Global Advisors | 2 (see below) |

- **"Unknown"** appears on the two GE RSP funds from mid-2020. GE Asset Management was sold to State Street, so the label is mapped to State Street and the funds count as a real switch from GE to State Street.

## 6. The artifact table

The earlier name is replaced by the later one ("forward"), or the later by the earlier ("back").

| Kind | Earlier name → later name | Direction | Funds |
|---|---|---|---|
| Trustee listed before the sponsor | BNY Mellon Investment Management → Invesco | forward | 5 |
| | BNY Mellon Investment Management → BlackRock | forward | 1 |
| | BNY Mellon Investment Management → State Street Global Advisors (via PDR Services) | forward | 1 |
| | BNY Mellon Investment Management → Wilshire | forward | 2 |
| Administrator or distributor listed before the adviser | BISYS Fund Services → Mississippi Valley Advisors | forward | 4 |
| | First Data Investor Services Group → Fleet Investment Advisers; → Old Kent Bank | forward | 4; 1 |
| | SEI → U.S. Bancorp Asset Management; → HighMark Capital Management | forward | 3; 1 |
| | Forum Financial Services → Allspring | forward | 1 |
| | Russell Investments → State Street Global Advisors | forward | 1 |
| White-label ETF platform listed instead of the brand | Exchange Traded Concepts → Vident; ROBO Global; Capital Link; Loncar; Amplify; GraniteShares; Recon Capital Advisors; VanEck | forward | 4; 3; 2; 2; 1; 1; 1; 1 |
| | Toroso Investments → SoFi; → SP Funds | forward | 3; 2 |
| | FolioBeyond → SP Funds; → SoFi; → Gotham Asset Management | forward | 3; 2; 1 |
| | SP Funds; SoFi; Gotham Asset Management; SonicShares → FolioBeyond | back | 3; 2; 1; 1 |
| | Astor Investment Management → Northern Lights | back | 3 |
| | Gotham Asset Management → FundVantage Trust | back | 3 |
| Brand partner | Vest Financial → First Trust | forward | 1 |
| Mislabel | UBS Global Asset Management → U.S. Global Investors | forward | 3 |
| | U.S. Global Investors → UBS Global Asset Management | back | 2 |

- **BNY Mellon is a real family for its own (Dreyfus) index funds.** The rule applies only to the listed pairs, where it appears before the sponsor. A fund that moves into BNY Mellon (Bear Stearns → BNY Mellon) is a real switch.

## 7. Real switchers

**Definition.** A fund is a real switcher if its refined ID changes in a month between January 2010 and August 2024.

**In the Table 2 sample without the variable-annuity funds:** 50 of 1,190 funds, 3,214 fund-months, 0.6% of assets.

| From → to | Funds | Month the label changes |
|---|---|---|
| Guggenheim Investments → Invesco | 13 | 2018 |
| DB Commodity Services → Invesco | 11 | 2010–2015 |
| Morgan Stanley Investment Management → Invesco | 4 | 2010 |
| OppenheimerFunds → Invesco | 4 | 2019 |
| USAA Asset Management Company → Victory Capital Management | 4 | 2023 |
| Compass Efficient Model Portfolios → Victory Capital Management | 3 | 2015 |
| ETF Securities → abrdn | 3 | 2021 |
| Evergreen Investment Management → Allspring | 2 | 2010 |
| U.S. Bancorp Asset Management → Nuveen | 2 | 2010 |
| GE Asset Management → State Street Global Advisors | 2 | 2020 |
| Lattice Strategies → Hartford Funds | 1 | 2018 |
| Recon Capital Advisors → Global X | 1 | 2018 |

**Why they are dropped: Invesco DB Commodity Index Tracking Fund.**
- Its fee is 0.82–0.90% throughout.
- Its donors go from 9 sibling commodity funds (fees near 0.85%) to 176 Invesco funds led by QQQ (fee 0.20%).
- Its instrument falls from 0.84 to 0.25 while its market share falls with the commodity bust.
- Dropping this one fund moves the paper's T2 without variable-annuity funds from +7.2 to −1.5.

Other real transitions in the index CSV fall outside 2010–2024 or outside Table 2 (for example Merrill Lynch → BlackRock in 2004–2007, One Group → JPMorgan in 2005, MetLife → Brighthouse on variable-annuity funds). All 48 real pairs are in `family_transitions.csv`.

## 8. How to run and use it

```
SC_DATA=/folder/with/the/index/csv  python code/sc_family_refined.py
```

It prints the counts by rule and the list of real switchers, and writes the two CSV files.

In Python:

```python
from sc_family_refined import refined_family, transitions_table
family, switches = refined_family(2010, 2024 + 8/12)
# family:   product_j, month_t, firm_f, family      (one row per fund-month in the index CSV)
# switches: product_j, month_t, family_from, family_to   (real switches in the window)
real_switchers = set(switches.product_j)
```

- **Input:** `nonLev_funds_product_month_level_v2_patched.csv`, columns `product_j`, `month_t`, `firm_f`.
- **To change a classification:** edit the dictionaries `ALIAS` and `ARTIFACT` at the top of the script and re-run. The exclusion set changes with them, so the estimates must be re-run too.
- **In the estimation scripts:** `SC_FAMILY=refined` uses the refined ID for the instrument, `SC_NOSWITCH=1` drops the real switchers, and `SC_OWNER=refined` uses it for ownership on the supply side.

## 9. What to check

- **The alias and artifact entries are our judgment** from the firm names and general knowledge of who owns whom. They were not checked against filings.
- **Dates are when the label changes in the data,** which can lag the deal. IndexIQ → New York Life changes in 2024, though the acquisition was earlier.
- **Calls worth a second look:**
  - "Unknown" → State Street for the GE RSP funds.
  - Vest Financial → First Trust treated as the same family.
  - DBX Strategic Advisors and DWS treated as one firm; Guggenheim → Invesco treated as real.
  - Ivy Investments ↔ Delaware Management Company is classified real in both directions in 2021; these funds are not in Table 2.
- **Pairs classified real only by default** (not reviewed one by one) are mostly outside Table 2. They are the rows with rule "real" in `family_transitions.csv`.
