/*
  Singular Test: Data Freshness
  
  Validates that data in bronze layer is not too stale.
  This helps catch ingestion failures or outdated data.
  
  Threshold: Data should be less than 365 days old
  (Adjust threshold based on your refresh schedule)
  
  This test FAILS if data is too old.
*/

WITH freshness_checks AS (
  SELECT 
    'bronze.acled_jordan_events' as table_name,
    MAX(event_date) as latest_date,
    DATEDIFF(CURRENT_DATE(), MAX(event_date)) as days_old,
    365 as threshold_days,
    CASE 
      WHEN DATEDIFF(CURRENT_DATE(), MAX(event_date)) <= 365 THEN 'PASS'
      ELSE 'FAIL'
    END as status
  FROM {{ source('bronze', 'acled_jordan_events') }}
  
  UNION ALL
  
  SELECT 
    'bronze.google_trends',
    MAX(event_date),
    DATEDIFF(CURRENT_DATE(), MAX(event_date)),
    365,
    CASE 
      WHEN DATEDIFF(CURRENT_DATE(), MAX(event_date)) <= 365 THEN 'PASS'
      ELSE 'FAIL'
    END
  FROM {{ source('bronze', 'google_trends') }}
  
  UNION ALL
  
  SELECT 
    'bronze.gdelt_jordan_topics',
    MAX(article_date),
    DATEDIFF(CURRENT_DATE(), MAX(article_date)),
    365,
    CASE 
      WHEN DATEDIFF(CURRENT_DATE(), MAX(article_date)) <= 365 THEN 'PASS'
      ELSE 'FAIL'
    END
  FROM {{ source('bronze', 'gdelt_jordan_topics') }}
)

-- Return stale tables (test fails if any table is stale)
SELECT 
  table_name,
  latest_date,
  days_old,
  threshold_days,
  CONCAT('Data is ', days_old, ' days old (threshold: ', threshold_days, ' days)') as message
FROM freshness_checks
WHERE status = 'FAIL'
