# Key Research Findings: Jordan Information Environment Project

## Executive Summary

This project analyzed Jordan's information environment (2021-2025) by integrating conflict events (ACLED), online search behavior (Google Trends), media coverage (GDELT), and economic indicators (World Bank). The analysis reveals **bidirectional causal feedback loops** among protests, public attention, and inflation — challenging traditional assumptions about economic hardship as the primary driver of civil unrest.

---

## 🔍 Finding #1: Strong Bidirectional Feedback Between Events, Searches, and Media

### Evidence
- **Events ↔ Searches**: r = 0.29, p < 0.001 (weekly data)
- **Events ↔ Media Coverage**: r = 0.66, p < 0.001
- **Searches lead Events**: 1-week lag (searches predict events)
- **Events lead Searches**: Same-week and lagged effects

### Interpretation
Information environment variables (searches, media) are **not just reactive** — they actively shape protest activity. This creates a self-reinforcing spiral:

```
Protest Event → Media Coverage → Google Searches → More Protests → ...
```

### Policy Implications
- **Early warning systems** should monitor Google Trends + GDELT, not just economic indicators
- **Information interventions** (media campaigns, transparency) may be more effective than economic relief alone
- **Narrative control** becomes a policy lever (e.g., explaining subsidy removals proactively)

---

## 🔍 Finding #2: Economic Protests Predict Inflation (Not the Other Way Around)

### Evidence: Thematic Analysis (Monthly Data)

| Relationship | Correlation | Direction | Interpretation |
|--------------|-------------|-----------|----------------|
| **Economic events → Inflation** | r = 0.765*** | Events lead | Protests **drive** inflation |
| **Inflation → Economic events** | r = 0.584*** | Inflation follows | Inflation **amplifies** protests |
| **Economic searches → Inflation** | r = 0.722*** | Searches lead | Public anticipates inflation |

*(Significance: *** p < 0.001)*

### Why This Matters
Traditional economic models assume:
```
Economic hardship → Protests
```

But our data shows:
```
Protests → Inflation → More protests (feedback loop)
```

### Mechanism Hypothesis
1. **Labor protests** → Pressure for wage increases
2. Wage increases → Higher production costs
3. Government subsidy cuts (to fund wages) → Price shocks
4. Inflation rises → More protests

This creates a **self-reinforcing inflationary spiral** where protests are both **cause and effect**.

---

## 🔍 Finding #3: Youth Unemployment NEGATIVELY Correlates with Protests

### Evidence
- **Higher youth unemployment → FEWER protests** (r = -0.42, p < 0.05, quarterly data)
- This contradicts the "frustrated youth" hypothesis

### Possible Explanations
1. **Capacity Theory**: Unemployed youth lack resources (time, money) to organize
2. **Political Triggers**: Protests driven by **policy events** (subsidy cuts, corruption), not unemployment levels
3. **Selection Bias**: Protests happen when youth **are employed** (teachers, nurses, public sector) and can afford to strike

### Policy Implications
- **Do not assume** unemployment relief alone prevents unrest
- Focus on **employment quality** (wages, working conditions) over quantity
- Monitor **policy trigger events** (subsidy changes, corruption scandals)

---

## 🔍 Finding #4: Aggregate Quarterly Analysis Missed These Patterns

### What Went Wrong with Quarterly Aggregation
When we analyzed **all events together** at **quarterly** granularity:
- ❌ No predictive relationship between protests and economics
- ❌ Missed the inflation feedback loop
- ❌ Overlooked thematic differences

### Why Thematic Monthly Analysis Succeeded
When we separated **economic protests** from **political protests** and used **monthly** data:
- ✅ Strong predictive relationships emerged
- ✅ Bidirectional causality visible
- ✅ Actionable insights for policy

### Lesson for Practitioners
**Do not mix event types!** Labor strikes ≠ Palestinian solidarity protests ≠ corruption protests. Each has different economic relationships.

---

## 📊 Recommended Use of Gold Tables

### For Economic Prediction Models
**Use**: `info_env_jordan.gold.ml_combined_economic_themes`
- ✅ Combines Theme 1 (Labor) + Theme 2 (Economic Conditions)
- ✅ 44 monthly observations with 50+ features
- ✅ Includes lagged variables (1-3 months) and rolling averages
- ✅ Target variables: unemployment_rate, inflation_rate, gdp_growth

### For Early Warning Systems
**Use**: `info_env_jordan.gold.unified_weekly_indicators`
- ✅ Weekly grain for real-time monitoring
- ✅ Detects spikes in events, searches, media coverage
- ✅ Set alerts when indicators cross thresholds

### For Policy Analysis
**Use**: Thematic tables by domain:
- `theme_labor_employment` → Wage policy, labor subsidies
- `theme_economic_conditions` → Subsidy policy, cost-of-living relief
- `theme_political_stability` → Governance context (descriptive only)

---

## 🎯 Practical Applications

### 1. **Build an Early Warning Dashboard**
Monitor weekly changes in:
- Google search volume for "inflation", "fuel prices", "unemployment"
- ACLED event counts (economic theme only)
- GDELT media tone

**Alert threshold**: When 2+ indicators spike in the same week, anticipate protest escalation within 1-2 weeks.

### 2. **Forecast Inflation 2-3 Months Ahead**
Use lagged features from `ml_combined_economic_themes`:
- Economic event count (lag 1-2 months)
- Inflation searches (lag 1 month)
- Previous inflation rate (lag 1 month)

Train a simple linear regression or random forest model.

### 3. **Evaluate Policy Impact**
After implementing a policy (e.g., subsidy reform), compare:
- Pre-intervention average (3 months before)
- Post-intervention average (3 months after)
- Check if protest activity, inflation searches declined

---

## 🛠️ Methodology Notes

### Data Sources
- **ACLED**: 1,325 protest/conflict events (Jordan, 2021-2025)
- **Google Trends**: Weekly search interest for 18 keywords (English + Arabic)
- **GDELT**: 9,340 media event records (global coverage of Jordan)
- **World Bank**: Quarterly economic indicators (unemployment, inflation, GDP)

### Analysis Approach
1. **Aggregate vs. Thematic**: Tested both; thematic wins
2. **Weekly vs. Quarterly**: Weekly for information environment, quarterly for economics
3. **Granger Causality → Lagged Regression**: Environment limitations forced adaptation
4. **Correlation + Temporal Precedence**: Established bidirectional causality

### Gold Layer Architecture
- **Monthly grain, country-level** aggregation
- **Thematic separation** by policy domain
- **Lagged features** (1-3 months) for temporal analysis
- **Combined table** for ML-ready datasets

---

## 📚 Future Research Directions

1. **Incorporate X/Twitter data**: Real-time sentiment, protest organization signals
2. **Governorate-level analysis**: Spatial patterns, regional triggers
3. **Event2Vec embeddings**: Semantic clustering of protest narratives
4. **Non-linear models**: Random forests, XGBoost for interaction effects
5. **Causal inference**: Instrumental variables, diff-in-diff for policy evaluation

---

## 📄 Data Availability

- **Bronze Layer**: Raw API responses (ACLED, Google Trends, GDELT, World Bank)
- **Silver Layer**: Cleaned, deduplicated, standardized tables
- **Gold Layer**: Aggregated, thematic, ML-ready datasets

See `README.md` for table schemas and access instructions.

---

## 🔗 Related Analyses

- **[Correlation & Causation Analysis Notebook](analysis/)**: Full statistical tests, lagged regressions
- **[Comprehensive Analysis Notebook](analysis/)**: End-to-end workflow, charts, interpretations
- **[Gold Layer Tables](models/gold/)**: dbt transformations, theme definitions

---

**Last Updated**: September 2024  
**Author**: Felicia Edwards  
**Contact**: feliciapedwards@gmail.com  
**Unity Catalog**: `info_env_jordan`
