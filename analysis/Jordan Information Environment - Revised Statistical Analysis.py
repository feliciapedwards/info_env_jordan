# Databricks notebook source
# MAGIC %md
# MAGIC # Jordan Information Environment: Revised Statistical Analysis
# MAGIC
# MAGIC Fixes to the original analysis:
# MAGIC 1. Quarterly economic data is NOT forward-filled to months (this inflated n from ~14 to ~44).
# MAGIC 2. Series are tested for stationarity and differenced before any lag analysis.
# MAGIC 3. Counts are modelled with count models; Spearman is reported alongside Pearson.
# MAGIC 4. Block-bootstrap CIs and multiple-comparison correction replace naive p-values.
# MAGIC 5. Hypotheses are pre-specified; a holdout period is reserved.
# MAGIC
# MAGIC **Pre-specified hypotheses**
# MAGIC * H1 (weekly): changes in search interest Granger-cause changes in event counts (and vice versa).
# MAGIC * H2 (weekly): media article counts Granger-cause event counts (and vice versa).
# MAGIC * H3 (quarterly): economic events relate to inflation / youth unemployment changes.

# COMMAND ----------

# MAGIC %pip install statsmodels

# COMMAND ----------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests
from statsmodels.tsa.api import VAR
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm
import statsmodels.formula.api as smf

rng = np.random.default_rng(42)

# COMMAND ----------

# MAGIC %md ## 1. Load data (weekly; quarterly kept at native frequency)

# COMMAND ----------

weekly = spark.sql("""
    SELECT week_start_date, total_events, avg_trend_score, total_articles, avg_media_tone
    FROM info_env_jordan.gold.unified_weekly_indicators
    WHERE week_start_date >= '2022-01-01' AND week_start_date < '2025-06-01'
    ORDER BY week_start_date
""").toPandas()
weekly['week_start_date'] = pd.to_datetime(weekly['week_start_date'])
weekly = weekly.set_index('week_start_date').astype(float)

quarterly = spark.sql("""
    SELECT year, quarter, total_events, avg_search_interest, total_articles,
           youth_unemployment, unemployment, gdp_growth, inflation
    FROM info_env_jordan.gold.quarterly_events_economics
    ORDER BY year, quarter
""").toPandas()

print(len(weekly), "weeks;", len(quarterly), "quarters")

# COMMAND ----------

# MAGIC %md ## 2. Descriptive checks (look before testing)

# COMMAND ----------

print(weekly.describe().T[['mean', '50%', 'std', 'min', 'max']])
print("\nSkewness:\n", weekly.skew().round(2))
print("\nMissing weeks:", pd.date_range(weekly.index.min(), weekly.index.max(), freq='7D').difference(weekly.index).size)

fig, axes = plt.subplots(len(weekly.columns), 1, figsize=(11, 9), sharex=True)
for ax, c in zip(axes, weekly.columns):
    ax.plot(weekly.index, weekly[c], lw=0.8)
    ax.set_ylabel(c, fontsize=8)
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md ## 3. Stationarity (ADF: H0 = unit root; KPSS: H0 = stationary)

# COMMAND ----------

def stationarity(s):
    s = s.dropna()
    return {'adf_p': adfuller(s, autolag='AIC')[1],
            'kpss_p': kpss(s, regression='c', nlags='auto')[1]}

rows = []
for c in weekly.columns:
    lvl = stationarity(weekly[c])
    dif = stationarity(weekly[c].diff())
    rows.append({'var': c, 'level_adf_p': lvl['adf_p'], 'level_kpss_p': lvl['kpss_p'],
                 'diff_adf_p': dif['adf_p'], 'diff_kpss_p': dif['kpss_p']})
print(pd.DataFrame(rows).round(4).to_string(index=False))

# COMMAND ----------

# MAGIC %md ## 4. Transform, difference, and reserve a holdout (last 20%)

# COMMAND ----------

tx = pd.DataFrame({
    'events': np.log1p(weekly['total_events']),
    'search': weekly['avg_trend_score'],
    'media': np.log1p(weekly['total_articles']),
})
tx_d = tx.diff().dropna()

split = int(len(tx_d) * 0.8)
explore, holdout = tx_d.iloc[:split], tx_d.iloc[split:]
print("explore weeks:", len(explore), "| holdout weeks:", len(holdout))

# COMMAND ----------

# MAGIC %md ## 5. Cross-correlations on differenced data: block-bootstrap CIs and FDR correction

# COMMAND ----------

def block_bootstrap_ci(x, y, n_boot=1000, block=8):
    n = len(x)
    nb = int(np.ceil(n / block))
    out = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        out[i] = stats.spearmanr(x[idx], y[idx])[0]
    return np.percentile(out, [2.5, 97.5])

def crosscorr(data, a, b, max_lag=4):
    """corr(a_t, b_{t+k}); k>0 means a leads b."""
    rows = []
    for k in range(-max_lag, max_lag + 1):
        x = data[a].shift(k).dropna()
        y = data[b].loc[x.index]
        rho, p = stats.spearmanr(x, y)
        r, _ = stats.pearsonr(x, y)
        lo, hi = block_bootstrap_ci(x.values, y.values)
        rows.append({'pair': f'{a}->{b}', 'k': k, 'spearman': rho, 'pearson': r,
                     'p': p, 'ci_lo': lo, 'ci_hi': hi, 'n': len(x)})
    df = pd.DataFrame(rows)
    df['p_fdr'] = multipletests(df['p'], method='fdr_bh')[1]
    return df

pairs = [('search', 'events'), ('media', 'events'), ('media', 'search')]
cc = pd.concat([crosscorr(explore, a, b) for a, b in pairs])
print(cc.round(3).to_string(index=False))

# COMMAND ----------

# MAGIC %md ## 6. Granger causality (H1, H2) on differenced series, both directions

# COMMAND ----------

def granger_table(data, cause, effect, maxlag=4):
    res = grangercausalitytests(data[[effect, cause]], maxlag=maxlag, verbose=False)
    return [{'cause': cause, 'effect': effect, 'lag': l,
             'F': res[l][0]['ssr_ftest'][0], 'p': res[l][0]['ssr_ftest'][1]} for l in res]

g = pd.DataFrame(sum([granger_table(explore, a, b) + granger_table(explore, b, a)
                      for a, b in [('search', 'events'), ('media', 'events')]], []))
g['p_fdr'] = multipletests(g['p'], method='fdr_bh')[1]
print(g.round(4).to_string(index=False))

var = VAR(explore).fit(maxlags=6, ic='aic')
print(var.summary())

# COMMAND ----------

# MAGIC %md ## 7. Count model for weekly events (handles overdispersion)
# MAGIC Negative binomial with lagged predictors and a time trend, HAC standard errors.

# COMMAND ----------

cm = weekly.copy()
cm['search_l1'] = cm['avg_trend_score'].shift(1)
cm['media_l1'] = np.log1p(cm['total_articles']).shift(1)
cm['events_l1'] = cm['total_events'].shift(1)
cm['t'] = np.arange(len(cm)) / 52.0
cm = cm.dropna()
cm_train = cm.iloc[:int(len(cm) * 0.8)]
cm_test = cm.iloc[int(len(cm) * 0.8):]

nb = smf.glm('total_events ~ search_l1 + media_l1 + events_l1 + t', data=cm_train,
             family=sm.families.NegativeBinomial()).fit(cov_type='HAC', cov_kwds={'maxlags': 4})
print(nb.summary())

base = smf.glm('total_events ~ events_l1 + t', data=cm_train,
               family=sm.families.NegativeBinomial()).fit()
mae = lambda m: np.mean(np.abs(cm_test['total_events'] - m.predict(cm_test)))
print(f"\nHoldout MAE  full model: {mae(nb):.2f} | baseline: {mae(base):.2f}")

# COMMAND ----------

# MAGIC %md ## 8. Economics at native quarterly frequency
# MAGIC n is small (~14 quarters): report CIs, not just p-values. No monthly forward-fill.

# COMMAND ----------

q = quarterly.copy()
for c in ['total_events', 'avg_search_interest', 'inflation', 'youth_unemployment', 'unemployment']:
    q[c + '_d'] = q[c].diff()
for c in ['total_events_d', 'avg_search_interest_d']:
    q[c + '_l1'] = q[c].shift(1)

def fisher_ci(r, n, alpha=0.05):
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
    zc = stats.norm.ppf(1 - alpha / 2)
    return np.tanh(z - zc * se), np.tanh(z + zc * se)

tests = [
    ('total_events_d_l1', 'inflation_d'),
    ('inflation_d', 'total_events_d'),
    ('total_events_d_l1', 'youth_unemployment_d'),
    ('youth_unemployment_d', 'total_events_d'),
    ('avg_search_interest_d_l1', 'inflation_d'),
]
rows = []
for x, y in tests:
    d = q[[x, y]].dropna()
    rho, p = stats.spearmanr(d[x], d[y])
    r, _ = stats.pearsonr(d[x], d[y])
    lo, hi = fisher_ci(r, len(d))
    rows.append({'x': x, 'y': y, 'n': len(d), 'pearson': r, 'ci_lo': lo, 'ci_hi': hi,
                 'spearman': rho, 'p_spearman': p})
qt = pd.DataFrame(rows)
qt['p_fdr'] = multipletests(qt['p_spearman'], method='fdr_bh')[1]
print(qt.round(3).to_string(index=False))
print("\nTreat as exploratory. Prefer monthly CPI from Jordan's Department of Statistics to raise n.")

# COMMAND ----------

# MAGIC %md ## 9. Permutation null for "best lag" selection
# MAGIC The original code reported the max |r| over 9 lags. This shows how large that max is under no relationship.

# COMMAND ----------

def max_abs_lag_corr(x, y, max_lag=4):
    best = 0
    for k in range(-max_lag, max_lag + 1):
        a = pd.Series(x).shift(k).dropna()
        b = pd.Series(y).iloc[a.index]
        best = max(best, abs(stats.spearmanr(a, b)[0]))
    return best

def circular_shift_null(x, y, n_perm=500):
    n = len(x)
    return np.array([max_abs_lag_corr(x, np.roll(y, rng.integers(8, n - 8))) for _ in range(n_perm)])

x, y = explore['search'].values, explore['events'].values
obs = max_abs_lag_corr(x, y)
null = circular_shift_null(x, y)
print(f"observed max|rho| = {obs:.3f}; permutation p = {(null >= obs).mean():.4f}")

# COMMAND ----------

# MAGIC %md ## 10. Confirmatory check on the holdout (pre-specified lag-1 Granger tests only)

# COMMAND ----------

hold_rows = []
for cause, effect in [('search', 'events'), ('events', 'search'), ('media', 'events'), ('events', 'media')]:
    r = grangercausalitytests(holdout[[effect, cause]], maxlag=1, verbose=False)[1][0]['ssr_ftest']
    hold_rows.append({'cause': cause, 'effect': effect, 'F': r[0], 'p': r[1]})
h = pd.DataFrame(hold_rows)
h['p_bonf'] = (h['p'] * len(h)).clip(upper=1)
print(h.round(4).to_string(index=False))
print("\nOnly claims that survive here (and the FDR correction above) belong in FINDINGS.md.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reporting rules
# MAGIC * Say "predicts / is associated with", never "drives", unless the design supports it (IV, diff-in-diff).
# MAGIC * Report effect size and CI with every p-value.
# MAGIC * Hand-code ~100 events to estimate `ai_classify()` accuracy before using theme splits.
# MAGIC * Add controls (global food/fuel prices, seasonality, COVID period) before any causal language.
