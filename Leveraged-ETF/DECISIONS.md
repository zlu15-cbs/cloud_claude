# Decisions (index-market demand)

| Decision | Rejected | Reason |
|---|---|---|
| Share class in the share-class instrument = **CRSP `inst_fund` / `retail_fund` flags** (ETF from `ETF_ind`); `new_iv.add_z_flag` → `Z_flag` | name keywords (`new_iv.share_class`); Danny's "flags or keywords" | Web check of 32 sampled classes: CRSP right in every verifiable case, time-varying (tracks Vanguard Investor-share closures); keywords misclassify Admiral (retail) and Class R (retirement plans) and leave single-class funds unclassified. `RESULTS_danny_iv_compare.md` §4. |
