{{ config(
    materialized='table',
    tags=['silver', 'gdelt', 'media']
) }}

/*
  Silver model: GDELT Jordan Topics
  
  Transforms raw GDELT API data into cleaned, analytics-ready format.
  
  Transformations:
  - Convert article_date string to DATE type
  - Filter out null dates and topics
  - Add processing timestamp for audit trail
  
  Source: Bronze table from GDELT API ingestion
  Target: Silver layer for media analysis
*/

SELECT 
  TO_DATE(article_date) AS article_date,
  topic,
  article_count,
  avg_tone,
  CURRENT_TIMESTAMP() AS processed_at
  
FROM {{ source('bronze', 'gdelt_jordan_topics') }}

WHERE article_date IS NOT NULL
  AND topic IS NOT NULL