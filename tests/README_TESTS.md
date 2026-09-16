# dbt Test Suite

This directory contains data quality and pipeline validation tests for the Jordan Information Environment project.

## Test Structure

```
tests/
├── generic/                          # Reusable test templates
│   ├── test_reasonable_fatalities.sql
│   └── test_valid_jordan_coordinates.sql
│
├── singular/                         # One-off, specific tests
│   ├── test_acled_event_date_consistency.sql
│   ├── test_end_to_end_pipeline.sql    ⭐ PRIMARY E2E TEST
│   ├── test_data_freshness.sql
│   └── test_gold_correlation_summary.sql
│
└── schema tests (defined in models/*/schema.yml)
```

---

## Running Tests

### Run ALL Tests
```bash
dbt test
```

### Run End-to-End Pipeline Test (⭐ Start Here)
```bash
dbt test --select test_end_to_end_pipeline
```

### Run Specific Test Types
```bash
# Singular tests only
dbt test --select test_type:singular

# Generic tests only
dbt test --select test_type:generic

# Schema tests only
dbt test --select test_type:schema
```

### Run Tests for Specific Models
```bash
# Test a specific model
dbt test --select acled_jordan_events

# Test all silver models
dbt test --select silver.*

# Test all gold models
dbt test --select gold.*
```

---

## Test Descriptions

### 🔵 **Singular Tests** (Project-Specific)

#### `test_end_to_end_pipeline.sql` ⭐ **MOST IMPORTANT**

**Purpose**: Validates the entire Bronze → Silver → Gold pipeline in one test.

**What it checks**:
- ✅ Bronze tables have data (>100 events, >1000 trends, >1000 GDELT)
- ✅ Silver tables have reasonable row counts (100-10,000 range)
- ✅ Gold tables have expected grain (50-500 weeks, 10-100 months)
- ✅ Critical columns are not null
- ✅ Silver row counts ≤ Bronze (deduplication works)

**When to run**: 
- After `dbt run` to validate the pipeline
- Before GitHub push to ensure everything works
- After data refresh to catch issues

**Expected result**: 0 rows returned (all checks pass)

---

#### `test_acled_event_date_consistency.sql`

**Purpose**: Validates event dates are reasonable.

**What it checks**:
- ✅ No future dates
- ✅ No dates older than 10 years
- ✅ Consistency between bronze and silver

**Expected result**: 0 rows returned

---

#### `test_data_freshness.sql`

**Purpose**: Ensures data is not too stale.

**What it checks**:
- ✅ Bronze ACLED data < 365 days old
- ✅ Bronze Google Trends < 365 days old
- ✅ Bronze GDELT < 365 days old

**Expected result**: 0 rows returned  
**Note**: This test WILL fail if you haven't refreshed data in >1 year (expected behavior)

---

#### `test_gold_correlation_summary.sql`

**Purpose**: Validates key research findings are present.

**What it checks**:
- ✅ Economic events → inflation relationship exists
- ✅ Events ↔ searches relationships exist
- ✅ Events ↔ media relationship exists
- ✅ Correlations are strong enough (|r| ≥ 0.25)
- ✅ Statistically significant (p < 0.05)

**Expected result**: 0 rows returned

---

### 🟢 **Generic Tests** (Reusable)

#### `test_reasonable_fatalities`

**Purpose**: Flags events with unusually high fatality counts.

**Usage in schema.yml**:
```yaml
columns:
  - name: fatalities
    tests:
      - reasonable_fatalities:
          max_value: 500
```

---

#### `test_valid_jordan_coordinates`

**Purpose**: Validates lat/lon fall within Jordan's boundaries.

**Usage in schema.yml**:
```yaml
tests:
  - valid_jordan_coordinates:
      lat_column: latitude
      lon_column: longitude
```

---

### 🟡 **Schema Tests** (Defined in schema.yml)

**Location**: `models/silver/schema.yml`, `models/gold/schema.yml`

**Examples**:
- `not_null` - Column has no nulls
- `unique` - Column values are unique
- `dbt_utils.not_null_proportion` - At least 99% non-null
- `dbt_expectations.expect_column_values_to_be_between` - Range validation

---

## Expected Test Results

### ✅ All Passing (Healthy Pipeline)

```bash
$ dbt test

Completed successfully

Done. PASS=25 WARN=0 ERROR=0 SKIP=0 TOTAL=25
```

### ❌ Test Failures (Issues Found)

```bash
$ dbt test

Failure in test test_end_to_end_pipeline (tests/singular/test_end_to_end_pipeline.sql)
  Got 2 results, configured to fail if != 0

  actual_count | check_name                      | expected
  -------------|----------------------------------|----------------------------------
  0            | gold_weekly_indicators_grain    | Expected 50-500 weeks
  150          | gold_economic_inflation_not_null| Expected <10 nulls in inflation_rate
```

**How to interpret**:
- Each failed check shows what went wrong
- `actual_count` = what the test found
- `expected` = what should have happened

---

## Debugging Test Failures

### 1. Run the test query directly

Copy the test SQL and run it manually to see the full results:

```sql
-- In a notebook
SELECT * FROM info_env_jordan.bronze.acled_jordan_events
WHERE event_date > CURRENT_DATE();  -- Check for future dates
```

### 2. Check dbt logs

```bash
# View detailed test output
cat target/run/info_env_jordan/tests/singular/test_end_to_end_pipeline.sql
```

### 3. Run tests in debug mode

```bash
dbt test --select test_end_to_end_pipeline --debug
```

---

## Adding New Tests

### For a New Generic Test

1. Create `tests/generic/test_my_custom_check.sql`
2. Use jq template syntax: `{% test my_custom_check(model, column_name) %}`
3. Return rows that FAIL the test
4. Apply in `schema.yml`:
   ```yaml
   tests:
     - my_custom_check:
         column_name: my_column
   ```

### For a New Singular Test

1. Create `tests/singular/test_my_check.sql`
2. Write SQL that returns rows that FAIL
3. Use `{{ ref('model_name') }}` or `{{ source('schema', 'table') }}`
4. Run: `dbt test --select test_my_check`

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: dbt Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run dbt tests
        run: |
          dbt deps
          dbt test --select test_end_to_end_pipeline
```

---

## Test Maintenance

### When to Update Tests

1. **Data refresh**: Run tests after ingesting new data
2. **Schema changes**: Update tests if column names/types change
3. **New models**: Add tests for new silver/gold tables
4. **Threshold changes**: Adjust row count thresholds as data grows

### Test Thresholds to Review Quarterly

In `test_end_to_end_pipeline.sql`:
- Bronze row counts (currently: >100, >1000, >1000)
- Silver row counts (currently: 100-10,000 range)
- Gold row counts (currently: 50-500 weeks, 10-100 months)

In `test_data_freshness.sql`:
- Staleness threshold (currently: 365 days)

---

## Quick Reference

| Want to... | Run this |
|------------|----------|
| **Validate entire pipeline** | `dbt test --select test_end_to_end_pipeline` |
| **Check data quality** | `dbt test --select test_type:singular` |
| **Test one model** | `dbt test --select model_name` |
| **Test gold layer** | `dbt test --select gold.*` |
| **See test SQL** | `cat tests/singular/test_*.sql` |

---

**Last Updated**: September 16, 2024  
**Maintained By**: feliciapedwards@gmail.com

**Questions?** See the main README.md or DATA_DICTIONARY.md
