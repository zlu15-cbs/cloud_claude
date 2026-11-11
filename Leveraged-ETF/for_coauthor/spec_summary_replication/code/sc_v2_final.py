"""Downstream and conduct for V2 with the cheap indicator rebuilt on the source panel (run sc_v2_robust.py first; it saves
the coefficients). V2n = with the variable-annuity funds on the supply side (107,863 rows); V2nx = without (100,092).
    python sc_v2_final.py downstream ; python sc_v2_final.py conduct V2n ; python sc_v2_final.py conduct V2nx
With SC_ALT=1 the same for T2alt and A5alt (T2 and A5 without variable-annuity funds, six-asset-class exclusion; saved by
SC_ONLY=lipper6,pooled,wavg python sc_t2a5_nova_grid.py).
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sc_downstream  # noqa: E402

if __name__ == '__main__':
    pd.set_option('display.width', 250, 'display.max_columns', 40)
    sc_downstream.SPECS = ['T2alt', 'A5alt'] if os.environ.get('SC_ALT') else ['V2n', 'V2nx']
    if sys.argv[1] == 'downstream':
        sc_downstream.downstream()
    else:
        sc_downstream.conduct(sys.argv[2])
