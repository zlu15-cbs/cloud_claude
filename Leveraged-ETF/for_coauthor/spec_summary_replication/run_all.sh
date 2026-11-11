#!/bin/sh
# Replicates RESULTS_spec_summary.md. Usage:  SC_DATA=/path/to/folder/with/the/two/csv/files  sh run_all.sh
# Outputs are written to ./work. Total time: about 1 hour for everything except conduct; conduct adds about 30 minutes
# per specification and needs about 2.5 GB of memory each (run them one or two at a time).
set -e
: "${SC_DATA:?set SC_DATA to the folder holding the index CSV and the CRSP fund summary}"
export SC_DATA
C="$(cd "$(dirname "$0")" && pwd)/code"
mkdir -p work && cd work
python3 "$C/sc_build.py"            # panel, cheap indicator, instruments -> $SC_DATA/cache/panel.pkl
python3 "$C/sc_demand.py"           # columns 1-3 with VA: sc_demand.csv
python3 "$C/sc_downstream.py"       # scale, MC, location: sc_scale.csv, sc_mc.csv, sc_where.csv
mkdir -p a5 && cd a5
python3 "$C/sc_a5.py"               # column 4 with VA: sc_a5_demand.csv
python3 "$C/sc_a5.py" downstream
cd .. && mkdir -p exva && cd exva
python3 "$C/sc_exva.py"             # all "no VA" columns: sc_exva_demand.csv
python3 "$C/sc_exva.py" downstream
python3 "$C/sc_va_checks.py"        # sections 1 and 6: who the VA funds are, the three treatments, their fee data
cd ..
if [ "$1" = "conduct" ]; then
  for s in 1_T2 4p 3_V2; do python3 "$C/sc_downstream.py" conduct $s; done
  (cd a5 && python3 "$C/sc_a5.py" conduct A5)
  (cd exva && for s in 4px V2x; do python3 "$C/sc_exva.py" conduct $s; done)
fi
