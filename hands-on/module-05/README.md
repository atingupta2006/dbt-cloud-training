# Module 05 – Development Workflow & Project Organization

**Duration:** 4 hours (Sessions 9–10)

---

## Lab 1: Run-Test-Build Workflow (30 min)

**Why:** You rarely run the entire project. Efficient development means running specific models, testing them, and using `dbt build` for full pipeline validation.

### Steps

1. Run a single model:

```bash
dbt run --select stg_customers
```

2. Run a model and everything downstream (+ suffix):

```bash
dbt run --select stg_customers+
```

This runs `stg_customers` first, then any model that depends on it (e.g., `fct_orders`).

3. Run a model and everything upstream (+ prefix):

```bash
dbt run --select +fct_orders
```

This runs all ancestors of `fct_orders` first, then `fct_orders` itself.

4. Test a specific model:

```bash
dbt test --select stg_orders
```

5. Build entire project (run + test + seed + snapshot in DAG order):

```bash
dbt build
```

6. Build only a specific directory:

```bash
dbt build --select staging
```

---

## Lab 2: Model Selection Syntax (20 min)

**Why:** In large projects with hundreds of models, precise selection saves time and compute. You need to target exactly what you want without running everything.

### Steps

1. Run all staging models:

```bash
dbt run --select staging.*
```

2. Run all marts except one expensive model:

```bash
dbt run --select marts --exclude fct_sales
```

3. Add a tag to a model — open `models/staging/schema.yml` in VSCode and add:

```yaml
  - name: stg_orders
    config:
      tags: ['daily']
```

4. Run by tag:

```bash
dbt run --select tag:daily
```

5. Preview what a selection would run (without actually running):

```bash
dbt list --select +fct_orders
```

---

## Lab 3: Refactor to Layers (50 min)

**Why:** Monolithic SQL (all joins and logic in one file) is hard to debug, test, and maintain. Layering separates concerns: Staging cleans, Intermediate enriches, Marts serves. The intermediate layer uses `ephemeral` materialization — it generates no physical table, just inlined SQL.

### Scenario

We want to create `dim_customers_enhanced` — a customer dimension with order history stats. Instead of writing all logic in one file, we split it across three layers.

### Steps

1. Ensure `models/staging/stg_orders.sql` exists (created in Module 02). It should select clean columns from `source('olist_raw', 'orders')`.

2. Create the intermediate directory:

```bash
mkdir -p models/intermediate
```

3. Create `models/intermediate/int_customer_order_history.sql` in VSCode:

```sql
{{ config(materialized='ephemeral') }}

SELECT
    customer_id,
    MIN(order_purchase_timestamp) AS first_order_date,
    MAX(order_purchase_timestamp) AS last_order_date,
    COUNT(order_id) AS total_orders
FROM {{ ref('stg_orders') }}
GROUP BY customer_id
```

> Ephemeral models don't create tables or views. dbt inlines the SQL as a CTE wherever it's referenced.

4. Create `models/marts/dim_customers_enhanced.sql` in VSCode:

```sql
WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

order_history AS (
    SELECT * FROM {{ ref('int_customer_order_history') }}
)

SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    h.first_order_date,
    h.last_order_date,
    h.total_orders
FROM customers c
LEFT JOIN order_history h
    ON c.customer_id = h.customer_id
```

5. Update the `models` section of your `dbt_project.yml` to include the intermediate layer. Replace the existing `models:` block with this complete version (it keeps staging and marts from Module 01 and adds intermediate):

```yaml
models:
  olist_dbt_project:
    staging:
      +materialized: view
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
```

6. Build and verify:

```bash
dbt build --select +dim_customers_enhanced
```

7. Confirm `int_customer_order_history` does NOT exist as a table or view in Snowflake:

```sql
SHOW VIEWS IN SCHEMA OLIST_DB.ANALYTICS;
SHOW TABLES IN SCHEMA OLIST_DB.ANALYTICS;
```

Only `dim_customers_enhanced` appears as a table. The ephemeral intermediate model was inlined as a CTE.
