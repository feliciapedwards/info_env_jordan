# Jordan Information Environment Project

## Overview

This project analyzes Jordan's information environment through multiple data sources, combining geopolitical events, economic indicators, digital trends, and geographic data. The project implements a medallion architecture (bronze → silver → gold) with dbt transformations to create a comprehensive analytical platform.

## Project Structure

```
Jordan Information Environment Project/
├── bronze/              # Raw data ingestion notebooks
├── models/              # dbt transformation models
│   ├── silver/         # Silver layer dbt models
│   ├── gold/           # Gold layer dbt models
│   └── sources.yml     # dbt source definitions
├── analysis/            # Exploratory analysis and reporting
├── archive/             # Archived legacy notebooks
├── tests/               # dbt tests
├── dbt_project.yml      # dbt project configuration
├── profiles.yml         # dbt connection profiles
├── run_dbt              # dbt execution notebook
└── README.md           # This file
```

## Data Sources

The project integrates five primary data sources:

### 1. **ACLED (Armed Conflict Location & Event Data)**
   - **Source**: Political violence and protest events
   - **Bronze**: `01_ingest_acle`
   - **Silver**: via dbt model `acled_jordan_events.sql`
   - **Tables**: `info_env_jordan.bronze.acled_jordan` → `info_env_jordan.silver.acled_jordan`
   - **Analysis**: Event patterns, conflict dynamics, protest activities

### 2. **World Bank Indicators**
   - **Source**: Economic and development indicators
   - **Bronze**: `01_ingest_worldbank`
   - **Silver**: (not transformed - stays as bronze/reference only)
   - **Analysis**: Economic trends, development metrics

### 3. **Google Trends**
   - **Source**: Search interest and digital engagement
   - **Bronze**: `01_ingest_google_trends`
   - **Analysis**: Public attention patterns, information seeking behavior

### 4. **GDELT (Global Database of Events, Language, and Tone)**
   - **Source**: Global news and media monitoring
   - **Bronze**: `01_ingest_gdelt`
   - **Analysis**: Media coverage, sentiment, global attention

### 5. **geoBoundaries**
   - **Source**: Administrative boundaries (governorates)
   - **Bronze**: `01_bronze_geo`
   - **Silver**: (not transformed - stays as bronze/reference only)
   - **Tables**: `info_env_jordan.bronze.geo_jordan_governorates`
   - **Purpose**: Spatial context and geographic joins

## Data Architecture

### Medallion Architecture

The project follows the medallion architecture pattern:

#### **Bronze Layer** (Raw Data)
- Direct ingestion from source APIs and files
- Minimal transformation, preserving original structure
- Schema: `info_env_jordan.bronze`
- Format: Delta tables with full history

#### **Silver Layer** (Cleaned & Standardized)
- Data quality checks and cleaning
- Standardized schemas and naming conventions
- Business logic applied
- Schema: `info_env_jordan.silver`
- Transformations via dbt

#### **Gold Layer** (Business-Ready Analytics)
- Aggregated metrics and KPIs
- Denormalized for reporting
- Optimized for query performance
- Schema: `info_env_jordan.gold`
- Analytics-ready datasets

## Key Notebooks

### Ingestion (Bronze)
1. **01_bronze_geo**: Ingest Jordan governorate boundaries from geoBoundaries
2. **01_ingest_acle**: Load ACLED political events data
3. **01_ingest_worldbank**: Extract World Bank indicators
4. **01_ingest_google_trends**: Capture Google search trends
5. **01_ingest_gdelt**: Import GDELT news events

### Transformation (Silver)
1. **models/silver/acled_jordan_events.sql**: Clean and standardize ACLED events (dbt)
2. **models/silver/google_trends.sql**: Clean and deduplicate Google Trends (dbt)
3. **models/silver/gdelt_jordan_topics.sql**: Clean GDELT media events (dbt)
4. Legacy notebooks archived in archive/legacy_silver_notebooks.
5. World Bank and geoBoundaries: Stays in bronze (reference only, not transformed to silver layer)

### Analysis
1. **Jordan Information Environment - Comprehensive Analysis**: End-to-end analysis
2. **ACLED Jordan Events Analysis**: Deep dive into political events
3. **ACLED Jordan Silver Layer ETL**: ETL pipeline documentation
4. **02_eda_geo_governorates**: Geographic data exploration
5. **02_bronze_worldbank_eda**: Economic indicators exploration

### Queries
- **Schema for Jordan Project**: Database schema documentation
- **02_bronze_google_trends_eda**: Trends analysis
- **02_bronze_acle_eda**: ACLED data quality checks
- **inspect silver acled jordan**: Silver layer validation

## Technology Stack

- **Platform**: Databricks on AWS
- **Storage**: Delta Lake (Unity Catalog)
- **Compute**: Apache Spark
- **Transformation**: dbt (data build tool)
- **Languages**: Python, SQL
- **Schema**: `info_env_jordan` (catalog/database)

## Getting Started

### Prerequisites
- Access to Databricks workspace
- Permissions for `info_env_jordan` catalog
- API credentials for data sources (see setup below)

### API Credentials Setup

This project requires API keys for certain data sources. **Never commit API keys to git!**

#### Required API Keys:

1. **SerpAPI** (for Google Trends)
   - Sign up: https://serpapi.com/
   - Free tier: 100 searches/month
   - Required for: `bronze/01_ingest_google_trends`

2. **ACLED** (for conflict/event data)
   - Sign up: https://developer.acleddata.com/
   - Free tier: Academic/research use
   - Required for: `bronze/01_ingest_acle`

3. **No credentials needed** for:
   - World Bank API (public)
   - GDELT API (public)
   - geoBoundaries (public)

#### Storing Credentials Securely in Databricks:

**Option 1: Using Databricks CLI**
```bash
# Configure CLI (one-time setup)
databricks configure --token

# Create secret scopes
databricks secrets create-scope serpapi
databricks secrets create-scope acled

# Add your API keys
databricks secrets put-secret serpapi api_key
databricks secrets put-secret acled email
databricks secrets put-secret acled api_key
```

**Option 2: Using Databricks UI**
1. Navigate to: `https://your-workspace.cloud.databricks.com/#secrets/createScope`
2. Create scope: `serpapi`
3. Add secret: `api_key` = [your SerpAPI key]
4. Repeat for `acled` scope with `email` and `api_key` secrets

**In Notebooks**: Credentials are accessed via:
```python
api_key = dbutils.secrets.get(scope="serpapi", key="api_key")
```

### Running the Pipeline

1. **Ingest Bronze Data**
   ```python
   # Run bronze ingestion notebooks in order
   # Each notebook handles one data source
   ```

2. **Transform to Silver**
   ```python
   # Run dbt transformations using the run_dbt notebook
   # See "dbt Integration" section below for details
   ```

3. **Create Gold Analytics**
   ```python
   # Run gold layer dbt models
   # Or create custom aggregations
   ```

### dbt Integration

The project uses dbt (data build tool) for all data transformations from Bronze → Silver → Gold.

#### Configuration Files
- **`dbt_project.yml`**: Main project configuration
- **`profiles.yml`**: Databricks connection settings
- **`models/sources.yml`**: Bronze table definitions and freshness checks
- **`models/silver/schema.yml`**: Silver layer tests and documentation

#### dbt Models
- **Silver Layer**: `/models/silver/`
  - `acled_jordan_events.sql` - ACLED events with AI enrichments
  - `gdelt_jordan_topics.sql` - GDELT media coverage
  - `google_trends.sql` - Google Trends search data
- **Gold Layer**: `/models/gold/` (future aggregations and business metrics)

#### Running dbt

**Option 1: Using the run_dbt notebook**
```python
# Open and run the run_dbt notebook in this project folder
# It handles all environment setup and execution
```

**Option 2: Manual dbt commands**
```bash
# Test connection
dbt debug --project-dir /Workspace/Users/feliciapedwards@gmail.com/Jordan\ Information\ Environment\ Project

# Run all models
dbt run --project-dir /Workspace/Users/feliciapedwards@gmail.com/Jordan\ Information\ Environment\ Project

# Run tests
dbt test --project-dir /Workspace/Users/feliciapedwards@gmail.com/Jordan\ Information\ Environment\ Project

# Run specific model
dbt run --select acled_jordan_events --project-dir /Workspace/Users/feliciapedwards@gmail.com/Jordan\ Information\ Environment\ Project
```

#### Data Quality Tests

The silver models include comprehensive tests:
- **Not null checks**: Critical fields must be populated
- **Unique constraints**: `event_id_cnty` must be unique
- **Value ranges**: Coordinates, dates, scores within expected bounds
- **Accepted values**: Controlled vocabularies for categorical fields
- **Uniqueness combinations**: `(event_date, search_term)` unique in google_trends
- **Freshness checks**: Alerts if bronze data is stale

### Testing the Pipeline

#### Run End-to-End Validation ⭐
```bash
dbt test --select test_end_to_end_pipeline
```

This validates the entire Bronze → Silver → Gold pipeline in one test:
- ✅ All layers have data (bronze >100 events, >1000 trends)
- ✅ Row counts are reasonable (silver 100-10,000 range)
- ✅ Gold tables have expected grain (262 weeks, 44 months)
- ✅ Critical columns are not null
- ✅ Data lineage is intact (silver ≤ bronze rows)

#### Run All Tests
```bash
dbt test
```

**Test Coverage**: 21 data quality checks across:
- 4 singular tests (end-to-end, date consistency, freshness, correlation validation)
- 2 generic tests (fatality ranges, coordinate validation)
- ~15 schema tests (null checks, type validation, value ranges)

**Documentation**: See [tests/README_TESTS.md](tests/README_TESTS.md) for detailed test documentation, debugging guides, and CI/CD integration examples

## Data Catalog

### Bronze Tables
- `info_env_jordan.bronze.geo_jordan_governorates`
- `info_env_jordan.bronze.acled_jordan`
- Additional tables created by ingestion notebooks

### Silver Tables
- `info_env_jordan.silver.acled_jordan_events` - Cleaned ACLED events with AI enrichments
- `info_env_jordan.silver.google_trends` - Deduplicated Google Trends search data
- `info_env_jordan.silver.gdelt_jordan_topics` - GDELT media coverage

### Gold Tables (Theme-Based Analytics)

**Theme 1: Labor & Employment** (`theme_labor_employment`)
- Labor protests + unemployment searches → predicts unemployment rate
- Use for: Wage policy, labor subsidies, employment programs

**Theme 2: Economic Conditions** (`theme_economic_conditions`)
- Economic protests + inflation searches → predicts inflation/GDP
- Use for: Subsidy policy, fiscal interventions, cost-of-living relief

**Theme 3: Political Stability** (`theme_political_stability`)
- Government/corruption protests (descriptive analysis, weak economic correlation)
- Use for: Governance context, not economic prediction

**Theme 4: Regional/Identity** (`theme_regional_identity`)
- Palestinian solidarity + tribal violence (NO economic correlation)
- Use for: Contextual understanding, not economic policy

**Combined Table** (`ml_combined_economic_themes`)
- ✅ **PRIMARY TABLE for economic prediction and policy analysis**
- Combines Themes 1 & 2 only (economically-relevant features)
- ~44 monthly observations with 50+ features
- Target variables: unemployment_rate, inflation_rate, gdp_growth
- Includes lagged features (1-3 months) and rolling averages

## Gold Layer: Theme-Based Policy Analysis

### Why Theme-Based Architecture?

The gold layer organizes data into **policy-relevant themes** to:
- ✅ Separate economic signals from noise
- ✅ Enable targeted policy recommendations
- ✅ Track policy effectiveness by domain
- ✅ Prioritize resources based on predictive impact

### Monthly Grain, Country-Level

**Design Decision**: All gold tables aggregate to **monthly, country-level** grain because:
- Balances sample size (~44 months) vs. signal strength
- Aligns with economic reporting cycles (monthly/quarterly indicators)
- Enables 1-3 month lag analysis ("Do protests predict unemployment 2 months ahead?")
- Smooths daily event volatility while preserving trends

### Theme-to-Policy Mapping

| Theme | Policy Questions | Predictive Power | Action |
|-------|-----------------|------------------|--------|
| **Labor & Employment** | Raise wages? Deploy subsidies? | Strong (r ≈ 0.65) | ✅ Use for prediction |
| **Economic Conditions** | Remove subsidies? Inflation risk? | Strong (r ≈ 0.55) | ✅ Use for prediction |
| **Political Stability** | Corruption impact on GDP? | Moderate (r ≈ 0.32) | ⚠️ Context only |
| **Regional/Identity** | Do Palestinian protests hurt economy? | None (r < 0.1) | ❌ Exclude from models |

## Analysis Capabilities

The theme-based gold layer enables:

1. **Correlation Analysis**: Which events/searches predict which economic outcomes?
2. **Lag Analysis**: Do events lead economic changes by 1-3 months?
3. **Feature Engineering**: Rolling averages, momentum, interactions
4. **Predictive Modeling**: Train ML models on `ml_combined_economic_themes`
5. **Policy Impact Measurement**: Track indicators before/after interventions
6. **Early Warning Dashboard**: Real-time alerts when crisis signals spike

## Development Workflow

1. **Data Ingestion**: Update bronze notebooks when source APIs change
2. **Schema Changes**: Update dbt models in `/models/`
3. **New Sources**: Add ingestion notebook → update dbt sources.yml
4. **Quality Checks**: Use analysis notebooks for validation
5. **Documentation**: Keep this README updated

## Maintenance

- **Refresh Frequency**: Define cadence for each data source
- **Data Quality**: Monitor via analysis queries
- **Schema Evolution**: Use Delta Lake schema evolution features
- **Cost Optimization**: Monitor compute usage and optimize queries

## Future Enhancements

- [ ] Automate bronze ingestion with Databricks Jobs
- [ ] Implement data quality checks with Great Expectations
- [ ] Create gold layer dashboards
- [ ] Add more data sources (Twitter/X, local news)
- [ ] Implement streaming ingestion where applicable
- [ ] Set up automated alerts for data anomalies

## Contact & Support

For questions or issues with this project, contact the data engineering team.

## License

MIT License - See [LICENSE](LICENSE) file for details.

This project is open source and available for educational and research purposes.

---

**Last Updated**: September 2026  
**Maintainer**: feliciapedwards@gmail.com  
**Unity Catalog**: `info_env_jordan`