# How negative can implied marginal cost be? Securities-lending bounds for the index market

Purpose: an evidence-based admissibility rule for demand specifications. A specification is plausible only if the negative marginal costs it implies are no larger, and no more common, than securities-lending revenue can explain. Units are percent of AUM per year, the same units as `prices`.

## 1. What the sources say

| Fact | Source |
|---|---|
| Average net lending return passed to fundholders, 2018–2022, funds authorized to lend: U.S. small cap ~3 bp/yr (the highest category); high-yield bond ~2 bp; large cap, taxable bond lower. The top sponsors (State Street, Invesco) averaged ~3.5 bp in 2022. | Morningstar, *An Inside Look at Securities Lending* (Aug 2023), pp. 1, 8–9 |
| Vanguard offset ~16% of its funds' fees with lending income on average (2018–2022), the highest of the 10 largest sponsors. | Morningstar (2023), p. 1 |
| Extremes: iShares Russell 2000 (IWM) earned 0.14%/yr in 2019–2021 against a 0.19% fee. iShares Micro-Cap (IWC) earned 0.59% in 2020 against a 0.60% fee. | Morningstar (2023), p. 9 |
| 81% of the iShares ETFs that lent in 2017 earned ≤ 0.05% of net assets. | BlackRock (2017), as reported in trade press |
| iShares MSCI EM Small Cap UCITS: 0.53% lending return against a 0.74% fee (Jun 2026). World Small Cap: 0.07% against 0.35%. | iShares product pages |
| Dimensional U.S. equity funds averaged ~1.1 bp in 2020–2024. | Investment Executive, citing Dimensional |
| ETF lending revenue can be "on the order of the size of the expense ratio" for some funds. Index mutual funds are similar but slightly lower. | Blocher & Whaley, *Passive Investing: The Role of Securities Lending* (working paper; abstract only — the tables could not be retrieved) |
| **Who keeps the revenue.** Vanguard returns all net lending revenue to the funds (lending at cost). BlackRock has kept roughly 30–35% of net revenue in the past (various 2010–2013 sources). Some managers keep upward of 19% of gross. | Vanguard; etf.com; Morningstar UK |
| SPY is a unit investment trust and cannot lend its securities. | ETF Trends (secondary source; not checked against the trust agreement) |

## 2. What this implies for implied MC (my inference, not from a source)

**Which revenue offsets cost.** In the supply model, the sponsor sets the expense ratio p. Lending income credited to the *fund* raises investors' net return; the sponsor does not receive it. Only the part the sponsor (or its affiliated lending agent) keeps, call it a, enters the sponsor's first-order condition:

    p + a − c = markup   ⇒   implied MC (p − markup) = c − a ≥ −a.

So the right lower bound on implied MC is −a, the **sponsor-retained** share, not the fund's lending return. That makes the admissible range tighter than "lending income".

| Fund type | Fund's lending return L | Sponsor-retained a | Lower bound on implied MC |
|---|---|---|---|
| Typical index fund that lends | ≤ 5 bp (81% of iShares) | ≤ ~2–3 bp (if the sponsor keeps ~1/3 of net) | about −0.03% |
| U.S. small cap (IWM-type) | ~10–15 bp | ~5–8 bp | about −0.08% |
| Micro-cap / EM small cap (extremes) | 50–60 bp | up to ~0.3% | about −0.3% |
| Vanguard (lends at cost) | a few bp | ≈ 0 | ≈ 0: lending cannot explain a negative MC |
| UITs (SPY) | 0 | 0 | 0 |

A looser bound treats the fund's whole lending return L as available. This is defensible if the demand side prices funds at their net-of-lending cost, which ours does not. Even then, the bound is about −0.05% for typical funds and about −0.6% at the extremes.

**Proposed admissibility rule** for a demand specification, on implied MC after the scale adjustment:

1. **Magnitude.** First round (Gene's ruling: the thresholds doubled): at most 2% of fund-months below −0.20%; none below −0.60%. Evidence-based tight version: at most 1% below −0.10%; none below −0.30%. A 1% floor is not supported: no source shows a fund lending return above ~0.6%, and the sponsor keeps only part of it.
2. **Share.** Fund-months with MC < 0 should be a minority, and those below −0.05% a small one. BlackRock's 81%-at-≤ 5 bp implies that ≲ 20% of lending fund-months could plausibly sit below −0.03%. I suggest a soft cap of 20% and a hard cap of one third.
3. **Pattern (the sharpest test).** Negative MCs should cluster where lending revenue is high: small-cap, micro-cap, EM and international equity. They should **not** appear among Vanguard funds (lending at cost) or SPY (cannot lend). Negative MCs concentrated in large-cap Vanguard or SPY funds count against the specification whatever the share.
4. **No upward-sloping demand**: the share of fund-months with e > 0 must be 0, as before.

These thresholds are judgement calls built on the evidence in §1. Rules 1–2 fix the numbers. Rule 3 needs only the asset-class map (`asset_class.py`) and family names already in the data.

## 3. Open items

- The exact per-category figures in Morningstar Exhibits 6–8 and Appendices B–D are images; only the text figures above were extractable.
- The Blocher–Whaley tables and current BlackRock or State Street agent splits were not retrieved. N-CEN filings (Item C.6, securities-lending income and fees) give fund-level gross income, agent fees and net income from 2018. They would let us set a fund-specific bound a_j instead of the category rule above, if that is worth the effort.

## Sources

- [Morningstar, An Inside Look at Securities Lending (2023)](https://assets.contentstack.io/v3/assets/blt4eb669caa7dc65b2/blt8ce439cb53f1c215/64f07841de63418d439e3cc7/2023_Securities_Lending_Report.pdf)
- [Morningstar, Which Funds Benefit Most From Securities Lending](https://www.morningstar.com/columns/rekenthaler-report/which-funds-benefit-most-securities-lending)
- [Investment Executive, Securities lending: How ETFs benefit](https://www.investmentexecutive.com/news/product/securities-lending-how-etfs-benefit/)
- [etf.com, Is Securities Lending Good For ETF Investors?](https://www.etf.com/sections/news/securities-lending-good-etf-investors)
- [iShares MSCI EM Small Cap UCITS ETF](https://www.ishares.com/ch/individual/en/products/251859/ishares-msci-emerging-markets-smallcap-ucits-etf)
- [iShares MSCI World Small Cap UCITS ETF](https://www.ishares.com/ch/individual/en/products/296576/ishares-msci-world-small-cap-ucits-etf)
- [Blocher & Whaley, Passive Investing: The Role of Securities Lending](https://acfr.aut.ac.nz/__data/assets/pdf_file/0010/29917/WhaleyPassive-Investing.pdf)
- [Vanderbilt news on Blocher & Whaley](https://news.vanderbilt.edu/2015/01/23/vanderbilt-researchers-call-for-more-transparency-with-passive-investing-revenue/)
- [Vanguard, Securities lending at Vanguard](https://vanguard.co.uk/professional/insights-education/insights/securities-lendingat-vanguard-putting-the-investor-first)
- [etf.com, Nadig: iShares' Change Good For Investors](https://www.etf.com/sections/etfcom-analysis/nadig-ishares-change-good-investors)
- [Morningstar UK, iShares sweetens the pot for Irish-domiciled funds](https://www.morningstar.co.uk/uk/news/66945/ishares-sweetens-the-pot-for-irish-domiciled-funds.aspx)
- [ETF Trends on SPY's UIT structure](https://www.etftrends.com/?p=189808)
