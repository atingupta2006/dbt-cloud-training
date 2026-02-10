# Module 02 – Building Models & Sources

**Duration:** 4 hours (Sessions 3–4)

---

## Lab 1: Staging Models with source() and ref() (25 min)

**Why:** `source()` decouples models from physical table names — if the raw schema changes, you update one YAML file instead of every SQL file. `ref()` builds a dependency graph (DAG) so dbt knows the correct execution order.

### Steps

1. Create `models/staging/sources.yml` in VSCode:

```yaml
version: 2

sources:
  - name: olist_raw
    schema: RAW
    tables:
      - name: customers
      - name: orders
      - name: order_items
      - name: products
      - name: payments
```

2. Update `models/staging/stg_customers.sql` (replace the hardcoded version from Module 01):

```sql
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM {{ source('olist_raw', 'customers') }}
```

3. Create `models/staging/stg_orders.sql`:

```sql
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
FROM {{ source('olist_raw', 'orders') }}
```

4. Create `models/staging/stg_order_items.sql`:

```sql
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price,
    freight_value
FROM {{ source('olist_raw', 'order_items') }}
```

5. Create `models/staging/stg_payments.sql`:

```sql
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM {{ source('olist_raw', 'payments') }}
```

6. Create `models/marts/fct_orders.sql`:

```sql
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
)

SELECT
    o.order_id,
    o.customer_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
```

7. Run all models:

```bash
dbt run
```

Check the logs — staging models run before `fct_orders` because `ref()` tells dbt the dependency order.

---

## Lab 2: Build Incremental Fact Table (35 min)

**Why:** Full rebuilds are expensive on large tables. Incremental models process only new/changed rows on subsequent runs, cutting execution time from minutes to seconds.

### Steps

1. Create `models/marts/fct_sales.sql` in VSCode:

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
        order_item_id,
        product_id,
        price,
        freight_value
    FROM {{ ref('stg_order_items') }}
),

joined AS (
    SELECT
        CONCAT(o.order_id, '-', i.order_item_id) AS order_item_id,
        o.order_id,
        i.product_id,
        o.customer_id,
        o.order_purchase_timestamp,
        i.price,
        i.freight_value
    FROM orders o
    JOIN items i ON o.order_id = i.order_id

    {% if is_incremental() %}
    WHERE o.order_purchase_timestamp > (
        SELECT MAX(order_purchase_timestamp) FROM {{ this }}
    )
    {% endif %}
)

SELECT * FROM joined
```

2. First run — builds the full table:

```bash
dbt run --select fct_sales
```

3. Run again — processes only new rows (none in this case):

```bash
dbt run --select fct_sales
```

4. Force a complete rebuild:

```bash
dbt run --select fct_sales --full-refresh
```

---

## Lab 3: Source Freshness (20 min)

**Why:** Freshness checks alert you when raw data stops arriving. If `orders` hasn't been updated in 24 hours, something is broken upstream.

### Steps

1. Update `models/staging/sources.yml` to add freshness config:

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
      - name: orders
        loaded_at_field: order_purchase_timestamp
      - name: order_items
      - name: products
      - name: payments
```

> Only the `orders` table has a proper timestamp column for freshness. Tables without `loaded_at_field` are skipped.

2. Run freshness check:

```bash
dbt source freshness
```

Output shows PASS, WARN, or ERROR for each configured table.

> **Note:** The Olist dataset contains historical data (2016–2018), so the freshness check will show ERROR because the most recent order timestamp is years old. This is expected — in a live production system, data this stale would correctly trigger an alert.

---

## Lab 4: Verify Complete Pipeline (10 min)

**Why:** Running everything together confirms that sources, staging, and marts connect correctly end-to-end.

### Steps

1. Run all models:

```bash
dbt run
```

2. Verify in Snowflake Web UI → Worksheets:

```sql
SHOW VIEWS IN SCHEMA OLIST_DB.ANALYTICS;
SHOW TABLES IN SCHEMA OLIST_DB.ANALYTICS;
```

You should see 4 staging views and 2 mart tables (fct_orders, fct_sales).
