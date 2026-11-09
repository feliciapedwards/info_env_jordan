{{ config(
    materialized='table',
    schema='gold',
    tags=['gold', 'unified', 'weekly', 'indicators']
) }}

/*
  Gold Model: Unified Weekly Indicators

  PURPOSE:
  Unified weekly view combining all four data sources for time-series and
  correlation analysis: GDELT media coverage, Google Trends search interest,
  and ACLED events, on a weekly spine.

  SOURCES (silver, via ref):
  - acled_jordan_events  (weekly spine + event counts)
  - gdelt_jordan_topics   (media topics, article counts, tone)
  - google_trends         (search terms, trend scores)

  NOTE:
  Ported from the analysis notebook 'Jordan Information Environment -
  Comprehensive Analysis' (cell: Create Unified Weekly Dataset), which
  previously created this table via CREATE OR REPLACE TABLE. dbt now owns
  this table; rebuild with `dbt run --select unified_weekly_indicators`.

  GRAIN: One row per week (country-level)
  PRIMARY KEY: week_start_date (weeks start Sunday)
*/

WITH weekly_spine AS (
  SELECT DISTINCT
    DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
    YEAR(event_date) AS year,
    WEEKOFYEAR(event_date) AS week
  FROM {{ ref('acled_jordan_events') }}
  WHERE event_date >= '2020-01-01'
),

media_weekly AS (
  SELECT
    DATE_TRUNC('WEEK', article_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
    COUNT(DISTINCT topic) AS topic_count,
    SUM(article_count) AS total_articles,
    AVG(avg_tone) AS avg_media_tone,
    MIN(avg_tone) AS min_tone,
    MAX(avg_tone) AS max_tone
  FROM {{ ref('gdelt_jordan_topics') }}
  WHERE article_date >= '2020-01-01'
  GROUP BY DATE_TRUNC('WEEK', article_date + INTERVAL 1 DAY) - INTERVAL 1 DAY
),

trends_weekly AS (
  SELECT
    DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
    COUNT(DISTINCT search_term) AS search_terms_count,
    AVG(trend_score) AS avg_trend_score,
    MAX(trend_score) AS max_trend_score,
    AVG(CASE WHEN search_term IN ('unemployment', 'inflation', 'economy', 'prices') THEN trend_score ELSE 0 END) AS economic_search_intensity
  FROM {{ ref('google_trends') }}
  WHERE event_date >= '2020-01-01'
  GROUP BY DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY
),

events_weekly AS (
  SELECT
    DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY AS week_start_date,
    COUNT(*) AS total_events,
    SUM(fatalities) AS total_fatalities,
    SUM(CASE WHEN disorder_type = 'Demonstrations' THEN 1 ELSE 0 END) AS demonstrations_count,
    SUM(CASE WHEN disorder_type = 'Political violence' THEN 1 ELSE 0 END) AS political_violence_count,
    SUM(CASE WHEN disorder_type = 'Strategic developments' THEN 1 ELSE 0 END) AS strategic_dev_count,
    SUM(CASE WHEN event_type = 'Protests' THEN 1 ELSE 0 END) AS protests_count,
    SUM(CASE WHEN event_type = 'Riots' THEN 1 ELSE 0 END) AS riots_count,
    COUNT(DISTINCT admin1) AS affected_governorates
  FROM {{ ref('acled_jordan_events') }}
  WHERE event_date >= '2020-01-01'
  GROUP BY DATE_TRUNC('WEEK', event_date + INTERVAL 1 DAY) - INTERVAL 1 DAY
)

SELECT
  s.week_start_date,
  s.year,
  s.week,
  COALESCE(m.topic_count, 0) AS media_topic_count,
  COALESCE(m.total_articles, 0) AS total_articles,
  m.avg_media_tone,
  m.min_tone,
  m.max_tone,
  COALESCE(t.search_terms_count, 0) AS search_terms_count,
  t.avg_trend_score,
  t.max_trend_score,
  t.economic_search_intensity,
  COALESCE(e.total_events, 0) AS total_events,
  COALESCE(e.total_fatalities, 0) AS total_fatalities,
  COALESCE(e.demonstrations_count, 0) AS demonstrations_count,
  COALESCE(e.political_violence_count, 0) AS political_violence_count,
  COALESCE(e.strategic_dev_count, 0) AS strategic_dev_count,
  COALESCE(e.protests_count, 0) AS protests_count,
  COALESCE(e.riots_count, 0) AS riots_count,
  COALESCE(e.affected_governorates, 0) AS affected_governorates,
  CURRENT_TIMESTAMP() AS processed_at

FROM weekly_spine s
LEFT JOIN media_weekly m ON s.week_start_date = m.week_start_date
LEFT JOIN trends_weekly t ON s.week_start_date = t.week_start_date
LEFT JOIN events_weekly e ON s.week_start_date = e.week_start_date

ORDER BY s.week_start_date