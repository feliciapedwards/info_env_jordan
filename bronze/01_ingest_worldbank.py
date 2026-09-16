# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Bronze Layer Documentation
# MAGIC %md
# MAGIC # Bronze Layer: World Bank API Ingestion
# MAGIC
# MAGIC This notebook fetches economic indicators from the World Bank API and stores them as raw bronze tables.
# MAGIC
# MAGIC   https://databank.worldbank.org/metadataglossary/world-development-indicators/series/NY.GDP.MKTP.KD
# MAGIC
# MAGIC
# MAGIC   data dictionary: https://acleddata.com/methodology/acled-codebook
# MAGIC
# MAGIC
# MAGIC ## Data Sources
# MAGIC - **Country**: Jordan (JOR)
# MAGIC - **Indicators**:
# MAGIC   - `NY.GDP.MKTP.KD.ZG`: GDP growth (annual %)
# MAGIC   - `FP.CPI.TOTL.ZG`: Inflation, consumer prices (annual %)
# MAGIC   - `SL.UEM.TOTL.ZS`: Unemployment, total (% of total labor force)
# MAGIC   - `SL.UEM.1524.ZS`: Unemployment, youth total (% of total labor force ages 15-24)
# MAGIC   - `AG.PRD.FOOD.XD`: Food production index
# MAGIC   - `SP.POP.TOTL`: Population, total
# MAGIC   - `NY.GDP.PCAP.CD`: GDP per capita (current US$)
# MAGIC
# MAGIC ## Output
# MAGIC Bronze tables (one per indicator):
# MAGIC - `info_env_jordan.bronze.gdp_growth`
# MAGIC - `info_env_jordan.bronze.inflation_cpi`
# MAGIC - `info_env_jordan.bronze.unemployment_total`
# MAGIC - `info_env_jordan.bronze.unemployment_youth`
# MAGIC - `info_env_jordan.bronze.food_production_index`
# MAGIC - `info_env_jordan.bronze.population`
# MAGIC - `info_env_jordan.bronze.gdp_per_capita`

# COMMAND ----------

# DBTITLE 1,Fetch World Bank API data
import requests
import time
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# World Bank API endpoint for Jordan's economic indicators
url = "https://api.worldbank.org/v2/country/JOR/indicator/NY.GDP.MKTP.KD.ZG;FP.CPI.TOTL.ZG;SL.UEM.TOTL.ZS;SL.UEM.1524.ZS;AG.PRD.FOOD.XD;SP.POP.TOTL;NY.GDP.PCAP.CD?source=2&format=json&per_page=1000"

# Fetch data with retry logic (handle 524 errors)
max_retries = 3
retry_delay = 5  # seconds

for attempt in range(max_retries):
    try:
        print(f"Attempt {attempt + 1}/{max_retries}: Fetching data from World Bank API...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Successfully fetched data")
        break
    except requests.exceptions.HTTPError as e:
        if attempt < max_retries - 1:
            print(f"✗ HTTP Error {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print(f"✗ Failed after {max_retries} attempts: {e}")
            raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise

# Parse JSON response
# World Bank API returns [metadata, data] - we need data[1]
if len(data) > 1 and data[1]:
    records = data[1]
    print(f"\n✓ Parsed {len(records)} records from API response")
else:
    raise ValueError("No data returned from World Bank API")

# Transform to list of tuples for Spark DataFrame
rows = []
for record in records:
    rows.append((
        record.get('date'),  # year
        record.get('countryiso3code'),  # country code
        record['country'].get('value') if record.get('country') else None,  # country name
        record['indicator'].get('id') if record.get('indicator') else None,  # indicator code
        record['indicator'].get('value') if record.get('indicator') else None,  # indicator name
        record.get('value')  # value
    ))

print(f"✓ Transformed {len(rows)} rows")

# Define schema
schema = StructType([
    StructField("year", StringType(), True),
    StructField("country_code", StringType(), True),
    StructField("country_name", StringType(), True),
    StructField("indicator_code", StringType(), True),
    StructField("indicator_name", StringType(), True),
    StructField("value", DoubleType(), True)
])

# Create Spark DataFrame
worldbank_df = spark.createDataFrame(rows, schema)

print(f"\n✓ Created Spark DataFrame with {worldbank_df.count()} rows")
print("\nSchema:")
worldbank_df.printSchema()

# Display sample
print("\nSample data:")
display(worldbank_df.limit(1000))

# COMMAND ----------

# DBTITLE 1,Save bronze table and verify
# Split data into separate tables by indicator
# Each economic indicator gets its own bronze table

# GDP Growth
gdp_growth_df = worldbank_df.filter(worldbank_df.indicator_code == "NY.GDP.MKTP.KD.ZG")
gdp_growth_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.gdp_growth")
print(f"✓ Saved GDP growth: {gdp_growth_df.count()} rows")

# Inflation (CPI)
inflation_df = worldbank_df.filter(worldbank_df.indicator_code == "FP.CPI.TOTL.ZG")
inflation_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.inflation_cpi")
print(f"✓ Saved inflation (CPI): {inflation_df.count()} rows")

# Unemployment - Total
unemployment_total_df = worldbank_df.filter(worldbank_df.indicator_code == "SL.UEM.TOTL.ZS")
unemployment_total_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.unemployment_total")
print(f"✓ Saved unemployment (total): {unemployment_total_df.count()} rows")

# Unemployment - Youth
unemployment_youth_df = worldbank_df.filter(worldbank_df.indicator_code == "SL.UEM.1524.ZS")
unemployment_youth_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.unemployment_youth")
print(f"✓ Saved unemployment (youth): {unemployment_youth_df.count()} rows")

# Food Production Index
food_production_df = worldbank_df.filter(worldbank_df.indicator_code == "AG.PRD.FOOD.XD")
food_production_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.food_production_index")
print(f"✓ Saved food production index: {food_production_df.count()} rows")

# Population
population_df = worldbank_df.filter(worldbank_df.indicator_code == "SP.POP.TOTL")
population_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.population")
print(f"✓ Saved population: {population_df.count()} rows")

# GDP Per Capita
gdp_per_capita_df = worldbank_df.filter(worldbank_df.indicator_code == "NY.GDP.PCAP.CD")
gdp_per_capita_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.gdp_per_capita")
print(f"✓ Saved GDP per capita: {gdp_per_capita_df.count()} rows")

# Show all bronze tables
print("\n" + "="*50)
print("Bronze Layer Tables:")
print("="*50)
spark.sql("SHOW TABLES IN info_env_jordan.bronze").show(truncate=False)

# COMMAND ----------

# DBTITLE 1,Save unified long format table
# Save unified long format table (all indicators in one table)
worldbank_df.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.worldbank_jordan_long")
print(f"✓ Saved unified long format table: {worldbank_df.count()} rows")
print("\nStructure: year | country_code | country_name | indicator_code | indicator_name | value")
display(worldbank_df.orderBy("year", "indicator_code").limit(10))

# COMMAND ----------

# DBTITLE 1,Create wide format table
from pyspark.sql.functions import col, max as spark_max

# Create wide format table (pivot indicators into columns)
worldbank_wide = worldbank_df.groupBy("year", "country_code", "country_name") \
    .pivot("indicator_code") \
    .agg(spark_max("value"))

# Rename columns to friendly names
worldbank_wide = worldbank_wide \
    .withColumnRenamed("NY.GDP.MKTP.KD.ZG", "gdp_growth") \
    .withColumnRenamed("FP.CPI.TOTL.ZG", "inflation_cpi") \
    .withColumnRenamed("SL.UEM.TOTL.ZS", "unemployment_total") \
    .withColumnRenamed("SL.UEM.1524.ZS", "unemployment_youth") \
    .withColumnRenamed("AG.PRD.FOOD.XD", "food_production_index") \
    .withColumnRenamed("SP.POP.TOTL", "population") \
    .withColumnRenamed("NY.GDP.PCAP.CD", "gdp_per_capita")

# Cast year to integer for easier joins
worldbank_wide = worldbank_wide.withColumn("year", col("year").cast("int"))

worldbank_wide.write.mode("overwrite").saveAsTable("info_env_jordan.bronze.worldbank_jordan_wide")
print(f"✓ Saved wide format table: {worldbank_wide.count()} rows")
print("\nStructure: One row per year with all indicators as columns")
display(worldbank_wide.orderBy(col("year").desc()))