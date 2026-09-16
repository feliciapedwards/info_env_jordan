{% test valid_jordan_coordinates(model, lat_column, lon_column) %}

/*
  Custom Generic Test: Valid Jordan Geographic Coordinates
  
  Validates that latitude/longitude pairs fall within Jordan's bounding box.
  
  Jordan's approximate boundaries:
  - Latitude: 29.2°N to 33.4°N
  - Longitude: 34.9°E to 39.3°E
  
  Usage in schema.yml:
    tests:
      - valid_jordan_coordinates:
          lat_column: latitude
          lon_column: longitude
  
  Returns: Records that fall OUTSIDE Jordan's geographic boundaries
*/

SELECT 
  {{ lat_column }} AS latitude,
  {{ lon_column }} AS longitude,
  COUNT(*) AS invalid_coordinate_count
FROM {{ model }}
WHERE 
  {{ lat_column }} IS NOT NULL
  AND {{ lon_column }} IS NOT NULL
  AND (
    {{ lat_column }} < 29.2  -- Too far south
    OR {{ lat_column }} > 33.4  -- Too far north
    OR {{ lon_column }} < 34.9  -- Too far west
    OR {{ lon_column }} > 39.3  -- Too far east
  )
GROUP BY {{ lat_column }}, {{ lon_column }}
HAVING COUNT(*) > 0

{% endtest %}