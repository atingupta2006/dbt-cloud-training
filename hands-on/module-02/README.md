# Module 02 Labs — Building Models & Sources

**Prerequisites:** Module 01 completed

**Duration:** ~80 minutes

**Instructor Note:** Walk through each lab step-by-step. Ensure students create all staging models before proceeding to marts.

---

## Lab 1 — Staging Models with ref() (25 min)

**Objective**: Build staging models and downstream model using ref().

**Concept: ref() Function**

Replaces hard-coded table names with `{{ ref('model_name') }}`.

Benefits:
- Auto-resolves to correct database.schema.table
- Builds dependency graph (DAG)
- Controls execution order automatically
- Tracks lineage between models

### Tasks

1. Create `~/olist_dbt_project/models/staging/sources.yml` in VSCode:

```yaml
version: 2

sources:
  - name: olist_raw
    schema: RAW
    tables:
      - name: customers
        identifier: customers
      - name: orders
        identifier: orders
      - name: order_items
        identifier: order_items
      - name: products
        identifier: products
      - name: payments
        identifier: payments
```

**Note:** The database name (OLIST_DB) is inherited from your `profiles.yml` configuration.

2. Create staging model files in VSCode:

- `~/olist_dbt_project/models/staging/stg_customers.sql`
- `~/olist_dbt_project/models/staging/stg_orders.sql`
- `~/olist_dbt_project/models/staging/stg_order_items.sql`
- `~/olist_dbt_project/models/staging/stg_payments.sql`

3. Add to `stg_customers.sql`:

```sql
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM {{ source('olist_raw', 'customers') }}
```

5. Edit stg_orders.sql

```sql
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
FROM {{ source('olist_raw', 'orders') }}
```

6. Edit stg_order_items.sql

```sql
SELECT
    order_id,
    product_id,
    price,
    freight_value
FROM {{ source('olist_raw', 'order_items') }}
```

7. Edit stg_payments.sql

```sql
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM {{ source('olist_raw', 'payments') }}
```

8. Create marts directory

```bash
mkdir -p ~/olist_dbt_project/models/marts
```

9. Create `~/olist_dbt_project/models/marts/fct_orders.sql` in VSCode:

```sql
WITH orders AS (

    SELECT *
    FROM {{ ref('stg_orders') }}

),

customers AS (

    SELECT *
    FROM {{ ref('stg_customers') }}

)

SELECT
    o.order_id,
    o.customer_id,
    c.customer_city,
    o.order_status
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
```

11. Run models

```bash
dbt run
```

### Success

Logs show staging models run before fct_orders

---

## Lab 2 — Build Incremental Fact Table (35 min)

**Objective**: Create fct_sales incremental model.

**Concept: Incremental Models**

Optimization for large tables—processes only new/changed data instead of full rebuild.

Key components:
- `materialized='incremental'`: Enables incremental logic
- `unique_key`: Identifies rows for merge/upsert
- `is_incremental()`: Adds filter on subsequent runs
- `--full-refresh`: Forces complete rebuild

First run builds full table; subsequent runs process only new records.

### Tasks

1. Create `~/olist_dbt_project/models/marts/fct_sales.sql` in VSCode:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_item_id'
) }}

WITH orders AS (

    SELECT
        order_id,
        customer_id,
        order_purchase_timestamp
    FROM {{ ref('stg_orders') }}

),

items AS (

    SELECT
        order_id,
        product_id,
        price,
        freight_value
    FROM {{ ref('stg_order_items') }}

),

joined AS (

    SELECT
        CONCAT(o.order_id, '-', i.product_id) AS order_item_id,
        o.order_id,
        i.product_id,
        o.customer_id,
        o.order_purchase_timestamp,
        i.price,
        i.freight_value
    FROM orders o
    JOIN items i
        ON o.order_id = i.order_id

    {% if is_incremental() %}
    WHERE o.order_purchase_timestamp > (
        SELECT MAX(order_purchase_timestamp)
        FROM {{ this }}
    )
    {% endif %}

)

SELECT * FROM joined
```

2. Run first time

```bash
dbt run --select fct_sales
```

3. Insert one new row into RAW.orders (in Snowflake)

4. Run again

```bash
dbt run --select fct_sales
```

6. Full refresh

```bash
dbt run --select fct_sales --full-refresh
```

### Success

Second run processes fewer rows than first

---

## Lab 3 — Source Freshness Configuration (20 min)

**Objective**: Add freshness checks to monitor data staleness.

**Concept: Source Freshness**

Monitors raw data staleness by checking timestamp columns.

Key elements:
- `loaded_at_field`: Timestamp column showing when data was last updated
- `warn_after`: Warning threshold (e.g., 12 hours)
- `error_after`: Error threshold (e.g., 24 hours)
- `dbt source freshness`: Queries max timestamp and compares to current time

Results: PASS (fresh), WARN (stale), or ERROR (very stale).

### Tasks

1. Update sources.yml to add freshness configuration

Edit `~/olist_dbt_project/models/staging/sources.yml`:

```yaml
version: 2

sources:
  - name: olist_raw
    schema: RAW
    freshness:
      warn_after:
        count: 12
        period: hour
      error_after:
        count: 24
        period: hour
    tables:
      - name: customers
        identifier: customers
        loaded_at_field: customer_id
      - name: orders
        identifier: orders
        loaded_at_field: order_purchase_timestamp
      - name: order_items
        identifier: order_items
        loaded_at_field: order_id
      - name: products
        identifier: products
      - name: payments
        identifier: payments
```

**Note:** We added freshness checks for `orders`, `customers`, and `order_items` tables. The `products` and `payments` tables don't have freshness checks configured (no `loaded_at_field`).

2. Run freshness checks

```bash
dbt source freshness
```

**Expected output:**
```
14:30:00 | Concurrency: 4 threads
14:30:00 | 
14:30:00 | 1 of 3 START freshness of olist_raw.orders ..................... [RUN]
14:30:01 | 1 of 3 PASS freshness of olist_raw.orders ...................... [PASS in 0.8s]
14:30:01 | 2 of 3 START freshness of olist_raw.customers .................. [RUN]
14:30:02 | 2 of 3 WARN freshness of olist_raw.customers ................... [WARN in 0.7s]
14:30:02 | 3 of 3 START freshness of olist_raw.order_items ................ [RUN]
14:30:03 | 3 of 3 PASS freshness of olist_raw.order_items ................. [PASS in 0.6s]
```

**Note:** Some tables may show WARN status depending on when data was last loaded. This is expected for demo data.

3. Inspect freshness results

Check the generated JSON file:

```bash
cat ~/olist_dbt_project/target/sources.json
```

This contains detailed timestamps for each source table.

### Success

 - ✅ Freshness checks run successfully
 - ✅ Output shows PASS/WARN status for each configured table
 - ✅ sources.json file generated with detailed results

---

## Lab 4 — Verify Complete Pipeline (10 min)

**Objective**: Test the complete Module 02 pipeline end-to-end.

### Tasks

1. Run all models

```bash
dbt run
```

**Expected output:**
```
14:30:00 | Concurrency: 4 threads
14:30:00 | 
14:30:00 | 1 of 6 START sql view model ANALYTICS.stg_customers ............ [RUN]
14:30:00 | 2 of 6 START sql view model ANALYTICS.stg_orders ............... [RUN]
14:30:00 | 3 of 6 START sql view model ANALYTICS.stg_order_items .......... [RUN]
14:30:00 | 4 of 6 START sql view model ANALYTICS.stg_payments ............. [RUN]
14:30:01 | 1 of 6 OK created sql view model ANALYTICS.stg_customers ....... [SUCCESS in 0.8s]
14:30:01 | 2 of 6 OK created sql view model ANALYTICS.stg_orders .......... [SUCCESS in 0.9s]
14:30:01 | 3 of 6 OK created sql view model ANALYTICS.stg_order_items ..... [SUCCESS in 0.8s]
14:30:01 | 4 of 6 OK created sql view model ANALYTICS.stg_payments ........ [SUCCESS in 0.9s]
14:30:01 | 5 of 6 START sql table model ANALYTICS.fct_orders .............. [RUN]
14:30:02 | 5 of 6 OK created sql table model ANALYTICS.fct_orders ......... [SUCCESS in 1.2s]
14:30:02 | 6 of 6 START sql incremental model ANALYTICS.fct_sales ......... [RUN]
14:30:03 | 6 of 6 OK created sql incremental model ANALYTICS.fct_sales .... [SUCCESS in 1.0s]
```

2. Run freshness checks

```bash
dbt source freshness
```

3. Verify in Snowflake

```sql
-- Check staging views
SHOW VIEWS IN SCHEMA OLIST_DB.ANALYTICS;

-- Check mart tables
SHOW TABLES IN SCHEMA OLIST_DB.ANALYTICS;

-- Count records
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.fct_orders;
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.fct_sales;
```

### Success

 - ✅ All 6 models run successfully (4 staging views + 2 marts)
 - ✅ Staging models created as views
 - ✅ fct_orders created as table
 - ✅ fct_sales created as incremental table
 - ✅ Freshness checks complete
 - ✅ DAG executes in correct order (staging before marts)

---

## Module 02 Summary

### What You Built

**Staging Layer (4 models):**
- stg_customers
- stg_orders
- stg_order_items
- stg_payments

**Marts Layer (2 models):**
- fct_orders (table materialization)
- fct_sales (incremental materialization)

**Configuration:**
- sources.yml with 5 source tables
- Freshness checks on 3 tables

### Key Concepts Mastered

1. **ref() Function**: Build dependencies between models
2. **source() Function**: Reference raw source tables
3. **Incremental Models**: Optimize large table processing
4. **Source Freshness**: Monitor data staleness
5. **Materialization**: Views vs Tables vs Incremental
6. **DAG**: Dependency graph and execution order

### Commands Learned

```bash
dbt run                        # Run all models
dbt run --select <model>       # Run specific model
dbt run --full-refresh         # Rebuild incremental tables
dbt source freshness           # Check source data freshness
```

### Next Steps

Module 03 will cover:
- Seeds for reference data
- Generic tests (not_null, unique, relationships)
- Custom singular tests
- Data quality validation
