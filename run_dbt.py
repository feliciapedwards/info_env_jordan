# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Run dbt - Jordan Info Environment
# MAGIC %md
# MAGIC # Run dbt Models
# MAGIC
# MAGIC This notebook executes dbt transformations for the Jordan Information Environment project.
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Bronze tables must be populated (run ingestion notebooks first)
# MAGIC - SQL warehouse must be running
# MAGIC - Environment variables configured below

# COMMAND ----------

# DBTITLE 1,Install dbt-databricks
# MAGIC %pip install dbt-databricks --quiet
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Configure dbt Connection
import os

# IMPORTANT: Update the warehouse ID below!
# To find your warehouse ID:
# 1. Go to SQL Warehouses in the sidebar
# 2. Click on your warehouse
# 3. Copy the ID from the URL (after /sql/warehouses/)
# 4. Paste it below

WAREHOUSE_ID = 'bcc51c1c0180574d'  # Serverless Starter Warehouse

# Set Databricks connection parameters
os.environ['DBT_DATABRICKS_HOST'] = spark.conf.get('spark.databricks.workspaceUrl')
os.environ['DBT_DATABRICKS_HTTP_PATH'] = f'/sql/1.0/warehouses/{WAREHOUSE_ID}'
os.environ['DBT_DATABRICKS_TOKEN'] = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

print("✓ Environment variables configured")
print(f"  Host: {os.environ['DBT_DATABRICKS_HOST']}")
print(f"  HTTP Path: {os.environ['DBT_DATABRICKS_HTTP_PATH']}")

if WAREHOUSE_ID == 'YOUR_WAREHOUSE_ID':
    print("\n⚠️  WARNING: You need to update the WAREHOUSE_ID above!")
    print("   Go to SQL Warehouses → Click your warehouse → Copy ID from URL")

# COMMAND ----------

# DBTITLE 1,Test dbt Connection
import subprocess

project_dir = '/Workspace/Users/feliciapedwards@gmail.com/Jordan Information Environment Project'

print("Testing dbt connection...")
result = subprocess.run(
    ['dbt', 'debug', '--project-dir', project_dir],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode != 0:
    print("❌ Error:", result.stderr)

# COMMAND ----------

# DBTITLE 1,Run All dbt Models
import subprocess

project_dir = '/Workspace/Users/feliciapedwards@gmail.com/Jordan Information Environment Project'

print("Running dbt models...\n")
result = subprocess.run(
    ['dbt', 'run', '--project-dir', project_dir],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode == 0:
    print("\n✓ All models ran successfully!")
else:
    print("\n❌ Error:", result.stderr)

# COMMAND ----------

# DBTITLE 1,Run dbt Tests
import subprocess

project_dir = '/Workspace/Users/feliciapedwards@gmail.com/Jordan Information Environment Project'

print("Running dbt data quality tests...\n")
result = subprocess.run(
    ['dbt', 'test', '--project-dir', project_dir],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode == 0:
    print("\n✓ All tests passed!")
else:
    print("\n⚠️ Some tests failed. Review output above.")

# COMMAND ----------

# DBTITLE 1,Run Specific Model
import subprocess

project_dir = '/Workspace/Users/feliciapedwards@gmail.com/Jordan Information Environment Project'
model_name = 'economic_indicators_monthly'  # Change this to run different models

print(f"Running model: {model_name}...\n")
result = subprocess.run(
    ['dbt', 'run', '--select', model_name, '--project-dir', project_dir],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode == 0:
    print(f"\n✓ Model {model_name} ran successfully!")
else:
    print("\n❌ Error:", result.stderr)

# COMMAND ----------

# DBTITLE 1,Verify Results
# MAGIC %sql
# MAGIC -- Check row counts in silver tables created by dbt
# MAGIC SELECT 'gdelt_jordan_topics' AS table_name, COUNT(*) AS row_count 
# MAGIC FROM info_env_jordan.silver.gdelt_jordan_topics
# MAGIC UNION ALL
# MAGIC SELECT 'google_trends', COUNT(*) 
# MAGIC FROM info_env_jordan.silver.google_trends
# MAGIC UNION ALL  
# MAGIC SELECT 'acled_jordan_events', COUNT(*) 
# MAGIC FROM info_env_jordan.silver.acled_jordan_events

# COMMAND ----------

# DBTITLE 1,View AI Classification Confidence Scores
# MAGIC %sql
# MAGIC -- Preview the new confidence scores from ai_classify v2.1
# MAGIC SELECT 
# MAGIC   event_id_cnty,
# MAGIC   event_date,
# MAGIC   event_type,
# MAGIC   notes,
# MAGIC   
# MAGIC   -- Primary classification with confidence
# MAGIC   primary_cause,
# MAGIC   ROUND(primary_cause_confidence, 3) AS primary_conf,
# MAGIC   
# MAGIC   -- Specific classification with confidence
# MAGIC   specific_primary_cause,
# MAGIC   ROUND(specific_primary_cause_confidence, 3) AS specific_conf
# MAGIC   
# MAGIC FROM info_env_jordan.silver.acled_jordan_events
# MAGIC WHERE event_date >= '2024-01-01'
# MAGIC ORDER BY event_date DESC
# MAGIC LIMIT 15

# COMMAND ----------

# DBTITLE 1,Analyze Confidence Score Distribution
# MAGIC %sql
# MAGIC -- Analyze confidence score distribution and identify low-confidence classifications
# MAGIC
# MAGIC -- Overall confidence statistics
# MAGIC SELECT 
# MAGIC   'Primary Cause' AS classification_type,
# MAGIC   ROUND(AVG(primary_cause_confidence), 3) AS avg_confidence,
# MAGIC   ROUND(MIN(primary_cause_confidence), 3) AS min_confidence,
# MAGIC   ROUND(MAX(primary_cause_confidence), 3) AS max_confidence,
# MAGIC   ROUND(STDDEV(primary_cause_confidence), 3) AS std_dev,
# MAGIC   SUM(CASE WHEN primary_cause_confidence < 0.7 THEN 1 ELSE 0 END) AS low_confidence_count,
# MAGIC   COUNT(*) AS total_events
# MAGIC FROM info_env_jordan.silver.acled_jordan_events
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'Specific Cause',
# MAGIC   ROUND(AVG(specific_primary_cause_confidence), 3),
# MAGIC   ROUND(MIN(specific_primary_cause_confidence), 3),
# MAGIC   ROUND(MAX(specific_primary_cause_confidence), 3),
# MAGIC   ROUND(STDDEV(specific_primary_cause_confidence), 3),
# MAGIC   SUM(CASE WHEN specific_primary_cause_confidence < 0.7 THEN 1 ELSE 0 END),
# MAGIC   COUNT(*)
# MAGIC FROM info_env_jordan.silver.acled_jordan_events

# COMMAND ----------

# DBTITLE 1,Review Low Confidence Classifications
# MAGIC %sql
# MAGIC -- Events with low confidence scores that may need manual review
# MAGIC -- Threshold: confidence < 0.70 on either classification
# MAGIC
# MAGIC SELECT 
# MAGIC   event_date,
# MAGIC   event_type,
# MAGIC   
# MAGIC   -- Show both classifications and their confidence
# MAGIC   primary_cause,
# MAGIC   ROUND(primary_cause_confidence, 3) AS primary_conf,
# MAGIC   specific_primary_cause,
# MAGIC   ROUND(specific_primary_cause_confidence, 3) AS specific_conf,
# MAGIC   
# MAGIC   -- Flag which classification is uncertain
# MAGIC   CASE 
# MAGIC     WHEN primary_cause_confidence < 0.70 AND specific_primary_cause_confidence < 0.70 
# MAGIC       THEN 'Both uncertain'
# MAGIC     WHEN primary_cause_confidence < 0.70 
# MAGIC       THEN 'Primary uncertain'
# MAGIC     WHEN specific_primary_cause_confidence < 0.70 
# MAGIC       THEN 'Specific uncertain'
# MAGIC   END AS uncertainty_flag,
# MAGIC   
# MAGIC   -- Truncate notes for readability
# MAGIC   SUBSTRING(notes, 1, 150) AS notes_preview
# MAGIC   
# MAGIC FROM info_env_jordan.silver.acled_jordan_events
# MAGIC WHERE primary_cause_confidence < 0.70 
# MAGIC    OR specific_primary_cause_confidence < 0.70
# MAGIC ORDER BY 
# MAGIC   LEAST(primary_cause_confidence, specific_primary_cause_confidence) ASC,
# MAGIC   event_date DESC
# MAGIC LIMIT 20

# COMMAND ----------

# DBTITLE 1,Run Gold Layer Models
import subprocess

project_dir = '/Workspace/Users/feliciapedwards@gmail.com/Jordan Information Environment Project'

print("Running gold layer models...\n")
result = subprocess.run(
    ['dbt', 'run', '--select', 'gold', '--project-dir', project_dir],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode == 0:
    print("\n✅ Gold layer models built successfully!")
else:
    print("\n❌ Error:", result.stderr)

# COMMAND ----------

# DBTITLE 1,Verify Gold Tables
# MAGIC %sql
# MAGIC -- Check all gold layer tables
# MAGIC SELECT 'theme_labor_employment' AS table_name, COUNT(*) AS row_count 
# MAGIC FROM info_env_jordan.gold.theme_labor_employment
# MAGIC UNION ALL
# MAGIC SELECT 'theme_economic_conditions', COUNT(*) 
# MAGIC FROM info_env_jordan.gold.theme_economic_conditions
# MAGIC UNION ALL
# MAGIC SELECT 'theme_political_stability', COUNT(*) 
# MAGIC FROM info_env_jordan.gold.theme_political_stability
# MAGIC UNION ALL
# MAGIC SELECT 'theme_regional_identity', COUNT(*) 
# MAGIC FROM info_env_jordan.gold.theme_regional_identity
# MAGIC UNION ALL
# MAGIC SELECT 'ml_combined_economic_themes', COUNT(*) 
# MAGIC FROM info_env_jordan.gold.ml_combined_economic_themes
# MAGIC ORDER BY table_name

# COMMAND ----------

# DBTITLE 1,Preview Combined Economic Themes (Primary KPI Table)
# MAGIC %sql
# MAGIC -- Preview the primary table for KPIs and economic analysis
# MAGIC SELECT 
# MAGIC   event_month,
# MAGIC   total_labor_events,
# MAGIC   total_economic_events,
# MAGIC   total_distress_events,
# MAGIC   avg_unemployment_search,
# MAGIC   avg_inflation_search,
# MAGIC   combined_search_intensity,
# MAGIC   violence_ratio,
# MAGIC   high_alert_flag,
# MAGIC   target_unemployment_rate,
# MAGIC   target_inflation_rate,
# MAGIC   target_gdp_growth
# MAGIC FROM info_env_jordan.gold.ml_combined_economic_themes
# MAGIC ORDER BY event_month DESC
# MAGIC LIMIT 12

# COMMAND ----------

# DBTITLE 1,Verify Economic Indicators Monthly
# MAGIC %sql
# MAGIC -- Verify the new monthly economic indicators table
# MAGIC -- Expected: ~264 rows (88 quarters × 3 months)
# MAGIC
# MAGIC SELECT 
# MAGIC   'Row Count' as metric,
# MAGIC   CAST(COUNT(*) AS STRING) as value
# MAGIC FROM info_env_jordan.silver.economic_indicators_monthly
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'Date Range',
# MAGIC   CONCAT(MIN(event_month), ' to ', MAX(event_month))
# MAGIC FROM info_env_jordan.silver.economic_indicators_monthly
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Complete Records (All 4 indicators)',
# MAGIC   CAST(COUNT(*) AS STRING)
# MAGIC FROM info_env_jordan.silver.economic_indicators_monthly
# MAGIC WHERE gdp_growth_rate IS NOT NULL 
# MAGIC   AND unemployment_rate IS NOT NULL
# MAGIC   AND youth_unemployment_rate IS NOT NULL
# MAGIC   AND inflation_rate IS NOT NULL

# COMMAND ----------

# DBTITLE 1,Preview Economic Indicators Monthly Data
# MAGIC %sql
# MAGIC -- Preview the monthly economic indicators
# MAGIC -- Shows the quarterly expansion: each quarter repeats across 3 months
# MAGIC
# MAGIC SELECT 
# MAGIC   event_month,
# MAGIC   ROUND(gdp_growth_rate, 2) as gdp_growth,
# MAGIC   ROUND(unemployment_rate, 1) as unemployment,
# MAGIC   ROUND(youth_unemployment_rate, 1) as youth_unemployment,
# MAGIC   ROUND(inflation_rate, 2) as inflation,
# MAGIC   source_quarter,
# MAGIC   month_of_quarter,
# MAGIC   has_forward_filled_values as has_filled_values
# MAGIC FROM info_env_jordan.silver.economic_indicators_monthly
# MAGIC WHERE event_month >= '2022-01-01'
# MAGIC ORDER BY event_month DESC
# MAGIC LIMIT 20

# COMMAND ----------

# DBTITLE 1,Join Mechanics Demo: Events + Economic Indicators
# MAGIC %sql
# MAGIC -- DEMONSTRATION: How the join works between event data and economic indicators
# MAGIC -- This shows the exact pattern your gold layer models will use
# MAGIC
# MAGIC -- Step 1: Get some event data from silver (GDELT topics as example)
# MAGIC WITH sample_events AS (
# MAGIC   SELECT 
# MAGIC     DATE_TRUNC('month', article_date) AS event_month,  -- Convert daily dates to monthly grain
# MAGIC     COUNT(*) as event_count,
# MAGIC     -- Event data columns
# MAGIC     SUM(CASE WHEN topic = 'labor_employment' THEN article_count ELSE 0 END) as labor_event_articles
# MAGIC   FROM info_env_jordan.silver.gdelt_jordan_topics
# MAGIC   WHERE article_date >= '2024-01-01'
# MAGIC   GROUP BY DATE_TRUNC('month', article_date)
# MAGIC ),
# MAGIC
# MAGIC -- Step 2: The new economic indicators (monthly grain)
# MAGIC economic_data AS (
# MAGIC   SELECT 
# MAGIC     event_month,
# MAGIC     unemployment_rate,
# MAGIC     inflation_rate,
# MAGIC     gdp_growth_rate,
# MAGIC     source_quarter,
# MAGIC     month_of_quarter
# MAGIC   FROM info_env_jordan.silver.economic_indicators_monthly
# MAGIC   WHERE event_month >= '2024-01-01'
# MAGIC )
# MAGIC
# MAGIC -- Step 3: JOIN on event_month (both tables have monthly grain)
# MAGIC SELECT 
# MAGIC   e.event_month,
# MAGIC   
# MAGIC   -- Event metrics
# MAGIC   e.event_count,
# MAGIC   e.labor_event_articles,
# MAGIC   
# MAGIC   -- Economic indicators (the TARGET variables for ML)
# MAGIC   econ.unemployment_rate,
# MAGIC   econ.inflation_rate,
# MAGIC   econ.gdp_growth_rate,
# MAGIC   
# MAGIC   -- Metadata showing where economic data came from
# MAGIC   econ.source_quarter,
# MAGIC   econ.month_of_quarter,
# MAGIC   
# MAGIC   -- This shows the join mechanics:
# MAGIC   CASE econ.month_of_quarter
# MAGIC     WHEN 1 THEN 'First month of quarter - economic data just refreshed'
# MAGIC     WHEN 2 THEN 'Second month - using same quarterly value'
# MAGIC     WHEN 3 THEN 'Third month - still using same quarterly value'
# MAGIC   END as quarter_position_note
# MAGIC   
# MAGIC FROM sample_events e
# MAGIC LEFT JOIN economic_data econ
# MAGIC   ON e.event_month = econ.event_month  -- Simple 1:1 join on month
# MAGIC   
# MAGIC ORDER BY e.event_month DESC
# MAGIC LIMIT 15

# COMMAND ----------

# DBTITLE 1,Before vs After: Gold Layer Join Pattern
# MAGIC %sql
# MAGIC -- BEFORE vs AFTER: How the gold layer join changes
# MAGIC -- BEFORE: Gold layer had placeholder CTEs that returned no rows
# MAGIC -- AFTER: Gold layer joins to real silver.economic_indicators_monthly
# MAGIC
# MAGIC -- New pattern that your gold models will use:
# MAGIC WITH monthly_labor_events AS (
# MAGIC   SELECT 
# MAGIC     DATE_TRUNC('month', event_date) AS event_month,
# MAGIC     COUNT(*) AS total_labor_events
# MAGIC   FROM info_env_jordan.silver.acled_jordan_events
# MAGIC   WHERE primary_cause = 'labor_workers_rights'
# MAGIC   GROUP BY 1
# MAGIC ),
# MAGIC
# MAGIC monthly_economic_indicators AS (
# MAGIC   -- NEW: Join to the real monthly economic indicators
# MAGIC   SELECT 
# MAGIC     event_month,
# MAGIC     unemployment_rate,
# MAGIC     inflation_rate,
# MAGIC     gdp_growth_rate,
# MAGIC     youth_unemployment_rate
# MAGIC   FROM info_env_jordan.silver.economic_indicators_monthly
# MAGIC )
# MAGIC
# MAGIC SELECT 
# MAGIC   events.event_month,
# MAGIC   events.total_labor_events,
# MAGIC   
# MAGIC   -- These target columns will now have REAL DATA instead of NULLs
# MAGIC   econ.unemployment_rate AS target_unemployment_rate,
# MAGIC   econ.inflation_rate AS target_inflation_rate,
# MAGIC   econ.gdp_growth_rate AS target_gdp_growth
# MAGIC   
# MAGIC FROM monthly_labor_events events
# MAGIC LEFT JOIN monthly_economic_indicators econ
# MAGIC   ON events.event_month = econ.event_month
# MAGIC   
# MAGIC WHERE events.event_month >= '2024-01-01'
# MAGIC ORDER BY events.event_month DESC
# MAGIC LIMIT 10