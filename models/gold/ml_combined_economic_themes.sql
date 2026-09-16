{{ config(
    materialized='table',
    schema='gold',
    tags=['gold', 'ml', 'combined', 'economic', 'policy']
) }}

/*
  Gold Model: Combined Economic Themes for ML
  
  PURPOSE:
  Unified monthly table combining labor/employment AND economic conditions themes
  for correlation analysis and predictive modeling.
  
  EXCLUDES:
  - Political stability theme (weak economic correlation)
  - Regional/identity theme (no economic correlation)
  
  USE CASE:
  - Primary table for economic prediction models
  - Correlation analysis: events + searches → unemployment + inflation
  - Lag analysis: Do events lead economic changes by 1-3 months?
  - Feature engineering: Interactions, rolling averages, momentum
  - Policy impact measurement
  
  GRAIN: One row per month (country-level)
  PRIMARY KEY: event_month
  TARGET VARIABLES: unemployment_rate, inflation_rate, gdp_growth_rate
*/

WITH labor_features AS (
  SELECT 
    event_month,
    
    -- Labor event features
    total_labor_events,
    teacher_strikes,
    wage_disputes,
    layoff_protests,
    violent_labor_events,
    peaceful_labor_protests,
    
    -- Employment search features
    avg_unemployment_search,
    avg_jobs_search,
    
    -- Lagged labor features
    labor_events_lag1,
    labor_events_lag2,
    labor_events_lag3,
    unemployment_search_lag1,
    unemployment_search_lag2,
    unemployment_search_lag3,
    
    -- Rolling averages
    labor_events_3mo_avg,
    unemployment_search_3mo_avg,
    
    -- Target variables from labor theme
    unemployment_rate,
    labor_force_participation_rate
    
  FROM {{ ref('theme_labor_employment') }}
),

economic_features AS (
  SELECT 
    event_month,
    
    -- Economic event features
    total_economic_events,
    fuel_price_protests,
    inflation_protests,
    subsidy_protests,
    cost_living_protests,
    violent_economic_events,
    peaceful_economic_protests,
    
    -- Economic search features
    avg_inflation_search,
    avg_prices_search,
    avg_cost_living_search,
    
    -- Lagged economic features
    economic_events_lag1,
    economic_events_lag2,
    economic_events_lag3,
    inflation_search_lag1,
    inflation_search_lag2,
    inflation_search_lag3,
    
    -- Rolling averages
    economic_events_3mo_avg,
    inflation_search_3mo_avg,
    
    -- Target variables from economic theme
    inflation_rate,
    gdp_growth_rate,
    cpi_index
    
  FROM {{ ref('theme_economic_conditions') }}
),

month_spine AS (
  SELECT DISTINCT event_month
  FROM {{ ref('theme_labor_employment') }}
)

-- Combine labor + economic features with FULL OUTER JOIN
SELECT 
  COALESCE(l.event_month, e.event_month) AS event_month,
  
  -- ========================================
  -- LABOR & EMPLOYMENT PREDICTORS
  -- ========================================
  
  -- Current month labor events
  COALESCE(l.total_labor_events, 0) AS total_labor_events,
  COALESCE(l.teacher_strikes, 0) AS teacher_strikes,
  COALESCE(l.wage_disputes, 0) AS wage_disputes,
  COALESCE(l.layoff_protests, 0) AS layoff_protests,
  COALESCE(l.violent_labor_events, 0) AS violent_labor_events,
  COALESCE(l.peaceful_labor_protests, 0) AS peaceful_labor_protests,
  
  -- Current month employment searches
  l.avg_unemployment_search,
  l.avg_jobs_search,
  
  -- Lagged labor features (for predictive models)
  l.labor_events_lag1,
  l.labor_events_lag2,
  l.labor_events_lag3,
  l.unemployment_search_lag1,
  l.unemployment_search_lag2,
  l.unemployment_search_lag3,
  
  -- Smoothed labor features
  l.labor_events_3mo_avg,
  l.unemployment_search_3mo_avg,
  
  -- ========================================
  -- ECONOMIC CONDITIONS PREDICTORS
  -- ========================================
  
  -- Current month economic events
  COALESCE(e.total_economic_events, 0) AS total_economic_events,
  COALESCE(e.fuel_price_protests, 0) AS fuel_price_protests,
  COALESCE(e.inflation_protests, 0) AS inflation_protests,
  COALESCE(e.subsidy_protests, 0) AS subsidy_protests,
  COALESCE(e.cost_living_protests, 0) AS cost_living_protests,
  COALESCE(e.violent_economic_events, 0) AS violent_economic_events,
  COALESCE(e.peaceful_economic_protests, 0) AS peaceful_economic_protests,
  
  -- Current month economic searches
  e.avg_inflation_search,
  e.avg_prices_search,
  e.avg_cost_living_search,
  
  -- Lagged economic features (for predictive models)
  e.economic_events_lag1,
  e.economic_events_lag2,
  e.economic_events_lag3,
  e.inflation_search_lag1,
  e.inflation_search_lag2,
  e.inflation_search_lag3,
  
  -- Smoothed economic features
  e.economic_events_3mo_avg,
  e.inflation_search_3mo_avg,
  
  -- ========================================
  -- COMBINED/INTERACTION FEATURES
  -- ========================================
  
  -- Total distress signal (labor + economic)
  COALESCE(l.total_labor_events, 0) + COALESCE(e.total_economic_events, 0) AS total_distress_events,
  
  -- Combined search intensity
  COALESCE(l.avg_unemployment_search, 0) + COALESCE(e.avg_inflation_search, 0) AS combined_search_intensity,
  
  -- Violence ratio (violent events / total events)
  CASE 
    WHEN (COALESCE(l.total_labor_events, 0) + COALESCE(e.total_economic_events, 0)) > 0
    THEN (COALESCE(l.violent_labor_events, 0) + COALESCE(e.violent_economic_events, 0)) * 1.0 / 
         (COALESCE(l.total_labor_events, 0) + COALESCE(e.total_economic_events, 0))
    ELSE 0
  END AS violence_ratio,
  
  -- Search-event alignment (both high = crisis signal)
  CASE 
    WHEN l.avg_unemployment_search > 70 AND l.total_labor_events > 10 THEN 1
    WHEN e.avg_inflation_search > 70 AND e.total_economic_events > 10 THEN 1
    ELSE 0
  END AS high_alert_flag,
  
  -- ========================================
  -- TARGET VARIABLES (what we predict)
  -- ========================================
  
  l.unemployment_rate AS target_unemployment_rate,
  l.labor_force_participation_rate AS target_labor_participation,
  e.inflation_rate AS target_inflation_rate,
  e.gdp_growth_rate AS target_gdp_growth,
  e.cpi_index AS target_cpi,
  
  -- ========================================
  -- METADATA
  -- ========================================
  
  -- Time features (for seasonality)
  MONTH(COALESCE(l.event_month, e.event_month)) AS month_num,
  QUARTER(COALESCE(l.event_month, e.event_month)) AS quarter_num,
  YEAR(COALESCE(l.event_month, e.event_month)) AS year_num,
  
  CURRENT_TIMESTAMP() AS processed_at

FROM labor_features l
FULL OUTER JOIN economic_features e ON l.event_month = e.event_month

ORDER BY event_month
