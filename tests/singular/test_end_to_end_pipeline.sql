/*
  ============================================
  END-TO-END PIPELINE TEST
  ============================================
  
  Purpose: Validates that data flows correctly through the entire
           Bronze → Silver → Gold medallion architecture.
  
  Test Strategy:
  1. Bronze: All source tables have data
  2. Silver: Row counts are reasonable after cleaning
  3. Gold: Aggregations produce expected results
  4. Cross-layer: Data lineage is intact
  
  This test FAILS if ANY check fails.
  Run with: dbt test --select test_end_to_end_pipeline
  
  Last Updated: 2024-09-16
*/

WITH bronze_checks AS (
  -- Check 1: Bronze tables have data
  SELECT 
    'bronze_acled_has_data' as check_name,
    CASE WHEN COUNT(*) > 100 THEN 'PASS' ELSE 'FAIL' END as status,
    COUNT(*) as actual_count,
    'Expected >100 ACLED events' as expected
  FROM {{ source('bronze', 'acled_jordan_events') }}
  
  UNION ALL
  
  SELECT 
    'bronze_google_trends_has_data',
    CASE WHEN COUNT(*) > 1000 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*),
    'Expected >1000 search observations'
  FROM {{ source('bronze', 'google_trends') }}
  
  UNION ALL
  
  SELECT 
    'bronze_gdelt_has_data',
    CASE WHEN COUNT(*) > 1000 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*),
    'Expected >1000 media records'
  FROM {{ source('bronze', 'gdelt_jordan_topics') }}
),

silver_checks AS (
  -- Check 2: Silver tables exist and have reasonable row counts
  SELECT 
    'silver_acled_row_count' as check_name,
    CASE 
      WHEN COUNT(*) BETWEEN 100 AND 10000 THEN 'PASS' 
      ELSE 'FAIL' 
    END as status,
    COUNT(*) as actual_count,
    'Expected 100-10,000 events' as expected
  FROM {{ ref('acled_jordan_events') }}
  
  UNION ALL
  
  SELECT 
    'silver_google_trends_row_count',
    CASE 
      WHEN COUNT(*) BETWEEN 1000 AND 50000 THEN 'PASS' 
      ELSE 'FAIL' 
    END,
    COUNT(*),
    'Expected 1,000-50,000 observations'
  FROM {{ ref('google_trends') }}
  
  UNION ALL
  
  SELECT 
    'silver_gdelt_row_count',
    CASE 
      WHEN COUNT(*) BETWEEN 1000 AND 50000 THEN 'PASS' 
      ELSE 'FAIL' 
    END,
    COUNT(*),
    'Expected 1,000-50,000 records'
  FROM {{ ref('gdelt_jordan_topics') }}
),

gold_checks AS (
  -- Check 3: Gold tables have expected grain
  SELECT 
    'gold_weekly_indicators_grain' as check_name,
    CASE 
      WHEN COUNT(*) BETWEEN 50 AND 500 THEN 'PASS' 
      ELSE 'FAIL' 
    END as status,
    COUNT(*) as actual_count,
    'Expected 50-500 weeks' as expected
  FROM {{ ref('unified_weekly_indicators') }}
  
  UNION ALL
  
  SELECT 
    'gold_theme_economic_grain',
    CASE 
      WHEN COUNT(*) BETWEEN 10 AND 100 THEN 'PASS' 
      ELSE 'FAIL' 
    END,
    COUNT(*),
    'Expected 10-100 months'
  FROM {{ ref('theme_economic_conditions') }}
  
  UNION ALL
  
  SELECT 
    'gold_theme_labor_grain',
    CASE 
      WHEN COUNT(*) BETWEEN 10 AND 100 THEN 'PASS' 
      ELSE 'FAIL' 
    END,
    COUNT(*),
    'Expected 10-100 months'
  FROM {{ ref('theme_labor_employment') }}
  
  UNION ALL
  
  SELECT 
    'gold_ml_combined_features',
    CASE 
      WHEN COUNT(*) BETWEEN 10 AND 100 THEN 'PASS' 
      ELSE 'FAIL' 
    END,
    COUNT(*),
    'Expected 10-100 months'
  FROM {{ ref('ml_combined_economic_themes') }}
),

data_quality_checks AS (
  -- Check 4: Critical columns are not null in gold tables
  SELECT 
    'gold_weekly_total_events_not_null' as check_name,
    CASE 
      WHEN COUNT(*) = 0 THEN 'PASS' 
      ELSE 'FAIL' 
    END as status,
    COUNT(*) as actual_count,
    'Expected 0 nulls in total_events' as expected
  FROM {{ ref('unified_weekly_indicators') }}
  WHERE total_events IS NULL
  
  UNION ALL
  
  SELECT 
    'gold_weekly_date_not_null',
    CASE 
      WHEN COUNT(*) = 0 THEN 'PASS' 
      ELSE 'FAIL' 
    END,
    COUNT(*),
    'Expected 0 nulls in week_start_date'
  FROM {{ ref('unified_weekly_indicators') }}
  WHERE week_start_date IS NULL
  
  UNION ALL
  
  SELECT 
    'gold_economic_inflation_not_null',
    CASE 
      WHEN COUNT(*) < 10 THEN 'PASS'  -- Allow some nulls for early months
      ELSE 'FAIL' 
    END,
    COUNT(*),
    'Expected <10 nulls in inflation_rate'
  FROM {{ ref('theme_economic_conditions') }}
  WHERE inflation_rate IS NULL
),

cross_layer_checks AS (
  -- Check 5: Silver row counts match or are less than bronze (after deduplication)
  SELECT 
    'silver_bronze_acled_consistency' as check_name,
    CASE 
      WHEN silver_count <= bronze_count AND silver_count > 0 THEN 'PASS'
      ELSE 'FAIL'
    END as status,
    silver_count as actual_count,
    CONCAT('Bronze: ', bronze_count, ' | Silver: ', silver_count) as expected
  FROM (
    SELECT 
      (SELECT COUNT(*) FROM {{ source('bronze', 'acled_jordan_events') }}) as bronze_count,
      (SELECT COUNT(*) FROM {{ ref('acled_jordan_events') }}) as silver_count
  )
),

all_checks AS (
  SELECT * FROM bronze_checks
  UNION ALL
  SELECT * FROM silver_checks
  UNION ALL
  SELECT * FROM gold_checks
  UNION ALL
  SELECT * FROM data_quality_checks
  UNION ALL
  SELECT * FROM cross_layer_checks
)

-- Return ONLY the failed checks
-- If this query returns 0 rows, the test PASSES
-- If it returns any rows, the test FAILS
SELECT 
  check_name,
  status,
  actual_count,
  expected
FROM all_checks
WHERE status = 'FAIL'
ORDER BY check_name
