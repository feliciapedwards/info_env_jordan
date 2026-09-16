{{ config(
    materialized='table',
    schema='gold',
    tags=['gold', 'theme', 'economic', 'inflation', 'policy']
) }}

/*
  Gold Model: Economic Conditions Theme
  
  PURPOSE:
  Monthly aggregation of economic grievance events, inflation/price searches,
  and economic indicators to predict inflation and GDP trends.
  
  POLICY QUESTIONS:
  - Should Jordan remove fuel subsidies?
  - Will inflation worsen?
  - What's the impact of subsidy cuts?
  
  PREDICTIVE HYPOTHESIS:
  Economic protests + inflation searches predict inflation rate
  with 1-3 month lead time.
  
  GRAIN: One row per month (country-level)
  PRIMARY KEY: event_month
*/

WITH monthly_economic_events AS (
  SELECT 
    DATE_TRUNC('month', event_date) AS event_month,
    
    -- Economic grievance event counts
    COUNT(*) AS total_economic_events,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'fuel_price_protest') AS fuel_price_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'inflation_protest') AS inflation_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'tax_increase_opposition') AS tax_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'subsidy_removal_protest') AS subsidy_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'cost_of_living_protest') AS cost_living_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'utility_bill_protest') AS utility_protests,
    COUNT(*) FILTER (WHERE specific_primary_cause = 'poverty_complaint') AS poverty_complaints,
    
    -- Aggregate metrics
    SUM(fatalities) AS total_economic_fatalities,
    AVG(crowd_size_int) AS avg_economic_crowd_size,
    
    -- Event intensity
    COUNT(*) FILTER (WHERE is_violent = TRUE) AS violent_economic_events,
    COUNT(*) FILTER (WHERE is_peaceful_protest = TRUE) AS peaceful_economic_protests
    
  FROM {{ ref('acled_jordan_events') }}
  WHERE primary_cause = 'economic_grievances'  -- THEME FILTER
  GROUP BY 1
),

monthly_economic_searches AS (
  SELECT 
    DATE_TRUNC('month', event_date) AS event_month,
    
    -- Economic-related search trends
    AVG(trend_score) FILTER (WHERE search_term = 'inflation') AS avg_inflation_search,
    AVG(trend_score) FILTER (WHERE search_term = 'prices') AS avg_prices_search,
    AVG(trend_score) FILTER (WHERE search_term = 'cost of living') AS avg_cost_living_search,
    AVG(trend_score) FILTER (WHERE search_term = 'fuel prices') AS avg_fuel_search
    
  FROM {{ ref('google_trends') }}
  WHERE search_term IN ('inflation', 'prices', 'cost of living', 'fuel prices', 'economy')
  GROUP BY 1
),

monthly_economic_indicators AS (
  -- Placeholder for World Bank economic indicators
  -- TODO: Create silver.worldbank_indicators model first
  SELECT 
    CAST(NULL AS DATE) AS event_month,
    CAST(NULL AS DOUBLE) AS inflation_rate,
    CAST(NULL AS DOUBLE) AS gdp_growth_rate,
    CAST(NULL AS DOUBLE) AS cpi_index,
    CAST(NULL AS DOUBLE) AS consumer_confidence_index
  WHERE 1=0  -- Return no rows until worldbank_indicators is available
),

month_spine AS (
  -- Generate all months from min to max event_date
  SELECT DISTINCT DATE_TRUNC('month', event_date) AS event_month
  FROM {{ ref('acled_jordan_events') }}
  WHERE event_date IS NOT NULL
)

-- Combine all features
SELECT 
  s.event_month,
  
  -- Theme label
  'economic_conditions' AS theme,
  
  -- Event predictors (economic grievance-specific)
  COALESCE(e.total_economic_events, 0) AS total_economic_events,
  COALESCE(e.fuel_price_protests, 0) AS fuel_price_protests,
  COALESCE(e.inflation_protests, 0) AS inflation_protests,
  COALESCE(e.tax_protests, 0) AS tax_protests,
  COALESCE(e.subsidy_protests, 0) AS subsidy_protests,
  COALESCE(e.cost_living_protests, 0) AS cost_living_protests,
  COALESCE(e.utility_protests, 0) AS utility_protests,
  COALESCE(e.poverty_complaints, 0) AS poverty_complaints,
  COALESCE(e.violent_economic_events, 0) AS violent_economic_events,
  COALESCE(e.peaceful_economic_protests, 0) AS peaceful_economic_protests,
  COALESCE(e.total_economic_fatalities, 0) AS total_economic_fatalities,
  e.avg_economic_crowd_size,
  
  -- Search predictors (economic-related)
  t.avg_inflation_search,
  t.avg_prices_search,
  t.avg_cost_living_search,
  t.avg_fuel_search,
  
  -- Economic target variables (what we want to predict)
  i.inflation_rate,
  i.gdp_growth_rate,
  i.cpi_index,
  i.consumer_confidence_index,
  
  -- Lagged features for predictive modeling (1-3 month lags)
  LAG(COALESCE(e.total_economic_events, 0), 1) OVER (ORDER BY s.event_month) AS economic_events_lag1,
  LAG(COALESCE(e.total_economic_events, 0), 2) OVER (ORDER BY s.event_month) AS economic_events_lag2,
  LAG(COALESCE(e.total_economic_events, 0), 3) OVER (ORDER BY s.event_month) AS economic_events_lag3,
  
  LAG(t.avg_inflation_search, 1) OVER (ORDER BY s.event_month) AS inflation_search_lag1,
  LAG(t.avg_inflation_search, 2) OVER (ORDER BY s.event_month) AS inflation_search_lag2,
  LAG(t.avg_inflation_search, 3) OVER (ORDER BY s.event_month) AS inflation_search_lag3,
  
  -- Rolling averages (3-month moving average)
  AVG(COALESCE(e.total_economic_events, 0)) OVER (
    ORDER BY s.event_month 
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS economic_events_3mo_avg,
  
  AVG(t.avg_inflation_search) OVER (
    ORDER BY s.event_month 
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS inflation_search_3mo_avg,
  
  -- Metadata
  CURRENT_TIMESTAMP() AS processed_at

FROM month_spine s
LEFT JOIN monthly_economic_events e ON s.event_month = e.event_month
LEFT JOIN monthly_economic_searches t ON s.event_month = t.event_month
LEFT JOIN monthly_economic_indicators i ON s.event_month = i.event_month

ORDER BY s.event_month
