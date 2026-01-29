# Module 01 Labs – DBT Setup & Project Structure

**Prerequisites:** Module 00 completed

**Duration:** ~90 minutes

**Instructor Note:** Demonstrate each lab while students follow along using the same commands.

---

## Lab 1: Install DBT (20 min)

Objective: Install dbt 1.9.8 inside Python virtual environment

### Tasks

1. Create virtual environment
2. Activate virtual environment
3. Install dbt-core and dbt-snowflake
4. Verify installation

### Steps

```bash
python3 -m venv ~/.venv
```

```bash
source ~/.venv/bin/activate
```

```bash
pip install --upgrade pip
```

```bash
pip install dbt-core==1.9.8 dbt-snowflake==1.9.8
```

```bash
dbt --version
```

Expected snippet:

```text
Core:
  - installed: 1.9.8
Plugins:
  - snowflake: 1.9.8
```

### Success

* dbt command works
* Shows core 1.9.8 and snowflake adapter

---

## Lab 2: Initialize Project (20 min)

Objective: Create dbt project

### Tasks

1. Initialize project
2. Enter project directory

### Steps

```bash
dbt init olist_dbt_project
```

Select profile: `olist_dbt_project`

```bash
cd ~/olist_dbt_project
```

### Success

* Project created at ~/olist_dbt_project
* profiles.yml created at ~/.dbt/profiles.yml

---

## Lab 3: Configure Snowflake Connection (25 min)

Objective: Configure profiles.yml with Snowflake connection

### Tasks

1. Edit profiles.yml
2. Set environment variables
3. Run dbt debug

### Steps

Create `~/.dbt/profiles.yml` in VSCode with:

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

**Important:** This configuration uses environment variables for security. Never hardcode credentials in profiles.yml.

Create `.env` file in project root (use VSCode):

```bash
SNOWFLAKE_ACCOUNT=CSHDPGC-TI12670
SNOWFLAKE_USER=DBT_USER
SNOWFLAKE_PASSWORD=StrongPassword@123
SNOWFLAKE_ROLE=DBT_ROLE
SNOWFLAKE_DATABASE=OLIST_DB
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_SCHEMA=ANALYTICS
```

**Security Note:**
- The `.env` file stores sensitive credentials
- Add `.env` to `.gitignore` to prevent committing credentials to git
- In production, use secret management tools (AWS Secrets Manager, Azure Key Vault, etc.)
- The DBT_ROLE has permissions configured in Module 00 to create and manage objects

```bash
dbt debug
```

Expected snippet:

```text
Configuration:
  profiles.yml file [OK found and valid]
  dbt_project.yml file [OK found and valid]

Required dependencies:
  - git [OK found]

Connection:
  account: CSHDPGC-TI12670
  user: DBT_USER
  database: OLIST_DB
  warehouse: COMPUTE_WH
  role: DBT_ROLE
  schema: ANALYTICS
  Connection test: [OK connection ok]

All checks passed!
```

### Success

* All checks pass
* Connection to Snowflake verified

---

## Lab 4: Run Example Models (15 min)

Objective: Run dbt example models to verify setup

### Tasks

1. Run example models

### Steps

```bash
dbt run
```

Expected snippet:

```text
Completed successfully
```

### Success

* Example models build successfully

---

## Lab 5: Configure dbt_project.yml (25 min)

Objective: Set default materializations

### Tasks

1. Open dbt_project.yml
2. Set staging as views
3. Set marts as tables

### Steps

Open `~/olist_dbt_project/dbt_project.yml` in VSCode and update models section:

```yaml
models:
  olist_dbt_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

### Success

* Configuration updated

---

## Lab 6: Organize Folder Structure (30 min)

Objective: Create staging and marts folders and first model

### Tasks

1. Create folders
2. Remove example models
3. Create staging model
4. Run staging models

### Steps

```bash
mkdir -p ~/olist_dbt_project/models/staging
mkdir -p ~/olist_dbt_project/models/marts
rm -rf ~/olist_dbt_project/models/example
```

Create `~/olist_dbt_project/models/staging/stg_customers.sql` in VSCode:

```sql
SELECT
    customer_id,
    customer_city,
    customer_state
FROM OLIST_DB.RAW.customers
```

**Note:** In Module 02, we'll learn to use the `source()` function instead of hardcoding table references.

```bash
dbt run --select staging
```

Expected snippet:

```text
1 of 1 OK
```

### Success

* Staging model builds as view
