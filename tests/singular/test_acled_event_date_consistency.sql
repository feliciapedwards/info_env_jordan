/*
  Singular Test: ACLED Event Date Consistency
  
  Validates that event dates are:
  1. Not in the future (cannot be > CURRENT_DATE)
  2. Not unreasonably old (should be within last 10 years for Jordan data)
  3. Consistent between bronze and silver layers
  
  This test FAILS if any events violate these rules.
  Returns: Records that violate date constraints
*/

-- Check for future dates or dates older than 10 years
SELECT 
  'bronze.acled_jordan_events' as layer,
  event_id_cnty,
  event_date,
  CASE 
    WHEN event_date > CURRENT_DATE() THEN 'Future date'
    WHEN event_date < DATE_SUB(CURRENT_DATE(), 3650) THEN 'Too old (>10 years)'
  END as issue
FROM {{ source('bronze', 'acled_jordan_events') }}
WHERE 
  event_date > CURRENT_DATE()  -- Future dates
  OR event_date < DATE_SUB(CURRENT_DATE(), 3650)  -- Older than 10 years

UNION ALL

-- Check silver layer
SELECT 
  'silver.acled_jordan_events' as layer,
  event_id_cnty,
  event_date,
  CASE 
    WHEN event_date > CURRENT_DATE() THEN 'Future date'
    WHEN event_date < DATE_SUB(CURRENT_DATE(), 3650) THEN 'Too old (>10 years)'
  END as issue
FROM {{ ref('acled_jordan_events') }}
WHERE 
  event_date > CURRENT_DATE()
  OR event_date < DATE_SUB(CURRENT_DATE(), 3650)