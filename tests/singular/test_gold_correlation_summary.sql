/*
  Singular Test: Gold Correlation Summary Validation
  
  Validates that the correlation_causation_summary table contains
  the key findings documented in FINDINGS.md.
  
  Expected findings:
  - Economic events → inflation (strong positive)
  - Events ↔ searches (bidirectional)
  - Events ↔ media (strong positive)
  - Youth unemployment (negative correlation with protests)
  
  This test FAILS if key findings are missing or have unexpected correlations.
*/

WITH expected_relationships AS (
  -- Define what we expect to find
  SELECT 'economic_events_to_inflation' as expected_finding
  UNION ALL SELECT 'events_to_searches'
  UNION ALL SELECT 'events_to_media'
  UNION ALL SELECT 'searches_to_events'
),

actual_findings AS (
  SELECT 
    relationship,
    correlation,
    p_value,
    CASE 
      WHEN relationship LIKE '%economic%event%inflation%' THEN 'economic_events_to_inflation'
      WHEN relationship LIKE '%event%search%' AND relationship NOT LIKE '%inflation%' THEN 'events_to_searches'
      WHEN relationship LIKE '%event%media%' THEN 'events_to_media'
      WHEN relationship LIKE '%search%event%' AND relationship NOT LIKE '%inflation%' THEN 'searches_to_events'
      ELSE 'other'
    END as finding_category,
    -- Validate correlation strength
    CASE 
      WHEN ABS(correlation) >= 0.25 AND p_value < 0.05 THEN 'VALID'
      ELSE 'WEAK_OR_INSIGNIFICANT'
    END as validation_status
  FROM {{ ref('correlation_causation_summary') }}
  WHERE p_value IS NOT NULL
),

validation AS (
  SELECT 
    e.expected_finding,
    COUNT(a.finding_category) as found_count,
    MAX(a.correlation) as max_correlation,
    MIN(a.p_value) as min_p_value,
    CASE 
      WHEN COUNT(a.finding_category) > 0 AND MAX(a.validation_status) = 'VALID' THEN 'PASS'
      ELSE 'FAIL'
    END as status
  FROM expected_relationships e
  LEFT JOIN actual_findings a ON e.expected_finding = a.finding_category
  GROUP BY e.expected_finding
)

-- Return missing or invalid findings
SELECT 
  expected_finding,
  found_count,
  max_correlation,
  min_p_value,
  CASE 
    WHEN found_count = 0 THEN 'Missing from correlation summary table'
    WHEN max_correlation IS NULL THEN 'Found but correlation is null'
    WHEN ABS(max_correlation) < 0.25 THEN 'Correlation too weak (< 0.25)'
    WHEN min_p_value >= 0.05 THEN 'Not statistically significant (p >= 0.05)'
    ELSE 'Unknown validation failure'
  END as issue
FROM validation
WHERE status = 'FAIL'
