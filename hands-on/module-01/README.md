# Module 01 – DBT Setup & Project Structure

**Duration:** 4 hours (Sessions 1–2)

---

## Lab 1: Install DBT (20 min)

**Why:** A virtual environment isolates project dependencies from system Python. Installing dbt-snowflake automatically pulls in dbt-core as a dependency.

### Steps

1. Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

2. Install dbt:

```bash
pip install dbt-core==1.9.8 dbt-snowflake==1.9.8
```

3. Verify:

```bash
dbt --version
```

Expected output shows `installed: 1.9.8` for core and snowflake adapter.

---

## Lab 2: Initialize Project (20 min)

**Why:** `dbt init` generates the standard project skeleton — `models/`, `dbt_project.yml`, `seeds/`, `tests/` — and creates `~/.dbt/profiles.yml` if it does not exist yet.

### Steps

1. Initialize:

```bash
dbt init olist_dbt_project
```

When prompted, select **Snowflake** as the adapter.

2. Enter the project:

```bash
cd olist_dbt_project
```

3. Verify the skeleton:

```bash
ls -F
```

You should see `dbt_project.yml`, `models/`, `seeds/`, `tests/`, etc.

---

## Lab 3: Configure Snowflake Connection (25 min)

**Why:** dbt reads `~/.dbt/profiles.yml` at runtime to connect to your warehouse. We use `env_var()` so credentials are never hardcoded in files.

### Steps

1. Export environment variables (replace with your actual credentials):

```bash
export SNOWFLAKE_ACCOUNT="your_account_id"
export SNOWFLAKE_USER="DBT_USER"
export SNOWFLAKE_PASSWORD="StrongPassword@123"
export SNOWFLAKE_ROLE="DBT_ROLE"
export SNOWFLAKE_DATABASE="OLIST_DB"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export SNOWFLAKE_SCHEMA="ANALYTICS"
```

2. Open `~/.dbt/profiles.yml` in VSCode and replace contents with:

```yaml
olist_dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: "{{ env_var('SNOWFLAKE_ROLE') }}"
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}"
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}"
      schema: "{{ env_var('SNOWFLAKE_SCHEMA') }}"
      threads: 4
```

3. Test the connection:

```bash
dbt debug
```

Expected output ends with `All checks passed!`

4. Run the default example models to confirm everything works end-to-end:

```bash
dbt run
```

---

## Lab 4: Configure dbt_project.yml (25 min)

**Why:** Setting materialization defaults at the folder level means every model in `staging/` becomes a view and every model in `marts/` becomes a table — without configuring each file individually.

### Steps

1. Open `dbt_project.yml` in VSCode.

2. Update the `models` section:

```yaml
models:
  olist_dbt_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

3. Verify configs apply:

```bash
dbt run
```

---

## Lab 5: Organize Folder Structure (30 min)

**Why:** Staging models clean raw data (views — lightweight). Marts models serve analytics (tables — performant). This layered separation is the foundation of every production dbt project.

### Steps

1. Create directories and clean up defaults:

```bash
mkdir -p models/staging
mkdir -p models/marts
rm -rf models/example
```

2. Create `models/staging/stg_customers.sql` in VSCode:

```sql
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM OLIST_DB.RAW.customers
```

> In Module 02 we replace this file with a version that uses `source()` instead of the hardcoded table reference.

3. Run the staging layer:

```bash
dbt run --select staging
```

The model builds as a view in your ANALYTICS schema.
