"""Descriptives for the rolling 'cheap' status (A10): coverage, switching, and status of the 15 Table 5 funds."""
import common
from step1_table5_elasticity import top15
from step2_logit_screen import add_variables

d = add_variables(common.load('index'))
funds = top15(d)
for n in ('cheap_t33_w12', 'cheap_q20_w12', 'cheap_t33_w6'):
    g = d.sort_values('month_key').groupby('product_ids')[n]
    switches = (g.diff().abs() > 0).groupby(d.product_ids).sum()
    print(f'{n}: share of fund-months cheap {d[n].mean():.3f}; funds ever cheap {int((g.max() == 1).sum())} of '
          f'{d.product_ids.nunique()}; funds that switch status {int((switches > 0).sum())} '
          f'(in {int((switches > 1).sum())} more than once)')
last = d.sort_values('month_key').groupby('product_ids').last()
cut = d[d.month_key == d.month_key.max()].prices.quantile(1 / 3)
print(f'\nlast month: 33rd percentile fee = {cut:.3f}, 20th = {d[d.month_key == d.month_key.max()].prices.quantile(.2):.3f}')
print(last.loc[funds.product_ids, ['product_fund_name', 'prices', 'cheap_t33_w12', 'cheap_q20_w12', 'cheap_t33_w6']]
      .assign(product_fund_name=lambda x: x.product_fund_name.str.split(': ').str[-1].str[:45]).to_string())
