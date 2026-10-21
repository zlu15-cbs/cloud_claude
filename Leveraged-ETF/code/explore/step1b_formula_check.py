"""Step 1b: Table 5 Panel A elasticity = Table 2 Panel A col (4) price coefficient x p x (1 - s), last market.

Uses p and s of the 15 funds in their last market from step1_blp1.csv (written by step1_table5_elasticity.py).
"""
import sys

import pandas as pd

PAPER = {16416: -0.242, 56419: -0.580, 16417: -0.249, 16448: -1.494, 16437: -0.415, 27635: -0.725, 29218: -3.325,
         28279: -0.665, 28277: -0.666, 29250: -0.167, 63885: -0.160, 31461: -0.323, 50485: -0.243, 31466: -0.244,
         31462: -0.326}  # product_ids -> Table 5 Panel A elasticity, matched on AUM in the last month
d = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else 'step1_blp1.csv')
d['paper'] = d.product_ids.map(PAPER)
d['formula_3rc'] = -8.348 * d.p * (1 - d.s)
d['diff'] = d.formula_3rc - d.paper
d['name'] = d.name.str.replace(r'^.*?: ', '', regex=True).str[:45]
print(d[['firm', 'name', 'aum', 'month_t', 'p', 's', 'paper', 'formula_3rc', 'diff']].round(4).to_string(index=False))
print('max |diff|:', round(d['diff'].abs().max(), 4))
