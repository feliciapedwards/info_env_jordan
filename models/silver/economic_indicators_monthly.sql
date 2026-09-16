{{ config(
    materialized='table',
    schema='silver',
    tags=['silver', 'economic', 'world_bank', 'monthly']
) }}

/*
  Silver model: Economic Indicators Monthly
  
  Transforms quarterly economic data into monthly grain for gold layer consumption.
  
  Source: Bronze quarterly economic metrics (GDP, unemployment, inflation)
  Target: Monthly time series (2005-2026, ~264 months)
  
  Transformations:
  1. Pivot from long format (metric/value) to wide format (one column per indicator)
  2. Cast STRING values to DOUBLE for numeric analysis
  3. Convert year + quarter strings to proper DATE (quarter_start_date)
  4. Expand quarterly data to monthly grain (repeat values across 3 months)
  5. Forward fill missing values within reasonable gaps (1 quarter)
  6. Add data quality and lineage metadata
  
  Design Decision: Flat Repeat Strategy
  - Each quarter's value repeats identically across its 3 months
  - Q1 2022 (22.8% unemployment) → Jan/Feb/Mar 2022 all = 22.8%
  - Honest about data granularity; no false precision from interpolation
  - Appropriate because economic indicators are slow-moving context variables
  
  Output Grain: Monthly (one row per month)
  Coverage: 88 quarters × 3 months = 264 monthly rows
  
  Runtime: <1 minute (simple pivoting and expansion, no AI functions)
*/

WITH quarterly_pivoted AS (
  -- Step 1: Pivot from long to wide format and cast to numeric
  SELECT 
    year,
    quarter,
    CAST(MAX(CASE WHEN metric = 'gdp_growth' THEN value END) AS DOUBLE) as gdp_growth_rate,
    CAST(MAX(CASE WHEN metric = 'unemployment' THEN value END) AS DOUBLE) as unemployment_rate,
    CAST(MAX(CASE WHEN metric = 'youth_unemployment' THEN value END) AS DOUBLE) as youth_unemployment_rate,
    CAST(MAX(CASE WHEN metric = 'inflation_avg_qtr' THEN value END) AS DOUBLE) as inflation_rate
  FROM {{ source('bronze', 'jordan_econ_metrics_qtr') }}
  WHERE value IS NOT NULL  -- Filter out future placeholder rows
  GROUP BY year, quarter
),

with_dates AS (
  -- Step 2: Convert year + quarter to proper DATE (first day of quarter)
  SELECT 
    year,
    quarter,
    gdp_growth_rate,
    unemployment_rate,
    youth_unemployment_rate,
    inflation_rate,
    TO_DATE(
      CONCAT(
        year, '-',
        CASE quarter
          WHEN 'Q1' THEN '01-01'
          WHEN 'Q2' THEN '04-01'
          WHEN 'Q3' THEN '07-01'
          WHEN 'Q4' THEN '10-01'
        END
      )
    ) as quarter_start_date
  FROM quarterly_pivoted
),

filled AS (
  -- Step 3: Forward fill missing values (for gaps of 1 quarter or less)
  SELECT 
    year,
    quarter,
    quarter_start_date,
    
    -- Forward fill: Use last non-null value for each indicator
    COALESCE(
      gdp_growth_rate,
      LAST_VALUE(gdp_growth_rate) IGNORE NULLS 
        OVER (ORDER BY quarter_start_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
    ) as gdp_growth_rate,
    
    COALESCE(
      unemployment_rate,
      LAST_VALUE(unemployment_rate) IGNORE NULLS 
        OVER (ORDER BY quarter_start_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
    ) as unemployment_rate,
    
    COALESCE(
      youth_unemployment_rate,
      LAST_VALUE(youth_unemployment_rate) IGNORE NULLS 
        OVER (ORDER BY quarter_start_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
    ) as youth_unemployment_rate,
    
    COALESCE(
      inflation_rate,
      LAST_VALUE(inflation_rate) IGNORE NULLS 
        OVER (ORDER BY quarter_start_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
    ) as inflation_rate,
    
    -- Track whether value was forward filled for data quality monitoring
    CASE WHEN gdp_growth_rate IS NULL THEN TRUE ELSE FALSE END as gdp_forward_filled,
    CASE WHEN unemployment_rate IS NULL THEN TRUE ELSE FALSE END as unemployment_forward_filled,
    CASE WHEN youth_unemployment_rate IS NULL THEN TRUE ELSE FALSE END as youth_unemployment_forward_filled,
    CASE WHEN inflation_rate IS NULL THEN TRUE ELSE FALSE END as inflation_forward_filled
    
  FROM with_dates
),

expanded_to_monthly AS (
  -- Step 4: Expand quarterly to monthly (3 rows per quarter)
  -- Uses CROSS JOIN with month offset array [0, 1, 2]
  SELECT 
    ADD_MONTHS(quarter_start_date, m.month_offset) as event_month,
    
    -- Economic indicators (repeated across 3 months)
    gdp_growth_rate,
    unemployment_rate,
    youth_unemployment_rate,
    inflation_rate,
    
    -- Metadata: Track source quarter and data quality
    year || ' ' || quarter as source_quarter,
    'quarterly_repeated' as data_granularity,
    
    -- Flag if any values were forward filled
    (gdp_forward_filled OR unemployment_forward_filled OR 
     youth_unemployment_forward_filled OR inflation_forward_filled) as has_forward_filled_values,
    
    -- Month position within quarter (1, 2, or 3)
    m.month_offset + 1 as month_of_quarter,
    
    CURRENT_TIMESTAMP() as processed_at
    
  FROM filled
  CROSS JOIN (
    SELECT 0 as month_offset   -- First month of quarter (Jan/Apr/Jul/Oct)
    UNION ALL
    SELECT 1 as month_offset   -- Second month of quarter (Feb/May/Aug/Nov)
    UNION ALL
    SELECT 2 as month_offset   -- Third month of quarter (Mar/Jun/Sep/Dec)
  ) m
  
  -- Only include quarters where we have at least ONE non-null indicator
  WHERE gdp_growth_rate IS NOT NULL 
     OR unemployment_rate IS NOT NULL 
     OR youth_unemployment_rate IS NOT NULL 
     OR inflation_rate IS NOT NULL
)

-- Final output: Monthly economic indicators ready for gold layer
SELECT 
  event_month,
  gdp_growth_rate,
  unemployment_rate,
  youth_unemployment_rate,
  inflation_rate,
  source_quarter,
  data_granularity,
  has_forward_filled_values,
  month_of_quarter,
  processed_at
FROM expanded_to_monthly
ORDER BY event_month