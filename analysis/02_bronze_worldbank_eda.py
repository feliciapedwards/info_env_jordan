# Databricks notebook source
# DBTITLE 1,Bronze Layer EDA Documentation
# MAGIC %md
# MAGIC # Bronze Layer EDA - World Bank Economic Indicators
# MAGIC
# MAGIC This notebook performs comprehensive exploratory data analysis on seven World Bank economic indicator tables:
# MAGIC - **GDP Growth**: `info_env_jordan.bronze.gdp_growth`
# MAGIC - **Inflation (CPI)**: `info_env_jordan.bronze.inflation_cpi`
# MAGIC - **Unemployment Total**: `info_env_jordan.bronze.unemployment_total`
# MAGIC - **Unemployment Youth**: `info_env_jordan.bronze.unemployment_youth`
# MAGIC - **Food Production Index**: `info_env_jordan.bronze.food_production_index`
# MAGIC - **Population**: `info_env_jordan.bronze.population`
# MAGIC - **GDP per Capita**: `info_env_jordan.bronze.gdp_per_capita`
# MAGIC
# MAGIC ## Analysis Sections:
# MAGIC 1. Basic Overview (row counts, column counts, schemas)
# MAGIC 2. Null Value Analysis
# MAGIC 3. Year Range Analysis
# MAGIC 4. Summary Statistics for Values
# MAGIC 5. Data Quality Checks (duplicates, data types)
# MAGIC 6. Sample Data Preview
# MAGIC 7. Key Metrics by Indicator

# COMMAND ----------

# DBTITLE 1,Summary and Interpretation
# MAGIC %md
# MAGIC ## Summary and Interpretation
# MAGIC
# MAGIC ### Economic Trends in Jordan (2015-2024)
# MAGIC
# MAGIC - **2015-2019 vs 2020-2024**:
# MAGIC   - GDP Growth: Slight decline (-0.6%).
# MAGIC   - Inflation: Significantly worsened (+38.6%).
# MAGIC   - Unemployment (total and youth): Both are higher—youth unemployment is especially concerning (+16%).
# MAGIC   - GDP Per Capita & Food Production: Both improved slightly (up ~6%).
# MAGIC
# MAGIC - **COVID Impact & Recovery**:
# MAGIC   - 2020 marked a recession and spike in unemployment.
# MAGIC   - By 2024, most metrics were improving, but inflation remained elevated.
# MAGIC   - Persistently high youth unemployment remains a structural challenge.
# MAGIC
# MAGIC Overall, economic indicators for Jordan worsened during the pandemic period but show signs of recovery by 2024. The exception is inflation, which is still elevated, and youth unemployment, which, while improving, is still at concerning levels.
# MAGIC
# MAGIC ### Data Limitations:
# MAGIC **Important**: Our dataset only includes data through 2024. We are missing:
# MAGIC - Full year 2025 data
# MAGIC - First half of 2026 data (current date: June 2026)
# MAGIC
# MAGIC This limits our ability to draw definitive conclusions about the full post-COVID recovery trajectory. The economy may have continued improving (or worsening) in 2025-2026, which we cannot yet observe. Any conclusions about "current" economic conditions are based on 2024 data, which is now 1.5-2 years old.
# MAGIC
# MAGIC - *See cells 13–15 for detailed comparison and trend calculations.*

# COMMAND ----------

# DBTITLE 1,Row counts for all tables
# MAGIC %sql
# MAGIC -- 1. BASIC OVERVIEW: Row counts for all bronze tables
# MAGIC SELECT 'gdp_growth' AS table_name, COUNT(*) AS row_count FROM info_env_jordan.bronze.gdp_growth
# MAGIC UNION ALL
# MAGIC SELECT 'inflation_cpi' AS table_name, COUNT(*) AS row_count FROM info_env_jordan.bronze.inflation_cpi
# MAGIC UNION ALL
# MAGIC SELECT 'unemployment_total' AS table_name, COUNT(*) AS row_count FROM info_env_jordan.bronze.unemployment_total
# MAGIC UNION ALL
# MAGIC SELECT 'unemployment_youth' AS table_name, COUNT(*) AS row_count FROM info_env_jordan.bronze.unemployment_youth
# MAGIC UNION ALL
# MAGIC SELECT 'food_production_index' AS table_name, COUNT(*) AS row_count FROM info_env_jordan.bronze.food_production_index
# MAGIC UNION ALL
# MAGIC SELECT 'population' AS table_name, COUNT(*) AS row_count FROM info_env_jordan.bronze.population
# MAGIC UNION ALL
# MAGIC SELECT 'gdp_per_capita' AS table_name, COUNT(*) AS row_count FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC ORDER BY table_name

# COMMAND ----------

# DBTITLE 1,Schema inspection
# MAGIC %sql
# MAGIC -- Schema inspection for all tables
# MAGIC DESCRIBE TABLE info_env_jordan.bronze.gdp_growth

# COMMAND ----------

# DBTITLE 1,Null value analysis
# MAGIC %sql
# MAGIC -- 2. NULL VALUE ANALYSIS: Check for missing values in each table
# MAGIC SELECT 
# MAGIC   'gdp_growth' AS table_name,
# MAGIC   COUNT(*) AS total_rows,
# MAGIC   SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
# MAGIC   SUM(CASE WHEN country_code IS NULL THEN 1 ELSE 0 END) AS null_country_code,
# MAGIC   SUM(CASE WHEN indicator_code IS NULL THEN 1 ELSE 0 END) AS null_indicator_code,
# MAGIC   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
# MAGIC FROM info_env_jordan.bronze.gdp_growth
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'inflation_cpi' AS table_name,
# MAGIC   COUNT(*) AS total_rows,
# MAGIC   SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
# MAGIC   SUM(CASE WHEN country_code IS NULL THEN 1 ELSE 0 END) AS null_country_code,
# MAGIC   SUM(CASE WHEN indicator_code IS NULL THEN 1 ELSE 0 END) AS null_indicator_code,
# MAGIC   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
# MAGIC FROM info_env_jordan.bronze.inflation_cpi
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_total' AS table_name,
# MAGIC   COUNT(*) AS total_rows,
# MAGIC   SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
# MAGIC   SUM(CASE WHEN country_code IS NULL THEN 1 ELSE 0 END) AS null_country_code,
# MAGIC   SUM(CASE WHEN indicator_code IS NULL THEN 1 ELSE 0 END) AS null_indicator_code,
# MAGIC   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
# MAGIC FROM info_env_jordan.bronze.unemployment_total
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_youth' AS table_name,
# MAGIC   COUNT(*) AS total_rows,
# MAGIC   SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
# MAGIC   SUM(CASE WHEN country_code IS NULL THEN 1 ELSE 0 END) AS null_country_code,
# MAGIC   SUM(CASE WHEN indicator_code IS NULL THEN 1 ELSE 0 END) AS null_indicator_code,
# MAGIC   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
# MAGIC FROM info_env_jordan.bronze.unemployment_youth
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'food_production_index' AS table_name,
# MAGIC   COUNT(*) AS total_rows,
# MAGIC   SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
# MAGIC   SUM(CASE WHEN country_code IS NULL THEN 1 ELSE 0 END) AS null_country_code,
# MAGIC   SUM(CASE WHEN indicator_code IS NULL THEN 1 ELSE 0 END) AS null_indicator_code,
# MAGIC   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
# MAGIC FROM info_env_jordan.bronze.food_production_index
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'population' AS table_name,
# MAGIC   COUNT(*) AS total_rows,
# MAGIC   SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
# MAGIC   SUM(CASE WHEN country_code IS NULL THEN 1 ELSE 0 END) AS null_country_code,
# MAGIC   SUM(CASE WHEN indicator_code IS NULL THEN 1 ELSE 0 END) AS null_indicator_code,
# MAGIC   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
# MAGIC FROM info_env_jordan.bronze.population
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'gdp_per_capita' AS table_name,
# MAGIC   COUNT(*) AS total_rows,
# MAGIC   SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) AS null_year,
# MAGIC   SUM(CASE WHEN country_code IS NULL THEN 1 ELSE 0 END) AS null_country_code,
# MAGIC   SUM(CASE WHEN indicator_code IS NULL THEN 1 ELSE 0 END) AS null_indicator_code,
# MAGIC   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS null_value
# MAGIC FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC
# MAGIC ORDER BY table_name

# COMMAND ----------

# DBTITLE 1,Year range analysis
# MAGIC %sql
# MAGIC -- 3. YEAR RANGE ANALYSIS: Understand temporal coverage
# MAGIC SELECT 
# MAGIC   'gdp_growth' AS table_name,
# MAGIC   MIN(year) AS earliest_year,
# MAGIC   MAX(year) AS latest_year,
# MAGIC   COUNT(DISTINCT year) AS distinct_years
# MAGIC FROM info_env_jordan.bronze.gdp_growth
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'inflation_cpi' AS table_name,
# MAGIC   MIN(year) AS earliest_year,
# MAGIC   MAX(year) AS latest_year,
# MAGIC   COUNT(DISTINCT year) AS distinct_years
# MAGIC FROM info_env_jordan.bronze.inflation_cpi
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_total' AS table_name,
# MAGIC   MIN(year) AS earliest_year,
# MAGIC   MAX(year) AS latest_year,
# MAGIC   COUNT(DISTINCT year) AS distinct_years
# MAGIC FROM info_env_jordan.bronze.unemployment_total
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_youth' AS table_name,
# MAGIC   MIN(year) AS earliest_year,
# MAGIC   MAX(year) AS latest_year,
# MAGIC   COUNT(DISTINCT year) AS distinct_years
# MAGIC FROM info_env_jordan.bronze.unemployment_youth
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'food_production_index' AS table_name,
# MAGIC   MIN(year) AS earliest_year,
# MAGIC   MAX(year) AS latest_year,
# MAGIC   COUNT(DISTINCT year) AS distinct_years
# MAGIC FROM info_env_jordan.bronze.food_production_index
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'population' AS table_name,
# MAGIC   MIN(year) AS earliest_year,
# MAGIC   MAX(year) AS latest_year,
# MAGIC   COUNT(DISTINCT year) AS distinct_years
# MAGIC FROM info_env_jordan.bronze.population
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'gdp_per_capita' AS table_name,
# MAGIC   MIN(year) AS earliest_year,
# MAGIC   MAX(year) AS latest_year,
# MAGIC   COUNT(DISTINCT year) AS distinct_years
# MAGIC FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC
# MAGIC ORDER BY table_name

# COMMAND ----------

# DBTITLE 1,Summary statistics for values
# MAGIC %sql
# MAGIC -- 4. SUMMARY STATISTICS: Distribution of values by indicator
# MAGIC SELECT 
# MAGIC   'gdp_growth' AS indicator,
# MAGIC   COUNT(*) AS records,
# MAGIC   ROUND(MIN(value), 2) AS min_value,
# MAGIC   ROUND(MAX(value), 2) AS max_value,
# MAGIC   ROUND(AVG(value), 2) AS avg_value,
# MAGIC   ROUND(STDDEV(value), 2) AS stddev_value,
# MAGIC   COUNT(DISTINCT value) AS distinct_values
# MAGIC FROM info_env_jordan.bronze.gdp_growth
# MAGIC WHERE value IS NOT NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'inflation_cpi' AS indicator,
# MAGIC   COUNT(*) AS records,
# MAGIC   ROUND(MIN(value), 2) AS min_value,
# MAGIC   ROUND(MAX(value), 2) AS max_value,
# MAGIC   ROUND(AVG(value), 2) AS avg_value,
# MAGIC   ROUND(STDDEV(value), 2) AS stddev_value,
# MAGIC   COUNT(DISTINCT value) AS distinct_values
# MAGIC FROM info_env_jordan.bronze.inflation_cpi
# MAGIC WHERE value IS NOT NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_total' AS indicator,
# MAGIC   COUNT(*) AS records,
# MAGIC   ROUND(MIN(value), 2) AS min_value,
# MAGIC   ROUND(MAX(value), 2) AS max_value,
# MAGIC   ROUND(AVG(value), 2) AS avg_value,
# MAGIC   ROUND(STDDEV(value), 2) AS stddev_value,
# MAGIC   COUNT(DISTINCT value) AS distinct_values
# MAGIC FROM info_env_jordan.bronze.unemployment_total
# MAGIC WHERE value IS NOT NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_youth' AS indicator,
# MAGIC   COUNT(*) AS records,
# MAGIC   ROUND(MIN(value), 2) AS min_value,
# MAGIC   ROUND(MAX(value), 2) AS max_value,
# MAGIC   ROUND(AVG(value), 2) AS avg_value,
# MAGIC   ROUND(STDDEV(value), 2) AS stddev_value,
# MAGIC   COUNT(DISTINCT value) AS distinct_values
# MAGIC FROM info_env_jordan.bronze.unemployment_youth
# MAGIC WHERE value IS NOT NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'food_production_index' AS indicator,
# MAGIC   COUNT(*) AS records,
# MAGIC   ROUND(MIN(value), 2) AS min_value,
# MAGIC   ROUND(MAX(value), 2) AS max_value,
# MAGIC   ROUND(AVG(value), 2) AS avg_value,
# MAGIC   ROUND(STDDEV(value), 2) AS stddev_value,
# MAGIC   COUNT(DISTINCT value) AS distinct_values
# MAGIC FROM info_env_jordan.bronze.food_production_index
# MAGIC WHERE value IS NOT NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'population' AS indicator,
# MAGIC   COUNT(*) AS records,
# MAGIC   ROUND(MIN(value), 2) AS min_value,
# MAGIC   ROUND(MAX(value), 2) AS max_value,
# MAGIC   ROUND(AVG(value), 2) AS avg_value,
# MAGIC   ROUND(STDDEV(value), 2) AS stddev_value,
# MAGIC   COUNT(DISTINCT value) AS distinct_values
# MAGIC FROM info_env_jordan.bronze.population
# MAGIC WHERE value IS NOT NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'gdp_per_capita' AS indicator,
# MAGIC   COUNT(*) AS records,
# MAGIC   ROUND(MIN(value), 2) AS min_value,
# MAGIC   ROUND(MAX(value), 2) AS max_value,
# MAGIC   ROUND(AVG(value), 2) AS avg_value,
# MAGIC   ROUND(STDDEV(value), 2) AS stddev_value,
# MAGIC   COUNT(DISTINCT value) AS distinct_values
# MAGIC FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC WHERE value IS NOT NULL
# MAGIC
# MAGIC ORDER BY indicator

# COMMAND ----------

# DBTITLE 1,Check for duplicate years
# MAGIC %sql
# MAGIC -- 5. DATA QUALITY: Check for duplicate years in each table
# MAGIC SELECT 
# MAGIC   'gdp_growth' AS table_name,
# MAGIC   year,
# MAGIC   COUNT(*) AS occurrences
# MAGIC FROM info_env_jordan.bronze.gdp_growth
# MAGIC GROUP BY year
# MAGIC HAVING COUNT(*) > 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'inflation_cpi' AS table_name,
# MAGIC   year,
# MAGIC   COUNT(*) AS occurrences
# MAGIC FROM info_env_jordan.bronze.inflation_cpi
# MAGIC GROUP BY year
# MAGIC HAVING COUNT(*) > 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_total' AS table_name,
# MAGIC   year,
# MAGIC   COUNT(*) AS occurrences
# MAGIC FROM info_env_jordan.bronze.unemployment_total
# MAGIC GROUP BY year
# MAGIC HAVING COUNT(*) > 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'unemployment_youth' AS table_name,
# MAGIC   year,
# MAGIC   COUNT(*) AS occurrences
# MAGIC FROM info_env_jordan.bronze.unemployment_youth
# MAGIC GROUP BY year
# MAGIC HAVING COUNT(*) > 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'food_production_index' AS table_name,
# MAGIC   year,
# MAGIC   COUNT(*) AS occurrences
# MAGIC FROM info_env_jordan.bronze.food_production_index
# MAGIC GROUP BY year
# MAGIC HAVING COUNT(*) > 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'population' AS table_name,
# MAGIC   year,
# MAGIC   COUNT(*) AS occurrences
# MAGIC FROM info_env_jordan.bronze.population
# MAGIC GROUP BY year
# MAGIC HAVING COUNT(*) > 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'gdp_per_capita' AS table_name,
# MAGIC   year,
# MAGIC   COUNT(*) AS occurrences
# MAGIC FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC GROUP BY year
# MAGIC HAVING COUNT(*) > 1
# MAGIC
# MAGIC ORDER BY table_name, year

# COMMAND ----------

# DBTITLE 1,Sample: GDP Growth (recent years)
# MAGIC %sql
# MAGIC -- 6. SAMPLE DATA PREVIEW: GDP Growth
# MAGIC SELECT *
# MAGIC FROM info_env_jordan.bronze.gdp_growth
# MAGIC ORDER BY year DESC
# MAGIC LIMIT 10

# COMMAND ----------

# DBTITLE 1,Sample: Inflation (recent years)
# MAGIC %sql
# MAGIC -- Sample Data: Inflation (CPI)
# MAGIC SELECT *
# MAGIC FROM info_env_jordan.bronze.inflation_cpi
# MAGIC ORDER BY year DESC
# MAGIC LIMIT 10

# COMMAND ----------

# DBTITLE 1,Sample: Unemployment Total (recent years)
# MAGIC %sql
# MAGIC -- Sample Data: Unemployment Total
# MAGIC SELECT *
# MAGIC FROM info_env_jordan.bronze.unemployment_total
# MAGIC ORDER BY year DESC
# MAGIC LIMIT 10

# COMMAND ----------

# DBTITLE 1,Combined view: All indicators (recent 10 years)
# MAGIC %sql
# MAGIC -- 7. KEY METRICS: Time series view of all indicators (last 10 years)
# MAGIC SELECT 
# MAGIC   g.year,
# MAGIC   ROUND(g.value, 2) AS gdp_growth_pct,
# MAGIC   ROUND(i.value, 2) AS inflation_pct,
# MAGIC   ROUND(u.value, 2) AS unemployment_total_pct,
# MAGIC   ROUND(y.value, 2) AS unemployment_youth_pct,
# MAGIC   ROUND(f.value, 2) AS food_production_index,
# MAGIC   ROUND(p.value, 0) AS population,
# MAGIC   ROUND(gpc.value, 2) AS gdp_per_capita
# MAGIC FROM info_env_jordan.bronze.gdp_growth g
# MAGIC LEFT JOIN info_env_jordan.bronze.inflation_cpi i ON g.year = i.year
# MAGIC LEFT JOIN info_env_jordan.bronze.unemployment_total u ON g.year = u.year
# MAGIC LEFT JOIN info_env_jordan.bronze.unemployment_youth y ON g.year = y.year
# MAGIC LEFT JOIN info_env_jordan.bronze.food_production_index f ON g.year = f.year
# MAGIC LEFT JOIN info_env_jordan.bronze.population p ON g.year = p.year
# MAGIC LEFT JOIN info_env_jordan.bronze.gdp_per_capita gpc ON g.year = gpc.year
# MAGIC ORDER BY g.year DESC
# MAGIC LIMIT 10

# COMMAND ----------

# DBTITLE 1,Trend Analysis Documentation
# MAGIC %md
# MAGIC ## 8. Trend Analysis: Have Indicators Worsened Over Last 5 Years?
# MAGIC
# MAGIC To determine if economic conditions worsened, we'll compare:
# MAGIC - **Recent Period**: 2020-2024 (last 5 years)
# MAGIC - **Previous Period**: 2015-2019 (prior 5 years)
# MAGIC
# MAGIC ### What "Worsened" Means:
# MAGIC - **GDP Growth**: Lower = worse (negative = recession)
# MAGIC - **Inflation**: Higher = worse (erodes purchasing power)
# MAGIC - **Unemployment (Total & Youth)**: Higher = worse
# MAGIC - **Food Production**: Lower = worse (food security)
# MAGIC - **GDP per Capita**: Lower = worse (living standards)
# MAGIC - **Population**: Growing population = positive (economic growth indicator)

# COMMAND ----------

# DBTITLE 1,Period comparison: 2015-2019 vs 2020-2024
# MAGIC %sql
# MAGIC -- Compare average values: Recent (2020-2024) vs Previous (2015-2019) period
# MAGIC WITH recent_period AS (
# MAGIC   SELECT 'gdp_growth' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.gdp_growth
# MAGIC   WHERE year BETWEEN '2020' AND '2024' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'inflation_cpi' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.inflation_cpi
# MAGIC   WHERE year BETWEEN '2020' AND '2024' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'unemployment_total' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.unemployment_total
# MAGIC   WHERE year BETWEEN '2020' AND '2024' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'unemployment_youth' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.unemployment_youth
# MAGIC   WHERE year BETWEEN '2020' AND '2024' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'food_production_index' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.food_production_index
# MAGIC   WHERE year BETWEEN '2020' AND '2024' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'gdp_per_capita' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC   WHERE year BETWEEN '2020' AND '2024' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'population' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.population
# MAGIC   WHERE year BETWEEN '2020' AND '2024' AND value IS NOT NULL
# MAGIC ),
# MAGIC previous_period AS (
# MAGIC   SELECT 'gdp_growth' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.gdp_growth
# MAGIC   WHERE year BETWEEN '2015' AND '2019' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'inflation_cpi' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.inflation_cpi
# MAGIC   WHERE year BETWEEN '2015' AND '2019' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'unemployment_total' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.unemployment_total
# MAGIC   WHERE year BETWEEN '2015' AND '2019' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'unemployment_youth' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.unemployment_youth
# MAGIC   WHERE year BETWEEN '2015' AND '2019' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'food_production_index' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.food_production_index
# MAGIC   WHERE year BETWEEN '2015' AND '2019' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'gdp_per_capita' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC   WHERE year BETWEEN '2015' AND '2019' AND value IS NOT NULL
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'population' AS indicator, AVG(value) AS avg_value
# MAGIC   FROM info_env_jordan.bronze.population
# MAGIC   WHERE year BETWEEN '2015' AND '2019' AND value IS NOT NULL
# MAGIC )
# MAGIC SELECT 
# MAGIC   r.indicator,
# MAGIC   ROUND(p.avg_value, 2) AS avg_2015_2019,
# MAGIC   ROUND(r.avg_value, 2) AS avg_2020_2024,
# MAGIC   ROUND(r.avg_value - p.avg_value, 2) AS change,
# MAGIC   ROUND(((r.avg_value - p.avg_value) / p.avg_value) * 100, 2) AS pct_change,
# MAGIC   CASE 
# MAGIC     WHEN r.indicator IN ('gdp_growth', 'food_production_index', 'gdp_per_capita', 'population') AND r.avg_value < p.avg_value THEN '⬇️ Worsened'
# MAGIC     WHEN r.indicator IN ('gdp_growth', 'food_production_index', 'gdp_per_capita', 'population') AND r.avg_value > p.avg_value THEN '⬆️ Improved'
# MAGIC     WHEN r.indicator IN ('inflation_cpi', 'unemployment_total', 'unemployment_youth') AND r.avg_value > p.avg_value THEN '⬇️ Worsened'
# MAGIC     WHEN r.indicator IN ('inflation_cpi', 'unemployment_total', 'unemployment_youth') AND r.avg_value < p.avg_value THEN '⬆️ Improved'
# MAGIC     ELSE '➡️ Stable'
# MAGIC   END AS assessment
# MAGIC FROM recent_period r
# MAGIC JOIN previous_period p ON r.indicator = p.indicator
# MAGIC ORDER BY r.indicator

# COMMAND ----------

# DBTITLE 1,Year-over-year changes (2020-2024)
# MAGIC %sql
# MAGIC -- Year-over-year changes for last 5 years (2020-2024)
# MAGIC WITH combined_data AS (
# MAGIC   SELECT year, 'gdp_growth' AS indicator, value
# MAGIC   FROM info_env_jordan.bronze.gdp_growth
# MAGIC   WHERE year BETWEEN '2020' AND '2024'
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT year, 'inflation_cpi' AS indicator, value
# MAGIC   FROM info_env_jordan.bronze.inflation_cpi
# MAGIC   WHERE year BETWEEN '2020' AND '2024'
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT year, 'unemployment_total' AS indicator, value
# MAGIC   FROM info_env_jordan.bronze.unemployment_total
# MAGIC   WHERE year BETWEEN '2020' AND '2024'
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT year, 'unemployment_youth' AS indicator, value
# MAGIC   FROM info_env_jordan.bronze.unemployment_youth
# MAGIC   WHERE year BETWEEN '2020' AND '2024'
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT year, 'food_production_index' AS indicator, value
# MAGIC   FROM info_env_jordan.bronze.food_production_index
# MAGIC   WHERE year BETWEEN '2020' AND '2024'
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT year, 'gdp_per_capita' AS indicator, value
# MAGIC   FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC   WHERE year BETWEEN '2020' AND '2024'
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT year, 'population' AS indicator, value
# MAGIC   FROM info_env_jordan.bronze.population
# MAGIC   WHERE year BETWEEN '2020' AND '2024'
# MAGIC )
# MAGIC SELECT 
# MAGIC   indicator,
# MAGIC   year,
# MAGIC   ROUND(value, 2) AS value,
# MAGIC   ROUND(LAG(value) OVER (PARTITION BY indicator ORDER BY year), 2) AS prev_year_value,
# MAGIC   ROUND(value - LAG(value) OVER (PARTITION BY indicator ORDER BY year), 2) AS yoy_change
# MAGIC FROM combined_data
# MAGIC WHERE value IS NOT NULL
# MAGIC ORDER BY indicator, year DESC

# COMMAND ----------

# DBTITLE 1,5-year trend: 2020 vs 2024
# MAGIC %sql
# MAGIC -- Overall trend direction: Are indicators getting better or worse?
# MAGIC WITH first_last AS (
# MAGIC   SELECT 'gdp_growth' AS indicator,
# MAGIC          MAX(CASE WHEN year = '2020' THEN value END) AS value_2020,
# MAGIC          MAX(CASE WHEN year = '2024' THEN value END) AS value_2024
# MAGIC   FROM info_env_jordan.bronze.gdp_growth
# MAGIC   WHERE year IN ('2020', '2024')
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'inflation_cpi' AS indicator,
# MAGIC          MAX(CASE WHEN year = '2020' THEN value END) AS value_2020,
# MAGIC          MAX(CASE WHEN year = '2024' THEN value END) AS value_2024
# MAGIC   FROM info_env_jordan.bronze.inflation_cpi
# MAGIC   WHERE year IN ('2020', '2024')
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'unemployment_total' AS indicator,
# MAGIC          MAX(CASE WHEN year = '2020' THEN value END) AS value_2020,
# MAGIC          MAX(CASE WHEN year = '2024' THEN value END) AS value_2024
# MAGIC   FROM info_env_jordan.bronze.unemployment_total
# MAGIC   WHERE year IN ('2020', '2024')
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'unemployment_youth' AS indicator,
# MAGIC          MAX(CASE WHEN year = '2020' THEN value END) AS value_2020,
# MAGIC          MAX(CASE WHEN year = '2024' THEN value END) AS value_2024
# MAGIC   FROM info_env_jordan.bronze.unemployment_youth
# MAGIC   WHERE year IN ('2020', '2024')
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'food_production_index' AS indicator,
# MAGIC          MAX(CASE WHEN year = '2020' THEN value END) AS value_2020,
# MAGIC          MAX(CASE WHEN year = '2024' THEN value END) AS value_2024
# MAGIC   FROM info_env_jordan.bronze.food_production_index
# MAGIC   WHERE year IN ('2020', '2024')
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'gdp_per_capita' AS indicator,
# MAGIC          MAX(CASE WHEN year = '2020' THEN value END) AS value_2020,
# MAGIC          MAX(CASE WHEN year = '2024' THEN value END) AS value_2024
# MAGIC   FROM info_env_jordan.bronze.gdp_per_capita
# MAGIC   WHERE year IN ('2020', '2024')
# MAGIC   
# MAGIC   UNION ALL
# MAGIC   
# MAGIC   SELECT 'population' AS indicator,
# MAGIC          MAX(CASE WHEN year = '2020' THEN value END) AS value_2020,
# MAGIC          MAX(CASE WHEN year = '2024' THEN value END) AS value_2024
# MAGIC   FROM info_env_jordan.bronze.population
# MAGIC   WHERE year IN ('2020', '2024')
# MAGIC )
# MAGIC SELECT 
# MAGIC   indicator,
# MAGIC   ROUND(value_2020, 2) AS value_2020,
# MAGIC   ROUND(value_2024, 2) AS value_2024,
# MAGIC   ROUND(value_2024 - value_2020, 2) AS change_2020_to_2024,
# MAGIC   CASE 
# MAGIC     WHEN indicator IN ('gdp_growth', 'food_production_index', 'gdp_per_capita', 'population') AND value_2024 > value_2020 THEN '📈 Improving Trend'
# MAGIC     WHEN indicator IN ('gdp_growth', 'food_production_index', 'gdp_per_capita', 'population') AND value_2024 < value_2020 THEN '📉 Declining Trend'
# MAGIC     WHEN indicator IN ('inflation_cpi', 'unemployment_total', 'unemployment_youth') AND value_2024 < value_2020 THEN '📈 Improving Trend'
# MAGIC     WHEN indicator IN ('inflation_cpi', 'unemployment_total', 'unemployment_youth') AND value_2024 > value_2020 THEN '📉 Declining Trend'
# MAGIC     ELSE '➡️ Stable'
# MAGIC   END AS trend_assessment
# MAGIC FROM first_last
# MAGIC WHERE value_2020 IS NOT NULL AND value_2024 IS NOT NULL
# MAGIC ORDER BY indicator