# Databricks notebook source
# DBTITLE 1,Google Sheets Ingestion Overview
# MAGIC %md
# MAGIC # Bronze Layer: Google Sheets Data Ingestion
# MAGIC
# MAGIC **Source**: [Google Sheet](https://docs.google.com/spreadsheets/d/1677AMAPbqeNjJaDbXZ86tGtinkLTMwfWbYrAZrc5f_M/edit?usp=sharing)
# MAGIC
# MAGIC ## Ingestion Methods
# MAGIC
# MAGIC This notebook provides three methods to ingest Google Sheets data:
# MAGIC
# MAGIC 1. **Method 1: Public URL Export** (Simplest - requires sheet to be public)
# MAGIC 2. **Method 2: Google Sheets API** (For private sheets with service account)
# MAGIC 3. **Method 3: Manual Upload** (Download CSV and upload to Databricks)
# MAGIC
# MAGIC ## Prerequisites
# MAGIC
# MAGIC * **For Method 1**: Sheet must be shared with "Anyone with the link" (Viewer access)
# MAGIC * **For Method 2**: Google Cloud service account with Sheets API enabled
# MAGIC * **For Method 3**: Downloaded CSV file from Google Sheets
# MAGIC
# MAGIC ## Output
# MAGIC
# MAGIC Bronze table: `info_env_jordan.bronze.google_sheets_data` (adjust table name based on content)

# COMMAND ----------

# DBTITLE 1,Method 1: Fetch from Public Google Sheets URL
import requests
import pandas as pd
from io import StringIO

# Google Sheets configuration
sheet_id = "1677AMAPbqeNjJaDbXZ86tGtinkLTMwfWbYrAZrc5f_M"
gid = "1146765514"  # Specific sheet tab ID from the URL

# Construct CSV export URL
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

print("=" * 70)
print("METHOD 1: Fetching from Public Google Sheets URL")
print("=" * 70)
print(f"\nSheet ID: {sheet_id}")
print(f"Tab GID: {gid}")
print(f"Export URL: {csv_url}\n")

try:
    # Fetch the CSV data
    print("Fetching data from Google Sheets...")
    response = requests.get(csv_url, timeout=30)
    response.raise_for_status()
    
    # Parse CSV into pandas DataFrame
    csv_data = StringIO(response.text)
    pandas_df = pd.read_csv(csv_data)
    
    print(f"\n✓ Successfully fetched {len(pandas_df)} rows, {len(pandas_df.columns)} columns")
    print(f"\nColumn names:")
    for i, col in enumerate(pandas_df.columns, 1):
        print(f"  {i}. {col}")
    
    # Convert to Spark DataFrame
    google_sheets_df = spark.createDataFrame(pandas_df)
    
    print(f"\n✓ Converted to Spark DataFrame")
    print("\nSchema:")
    google_sheets_df.printSchema()
    
    # Display preview
    print("\nData preview (first 20 rows):")
    display(google_sheets_df.limit(20))
    
    print("\n" + "=" * 70)
    print("✓ SUCCESS: Data loaded from Google Sheets")
    print("=" * 70)
    print("\nNext step: Run the 'Save to Bronze Table' cell below")
    
except requests.exceptions.HTTPError as e:
    print(f"\n✗ HTTP Error: {e}")
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING")
    print("=" * 70)
    if "401" in str(e) or "403" in str(e):
        print("\nThe sheet is not publicly accessible.")
        print("\nTo fix this:")
        print("1. Open: https://docs.google.com/spreadsheets/d/1677AMAPbqeNjJaDbXZ86tGtinkLTMwfWbYrAZrc5f_M/edit?usp=sharing")
        print("2. Click 'Share' (top-right corner)")
        print("3. Change 'Restricted' to 'Anyone with the link'")
        print("4. Set permission to 'Viewer'")
        print("5. Click 'Done'")
        print("6. Re-run this cell")
        print("\nAlternatively, use Method 2 (Google Sheets API) or Method 3 (Manual Upload) below.")
    raise
except Exception as e:
    print(f"\n✗ Unexpected Error: {e}")
    print("\nTry Method 2 or Method 3 below.")
    raise

# COMMAND ----------

# DBTITLE 1,Method 3: Manual Upload Instructions
# MAGIC %md
# MAGIC ## Method 3: Manual Download and Upload (Recommended)
# MAGIC
# MAGIC Best for one-time loads or if you don't want to configure API access.
# MAGIC
# MAGIC ### Steps:
# MAGIC
# MAGIC 1. **Download from Google Sheets**:
# MAGIC    - Open: https://docs.google.com/spreadsheets/d/1677AMAPbqeNjJaDbXZ86tGtinkLTMwfWbYrAZrc5f_M/edit?usp=sharing
# MAGIC    - Click **File → Download → Comma Separated Values (.csv)**
# MAGIC    - Save the file to your computer
# MAGIC
# MAGIC 2. **Upload to Databricks**:
# MAGIC    - Drag and drop the CSV file into this chat window
# MAGIC    - I'll help you load it into the bronze table
# MAGIC
# MAGIC 3. After uploading, tell me and I'll create the code to load it

# COMMAND ----------

# DBTITLE 1,Save to Bronze Table
# Save the loaded data to a bronze table
# NOTE: Update the table name based on your data content

# Check if google_sheets_df exists (from one of the methods above)
if 'google_sheets_df' not in locals():
    print("✗ Error: No data loaded yet")
    print("\nPlease run Method 1 above first to load the data.")
    print("If Method 1 doesn't work (401 error), use Method 3: download the CSV and upload it here.")
else:
    # Define target table name (update this based on your data)
    target_table = "info_env_jordan.bronze.gdelt_jordan_topics"
    
    print("=" * 70)
    print("SAVING TO BRONZE TABLE")
    print("=" * 70)
    print(f"\nTarget table: {target_table}")
    print(f"Records to write: {google_sheets_df.count()}")
    print(f"Columns: {len(google_sheets_df.columns)}\n")
    
    # Write to bronze table
    google_sheets_df.write \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(target_table)
    
    print(f"✓ Successfully saved to {target_table}\n")
    
    # Verify the table
    print("Verifying saved table:")
    saved_df = spark.table(target_table)
    print(f"  Rows: {saved_df.count()}")
    print(f"  Columns: {len(saved_df.columns)}")
    
    print("\n" + "=" * 70)
    print("✓ BRONZE TABLE CREATED SUCCESSFULLY")
    print("=" * 70)

# COMMAND ----------

