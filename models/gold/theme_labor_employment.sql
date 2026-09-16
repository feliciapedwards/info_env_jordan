{{ config(
    materialized='table',
    schema='gold',
    tags=['gold', 'theme', 'labor', 'employment', 'policy']
) }}

/*
  Gold Model: Labor & Employment Theme
  
  PURPOSE:
  Monthly aggregation of labor-related events, unemployment searches, 
  and employment indicators to predict unemployment trends.
  
  POLICY QUESTIONS:
  - Should Jordan raise minimum wages?
  - Are labor subsidies effective?
  - Is unemployment worsening?
  
  PREDICTIVE HYPOTHESIS:
  Labor protests + unemployment searches predict unemployment rate 
  with 1-3 month lead time.
  
  GRAIN: One row per month (country-level)
  PRIMARY KEY: event_month
*/

WITH monthly_labor_events AS (
  SELECT 
    DATE_TRUNC('month', event_date) AS event_month,
    
    -- Labor-related event counts
    COUNT(*) AS total_labor_events,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'teacher_strike') AS teacher_strikes,
    COUNT(*) FILTER (WHERE specific_primary_cause LIKE '%wage%') AS wage_disputes,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'public_sector_wage_dispute') AS public_wage_disputes,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'private_sector_wage_dispute') AS private_wage_disputes,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'layoff_protest') AS layoff_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'working_conditions_protest') AS working_conditions_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'healthcare_worker_protest') AS healthcare_worker_protests,
    
    -- Aggregate metrics
    SUM(fatalities) AS total_labor_fatalities,
    AVG(crowd_size_int) AS avg_labor_crowd_size,
    
    -- Event intensity (protests with violence)
    COUNT(*) FILTER (WHERE is_violent = TRUE) AS violent_labor_events,
    COUNT(*) FILTER (WHERE is_peaceful_protest = TRUE) AS peaceful_labor_protests
    
  FROM {{ ref('acled_jordan_events') }}
  WHERE primary_cause = 'labor_workers_rights'  -- THEME FILTER
  GROUP BY 1
),

monthly_employment_searches AS (
  SELECT 
    DATE_TRUNC('month', event_date) AS event_month,
    
    -- Employment-related search trends (average scores)
    AVG(trend_score) FILTER (WHERE search_term = 'unemployment') AS avg_unemployment_search,
    AVG(trend_score) FILTER (WHERE search_term = 'jobs') AS avg_jobs_search,
    AVG(trend_score) FILTER (WHERE search_term = 'employment') AS avg_employment_search
    
  FROM {{ ref('google_trends') }}
  WHERE search_term IN ('unemployment', 'jobs', 'employment', 'wages', 'hiring')
  GROUP BY 1
),

monthly_employment_indicators AS (
  -- Placeholder for World Bank employment indicators
  -- TODO: Create silver.worldbank_indicators model first
  -- For now, return NULL so the model compiles
  SELECT 
    CAST(NULL AS DATE) AS event_month,
    CAST(NULL AS DOUBLE) AS unemployment_rate,
    CAST(NULL AS DOUBLE) AS labor_force_participation_rate,
    CAST(NULL AS DOUBLE) AS youth_unemployment_rate
  WHERE 1=0  -- Return no rows until worldbank_indicators is available
),

month_spine AS (
  -- Generate all months from min to max event_date
  SELECT DISTINCT DATE_TRUNC('month', event_date) AS event_month
  FROM {{ ref('acled_jordan_events') }}
  WHERE event_date IS NOT NULL
)

-- Combine all features with LEFT JOINs to preserve all months
SELECT 
  s.event_month,
  
  -- Theme label
  'labor_employment' AS theme,
  
  -- Event predictors (labor-specific)
  COALESCE(e.total_labor_events, 0) AS total_labor_events,
  COALESCE(e.teacher_strikes, 0) AS teacher_strikes,
  COALESCE(e.wage_disputes, 0) AS wage_disputes,
  COALESCE(e.public_wage_disputes, 0) AS public_wage_disputes,
  COALESCE(e.private_wage_disputes, 0) AS private_wage_disputes,
  COALESCE(e.layoff_protests, 0) AS layoff_protests,
  COALESCE(e.working_conditions_protests, 0) AS working_conditions_protests,
  COALESCE(e.healthcare_worker_protests, 0) AS healthcare_worker_protests,
  COALESCE(e.violent_labor_events, 0) AS violent_labor_events,
  COALESCE(e.peaceful_labor_protests, 0) AS peaceful_labor_protests,
  COALESCE(e.total_labor_fatalities, 0) AS total_labor_fatalities,
  e.avg_labor_crowd_size,
  
  -- Search predictors (employment-related)
  t.avg_unemployment_search,
  t.avg_jobs_search,
  t.avg_employment_search,
  
  -- Economic target variables (what we want to predict)
  i.unemployment_rate,
  i.labor_force_participation_rate,
  i.youth_unemployment_rate,
  
  -- Lagged features for predictive modeling (1-3 month lags)
  LAG(COALESCE(e.total_labor_events, 0), 1) OVER (ORDER BY s.event_month) AS labor_events_lag1,
  LAG(COALESCE(e.total_labor_events, 0), 2) OVER (ORDER BY s.event_month) AS labor_events_lag2,
  LAG(COALESCE(e.total_labor_events, 0), 3) OVER (ORDER BY s.event_month) AS labor_events_lag3,
  
  LAG(t.avg_unemployment_search, 1) OVER (ORDER BY s.event_month) AS unemployment_search_lag1,
  LAG(t.avg_unemployment_search, 2) OVER (ORDER BY s.event_month) AS unemployment_search_lag2,
  LAG(t.avg_unemployment_search, 3) OVER (ORDER BY s.event_month) AS unemployment_search_lag3,
  
  -- Rolling averages (3-month moving average)
  AVG(COALESCE(e.total_labor_events, 0)) OVER (
    ORDER BY s.event_month 
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS labor_events_3mo_avg,
  
  AVG(t.avg_unemployment_search) OVER (
    ORDER BY s.event_month 
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS unemployment_search_3mo_avg,
  
  -- Metadata
  CURRENT_TIMESTAMP() AS processed_at

FROM month_spine s
LEFT JOIN monthly_labor_events e ON s.event_month = e.event_month
LEFT JOIN monthly_employment_searches t ON s.event_month = t.event_month
LEFT JOIN monthly_employment_indicators i ON s.event_month = i.event_month

ORDER BY s.event_month
