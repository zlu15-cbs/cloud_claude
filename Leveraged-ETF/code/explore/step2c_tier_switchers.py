"""Which funds change group between the first-month and the 12-month-average fee tiers, and how much
within-fund fee variation (the source of identification for the cheap-group slope) they carry."""
import pandas as pd

import common
from step2_logit_screen import add_variables

d = add_variables(common.load('index'))
d['p_within'] = d.prices - d.groupby('product_ids').prices.transform('mean')
fund = d.groupby('product_ids').agg(name=('product_fund_name', 'last'), firm=('firm_ids', 'last'), n=('prices', 'size'),
                                    fee_first=('prices', 'first'), fee_min=('prices', 'min'), fee_max=('prices', 'max'),
                                    within_ss=('p_within', lambda x: (x ** 2).sum()),
                                    t1=('fee_t1', 'first'), t1_12=('fee12_t1', 'first'),
                                    b40=('fee_b40', 'first'), b40_12=('fee12_b40', 'first'))
for a, b, label in [('t1', 't1_12', 'cheapest third'), ('b40', 'b40_12', 'cheapest 40%')]:
    sw = fund[fund[a] != fund[b]]
    for g in (0, 1):
        tot = fund[fund[a] == 1].within_ss.sum() if g else fund[fund[a] == 0].within_ss.sum()
    print(f'\n{label}: {len(sw)} switching funds; their share of within-fund fee variation: '
          f'{sw.within_ss.sum() / fund.within_ss.sum():.3f} of all, '
          f'{sw[sw[a] == 1].within_ss.sum() / fund[fund[a] == 1].within_ss.sum():.3f} of the first-month cheap group')
    print(sw.sort_values('within_ss', ascending=False).head(10)
          .assign(name=lambda x: x.name.str.split(': ').str[-1].str[:40]).round(3).to_string())
