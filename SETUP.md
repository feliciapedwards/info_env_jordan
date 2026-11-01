# Setup: API Credentials & dbt CLI

## API Credentials Setup

This project requires API keys for certain data sources. **Never commit API keys to git!**

### Required API Keys

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

### Storing Credentials Securely in Databricks

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

## Running dbt via CLI

**Option 1: Using the `run_dbt` notebook** (recommended) — it handles environment setup and execution automatically.

**Option 2: Manual dbt commands**
```bash
# Test connection
dbt debug --project-dir /Workspace/Users/[your_email_address]/Jordan\ Information\ Environment\ Project

# Run all models
dbt run --project-dir /Workspace/Users/[your_email_address]/Jordan\ Information\ Environment\ Project

# Run tests
dbt test --project-dir /Workspace/Users/[your_email_address]/Jordan\ Information\ Environment\ Project

# Run a specific model
dbt run --select acled_jordan_events --project-dir /Workspace/Users/[your_email_address]/Jordan\ Information\ Environment\ Project
```

Replace `[your_email_address]` with the email associated with your Databricks workspace user folder.
