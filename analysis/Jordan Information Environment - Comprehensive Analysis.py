# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Overview
# MAGIC %md
# MAGIC # Jordan Information Environment - Comprehensive Analysis
# MAGIC
# MAGIC This notebook combines **all 4 data sources** to answer critical questions about Jordan's information environment:
# MAGIC
# MAGIC ## Data Sources:
# MAGIC 1. **GDELT Media Coverage** - Topics, article counts, and sentiment tone
# MAGIC 2. **Google Trends** - Search interest for economic and political keywords  
# MAGIC 3. **ACLED Events** - Protests, demonstrations, violence, and strategic developments
# MAGIC 4. **World Bank Economic Indicators** - Youth unemployment rates
# MAGIC
# MAGIC ## Key Questions:
# MAGIC 1. Have economic indicators worsened in Jordan over the last 5 years?
# MAGIC 2. Are protest or unrest events increasing?
# MAGIC 3. Are events concentrated in certain cities or regions?
# MAGIC 4. Does media attention rise around economic or political stress?
# MAGIC 5. What risks or implications should decision-makers watch?

# COMMAND ----------

# DBTITLE 1,Create Unified Weekly Dataset
# MAGIC %sql
# MAGIC -- Create unified weekly dataset combining all 4 data sources
# MAGIC CREATE OR REPLACE TABLE info_env_jordan.gold.unified_weekly_indicators
# MAGIC COMMENT 'Unified weekly view: media, trends, events, and economic indicators'
# MAGIC AS
# MAGIC WITH weekly_spine AS (
# MAGIC   SELECT DISTINCT 
# MAGIC     DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
# MAGIC     YEAR(event_date) AS year,
# MAGIC     WEEKOFYEAR(event_date) AS week
# MAGIC   FROM info_env_jordan.silver.acled_jordan_events
# MAGIC   WHERE event_date >= '2020-01-01'
# MAGIC ),
# MAGIC media_weekly AS (
# MAGIC   SELECT 
# MAGIC     DATE_TRUNC('WEEK', article_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
# MAGIC     COUNT(DISTINCT topic) AS topic_count,
# MAGIC     SUM(article_count) AS total_articles,
# MAGIC     AVG(avg_tone) AS avg_media_tone,
# MAGIC     MIN(avg_tone) AS min_tone,
# MAGIC     MAX(avg_tone) AS max_tone
# MAGIC   FROM info_env_jordan.silver.gdelt_jordan_topics
# MAGIC   WHERE article_date >= '2020-01-01'
# MAGIC   GROUP BY DATE_TRUNC('WEEK', article_date + INTERVAL 1 DAY) - INTERVAL 1 DAY
# MAGIC ),
# MAGIC trends_weekly AS (
# MAGIC   SELECT 
# MAGIC     DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
# MAGIC     COUNT(DISTINCT search_term) AS search_terms_count,
# MAGIC     AVG(trend_score) AS avg_trend_score,
# MAGIC     MAX(trend_score) AS max_trend_score,
# MAGIC     AVG(CASE WHEN search_term IN ('unemployment', 'inflation', 'economy', 'prices') THEN trend_score ELSE 0 END) AS economic_search_intensity
# MAGIC   FROM info_env_jordan.silver.google_trends
# MAGIC   WHERE event_date >= '2020-01-01'
# MAGIC   GROUP BY DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY
# MAGIC ),
# MAGIC events_weekly AS (
# MAGIC   SELECT 
# MAGIC     DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
# MAGIC     COUNT(*) AS total_events,
# MAGIC     SUM(fatalities) AS total_fatalities,
# MAGIC     SUM(CASE WHEN disorder_type = 'Demonstrations' THEN 1 ELSE 0 END) AS demonstrations_count,
# MAGIC     SUM(CASE WHEN disorder_type = 'Political violence' THEN 1 ELSE 0 END) AS political_violence_count,
# MAGIC     SUM(CASE WHEN disorder_type = 'Strategic developments' THEN 1 ELSE 0 END) AS strategic_dev_count,
# MAGIC     SUM(CASE WHEN event_type = 'Protests' THEN 1 ELSE 0 END) AS protests_count,
# MAGIC     SUM(CASE WHEN event_type = 'Riots' THEN 1 ELSE 0 END) AS riots_count,
# MAGIC     COUNT(DISTINCT admin1) AS affected_governorates
# MAGIC   FROM info_env_jordan.silver.acled_jordan_events
# MAGIC   WHERE event_date >= '2020-01-01'
# MAGIC   GROUP BY DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY
# MAGIC )
# MAGIC SELECT 
# MAGIC   s.week_start_date,
# MAGIC   s.year,
# MAGIC   s.week,
# MAGIC   COALESCE(m.topic_count, 0) AS media_topic_count,
# MAGIC   COALESCE(m.total_articles, 0) AS total_articles,
# MAGIC   m.avg_media_tone,
# MAGIC   m.min_tone,
# MAGIC   m.max_tone,
# MAGIC   COALESCE(t.search_terms_count, 0) AS search_terms_count,
# MAGIC   t.avg_trend_score,
# MAGIC   t.max_trend_score,
# MAGIC   t.economic_search_intensity,
# MAGIC   COALESCE(e.total_events, 0) AS total_events,
# MAGIC   COALESCE(e.total_fatalities, 0) AS total_fatalities,
# MAGIC   COALESCE(e.demonstrations_count, 0) AS demonstrations_count,
# MAGIC   COALESCE(e.political_violence_count, 0) AS political_violence_count,
# MAGIC   COALESCE(e.strategic_dev_count, 0) AS strategic_dev_count,
# MAGIC   COALESCE(e.protests_count, 0) AS protests_count,
# MAGIC   COALESCE(e.riots_count, 0) AS riots_count,
# MAGIC   COALESCE(e.affected_governorates, 0) AS affected_governorates,
# MAGIC   CURRENT_TIMESTAMP() AS processed_at
# MAGIC FROM weekly_spine s
# MAGIC LEFT JOIN media_weekly m ON s.week_start_date = m.week_start_date
# MAGIC LEFT JOIN trends_weekly t ON s.week_start_date = t.week_start_date
# MAGIC LEFT JOIN events_weekly e ON s.week_start_date = e.week_start_date
# MAGIC ORDER BY s.week_start_date;

# COMMAND ----------

# DBTITLE 1,Q1 Header
# MAGIC %md
# MAGIC ## Question 1: Have economic indicators worsened in Jordan over the last 5 years?

# COMMAND ----------

# DBTITLE 1,Q1: Youth Unemployment Trends
# MAGIC %sql
# MAGIC -- Analyze youth unemployment trends (2020-2025)
# MAGIC SELECT 
# MAGIC   CAST(year AS INT) AS year,
# MAGIC   ROUND(AVG(value), 2) AS avg_youth_unemployment_rate
# MAGIC FROM info_env_jordan.bronze.unemployment_youth
# MAGIC WHERE CAST(year AS INT) >= 2020 
# MAGIC   AND CAST(year AS INT) <= 2025
# MAGIC   AND country_name = 'Jordan'
# MAGIC GROUP BY CAST(year AS INT)
# MAGIC ORDER BY year;

# COMMAND ----------

# DBTITLE 1,Q1: Economic Search Interest
# MAGIC %sql
# MAGIC -- Economic search intensity trend from Google Trends
# MAGIC SELECT 
# MAGIC   year,
# MAGIC   ROUND(AVG(economic_search_intensity), 2) AS avg_economic_search,
# MAGIC   ROUND(AVG(avg_trend_score), 2) AS avg_overall_search_interest,
# MAGIC   COUNT(*) AS weeks_with_data
# MAGIC FROM info_env_jordan.gold.unified_weekly_indicators
# MAGIC WHERE year >= 2020
# MAGIC GROUP BY year
# MAGIC ORDER BY year;

# COMMAND ----------

# DBTITLE 1,Q2 Header
# MAGIC %md
# MAGIC ## Question 2: Are protest or unrest events increasing?

# COMMAND ----------

# DBTITLE 1,Q2: Yearly Event Trends
# MAGIC %sql
# MAGIC -- Analyze yearly trends in protests, demonstrations, and violence
# MAGIC SELECT 
# MAGIC   year,
# MAGIC   SUM(total_events) AS total_events,
# MAGIC   SUM(demonstrations_count) AS total_demonstrations,
# MAGIC   SUM(protests_count) AS total_protests,
# MAGIC   SUM(riots_count) AS total_riots,
# MAGIC   SUM(political_violence_count) AS total_political_violence,
# MAGIC   SUM(total_fatalities) AS total_fatalities,
# MAGIC   ROUND(AVG(total_events), 1) AS avg_weekly_events,
# MAGIC   -- Year-over-year change
# MAGIC   ROUND(
# MAGIC     100.0 * (SUM(total_events) - LAG(SUM(total_events)) OVER (ORDER BY year)) / 
# MAGIC     NULLIF(LAG(SUM(total_events)) OVER (ORDER BY year), 0), 1
# MAGIC   ) AS yoy_change_pct
# MAGIC FROM info_env_jordan.gold.unified_weekly_indicators
# MAGIC WHERE year >= 2020
# MAGIC GROUP BY year
# MAGIC ORDER BY year;

# COMMAND ----------

# DBTITLE 1,Q3 Header
# MAGIC %md
# MAGIC ## Question 3: Are events concentrated in certain cities or regions?

# COMMAND ----------

# DBTITLE 1,Q3: Geographic Distribution
# MAGIC %sql
# MAGIC -- Geographic distribution of events by governorate
# MAGIC SELECT 
# MAGIC   admin1 AS governorate,
# MAGIC   COUNT(*) AS total_events,
# MAGIC   SUM(fatalities) AS total_fatalities,
# MAGIC   SUM(CASE WHEN disorder_type = 'Demonstrations' THEN 1 ELSE 0 END) AS demonstrations,
# MAGIC   SUM(CASE WHEN disorder_type = 'Political violence' THEN 1 ELSE 0 END) AS political_violence,
# MAGIC   ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total_events,
# MAGIC   COUNT(DISTINCT location) AS unique_locations,
# MAGIC   COUNT(DISTINCT YEAR(event_date)) AS years_active
# MAGIC FROM info_env_jordan.silver.acled_jordan_events
# MAGIC WHERE event_date >= '2020-01-01'
# MAGIC   AND admin1 IS NOT NULL
# MAGIC GROUP BY admin1
# MAGIC ORDER BY total_events DESC
# MAGIC LIMIT 15;

# COMMAND ----------

# DBTITLE 1,Q4 Header
# MAGIC %md
# MAGIC ## Question 4: Does media attention rise around economic or political stress?

# COMMAND ----------

# DBTITLE 1,Q4: Media vs Stress Correlation
# MAGIC %sql
# MAGIC -- Correlate media coverage with stress events
# MAGIC WITH monthly_agg AS (
# MAGIC   SELECT 
# MAGIC     DATE_TRUNC('MONTH', week_start_date) AS month,
# MAGIC     AVG(total_articles) AS avg_articles,
# MAGIC     AVG(avg_media_tone) AS avg_tone,
# MAGIC     SUM(total_events) AS total_events,
# MAGIC     SUM(demonstrations_count) AS demonstrations,
# MAGIC     AVG(economic_search_intensity) AS economic_search,
# MAGIC     CASE 
# MAGIC       WHEN SUM(total_events) > 10 OR AVG(economic_search_intensity) > 20 
# MAGIC       THEN 'High Stress' 
# MAGIC       ELSE 'Normal' 
# MAGIC     END AS stress_level
# MAGIC   FROM info_env_jordan.gold.unified_weekly_indicators
# MAGIC   WHERE year >= 2020
# MAGIC   GROUP BY DATE_TRUNC('MONTH', week_start_date)
# MAGIC )
# MAGIC SELECT 
# MAGIC   stress_level,
# MAGIC   COUNT(*) AS months_count,
# MAGIC   ROUND(AVG(avg_articles), 1) AS avg_articles_per_week,
# MAGIC   ROUND(AVG(avg_tone), 2) AS avg_media_tone,
# MAGIC   ROUND(AVG(total_events), 1) AS avg_events_per_month,
# MAGIC   ROUND(AVG(economic_search), 1) AS avg_economic_search_intensity
# MAGIC FROM monthly_agg
# MAGIC GROUP BY stress_level
# MAGIC ORDER BY stress_level DESC;

# COMMAND ----------

# DBTITLE 1,Q5 Header
# MAGIC %md
# MAGIC ## Question 5: What risks or implications should decision-makers watch?

# COMMAND ----------

# DBTITLE 1,Q5: Leading Risk Indicators
# MAGIC %sql
# MAGIC -- Recent trends dashboard (last 12 weeks vs previous 12 weeks)
# MAGIC WITH recent_trends AS (
# MAGIC   SELECT 
# MAGIC     AVG(CASE WHEN week_start_date >= CURRENT_DATE - INTERVAL 12 WEEKS THEN total_events END) AS recent_events,
# MAGIC     AVG(CASE WHEN week_start_date BETWEEN CURRENT_DATE - INTERVAL 24 WEEKS AND CURRENT_DATE - INTERVAL 12 WEEKS THEN total_events END) AS prior_events,
# MAGIC     AVG(CASE WHEN week_start_date >= CURRENT_DATE - INTERVAL 12 WEEKS THEN avg_media_tone END) AS recent_tone,
# MAGIC     AVG(CASE WHEN week_start_date BETWEEN CURRENT_DATE - INTERVAL 24 WEEKS AND CURRENT_DATE - INTERVAL 12 WEEKS THEN avg_media_tone END) AS prior_tone,
# MAGIC     AVG(CASE WHEN week_start_date >= CURRENT_DATE - INTERVAL 12 WEEKS THEN economic_search_intensity END) AS recent_econ,
# MAGIC     AVG(CASE WHEN week_start_date BETWEEN CURRENT_DATE - INTERVAL 24 WEEKS AND CURRENT_DATE - INTERVAL 12 WEEKS THEN economic_search_intensity END) AS prior_econ,
# MAGIC     AVG(CASE WHEN week_start_date >= CURRENT_DATE - INTERVAL 12 WEEKS THEN demonstrations_count END) AS recent_demos,
# MAGIC     AVG(CASE WHEN week_start_date BETWEEN CURRENT_DATE - INTERVAL 24 WEEKS AND CURRENT_DATE - INTERVAL 12 WEEKS THEN demonstrations_count END) AS prior_demos
# MAGIC   FROM info_env_jordan.gold.unified_weekly_indicators
# MAGIC   WHERE year >= 2024
# MAGIC )
# MAGIC SELECT 
# MAGIC   'Events Activity' AS indicator,
# MAGIC   ROUND(recent_events, 1) AS recent_12_weeks,
# MAGIC   ROUND(prior_events, 1) AS prior_12_weeks,
# MAGIC   ROUND(100.0 * (recent_events - prior_events) / NULLIF(prior_events, 0), 1) AS change_pct,
# MAGIC   CASE 
# MAGIC     WHEN (recent_events - prior_events) / NULLIF(prior_events, 0) > 0.2 THEN '⚠️ Rising'
# MAGIC     WHEN (recent_events - prior_events) / NULLIF(prior_events, 0) < -0.2 THEN '✓ Declining'
# MAGIC     ELSE '→ Stable'
# MAGIC   END AS trend
# MAGIC FROM recent_trends
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC   'Media Tone',
# MAGIC   ROUND(recent_tone, 2),
# MAGIC   ROUND(prior_tone, 2),
# MAGIC   ROUND(100.0 * (recent_tone - prior_tone) / NULLIF(ABS(prior_tone), 0), 1),
# MAGIC   CASE 
# MAGIC     WHEN recent_tone < prior_tone THEN '⚠️ More Negative'
# MAGIC     WHEN recent_tone > prior_tone THEN '✓ More Positive'
# MAGIC     ELSE '→ Stable'
# MAGIC   END
# MAGIC FROM recent_trends
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC   'Economic Search Interest',
# MAGIC   ROUND(recent_econ, 1),
# MAGIC   ROUND(prior_econ, 1),
# MAGIC   ROUND(100.0 * (recent_econ - prior_econ) / NULLIF(prior_econ, 0), 1),
# MAGIC   CASE 
# MAGIC     WHEN (recent_econ - prior_econ) / NULLIF(prior_econ, 0) > 0.2 THEN '⚠️ Rising Concern'
# MAGIC     WHEN (recent_econ - prior_econ) / NULLIF(prior_econ, 0) < -0.2 THEN '✓ Declining Concern'
# MAGIC     ELSE '→ Stable'
# MAGIC   END
# MAGIC FROM recent_trends
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC   'Demonstrations',
# MAGIC   ROUND(recent_demos, 1),
# MAGIC   ROUND(prior_demos, 1),
# MAGIC   ROUND(100.0 * (recent_demos - prior_demos) / NULLIF(prior_demos, 0), 1),
# MAGIC   CASE 
# MAGIC     WHEN (recent_demos - prior_demos) / NULLIF(prior_demos, 0) > 0.2 THEN '⚠️ Rising'
# MAGIC     WHEN (recent_demos - prior_demos) / NULLIF(prior_demos, 0) < -0.2 THEN '✓ Declining'
# MAGIC     ELSE '→ Stable'
# MAGIC   END
# MAGIC FROM recent_trends;

# COMMAND ----------

# DBTITLE 1,Geographic Visualization
# MAGIC %md
# MAGIC ## Geographic Map: Event Locations in Jordan

# COMMAND ----------

# DBTITLE 1,Load Event Location Data
# Load event data with coordinates
events_df = spark.sql("""
  SELECT 
    event_id_cnty,
    event_date,
    location,
    admin1 AS governorate,
    disorder_type,
    event_type,
    fatalities,
    latitude,
    longitude
  FROM info_env_jordan.silver.acled_jordan_events
  WHERE event_date >= '2020-01-01'
    AND latitude IS NOT NULL
    AND longitude IS NOT NULL
    AND latitude != 0
    AND longitude != 0
""").toPandas()

print(f"Loaded {len(events_df):,} events with valid coordinates")
display(events_df.head())

# COMMAND ----------

# DBTITLE 1,Create Interactive Map
import plotly.express as px
import pandas as pd

# Create a map with event locations
fig = px.scatter_mapbox(
    events_df,
    lat="latitude",
    lon="longitude",
    color="disorder_type",
    hover_name="location",
    hover_data={
        "governorate": True,
        "event_type": True,
        "fatalities": True,
        "event_date": True,
        "latitude": False,
        "longitude": False
    },
    size_max=15,
    zoom=6,
    title="Jordan Events Map (2020-2025)",
    color_discrete_map={
        "Demonstrations": "#1f77b4",
        "Political violence": "#d62728",
        "Strategic developments": "#2ca02c"
    },
    mapbox_style="open-street-map",
    height=700
)

fig.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0},
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255, 255, 255, 0.8)"
    )
)

fig.show()

# COMMAND ----------

# DBTITLE 1,Event Density Heatmap
# Create a density heatmap showing event concentration
fig_density = px.density_mapbox(
    events_df,
    lat="latitude",
    lon="longitude",
    radius=10,
    zoom=6,
    mapbox_style="open-street-map",
    title="Event Density Heatmap - Jordan (2020-2025)",
    height=700,
    color_continuous_scale="YlOrRd"
)

fig_density.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0}
)

fig_density.show()

# COMMAND ----------

# DBTITLE 1,Key Findings Summary
# MAGIC %md
# MAGIC ---
# MAGIC ## 📊 Key Findings Summary
# MAGIC
# MAGIC ### 1️⃣ Economic Indicators Show Improvement
# MAGIC * **Youth unemployment declined from 43.9% (2021 peak) to 38.9% (2025)** — a 5 percentage point improvement
# MAGIC * Unemployment peaked during COVID-19 recovery period (2021) and has steadily declined since
# MAGIC * However, youth unemployment remains **critically high at nearly 40%**, still above pre-pandemic levels
# MAGIC
# MAGIC ### 2️⃣ Protest Activity Has Sharply Declined
# MAGIC * **2022-2023**: Peak unrest period with ~850 events per year (9-10 events/week)
# MAGIC * **2024**: Dramatic 45% drop to 457 events
# MAGIC * **2025**: Further 86% decline to just 65 events (3.3 events/week)
# MAGIC * **Fatalities decreased** from 27 (2022) to 6 (2024) to 0 (2025 so far)
# MAGIC * **Riot activity nearly eliminated**: 96 riots (2022) → 15 (2024) → 0 (2025)
# MAGIC
# MAGIC ### 3️⃣ Events Heavily Concentrated in Urban Centers
# MAGIC * **Amman dominates** with 41.5% of all events (544 total)
# MAGIC * **Irbid** accounts for 14.6% (192 events)
# MAGIC * **Southern governorates** (Maan, Al Karak, At Tafilah) show significant activity despite smaller populations
# MAGIC * Only 4 fatalities in Amman despite highest event count — most demonstrations are peaceful
# MAGIC
# MAGIC ### 4️⃣ Media Attention Correlates with Stress Events
# MAGIC * **High stress periods**: 2,223 articles/week with more negative tone (-1.64)
# MAGIC * **Normal periods**: 1,575 articles/week with less negative tone (-1.38)
# MAGIC * Media coverage increases ~41% during periods of heightened unrest
# MAGIC * 38 out of 42 months analyzed were classified as "High Stress"
# MAGIC
# MAGIC ### 5️⃣ Current Situation Appears Stable
# MAGIC * Recent trend indicators show stable conditions across all metrics
# MAGIC * However, **note**: Recent data may be incomplete, limiting near-term assessment
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Critical Questions for Deeper Analysis
# MAGIC %md
# MAGIC ## 🔍 Critical Questions for Deeper Analysis
# MAGIC
# MAGIC ### **Causality & Drivers**
# MAGIC 1. **What specific policy changes or interventions caused the 86% drop in protests between 2023-2025?**
# MAGIC    * Government reforms? Economic stimulus? Security measures?
# MAGIC    
# MAGIC 2. **Which actors and organizations are driving demonstrations?**
# MAGIC    * Labor unions? Student groups? Political parties? Tribal networks?
# MAGIC    
# MAGIC 3. **What are the specific grievances mentioned in protest events?**
# MAGIC    * Fuel prices? Bread prices? Tax policy? Corruption? Water access?
# MAGIC
# MAGIC ### **Regional Context & Spillover**
# MAGIC 4. **How do regional conflicts (Gaza, Syria, Iraq) impact Jordan's stability?**
# MAGIC    * Refugee flows? Economic pressure? Ideological contagion?
# MAGIC    
# MAGIC 5. **Are there border region patterns?** 
# MAGIC    * Events near Syrian border vs. Saudi border vs. Palestinian territories?
# MAGIC    
# MAGIC 6. **What role does external media (Al Jazeera, regional outlets) play vs. domestic media?**
# MAGIC
# MAGIC ### **Temporal Dynamics**
# MAGIC 7. **What is the lag time between economic stress signals and protest activity?**
# MAGIC    * Do price increases predict protests 2 weeks later? 2 months later?
# MAGIC    
# MAGIC 8. **Are there seasonal patterns?** 
# MAGIC    * Summer heat? Ramadan? Academic calendar? Budget cycles?
# MAGIC    
# MAGIC 9. **What happened in Q3-Q4 2022 to trigger the peak?**
# MAGIC    * Fuel subsidy cuts? Bread price increases? Political events?
# MAGIC
# MAGIC ### **Government Response & Resilience**
# MAGIC 10. **How does government response correlate with escalation/de-escalation?**
# MAGIC     * Arrests? Negotiations? Concessions? Media blackouts?
# MAGIC     
# MAGIC 11. **Which governorates have the most effective conflict resolution mechanisms?**
# MAGIC     * Why does Amman have low fatalities despite high event counts?
# MAGIC     
# MAGIC 12. **What is the government's early warning and response capacity?**
# MAGIC
# MAGIC ### **Topic & Narrative Analysis**
# MAGIC 13. **Which specific topics dominate media coverage during stress periods?**
# MAGIC     * Economic issues? Corruption? Foreign policy? Domestic politics?
# MAGIC     
# MAGIC 14. **What narratives emerge on social media vs. traditional media?**
# MAGIC     * Twitter/X trends? Facebook groups? WhatsApp circulation?
# MAGIC     
# MAGIC 15. **Are there coordinated information campaigns (domestic or foreign)?**
# MAGIC
# MAGIC ### **Vulnerable Groups & Equity**
# MAGIC 16. **Beyond youth unemployment, what about women's employment and wage gaps?**
# MAGIC     
# MAGIC 17. **How do urban vs. rural populations experience economic stress differently?**
# MAGIC     
# MAGIC 18. **What is the situation for Syrian refugees and impact on local job markets?**
# MAGIC
# MAGIC ### **Forward-Looking Risk Indicators**
# MAGIC 19. **What are leading indicators that predict protests 4-8 weeks ahead?**
# MAGIC     * Commodity prices? Google search spikes? Social media sentiment?
# MAGIC     
# MAGIC 20. **What scenario planning should decision-makers prepare for?**
# MAGIC     * Oil price shocks? Regional war escalation? Climate-driven water crisis?

# COMMAND ----------

# DBTITLE 1,Recommended Next Steps
# MAGIC %md
# MAGIC ## 🚀 Recommended Next Steps
# MAGIC
# MAGIC ### **Immediate Data Enhancements**
# MAGIC
# MAGIC **1. Add Actor/Organization Data**
# MAGIC ```sql
# MAGIC -- Identify which groups are organizing protests
# MAGIC SELECT actor1, actor2, associated_actor_1,
# MAGIC        COUNT(*) as event_count,
# MAGIC        disorder_type
# MAGIC FROM info_env_jordan.silver.acled_jordan_events
# MAGIC GROUP BY actor1, actor2, associated_actor_1, disorder_type
# MAGIC ORDER BY event_count DESC
# MAGIC ```
# MAGIC
# MAGIC **2. Extract Grievances from Event Notes**
# MAGIC ```sql
# MAGIC -- Text analysis of event notes to identify issues
# MAGIC SELECT notes, event_type, event_date
# MAGIC FROM info_env_jordan.silver.acled_jordan_events
# MAGIC WHERE notes IS NOT NULL
# MAGIC ORDER BY event_date DESC
# MAGIC ```
# MAGIC
# MAGIC **3. Add Commodity Price Data**
# MAGIC * Fuel prices (diesel, gasoline)
# MAGIC * Bread/wheat prices
# MAGIC * Electricity tariffs
# MAGIC * Water costs
# MAGIC
# MAGIC **4. Time-Lag Correlation Analysis**
# MAGIC ```python
# MAGIC # Calculate correlations with different lag periods
# MAGIC for lag_weeks in [1, 2, 4, 8, 12]:
# MAGIC     correlation = calculate_correlation(
# MAGIC         economic_indicators.shift(lag_weeks),
# MAGIC         protest_counts
# MAGIC     )
# MAGIC ```
# MAGIC
# MAGIC **5. Seasonal Decomposition**
# MAGIC ```python
# MAGIC # Identify seasonal patterns in protest activity
# MAGIC from statsmodels.tsa.seasonal import seasonal_decompose
# MAGIC result = seasonal_decompose(weekly_events, model='additive', period=52)
# MAGIC ```
# MAGIC
# MAGIC ### **Strategic Monitoring Dashboard**
# MAGIC
# MAGIC Create real-time alerts for:
# MAGIC * **Economic stress signals**: Unemployment > 40%, fuel price increases > 10%
# MAGIC * **Event velocity**: Week-over-week protest increase > 50%
# MAGIC * **Geographic clustering**: 3+ events in same governorate within 7 days
# MAGIC * **Media tone shifts**: Average tone drops below -2.0
# MAGIC * **Search interest spikes**: Economic keyword searches increase > 30%
# MAGIC
# MAGIC ### **Stakeholder-Specific Outputs**
# MAGIC
# MAGIC **For Policy Makers:**
# MAGIC * Monthly stability index (composite score 0-100)
# MAGIC * Early warning alerts (2-4 week lead time)
# MAGIC * Regional risk heat maps
# MAGIC
# MAGIC **For Analysts:**
# MAGIC * Event narratives & actor networks
# MAGIC * Scenario modeling tools
# MAGIC * Comparative regional analysis
# MAGIC
# MAGIC **For Operational Teams:**
# MAGIC * Daily event tracking
# MAGIC * Real-time media monitoring
# MAGIC * Geographic response prioritization