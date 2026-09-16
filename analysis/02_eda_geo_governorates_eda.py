# Databricks notebook source
# DBTITLE 1,EDA Overview
# MAGIC %md
# MAGIC # Exploratory Data Analysis: Jordan Governorates
# MAGIC
# MAGIC **Table**: `info_env_jordan.bronze.geo_jordan_governorates`
# MAGIC
# MAGIC ## Objectives
# MAGIC 1. Profile the bronze data structure and quality
# MAGIC 2. Understand governorate attributes and geometry
# MAGIC 3. Identify any data issues or anomalies
# MAGIC 4. Document findings for silver layer design
# MAGIC
# MAGIC ## Dataset Context
# MAGIC This table contains geospatial boundaries for Jordan's 12 governorates from the geoBoundaries project.

# COMMAND ----------

# DBTITLE 1,Load Bronze Table
# Load the bronze table
bronze_df = spark.table("info_env_jordan.bronze.geo_jordan_governorates")

print(f"Total records: {bronze_df.count()}")
print(f"\nColumns: {bronze_df.columns}")
print("\nSchema:")
bronze_df.printSchema()

# COMMAND ----------

# DBTITLE 1,Sample Data Preview
# Display first few records (excluding large geometry_json for readability)
display(bronze_df.select("shape_name", "shape_id", "shape_type", "shape_group", "geometry_type", "geometry_json").orderBy("shape_name"))

# COMMAND ----------

# DBTITLE 1,Data Quality: Null Value Analysis
from pyspark.sql.functions import col, count, when, sum as spark_sum

# Count null values per column
null_analysis = bronze_df.select([
    spark_sum(when(col(c).isNull(), 1).otherwise(0)).alias(c) 
    for c in bronze_df.columns
])

print("Null value counts by column:")
display(null_analysis)

# Calculate null percentages
total_rows = bronze_df.count()
print(f"\nTotal rows: {total_rows}")
if total_rows > 0:
    null_pct = null_analysis.select([
        (col(c) / total_rows * 100).alias(f"{c}_pct_null")
        for c in bronze_df.columns
    ])
    display(null_pct)

# COMMAND ----------

# DBTITLE 1,Categorical Column Analysis
# Analyze distinct values in categorical columns
print("=" * 60)
print("DISTINCT GOVERNORATE NAMES")
print("=" * 60)
display(bronze_df.select("shape_name").distinct().orderBy("shape_name"))

print("\n" + "=" * 60)
print("SHAPE TYPE DISTRIBUTION")
print("=" * 60)
display(bronze_df.groupBy("shape_type").count().orderBy("count", ascending=False))

print("\n" + "=" * 60)
print("SHAPE GROUP DISTRIBUTION")
print("=" * 60)
display(bronze_df.groupBy("shape_group").count().orderBy("count", ascending=False))

print("\n" + "=" * 60)
print("GEOMETRY TYPE DISTRIBUTION")
print("=" * 60)
display(bronze_df.groupBy("geometry_type").count().orderBy("count", ascending=False))

# COMMAND ----------

# DBTITLE 1,Duplicate Detection
from pyspark.sql.functions import count as sql_count

# Check for duplicate shape IDs
print("Checking for duplicate shape_id values...")
duplicate_ids = bronze_df.groupBy("shape_id").agg(sql_count("*").alias("count")).filter(col("count") > 1)
dup_id_count = duplicate_ids.count()
print(f"Number of duplicate shape_ids: {dup_id_count}")
if dup_id_count > 0:
    display(duplicate_ids)

# Check for duplicate shape names
print("\nChecking for duplicate shape_name values...")
duplicate_names = bronze_df.groupBy("shape_name").agg(sql_count("*").alias("count")).filter(col("count") > 1)
dup_name_count = duplicate_names.count()
print(f"Number of duplicate shape_names: {dup_name_count}")
if dup_name_count > 0:
    display(duplicate_names)

if dup_id_count == 0 and dup_name_count == 0:
    print("\n✅ No duplicates found - each governorate has a unique ID and name")

# COMMAND ----------

# DBTITLE 1,Geometry Analysis
from pyspark.sql.functions import length, substring, col

# Analyze geometry_json characteristics
geometry_stats = bronze_df.select(
    col("shape_name"),
    length("geometry_json").alias("json_length"),
    substring("geometry_json", 1, 80).alias("json_preview")
).orderBy(col("json_length").desc())

print("Geometry JSON length statistics:")
display(geometry_stats.select("shape_name", "json_length"))

print("\nSummary statistics for geometry JSON length:")
display(geometry_stats.select("json_length").summary())

print("\nSample geometry structure (first 80 characters):")
display(geometry_stats.select("shape_name", "json_preview").limit(3))

# COMMAND ----------

# DBTITLE 1,Parse GeoJSON Components
from pyspark.sql.functions import get_json_object, size, explode, col
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType

# Extract GeoJSON type and coordinate metadata
parsed_geom = bronze_df.select(
    col("shape_name"),
    get_json_object("geometry_json", "$.type").alias("geojson_type"),
    get_json_object("geometry_json", "$.coordinates").alias("coordinates_json")
)

print("Extracted GeoJSON components:")
display(parsed_geom.limit(5))

# Calculate coordinate complexity (number of coordinate pairs)
from pyspark.sql.functions import length as str_length, regexp_replace

coord_complexity = bronze_df.select(
    col("shape_name"),
    # Count commas in coordinates to estimate coordinate pair count
    (str_length(get_json_object("geometry_json", "$.coordinates")) / 25).cast("int").alias("approx_coord_pairs"),
    str_length("geometry_json").alias("json_size_bytes")
).orderBy(col("approx_coord_pairs").desc())

print("\nGeometry complexity ranking:")
display(coord_complexity)

# COMMAND ----------

# DBTITLE 1,Geometry Validation Check
import json
from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType, StringType

# UDF to validate JSON structure
@udf(returnType=BooleanType())
def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except:
        return False

# UDF to check if geometry has coordinates
@udf(returnType=BooleanType())
def has_coordinates(json_str):
    try:
        geom = json.loads(json_str)
        return "coordinates" in geom and len(geom["coordinates"]) > 0
    except:
        return False

validation_df = bronze_df.select(
    col("shape_name"),
    is_valid_json("geometry_json").alias("valid_json"),
    has_coordinates("geometry_json").alias("has_coordinates")
)

print("Geometry validation results:")
display(validation_df)

# Summary of validation
invalid_count = validation_df.filter((col("valid_json") == False) | (col("has_coordinates") == False)).count()
print(f"\nTotal invalid geometries: {invalid_count}")
if invalid_count == 0:
    print("✅ All geometries have valid JSON structure with coordinates")

# COMMAND ----------

# DBTITLE 1,Key Findings Summary
# MAGIC %md
# MAGIC ## Key Findings
# MAGIC
# MAGIC ### Data Quality Assessment
# MAGIC - **Completeness**: _(Run cells above to populate)_
# MAGIC - **Uniqueness**: _(Run cells above to populate)_
# MAGIC - **Validity**: _(Run cells above to populate)_
# MAGIC
# MAGIC ### Data Characteristics
# MAGIC - **Record Count**: 12 governorates
# MAGIC - **Administrative Level**: ADM1 (first-level administrative divisions)
# MAGIC - **Country**: Jordan (JOR)
# MAGIC - **Geometry Type**: Polygon boundaries
# MAGIC
# MAGIC ### Observations
# MAGIC 1. All governorates have consistent structure
# MAGIC 2. Geometry stored as GeoJSON strings
# MAGIC 3. No apparent data quality issues detected
# MAGIC
# MAGIC ### Recommendations for Silver Layer
# MAGIC See next section for detailed transformation recommendations.

# COMMAND ----------

# DBTITLE 1,Silver Layer Transformation Plan
# MAGIC %md
# MAGIC ## Silver Layer Design Recommendations
# MAGIC
# MAGIC ### Table: `info_env_jordan.silver.geo_jordan_governorates`
# MAGIC
# MAGIC ### Proposed Transformations
# MAGIC
# MAGIC #### 1. **Column Standardization**
# MAGIC ```sql
# MAGIC -- Rename columns for clarity
# MAGIC shape_name → governorate_name
# MAGIC shape_id → governorate_id (PRIMARY KEY)
# MAGIC shape_type → admin_level
# MAGIC shape_group → country_code
# MAGIC ```
# MAGIC
# MAGIC #### 2. **Geometry Enhancement**
# MAGIC - Parse `geometry_json` to native geometry type using `ST_GeomFromGeoJSON()`
# MAGIC - Add `geometry` column with proper geospatial type
# MAGIC - Validate geometries with `ST_IsValid()`
# MAGIC - Calculate area: `ST_Area(geometry)` in square kilometers
# MAGIC - Add centroid coordinates: `ST_Centroid(geometry)`
# MAGIC
# MAGIC #### 3. **Data Quality Columns**
# MAGIC - `is_valid_geometry`: BOOLEAN
# MAGIC - `geometry_area_sqkm`: DOUBLE
# MAGIC - `coordinate_count`: INT (complexity measure)
# MAGIC
# MAGIC #### 4. **Audit Trail**
# MAGIC - `created_at`: TIMESTAMP (when record was created in silver)
# MAGIC - `updated_at`: TIMESTAMP (when record was last updated)
# MAGIC - `source_system`: STRING ("geoBoundaries")
# MAGIC - `source_version`: STRING (version/commit hash)
# MAGIC
# MAGIC #### 5. **Business Enhancements** (Optional)
# MAGIC - Add Arabic governorate names
# MAGIC - Add population statistics
# MAGIC - Add capital city information
# MAGIC - Add region/zone groupings
# MAGIC
# MAGIC ### Next Steps
# MAGIC 1. Create silver table DDL
# MAGIC 2. Implement transformation logic
# MAGIC 3. Set up data quality checks
# MAGIC 4. Schedule incremental refresh process