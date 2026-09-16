{% test reasonable_fatalities(model, column_name, max_value=1000) %}

/*
  Custom Generic Test: Reasonable Fatality Counts
  
  Flags events with unusually high fatality counts that may indicate:
  - Data entry errors
  - Duplicate records
  - Events that need manual review
  
  Default threshold: 1000 fatalities (configurable)
  
  Usage in schema.yml:
    tests:
      - reasonable_fatalities:
          column_name: fatalities
          max_value: 500  # Optional: override default threshold
  
  Returns: Records exceeding the fatality threshold
*/

SELECT 
  *,
  {{ column_name }} AS fatality_count
FROM {{ model }}
WHERE {{ column_name }} > {{ max_value }}

{% endtest %}