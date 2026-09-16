# Data Dictionary - Jordan Information Environment Project

## Unity Catalog Structure

**Catalog**: `info_env_jordan`  
**Schemas**: `bronze`, `silver`, `gold`

---

## Bronze Layer Tables

**Total**: 16 tables | **Purpose**: Raw ingested data from APIs

### Core Event & Trends Tables

#### `info_env_jordan.bronze.acled_jordan_events`

**Description**: Raw ACLED political violence and protest events  
**Rows**: ~1,325 events (2021-2025)  
**Source**: ACLED API (https://acleddata.com/)  
**Refresh**: Manual/weekly

**Key Columns** (31 total):

| Column | Type | Description |
|--------|------|-------------|
| `event_id_cnty` | STRING | Unique ACLED event identifier (Primary Key) |
| `event_date` | DATE | Date when the event occurred |
| `event_type` | STRING | Protests, Riots, Violence, Strategic developments |
| `sub_event_type` | STRING | Detailed classification (e.g., Peaceful protest) |
| `actor1` | STRING | Primary actor/group |
| `actor2` | STRING | Secondary actor/group |
| `admin1` | STRING | Governorate name |
| `location` | STRING | Specific location description |
| `latitude` | DOUBLE | Geographic latitude (WGS84) |
| `longitude` | DOUBLE | Geographic longitude (WGS84) |
| `fatalities` | INT | Number of reported deaths |
| `notes` | STRING | Detailed event description |

---

#### `info_env_jordan.bronze.google_trends`

**Description**: Google search interest time series  
**Rows**: ~7,860 observations  
**Source**: SerpAPI (https://serpapi.com/)  
**Refresh**: Manual/weekly

**Schema** (9 columns):

| Column | Type | Description |
|--------|------|-------------|
| `event_date` | DATE | Search measurement date |
| `search_term` | STRING | Keyword (e.g., "inflation", "protests") |
| `search_interest` | INT | Normalized interest (0-100 scale) |
| `search_term_ar` | STRING | Arabic translation of search term |
| `category` | STRING | Economic, Political, Social |
| `geo` | STRING | Geographic scope (usually "JO") |
| `timeframe` | STRING | Query time range |
| `ingestion_timestamp` | TIMESTAMP | Load timestamp |

**Keywords Tracked**: inflation, unemployment, fuel prices, protests, corruption, etc. (English + Arabic)

---

#### `info_env_jordan.bronze.gdelt_jordan_topics`

**Description**: GDELT media coverage aggregated by topic  
**Rows**: ~9,340 topic-date records  
**Source**: GDELT BigQuery  
**Refresh**: Manual/daily

**Schema** (4 columns):

| Column | Type | Description |
|--------|------|-------------|
| `article_date` | DATE | Date of media coverage |
| `topic` | STRING | Extracted topic (economy, protests, government) |
| `article_count` | INT | Number of articles |
| `avg_tone` | DOUBLE | Average sentiment (-100 to +100) |

---

#### `info_env_jordan.bronze.geo_jordan_governorates`

**Description**: Administrative boundaries (governorates)  
**Rows**: 12 governorates  
**Source**: geoBoundaries  
**Refresh**: Annual

**Schema** (6 columns):

| Column | Type | Description |
|--------|------|-------------|
| `shape_name` | STRING | Governorate name (e.g., "Amman") |
| `shape_id` | STRING | Unique identifier |
| `shape_type` | STRING | ADM1 (governorate level) |
| `shape_group` | STRING | Country grouping |
| `geometry_type` | STRING | Polygon or MultiPolygon |
| `geometry_json` | STRING | GeoJSON geometry |

---

### Economic Indicator Tables

#### World Bank Indicators (2 formats)

**`info_env_jordan.bronze.worldbank_jordan_long`**  
**`info_env_jordan.bronze.worldbank_jordan_wide`**

**Description**: World Bank economic indicators in long and wide formats  
**Source**: World Bank API  
**Refresh**: Quarterly

**Indicators Included**:
- Unemployment (total, youth, by gender)
- GDP growth (annual %)
- Inflation (CPI)
- Population
- Food production index

**Individual Indicator Tables** (also available separately):
- `unemployment_total`
- `unemployment_youth`
- `inflation_cpi`
- `gdp_growth`
- `gdp_per_capita`
- `population`
- `food_production_index`
- `jordan_econ_metrics_qtr` (quarterly aggregation)

---

### Data Quality Tables

#### `info_env_jordan.bronze.gdelt_jordan_topics_drift_metrics`
#### `info_env_jordan.bronze.gdelt_jordan_topics_profile_metrics`

**Description**: Data quality monitoring metrics for GDELT ingestion  
**Purpose**: Track schema drift, data profiling statistics

---

## Silver Layer Tables

**Total**: 8 tables | **Purpose**: Cleaned, validated, analysis-ready data

### `info_env_jordan.silver.acled_jordan_events`

**Description**: Cleaned ACLED events with AI-derived enrichments  
**Rows**: 1,325 events  
**Source**: `bronze.acled_jordan_events` via dbt

**Transformations Applied**:
- ✓ Deduplicated by `event_id_cnty`
- ✓ Date validation and standardization
- ✓ Geographic coordinate validation
- ✓ Actor name normalization
- ✓ AI-derived event categorization
- ✓ Theme classification (economic, political, social)

**Schema** (43 columns - includes all bronze columns plus):

| New Column | Type | Description |
|------------|------|-------------|
| `event_category` | STRING | High-level category (protest, violence, etc.) |
| `is_economic` | BOOLEAN | Economic-themed event flag |
| `is_labor` | BOOLEAN | Labor/employment-themed flag |
| `is_political` | BOOLEAN | Political-themed flag |
| `admin1_standardized` | STRING | Standardized governorate name for joins |
| `data_quality_score` | DOUBLE | Quality score (0-1) |

**Data Quality Tests**:
- ✓ `event_id_cnty` is unique
- ✓ `event_date` not null
- ✓ Coordinates in valid Jordan range
- ✓ Fatalities >= 0

---

### `info_env_jordan.silver.google_trends`

**Description**: Validated search interest data  
**Rows**: 7,860  
**Source**: `bronze.google_trends` via dbt

**Transformations**:
- ✓ Deduplicated by (date, search_term)
- ✓ Search interest range validated (0-100)
- ✓ Date standardization

**Schema** (7 columns)

---

### `info_env_jordan.silver.gdelt_jordan_topics`

**Description**: Cleaned media coverage data  
**Rows**: 9,340  
**Source**: `bronze.gdelt_jordan_topics` via dbt

**Transformations**:
- ✓ Deduplicated
- ✓ Tone range validated (-100 to +100)
- ✓ Low-quality topics filtered

---

### `info_env_jordan.silver.economic_indicators_monthly`

**Description**: World Bank indicators at monthly grain  
**Rows**: ~400 monthly records  
**Source**: `bronze.worldbank_jordan_long` via dbt

**Schema** (10 columns):

| Column | Type | Description |
|--------|------|-------------|
| `year` | INT | Year |
| `month` | INT | Month (1-12) |
| `indicator_code` | STRING | WB indicator code |
| `indicator_name` | STRING | Indicator full name |
| `value` | DOUBLE | Indicator value |
| `unemployment_rate` | DOUBLE | Monthly unemployment % |
| `youth_unemployment_rate` | DOUBLE | Youth unemployment % |
| `inflation_rate` | DOUBLE | CPI inflation % |
| `gdp_growth` | DOUBLE | GDP growth % (annualized) |

---

### Other Silver Tables

#### `info_env_jordan.silver.geo_jordan_governorates`
Cleaned geographic boundaries with validation

#### `info_env_jordan.silver.economic_indicators_yearly`  
Annual economic indicators

#### `info_env_jordan.silver.worldbank_jordan_standardized`  
Standardized World Bank data (all indicators)

#### `info_env_jordan.silver.acled_disorder_trend_analysis`  
Trend analysis of disorder events

---

## Gold Layer Tables

**Total**: 14 tables | **Purpose**: Business metrics, ML-ready datasets, analytics

### Core Analytics Tables

#### `info_env_jordan.gold.unified_weekly_indicators` ⭐

**Description**: PRIMARY TABLE for weekly monitoring  
**Rows**: 262 weeks (2021-2025)  
**Grain**: One row per week_start_date  
**Use Case**: Early warning system, real-time dashboards

**Schema** (21 columns):

| Column | Type | Description | Use |
|--------|------|-------------|-----|
| `week_start_date` | DATE | Monday of the week | Time dimension |
| `event_count` | INT | Total ACLED events | Protest activity |
| `protest_event_count` | INT | Protest-only events | Peaceful activity |
| `violence_event_count` | INT | Violent events | Security risk |
| `avg_fatalities` | DOUBLE | Average deaths/event | Violence severity |
| `search_intensity_avg` | DOUBLE | Avg search interest (0-100) | Public attention |
| `top_search_term` | STRING | Most searched term | Public concern |
| `media_coverage_count` | INT | GDELT articles | Media attention |
| `media_tone_avg` | DOUBLE | Avg sentiment (-100 to +100) | Media sentiment |
| `economic_event_count` | INT | Economic-themed events | Economic protest |
| `labor_event_count` | INT | Labor-themed events | Labor unrest |
| `political_event_count` | INT | Political-themed events | Political tension |

**Recommended Alerts**:
- `event_count` > 20 (weekly spike)
- `search_intensity_avg` > 75 (high attention)
- `media_tone_avg` < -30 (negative sentiment)

---

#### `info_env_jordan.gold.theme_economic_conditions` ⭐

**Description**: PRIMARY TABLE for inflation/GDP prediction  
**Rows**: 44 months  
**Grain**: One row per month  
**Use Case**: Economic forecasting

**Schema** (31 columns):

| Column | Type | Description | Predictive Power |
|--------|------|-------------|------------------|
| `event_month` | DATE | First day of month | Time dimension |
| `economic_event_count` | INT | Economic protests/strikes | ⭐⭐⭐ Strong (r=0.765***) |
| `inflation_search_avg` | DOUBLE | Inflation search interest | ⭐⭐⭐ Strong (r=0.722***) |
| `fuel_search_avg` | DOUBLE | Fuel price searches | ⭐⭐ Moderate |
| `cost_living_search_avg` | DOUBLE | Cost searches | ⭐⭐ Moderate |
| `media_economy_tone` | DOUBLE | Economic news sentiment | ⭐⭐ Moderate |
| `inflation_rate` | DOUBLE | CPI inflation % | **TARGET** |
| `gdp_growth` | DOUBLE | GDP growth % | **TARGET** |
| `unemployment_rate` | DOUBLE | Unemployment % | Context |

**Key Finding**: Economic protests → inflation (r=0.765***), stronger than inflation → protests (r=0.584***)

---

#### `info_env_jordan.gold.theme_labor_employment` ⭐

**Description**: Labor protests & unemployment analysis  
**Rows**: 44 months  
**Use Case**: Employment forecasting, wage policy

**Schema** (29 columns):

| Column | Type | Description |
|--------|------|-------------|
| `event_month` | DATE | Month |
| `labor_event_count` | INT | Labor strikes, wage protests |
| `wage_protest_count` | INT | Wage-specific protests |
| `unemployment_search_avg` | DOUBLE | Unemployment searches |
| `jobs_search_avg` | DOUBLE | Job searches |
| `unemployment_rate` | DOUBLE | **TARGET** |
| `youth_unemployment_rate` | DOUBLE | **TARGET** |

**Counterintuitive Finding**: Youth unemployment negatively correlates with protests (r=-0.42*)

---

#### `info_env_jordan.gold.ml_combined_economic_themes` ⭐

**Description**: ML-READY dataset with lagged features  
**Rows**: ~44 months  
**Columns**: 48 features  
**Use Case**: PRIMARY for machine learning models

**Feature Types**:
1. **Current month** (15 features): Events, searches, media by theme
2. **Lagged features** (20 features): 1-3 month lags of key variables
3. **Rolling averages** (8 features): 3-month rolling means
4. **Target variables** (3): inflation_rate, unemployment_rate, gdp_growth

**Modeling Guidance**:
- **Baseline**: Linear regression (R² ~ 0.65 for inflation)
- **Recommended**: Random Forest, XGBoost (handles non-linearity)
- **Feature importance**: economic_event_count, inflation_search_avg are top 2

---

### Summary & Correlation Tables

#### `info_env_jordan.gold.correlation_causation_summary`

**Description**: Key statistical findings documented  
**Rows**: 8 relationships  
**Schema** (6 columns):

| Column | Type | Description |
|--------|------|-------------|
| `relationship` | STRING | X → Y relationship |
| `correlation` | DOUBLE | Pearson r |
| `p_value` | DOUBLE | Statistical significance |
| `lag_months` | INT | Temporal lag |
| `interpretation` | STRING | Plain English explanation |

---

#### `info_env_jordan.gold.economic_correlation_summary`

**Description**: Economic-specific correlations

---

### Weekly Analysis Tables

#### `info_env_jordan.gold.weekly_events_media_trends`
Weekly event and media co-movement patterns

#### `info_env_jordan.gold.weekly_unified_analysis`  
Weekly indicators with additional derived metrics

---

### Quarterly Tables

#### `info_env_jordan.gold.quarterly_events_economics`

**Description**: Quarterly aggregation of events + economics  
**Rows**: ~18 quarters  
**Note**: Monthly thematic analysis (above) performs better for prediction

---

### Other Thematic Tables

#### `info_env_jordan.gold.theme_political_stability`
Political events, governance indicators

#### `info_env_jordan.gold.theme_regional_identity`  
Regional/Palestinian solidarity events

---

### Utility Tables

#### `info_env_jordan.gold.dim_date`

**Description**: Date dimension for joins  
**Columns**: date, year, month, quarter, week, is_weekend, etc.

#### `info_env_jordan.gold.fact_jordan_daily_metrics`

**Description**: Daily grain fact table (finest temporal resolution)

#### `info_env_jordan.gold.yoy_disorder_significance`

**Description**: Year-over-year disorder trend analysis

---

## Data Quality Standards

### Bronze Layer
- Raw data preserved with minimal transformation
- All ingestion timestamps recorded
- Source identifiers maintained
- Schema validation on write

### Silver Layer
- Null handling: Document null treatment for each column
- Date standardization: All dates in YYYY-MM-DD format
- Name standardization: Consistent naming conventions
- Quality flags: Explicit flags for data quality issues
- Referential integrity: Validated foreign key relationships

### Gold Layer
- Business logic documented in dbt models
- Aggregation rules explicit
- Metric definitions aligned with business glossary
- Performance optimized (Z-ordering, partitioning)

---

## Common Join Keys

### Temporal Joins
- **Column**: `event_date` / `date` / `year`
- **Format**: DATE or INT (year)
- **Use**: Time series alignment across sources

### Geographic Joins
- **Column**: `admin1` / `admin1_standardized` / `shape_name`
- **Type**: STRING
- **Use**: Joining events to governorate boundaries
- **Note**: Name standardization required (e.g., "Amman Governorate" vs. "Amman")

### Spatial Joins
- **Columns**: `latitude` / `longitude` with `geometry_json`
- **Method**: ST_Contains() or ST_Within() using Sedona/GeoSpark
- **Use**: Point-in-polygon analysis

---

## Event Type Taxonomies

### ACLED Event Types
1. **Battles**: Armed clashes between organized groups
2. **Violence against civilians**: Attacks on non-combatants
3. **Protests**: Public demonstrations
4. **Riots**: Violent public gatherings
5. **Strategic developments**: Non-violent strategic actions
6. **Explosions/Remote violence**: Bombings, shelling

### Event Sub-Types
- See ACLED codebook for complete taxonomy
- Sub-types provide granular classification within each event type

---

## Naming Conventions

### Tables
- Format: `{catalog}.{schema}.{descriptive_name}`
- Example: `info_env_jordan.bronze.acled_jordan`
- Use snake_case for all table names

### Columns
- Use snake_case for all column names
- Avoid reserved keywords
- Use descriptive names (not abbreviations unless standard)
- Suffix boolean columns with `_flag` or `is_`
- Suffix datetime columns with `_date` or `_timestamp`

### Files and Notebooks
- Notebooks: `{sequence_number}_{purpose}_{source}`
  - Example: `01_ingest_worldbank`
- Queries: `{sequence_number}_{purpose}_{context}`
  - Example: `02_bronze_acle_eda`

---

## Units and Scales

### Spatial
- Coordinates: WGS84 (EPSG:4326)
- Latitude range: Valid Jordan extent (~29.2°N to 33.4°N)
- Longitude range: Valid Jordan extent (~34.9°E to 39.3°E)

### Temporal
- All dates: UTC unless specified
- Time precision documented in `time_precision` field
- Historical coverage varies by source

### Numeric
- Fatalities: Integer count
- Interest scores (Google Trends): 0-100 scale
- Goldstein scale (GDELT): -10 to +10 (conflict to cooperation)

---

## Data Retention

- **Bronze**: Full historical archive, no deletion
- **Silver**: Full historical archive, updates replace in-place
- **Gold**: Retention policy TBD based on business requirements

---

## Privacy and Security

- All data sources are public datasets
- No PII (Personally Identifiable Information) collected
- Actor names in ACLED are organizational, not individual
- Unity Catalog access controls apply at table level

---

---

## Quick Reference: Which Table Should I Use?

### For Real-Time Monitoring / Dashboards
➡️ **Use**: `gold.unified_weekly_indicators`  
**Why**: Weekly grain, all indicators in one place, early warning capable

### For Machine Learning / Prediction
➡️ **Use**: `gold.ml_combined_economic_themes`  
**Why**: 48 ML-ready features, lagged variables, proven predictive power

### For Economic Policy Analysis
➡️ **Use**:
- Inflation/GDP: `gold.theme_economic_conditions`
- Employment/wages: `gold.theme_labor_employment`  
**Why**: Thematic separation, monthly grain, validated correlations

### For Exploratory Analysis
➡️ **Use**: Silver layer tables (`silver.acled_jordan_events`, etc.)  
**Why**: Cleaned but not aggregated, maximum flexibility

### For Data Debugging
➡️ **Use**: Bronze layer tables  
**Why**: Raw API responses preserved

---

## How to Verify This Data Dictionary

Run these SQL queries to validate the documentation:

```sql
-- 1. Count tables per layer
SELECT 'bronze' as layer, COUNT(*) as table_count 
FROM (SHOW TABLES IN info_env_jordan.bronze) WHERE isTemporary = false
UNION ALL
SELECT 'silver', COUNT(*) 
FROM (SHOW TABLES IN info_env_jordan.silver) WHERE isTemporary = false
UNION ALL
SELECT 'gold', COUNT(*) 
FROM (SHOW TABLES IN info_env_jordan.gold) WHERE isTemporary = false;
-- Expected: bronze=16, silver=8, gold=14

-- 2. Verify key table row counts
SELECT 
  'acled_events' as table_name, 
  (SELECT COUNT(*) FROM info_env_jordan.bronze.acled_jordan_events) as actual_rows,
  1325 as documented_rows
UNION ALL
SELECT 'google_trends', 
  (SELECT COUNT(*) FROM info_env_jordan.bronze.google_trends), 7860
UNION ALL
SELECT 'unified_weekly', 
  (SELECT COUNT(*) FROM info_env_jordan.gold.unified_weekly_indicators), 262
UNION ALL
SELECT 'theme_economic', 
  (SELECT COUNT(*) FROM info_env_jordan.gold.theme_economic_conditions), 44;

-- 3. Check gold table schemas
DESCRIBE info_env_jordan.gold.unified_weekly_indicators;
-- Expected: 21 columns

DESCRIBE info_env_jordan.gold.ml_combined_economic_themes;
-- Expected: 48 columns

-- 4. Validate date ranges
SELECT 
  'ACLED' as source,
  MIN(event_date) as earliest,
  MAX(event_date) as latest,
  DATEDIFF(MAX(event_date), MIN(event_date)) as days_span
FROM info_env_jordan.bronze.acled_jordan_events
UNION ALL
SELECT 'Google Trends',
  MIN(event_date), MAX(event_date),
  DATEDIFF(MAX(event_date), MIN(event_date))
FROM info_env_jordan.bronze.google_trends;
```

---

## Data Dictionary Change Log

| Date | Version | Changes |
|------|---------|----------|
| 2024-09-16 | 2.0 | Complete rewrite: Documented all 38 tables (was 5), added schemas, use cases, verification queries |
| 2024-06-01 | 1.0 | Initial version with partial bronze layer documentation |

---

**Last Updated**: September 16, 2024  
**Version**: 2.0  
**Maintainer**: feliciapedwards@gmail.com  
**Verified Against**: Unity Catalog `info_env_jordan` (AWS Databricks)