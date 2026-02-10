# Module 08 – Environment Management

**Duration:** 2 hours (Session 15)

---

## Lab 1: Create Development Environment in dbt Cloud (25 min)

**Why:** Separating dev from prod prevents accidental writes to production tables. In dbt Cloud, each environment has its own Snowflake schema, credentials, and dbt version.

### Steps

1. Open browser → [https://cloud.getdbt.com](https://cloud.getdbt.com)
2. Create account or sign in
3. Create a new project and connect your GitHub repository
4. Navigate to **Account Settings → Projects → Your Project → Environments**
5. Click **New Environment**
6. Configure:

| Setting | Value |
|---------|-------|
| Name | Development |
| Type | Development |
| dbt Version | 1.9.8 |
| Adapter | Snowflake |
| Database | OLIST_DB |
| Schema | ANALYTICS_DEV |
| Warehouse | COMPUTE_WH |
| Threads | 4 |

7. Enter your personal Snowflake user and password
8. Click **Save**
9. Open the Cloud IDE and run:

```bash
dbt debug
```

Connection test should return `[OK]`.

---

## Lab 2: Create Production Environment in dbt Cloud (20 min)

**Why:** Production uses a separate schema (ANALYTICS instead of ANALYTICS_DEV) and potentially higher thread count for faster execution.

### Steps

1. Navigate to **Account Settings → Projects → Your Project → Environments**
2. Click **New Environment**
3. Configure:

| Setting | Value |
|---------|-------|
| Name | Production |
| Type | Deployment |
| dbt Version | 1.9.8 |
| Adapter | Snowflake |
| Database | OLIST_DB |
| Schema | ANALYTICS |
| Warehouse | COMPUTE_WH |
| Threads | 8 |

4. Enter production Snowflake credentials
5. Click **Save**
6. Click **Test Connection** to verify

---

## Lab 3: Compare CLI Multi-Target vs Cloud Environments (20 min)

**Why:** CLI uses `--target` flags in `profiles.yml` to switch environments. dbt Cloud uses the environment selector in the UI. Both achieve the same result — models landing in different schemas.

### Steps

1. Open `~/.dbt/profiles.yml` in VSCode. Add a prod target under the existing dev:

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
      schema: ANALYTICS_DEV
      threads: 4
    prod:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: "{{ env_var('SNOWFLAKE_ROLE') }}"
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}"
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}"
      schema: ANALYTICS
      threads: 8
```

2. Run against dev:

```bash
dbt run --target dev --select stg_customers
```

3. Verify in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.STG_CUSTOMERS;
```

4. Run against prod:

```bash
dbt run --target prod --select stg_customers
```

5. Verify in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.STG_CUSTOMERS;
```

Same model, two different schemas.

> **Important:** After this change, the dev target now builds to `ANALYTICS_DEV` instead of `ANALYTICS`. All subsequent `dbt run` commands (without `--target`) will use `ANALYTICS_DEV`. Your existing models in `ANALYTICS` remain untouched.

---

## Lab 4: Environment-Specific Logic (15 min)

**Why:** Dev datasets should be small (fast iteration). Prod datasets must be complete. Using `target.name` lets you LIMIT rows in dev without changing any config.

### Steps

1. Create `models/marts/orders_env_demo.sql` in VSCode:

```sql
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
FROM {{ ref('stg_orders') }}

{% if target.name == 'dev' %}
LIMIT 1000
{% endif %}
```

2. Run in dev:

```bash
dbt run --select orders_env_demo --target dev
```

3. Verify row count in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.ORDERS_ENV_DEMO;
```

Expected: 1,000 rows.

4. Run in prod:

```bash
dbt run --select orders_env_demo --target prod
```

5. Verify:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.ORDERS_ENV_DEMO;
```

Expected: full dataset (~99,000 rows).
