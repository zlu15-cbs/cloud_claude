"""Build Section 11 of blp_rc_identification.html from the result CSVs. python3 build.py RESULTS_DIR HTML_FILE"""
import os, sys, html
import numpy as np
import pandas as pd

R, HTML = sys.argv[1], sys.argv[2]
def csv(name):
    p = os.path.join(R, name)
    return pd.read_csv(p).iloc[0] if os.path.exists(p) else None
def f(r, k, nd=2):
    return 'pending' if r is None or k not in r or pd.isna(r[k]) else f'{float(r[k]):.{nd}f}'.replace('-', '−')
def est(r, b, s, nd=2):
    return 'pending' if r is None else f'{f(r, b, nd)} ({f(r, s, nd).replace("−", "")})'
def T(term, tip):
    return f'<span class="t" tabindex="0" data-tip="{html.escape(tip, quote=True)}">{term}</span>'
def E(tex, tip):
    return f'<span class="t" tabindex="0" data-tip="{html.escape(tip, quote=True)}">\\(\\displaystyle {tex}\\)</span>'

a1, a2, a2c = csv('step58_lag_step1.csv'), csv('step58_lag_step2_robust.csv'), csv('step58_lag_step2_clustered.csv')
b1, b2, b2c = csv('step58_age_step1.csv'), csv('step58_age_step2_robust.csv'), csv('step58_age_step2_clustered.csv')
ln = pd.read_csv(os.path.join(R, 'step57_lag_lognormal.csv')) if os.path.exists(os.path.join(R, 'step57_lag_lognormal.csv')) else None
fa = pd.read_csv(os.path.join(R, 'step58_lag_step2_robust_funds.csv')) if a2 is not None else None
fb = pd.read_csv(os.path.join(R, 'step58_age_step2_robust_funds.csv')) if b2 is not None else None

tip = dict(
    menu='Mutual-fund share classes and ETFs compete in the same market each month, with the same fee coefficient. No fee slope, month effect or trend is specific to either vehicle.',
    rc='A coefficient that differs across investors: its mean plus its standard deviation (σ) times a standard normal draw. It lets substitution be stronger between funds that are close in that characteristic.',
    y='The dependent variable of the logit: log of the fund\'s share of eligible assets minus log of the outside share (eligible assets not in the modelled funds).',
    pa='Each month the fund closes a fraction 1 − ρ of the gap between last month\'s log share ratio and a target that depends on this month\'s fee and characteristics. With ρ = 0.983, about 1.7% of the gap closes each month.',
    lr='What the coefficient would be if shares had fully adjusted: the monthly fee coefficient divided by 1 − ρ, and the monthly σ divided by the square root of 1 − ρ. It depends heavily on ρ.',
    J='Hansen\'s over-identification statistic: the two-step GMM criterion at its minimum. If the instruments are valid it is chi-squared with (moments − parameters) degrees of freedom. A large value means the instruments disagree with each other.',
    rw='Second-step GMM weight that allows a different error variance for each fund-month but treats fund-months as independent. This is the weight in Danny\'s package.',
    cw='Second-step GMM weight that also allows errors to be correlated across all funds in the same month, matching how the standard errors are clustered.',
    band='IV1 and IV4 count only rivals whose fee last month was within 10 basis points of the fund\'s own fee last month, above or below.',
    K='The Salanié–Wolak regressor K = p(p/2 − e), where p is the fund\'s characteristic and e its share-weighted market average. In a linear IV regression its coefficient estimates σ², the variance of the random coefficient. A negative estimate means a normal random coefficient cannot fit.',
    loo='Re-estimating with one of the five instruments removed, for each instrument in turn.',
    jk='Half-panel jackknife (Dhaene and Jochmans 2015). With fund effects and a lagged dependent variable, the lag coefficient is biased toward zero by roughly (1 + ρ)/T. Estimating on each half of every fund\'s history and combining with the full-sample estimate removes that bias to first order.',
    el='Percent change in a fund\'s share for a 1% change in its own fee. Averages are over fund-months weighted by assets (AUM-weighted) or equally within month and then across months.',
    iv0='Remote family fee: AUM-weighted fee of the same family\'s funds in other benchmarks and asset classes. A proxy for the family\'s common costs. Incremental F 17.1.',
    iv1='Prior matched rivals: number of other-family funds last month in the same asset class and access type, with fee within 10 bp and tracking error within 0.02 of the fund\'s own. Incremental F 348.3.',
    iv2='Prior remote capacity: number of other-family funds of the same vehicle (ETF or mutual fund) in other asset classes last month. Incremental F 42.7.',
    iv3='Current young rivals: number of other-family share classes in the same asset class that are at most twelve months old. Incremental F 4.3 (weak).',
    iv4='Prior local exits: certified liquidations over the previous twelve months of rivals matched as in IV1. Incremental F 88.9.',
    screen='A linear IV regression (2SLS) of the log share ratio on the fee and the K terms, with fund and month effects. It approximates the BLP model to second order in σ and runs in seconds, so it was used for the robustness checks. The headline estimates are from the full BLP model.',
    vehicle='ETF or mutual fund.',
    sv='Smallest singular value of the scaled Jacobian of the moments. Values near zero mean a parameter is not separately identified. Danny\'s Tables 8 and 10 have 0.03; Table 7 has 0.70.',
)

def lr_range():
    if fa is None: return 'pending'
    e = fa.e / (1 - float(a2['rho']))
    return f'{e.max():.1f} to {e.min():.1f}'.replace('-', '−')
def b_range():
    if fb is None: return 'pending'
    return f'{fb.e.max():.1f} to {fb.e.min():.1f}'.replace('-', '−')

def n15(fr, scale=1.0):
    return 'pending' if fr is None else f'{int((fr.e.abs() * scale > 1).sum())} of 15'
def Jcell(r, df=3):
    from scipy.stats import chi2
    if r is None: return 'pending'
    pv = chi2.sf(float(r['J']), df)
    return f'<span class="{"no" if pv < 0.05 else "ok"}">{float(r["J"]):.1f} on {df} df</span> ({"p &lt; 0.001" if pv < 0.001 else f"p = {pv:.2f}"})'

def lognormal_block():
    if ln is None or not len(ln):
        return '<p class="hint">Sign-constrained check: pending.</p>'
    nrm = ln[ln.label.str.startswith('normal')]
    lg = ln[ln.label.str.startswith('lognormal')].sort_values('objective')
    rows = ''.join(f'<tr><td>{("Normal, no dispersion" if r.sd_coef < 0.01 else "Normal") if r.label.startswith("normal") else "Lognormal (all negative)"}</td><td class="num">{r.mean_coef:.2f}</td><td class="num">{r.sd_coef:.2f}</td><td class="num">{r.objective:.3f}</td><td class="num">{r.aum_e:.3f}</td></tr>'.replace('-', '−')
                   for r in pd.concat([nrm, lg]).itertuples())
    return ('<p class="hint">One-step criterion with the same 2SLS weight and the same 500 draws per month, so rows are comparable. '
            'Lognormal rows are evaluations on a grid, not a search. Code: step57_lag_lognormal.py.</p>'
            '<div class="tblwrap"><table><thead><tr><th>Fee coefficient</th><th>Mean</th><th>SD</th><th>Criterion</th><th>AUM-weighted monthly elasticity</th></tr></thead><tbody>'
            + rows + '</tbody></table></div>')

def lognormal_sentence():
    if ln is None or not len(ln[ln.label.str.startswith('lognormal')]): return ''
    nb = ln[ln.label == 'normal, sigma 0.7827'].objective
    lgs = ln[ln.label.str.startswith('lognormal')].sort_values('objective')
    lg = lgs.iloc[0]
    n0 = ln[ln.label == 'normal, sigma 0.001'].objective
    if not len(nb): return ''
    nb = float(nb.iloc[0])
    m = lambda v, nd=2: f'{v:.{nd}f}'.replace('-', '−')
    txt = (f'Of the {len(lgs)} grid points with every coefficient negative, the best (mean {m(lg.mean_coef)}, SD {m(lg.sd_coef)}) has a criterion of {m(lg.objective, 3)}, '
           f'against {m(nb, 3)} for the normal coefficient' + (f' and {m(float(n0.iloc[0]), 3)} with no dispersion' if len(n0) else '') + '. ')
    txt += ('A sign-constrained coefficient fits better, so the positive share is not something the data require.' if lg.objective <= nb * 1.02
            else 'The sign-constrained coefficient fits worse on this grid, so the data favour the normal shape and the positive share remains a property of the estimate.')
    out = '<li>' + txt + '</li>'
    g = lgs.dropna(subset=['grad_sigma'])
    if (g.grad_sigma < 0).any() and (g.grad_sigma > 0).any():
        out += ('<li>The gradient of the lognormal criterion changes sign between the grid points (mean −0.46, SD 1.2) and (mean −0.7, SD 1.5), so it has an interior minimum near a mean of −0.5 and an SD of 1.3 per month. '
                'I did not search for it: each evaluation takes about eight minutes and the earlier lognormal searches stalled. Estimating A with a lognormal fee coefficient is the natural refinement if A is reported.</li>')
    return out

sec = f'''<!-- sec11 start -->
<h2 id="sec11">11. Preferred specifications for passive (1x) funds</h2>
<p>This section gives the two specifications I recommend for passive funds, one static and one with partial adjustment, and the evidence behind each. Both treat mutual-fund classes and ETFs as {T('one menu', tip['menu'])}, and both use Danny's five instruments unchanged. The data are his package of 25 Nov 2026: 98,110 passive fund-months, 1,063 share classes, 177 months. Its passive sample and instruments are identical to the 24 Nov package; his code was not run.</p>
<p class="hint">Headline estimates are from the full BLP model with his 3,000 archived draws per month. Robustness checks use the {T('linear screen', tip['screen'])}, where σ² is the coefficient on {T('K', tip['K'])}. Standard errors, in parentheses, are clustered by month. Fees are in percentage points. Code: step48 to step58 in code/explore; write-up in RESULTS_passive_one_menu.md.</p>

<div class="box">
<h3>Recommendation</h3>
<ul>
<li><strong>Main passive column: specification B.</strong> Static demand with a {T('random coefficient', tip['rc'])} on log fund age and none on the fee. It is Danny's Table 7 column (4) with the fee random coefficient removed; his own estimate of that coefficient is 0.05 (SE 20.5). The mean fee slope and the age coefficient hold in every instrument, band and period check below, and its elasticity can go directly into the static pricing condition.</li>
<li><strong>Dynamic extension: specification A.</strong> Table 7 plus last month's {T('log share ratio', tip['y'])}, read as {T('partial adjustment', tip['pa'])}. Its fee random coefficient is positive and survives every instrument and band check. Its {T('long-run', tip['lr'])} magnitudes depend on an adjustment speed the data do not pin down, so I would report it as evidence on fee heterogeneity, not as the source of markups.</li>
<li><strong>Not recommended: a fee random coefficient in the static model</strong> (Table 7 column 3). It fails four checks, listed below.</li>
<li><strong>Instruments in both: Danny's IV0 to IV4, unchanged,</strong> including the 10 bp {T('fee band', tip['band'])}.</li>
</ul>
</div>

<h3>The two models</h3>
<div class="eqwrap"><div class="eq">
<span>B:</span>
<span>\\(u_{{ijt}} =\\)</span>
{E('\\alpha\\, p_{jt}', 'One fee coefficient α for every investor and every fund. p is the annual expense ratio in percentage points.')}
<span>\\(+\\)</span>
{E('(\\beta_a + \\sigma_a \\nu_i)\\,\\ell_{jt}', 'Taste for fund age varies across investors: mean β_a, standard deviation σ_a, ν a standard normal draw. ℓ is log fund age.')}
<span>\\(+\\)</span>
{E("x_{jt}'\\beta", 'Controls: absolute tracking error and past one-year return.')}
<span>\\(+\\)</span>
{E('\\lambda_j + \\lambda_t + \\xi_{jt}', 'Fund fixed effect, month fixed effect, and the unobserved demand shock that the instruments must be uncorrelated with.')}
<span>\\(+\\,\\varepsilon_{{ijt}}\\)</span>
<span class="n">(19)</span></div></div>
<div class="eqwrap"><div class="eq">
<span>A:</span>
<span>\\(u_{{ijt}} =\\)</span>
{E('\\rho\\, y_{j,t-1}', "Last month's log share ratio of the same fund. ρ close to one means shares move slowly. It enters mean utility, the same for every investor.")}
<span>\\(+\\)</span>
{E('(\\alpha + \\sigma \\nu_i)\\, p_{jt}', 'The fee coefficient varies across investors: mean α, standard deviation σ, ν a standard normal draw. Both are per month.')}
<span>\\(+\\)</span>
{E("x_{jt}'\\beta", 'Controls: absolute tracking error, past one-year return and log fund age.')}
<span>\\(+\\)</span>
{E('\\lambda_j + \\lambda_t + \\xi_{jt}', 'Fund fixed effect, month fixed effect, and the unobserved demand shock.')}
<span>\\(+\\,\\varepsilon_{{ijt}}\\)</span>
<span class="n">(20)</span></div></div>
<div class="eqwrap"><div class="eq">
{E('y_{jt} - y_{j,t-1} = (1-\\rho)\\,(y^*_{jt} - y_{j,t-1})', "Partial adjustment: the change in the log share ratio is a fraction 1 − ρ of the gap to the target y*. Without a random coefficient this is algebraically the same as (20).")}
<span>\\(,\\qquad\\)</span>
{E('\\alpha^* = \\frac{\\alpha}{1-\\rho}', 'Long-run mean fee coefficient: the fee coefficient of the target.')}
<span>\\(,\\quad\\)</span>
{E('\\sigma^* = \\frac{\\sigma}{\\sqrt{1-\\rho}}', 'Long-run standard deviation of the fee coefficient. This mapping holds to second order in σ; it is an interpretation of (20), not a separate estimate.')}
<span class="n">(21)</span></div></div>

<div class="tblwrap"><table>
<thead><tr><th></th><th>B: static</th><th>A: partial adjustment</th></tr></thead>
<tbody>
<tr><td><strong>Random coefficient on</strong></td><td>Log fund age</td><td>Fee</td></tr>
<tr><td><strong>Mean utility</strong></td><td>Fee, tracking error, past return, log age</td><td>Same, plus last month's log share ratio</td></tr>
<tr><td><strong>Fixed effects</strong></td><td colspan="2">Fund (share class) and month</td></tr>
<tr><td><strong>Excluded instruments</strong></td><td colspan="2">{T('IV0', tip['iv0'])}, {T('IV1', tip['iv1'])}, {T('IV2', tip['iv2'])}, {T('IV3', tip['iv3'])}, {T('IV4', tip['iv4'])}</td></tr>
<tr><td><strong>Sample</strong></td><td>98,110 fund-months</td><td>96,499 (each fund's first month has no lag)</td></tr>
<tr><td><strong>Moments, parameters</strong></td><td>8 and 5</td><td>9 and 6</td></tr>
<tr><td><strong>Estimation</strong></td><td colspan="2">Two-step GMM; 3,000 archived draws per month; standard errors clustered by month</td></tr>
</tbody></table></div>

<h3>Estimates</h3>
<p class="hint">Two-step GMM with the {T('robust weight', tip['rw'])} that Danny's package uses. The last rows repeat the second step with a {T('month-clustered weight', tip['cw'])}. Code: step58_final_blp.py.</p>
<div class="tblwrap"><table>
<thead><tr><th></th><th>B: static</th><th>A: partial adjustment</th></tr></thead>
<tbody>
<tr><td>Mean fee coefficient</td><td class="num">{est(b2, 'b[prices]', 'se[prices]')}</td><td class="num">{est(a2, 'b[prices]', 'se[prices]')} per month</td></tr>
<tr><td>Random-coefficient SD</td><td class="num">age: {est(b2, 'sigma_age', 'sigma_age_se')}</td><td class="num">fee: {est(a2, 'sigma', 'sigma_se')} per month</td></tr>
<tr><td>Lag coefficient ρ</td><td class="num">none</td><td class="num">{est(a2, 'b[y_lag]', 'se[y_lag]', 3)}</td></tr>
<tr><td>{T('Long-run', tip['lr'])} mean fee coefficient and SD, at the estimated ρ</td><td class="num">same as above</td><td class="num">{f(a2, 'long_run_mean_fee_coef', 1)} and {f(a2, 'long_run_sigma', 1)}</td></tr>
<tr><td>{T('Own elasticity', tip['el'])}, equal-month average</td><td class="num">{f(b2, 'mean_own_elasticity_equal_month')}</td><td class="num">{f(a2, 'mean_own_elasticity_equal_month')} per month</td></tr>
<tr><td>Own elasticity, AUM-weighted</td><td class="num">{f(b2, 'aum_weighted_elasticity')}</td><td class="num">{f(a2, 'aum_weighted_elasticity')} per month; {f(a2, 'long_run_aum_weighted_elasticity')} long-run</td></tr>
<tr><td>15 largest Big-3 funds, last month</td><td class="num">{b_range()}</td><td class="num">{lr_range()} long-run</td></tr>
<tr><td>Of those 15, elasticity above 1 in absolute value</td><td class="num">{n15(fb)}</td><td class="num">{n15(fa, 1 / (1 - float(a2['rho'])) if a2 is not None else 1.0)} long-run; none per month</td></tr>
<tr><td>Fund-months with upward-sloping demand</td><td class="num">{'pending' if b2 is None else f"{100 * float(b2['share_e_pos']):.1f}%"}</td><td class="num">{'pending' if a2 is None else f"{100 * float(a2['share_e_pos']):.1f}%"}</td></tr>
<tr><td>{T('J', tip['J'])}, robust weight</td><td class="num">{Jcell(b2)}</td><td class="num">{Jcell(a2)}</td></tr>
<tr><td>J, month-clustered weight</td><td class="num">{Jcell(b2c)}</td><td class="num">{Jcell(a2c)}</td></tr>
<tr><td>Estimates with the clustered weight</td><td class="num">fee {est(b2c, 'b[prices]', 'se[prices]')}; age SD {est(b2c, 'sigma_age', 'sigma_age_se')}</td><td class="num">fee {est(a2c, 'b[prices]', 'se[prices]')}; fee SD {est(a2c, 'sigma', 'sigma_se')}</td></tr>
<tr><td>{T('Smallest scaled singular value', tip['sv'])}</td><td class="num">{f(b2, 'min_scaled_singular_value')}</td><td class="num">{f(a2, 'min_scaled_singular_value')}</td></tr>
</tbody></table></div>
<p class="hint">For comparison, Danny's Table 7: column (3), fee random coefficient only: fee −18.20 (0.92), fee SD 1.88 (0.37), elasticity −4.19, J 144.4 on 3 df. Column (4), fee and age: fee −16.11 (1.22), fee SD 0.05 (20.47), age SD 1.42 (0.27), elasticity −3.90, J 102.3 on 2 df.</p>

<h3>Why no fee random coefficient in the static model</h3>
<p>In the linear screen, Table 7's fee σ² is +3.1 (1.5). It changes sign under each of four changes that should not matter if it measured fee heterogeneity:</p>
<div class="tblwrap"><table>
<thead><tr><th>Change to Table 7</th><th>Static fee variance <span style="text-transform:none">σ²</span></th></tr></thead>
<tbody>
<tr><td>{T('Fee band', tip['band'])} of IV1 and IV4 at 8, 10, 11, 12, 15 bp</td><td>+2.9, +3.1, +1.3, <span class="no">−1.6, −3.1</span> (SE about 1.6)</td></tr>
<tr><td>Drop {T('IV2', tip['iv2'])}</td><td><span class="no">−17.1 (3.9)</span></td></tr>
<tr><td>Add an ETF taste trend</td><td><span class="no">−15.3 (4.8)</span></td></tr>
<tr><td>Add an age random coefficient</td><td><span class="no">−12.7 (3.0)</span>; in the BLP itself the fee SD goes to 0.05 (SE 20.5), his column (4)</td></tr>
</tbody></table></div>
<ul>
<li>IV2 counts same-{T('vehicle', tip['vehicle'])} funds in other asset classes, so it moves like an ETF-versus-mutual-fund time trend. The positive σ² rests on it.</li>
<li>Section 9 gave the reason: the market-position part of K asks for a negative σ² in these data.</li>
</ul>

<h3>Support for B</h3>
<p class="hint">Linear screen with the age K term and no fee K term. Baseline: fee −15.7 (1.0), age σ² +0.97 (0.14). Code: step55_final_checks.py.</p>
<div class="tblwrap"><table>
<thead><tr><th>Check</th><th>Fee slope</th><th>Age variance <span style="text-transform:none">σ²</span></th></tr></thead>
<tbody>
<tr><td>{T('One instrument dropped', tip['loo'])}: IV0, IV1, IV2, IV3, IV4</td><td>−17.2, −11.2, −16.4, −15.4, −16.0</td><td>+0.75, +1.21, +4.62, +0.95, +0.97 <span class="ok">all positive</span></td></tr>
<tr><td>Fee band 8, 12, 15 bp</td><td>−15.9, −18.6, −18.6</td><td>+0.99, +0.83, +0.81</td></tr>
<tr><td>ETF taste trend added</td><td>−13.6 (1.0)</td><td>+1.80 (0.30)</td></tr>
<tr><td>Before 2019; from 2019</td><td>−14.8 (1.6); −5.9 (1.3)</td><td>+0.97 (0.15); +0.62 (0.45)</td></tr>
<tr><td>Fee slope, one instrument at a time (logit)</td><td>IV0 −5.7, IV1 −17.2, IV2 −28.2, IV4 −15.9 <span class="ok">all negative</span></td><td></td></tr>
<tr><td>Mutual-fund rows alone; ETF rows alone</td><td><span class="no">+3.8 (1.3)</span>; −14.6 (0.9)</td><td><span class="no">−4.0 (0.7); −0.58 (0.21)</span></td></tr>
</tbody></table></div>
<ul>
<li><strong>What holds:</strong> the fee slope is negative and the age coefficient positive under every instrument, band and period change.</li>
<li><strong>What does not:</strong> the result is a pooled one. Within mutual funds alone the fee slope is positive, and within either vehicle alone the age σ² is negative. B is right only if the two vehicles really are one menu.</li>
<li>The fee slope is smaller from 2019 (−5.9 against −14.8).</li>
<li>The age SD and the mean age coefficient are estimated together and are strongly correlated: the mean rises from 0.65 without the random coefficient to 1.90 with it, and the smallest singular value is 0.05. The fee coefficient, which is what markups use, is not affected (−16.1 here, −15.7 in the screen).</li>
<li>About half of assets (48%) sit in funds whose own elasticity is below 1 in absolute value, including 9 of the 15 largest (Danny's Table 7 also has 9 of 15). A single-product static pricing condition gives those funds a negative marginal cost.</li>
<li>A return random coefficient (his columns 5 and 6) could be added. I leave it out: its σ² turns negative without IV3, and it makes the mean return coefficient negative, as his note points out.</li>
</ul>

<h3>Support for A</h3>
<p class="hint">Linear screen with the lagged log share ratio. Baseline: fee −0.47 (0.12), fee σ² +0.67 (0.26), lag 0.983 (0.002), J 7.1 on 3 df. Code: step52, step54, step55.</p>
<div class="tblwrap"><table>
<thead><tr><th>Check</th><th>Fee slope, per month</th><th>Fee variance <span style="text-transform:none">σ²</span>, per month</th></tr></thead>
<tbody>
<tr><td>One instrument dropped: IV0, IV1, IV2, IV3, IV4</td><td>−0.53, −0.64, −0.41, −0.47, −0.40</td><td>+0.78, +0.43, +0.45, +0.63, +0.73 <span class="ok">all positive</span></td></tr>
<tr><td>Fee band 6, 8, 12, 15, 20 bp</td><td>−0.44, −0.44, −0.52, −0.54, −0.66</td><td>+0.69, +0.70, +0.59, +0.57, +0.43</td></tr>
<tr><td>ETF taste trend added</td><td>−0.41 (0.15)</td><td>+0.49 (0.34)</td></tr>
<tr><td>Age term added</td><td>−0.42 (0.11)</td><td>+0.49 (0.26)</td></tr>
<tr><td>Fee slope, one instrument at a time (logit)</td><td>IV0 −0.55, IV1 −0.20, IV2 −1.18, IV4 −0.79 <span class="ok">all negative</span></td><td></td></tr>
<tr><td>Mutual-fund rows alone; ETF rows alone (logit)</td><td><span class="ok">−0.11 (0.08); −0.18 (0.11)</span></td><td></td></tr>
<tr><td>Before 2019; from 2019</td><td>−0.65 (0.22); <span class="no">+0.24 (0.32)</span></td><td>+1.35 (0.60); +3.3 (1.9)</td></tr>
</tbody></table></div>
<ul>
<li><strong>What holds:</strong> the sign of the fee slope and of σ² under every instrument and band change; no upward-sloping demand within either vehicle; J does not reject with the clustered weight.</li>
<li><strong>What is weaker:</strong> σ² loses significance with an ETF trend or the age term, and in sub-periods the estimates are imprecise (from 2019 the fee slope is positive but insignificant).</li>
</ul>

<h3>What A cannot deliver: the adjustment speed</h3>
<div class="tblwrap"><table>
<thead><tr><th>Estimate of the lag coefficient <span style="text-transform:none">ρ</span></th><th>Value</th></tr></thead>
<tbody>
<tr><td>Full sample</td><td>0.983 (0.002)</td></tr>
<tr><td>Funds with at least 170 months</td><td>0.987 (0.003)</td></tr>
<tr><td>{T('Bias-corrected', tip['jk'])}</td><td><span class="no">1.000</span></td></tr>
</tbody></table></div>
<div class="tblwrap"><table>
<thead><tr><th>Lag coefficient imposed</th><th>Fee slope, per month</th><th>Fee variance <span style="text-transform:none">σ²</span>, per month</th><th>Long-run fee slope</th><th>Long-run SD</th></tr></thead>
<tbody>
<tr><td class="num">0.95</td><td class="num">−1.02 (0.10)</td><td class="num">+0.82 (0.27)</td><td class="num">−20</td><td class="num">4.0</td></tr>
<tr><td class="num">0.98</td><td class="num">−0.51 (0.10)</td><td class="num">+0.70 (0.26)</td><td class="num">−25</td><td class="num">5.9</td></tr>
<tr><td class="num">0.99</td><td class="num">−0.34 (0.10)</td><td class="num">+0.66 (0.26)</td><td class="num">−34</td><td class="num">8.1</td></tr>
<tr><td class="num">1.00</td><td class="num">−0.17 (0.10)</td><td class="num">+0.62 (0.26)</td><td colspan="2">no long-run level: fees move the growth of a fund's share</td></tr>
</tbody></table></div>
<ul>
<li>For ρ between 0.95 and 0.99 the long-run fee slope is −20 to −34, the same order as the static −16 to −18. The data cannot rule out ρ = 1, where no long-run level exists.</li>
<li>If A is used for magnitudes, ρ should be set from outside evidence on how fast index-fund assets turn over, with this table as the sensitivity range.</li>
<li>The partial-adjustment model cannot be estimated directly at monthly frequency. At ρ = 0.983 the implied target shares put more than half the market in a single fund in 159 of 176 months, because monthly share changes are divided by 0.017.</li>
</ul>

<h3>What A cannot deliver: the sign of each investor's coefficient</h3>
<ul>
<li>Read literally, (20) with a mean of {f(a2, 'b[prices]')} and an SD of {f(a2, 'sigma')} gives a positive fee coefficient to {'pending' if a2 is None else f"{100 * float(a2['share_pos_coef_access0']):.0f}%"} of investors. Under the long-run reading (21) the ratio of mean to SD is about 4.5 and almost none are positive. The two readings fit the data equally to second order in σ.</li>
{lognormal_sentence()}
</ul>
{lognormal_block()}

<h3>The instruments</h3>
<div class="tblwrap"><table>
<thead><tr><th>IV</th><th>What it is</th><th>Incremental fee F (his Table 8)</th><th>Note</th></tr></thead>
<tbody>
<tr><td>{T('IV0', tip['iv0'])}</td><td>Same-family fee in other asset classes</td><td class="num">17.1</td><td>The only instrument not built from rivals. Alone it gives a negative fee slope: −5.7 (1.1) static, −0.55 (0.19) per month in A.</td></tr>
<tr><td>{T('IV1', tip['iv1'])}</td><td>Count of rivals within the 10 bp fee band</td><td class="num">348.3</td><td>Built from rival fees.</td></tr>
<tr><td>{T('IV2', tip['iv2'])}</td><td>Same-vehicle funds in other asset classes</td><td class="num">42.7</td><td>Moves like an ETF-versus-mutual-fund trend.</td></tr>
<tr><td>{T('IV3', tip['iv3'])}</td><td>Young rivals in the same asset class</td><td class="num">4.3</td><td>Weak. Dropping it changes little.</td></tr>
<tr><td>{T('IV4', tip['iv4'])}</td><td>Rival liquidations, matched like IV1</td><td class="num">88.9</td><td>Built from rival fees.</td></tr>
</tbody></table></div>
<ul>
<li><strong>The 10 bp band is not special.</strong> From 6 to 20 bp, A's σ² stays between +0.43 and +0.70, B's age σ² between +0.81 and +0.99, and both fee slopes stay negative. Only the static fee σ² changes sign.</li>
<li><strong>The band itself is needed.</strong> With the fee and tracking matching removed, as in Danny's new leveraged instruments, the rival count's first-stage F falls from 368 to about 15, the static fee σ² turns negative and A's fee slope goes to zero.</li>
<li><strong>Exclusion.</strong> IV1 and IV4 move when rivals' fees enter or leave the band. They are valid only if rivals' fee changes are unrelated to the fund's own demand shock. Danny's note lists this as a maintained assumption.</li>
</ul>

<div class="box">
<h3>Issues to state in the paper, for either specification</h3>
<ul>
<li>Over-identification rejects under the robust weight in both. Only A passes, and only with the month-clustered weight.</li>
<li>Identification is pooled across mutual funds and ETFs. Within mutual funds alone, static demand slopes up.</li>
<li>IV1 and IV4 rest on rival fees.</li>
<li>The fee slope is weaker from 2019 in both.</li>
<li>B has no fee heterogeneity: funds differ in elasticity only through their fee level, share and age.</li>
</ul>
</div>
<!-- sec11 end -->
'''
s = open(HTML).read()
if '<!-- sec11 start -->' in s:
    s = s[:s.index('<!-- sec11 start -->')] + sec + s[s.index('<!-- sec11 end -->') + len('<!-- sec11 end -->\n'):]
else:
    s = s.replace('\n<footer>', '\n' + sec + '\n<footer>', 1)
if 'td:first-child { min-width' not in s:
    s = s.replace("td.num { white-space: nowrap }", "td.num { white-space: nowrap }\n.tblwrap td:first-child { min-width: 8.5rem }", 1)
s = s.replace('Section 10 added 25 Nov</p>', 'Section 10 added 25 Nov · Section 11 added 26 Nov</p>')
bullet = '<li><a href="#sec11">Section 11</a> gives the preferred passive specifications: a static model with a random coefficient on fund age and none on the fee, and a partial-adjustment model in which the fee random coefficient is positive and robust in sign.</li>\n'
if '#sec11' not in s.split('<h2>1.')[0]:
    s = s.replace('his σ there is fragile for other reasons.</li>\n', 'his σ there is fragile for other reasons.</li>\n' + bullet, 1)
foot = ' Section 11 uses Danny\'s Section 3 package of 25 Nov 2026 (passive data and instruments unchanged from 24 Nov), read without running his code; Dhaene and Jochmans (2015) for the half-panel jackknife.'
if 'Dhaene and Jochmans' not in s.split('<footer>')[1]:
    s = s.replace('Equation (18) is the standard lognormal random coefficient.', 'Equation (18) is the standard lognormal random coefficient.' + foot, 1)
open(HTML, 'w').write(s)
print('built; pending cells:', sec.count('pending'))
