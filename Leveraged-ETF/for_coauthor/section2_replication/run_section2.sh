#!/bin/sh
# Replicates the last table of section 2 of RESULTS_spec_summary.md: the sample with both exclusions (no variable-annuity
# funds, no funds with a real acquisition or transfer), refined family ID, six specifications.
#   SC_DATA=/folder  SC_SOURCE=/path/index_funds_preprocess_oct2026.csv  SC_DANNY=/folder/with/classified_donors.csv  sh run_section2.sh
#   add "conduct" as an argument to also run the conduct tests (about 8 minutes each, 2.5 GB each)
# SC_DATA must hold nonLev_funds_product_month_level_v2_patched.csv and CRSP_fund_summary_2026_qtrly_combined.csv.
# A cache/ subfolder is created inside SC_DATA; nothing else is written there. Outputs go to ./work.
# Run the estimation steps one at a time, as below. Time: about 25 minutes without conduct.
set -e
: "${SC_DATA:?set SC_DATA}" ; : "${SC_SOURCE:?set SC_SOURCE}" ; : "${SC_DANNY:?set SC_DANNY}"
export SC_DATA SC_SOURCE SC_DANNY
C="$(cd "$(dirname "$0")" && pwd)/code"
mkdir -p work && cd work

python3 "$C/sc_build.py"              # Table 2 sample (108,300 fund-months) -> $SC_DATA/cache/panel.pkl
python3 "$C/sc_family_refined.py"     # refined family ID: family_transitions.csv, family_real_switches_table2.csv

# sample and definitions for every step below
export SC_FAMILY=refined    # family = refined ID, for the instrument
export SC_DONORS=csv        # instrument donors: fund-months in the index CSV
export SC_CHEAP=csv         # V2's cheap status: index CSV, entry month on or after January 2005
export SC_PURE=1 SC_RULE=all SC_NOSWITCH=1   # drop the funds with a real acquisition or transfer in 2010-2024
                                             # (the variable-annuity funds are dropped by the scripts' "no VA" sample)

mkdir -p paper && (cd paper && SC_SAVE=p SC_ONLY=index,pooled,wavg   python3 -u "$C/sc_t2a5_nova_grid.py" | tee log)   # T2, A5: paper's exclusion
mkdir -p broad && (cd broad && SC_SAVE=b SC_ONLY=lipper6,pooled,wavg python3 -u "$C/sc_t2a5_nova_grid.py" | tee log)   # T2, A5: broad-asset-class exclusion
mkdir -p v2    && (cd v2    && SC_SAVE=r SC_GRID=agg                 python3 -u "$C/sc_v2_robust.py"      | tee log)   # V2: median and weighted mean, 20th and 25th pct

# supply side: scale, marginal costs, where the negatives are
export SC_OWNER=refined     # ownership by the refined family ID
export SC_SPECS=T2p,A5p,T2b,A5b,V2r,V2wr
mkdir -p down && cd down
python3 -u "$C/sc_v2_final.py" downstream | tee downstream.log
if [ "$1" = conduct ]; then
  export SC_SCHEMES=A       # conduct test at eta = 0.024 only; unset for all four scale schemes (about 30 minutes each)
  for s in T2p A5p T2b A5b V2r V2wr; do python3 -u "$C/sc_v2_final.py" conduct $s | tee conduct_$s.log; done
fi
