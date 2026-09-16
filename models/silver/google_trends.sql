{{ config(
    materialized='table',
    tags=['silver', 'google_trends', 'economic']
) }}

/*
  Silver model: Google Trends
  
  Transforms raw Google Trends API data into deduplicated, cleaned format.
  
  Transformations:
  - Convert Unix timestamp to datetime
  - Deduplicate: Keep latest record per (event_date, search_term)
  - Filter out null values in critical fields
  - Add processing timestamp
  
  Deduplication Strategy:
  - QUALIFY + ROW_NUMBER ensures one row per date/search_term
  - Keeps the most recent timestamp when duplicates exist
  
  Source: Bronze table from Google Trends API ingestion
  Target: Silver layer for economic trend analysis
*/

SELECT 
  event_date,
  google_trends_date_label,
  FROM_UNIXTIME(timestamp) AS timestamp_datetime,
  search_term,
  trend_score,
  trend_value_display,
  CURRENT_TIMESTAMP() AS processed_at
  
FROM {{ source('bronze', 'google_trends') }}

WHERE event_date IS NOT NULL
  AND search_term IS NOT NULL
  AND trend_score IS NOT NULL

-- Deduplication: Keep latest record per date/search_term
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY event_date, search_term 
  ORDER BY timestamp DESC
) = 1