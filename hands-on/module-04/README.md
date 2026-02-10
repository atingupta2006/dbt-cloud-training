# Module 04 – Snapshots & Integration

**Duration:** 4 hours (Sessions 7–8)

---

## Lab 1: Create Customer Snapshot (45 min)

**Why:** Dimension data changes over time (a customer moves cities). Snapshots implement SCD Type 2 — they keep every historical version of a record so you can analyze data as it was at any point in time.

### Steps

1. Create `snapshots/customers_snapshot.sql` in VSCode:

```sql
{% snapshot customers_snapshot %}

{{
    config(
      target_schema='SNAPSHOTS',
      unique_key='customer_id',
      strategy='check',
      check_cols=['customer_city', 'customer_state', 'customer_zip_code_prefix']
    )
}}

SELECT *
FROM {{ source('olist_raw', 'customers') }}

{% endsnapshot %}
```

> We use `check` strategy because the Olist customers table has no `updated_at` timestamp. dbt compares the listed columns on each run to detect changes.

2. Run the initial snapshot (baseline):

```bash
dbt snapshot
```

3. Verify in Snowflake Web UI:

```sql
SELECT
    customer_id,
    customer_city,
    customer_state,
    dbt_valid_from,
    dbt_valid_to
FROM OLIST_DB.SNAPSHOTS.customers_snapshot
LIMIT 10;
```

All rows have `dbt_valid_to = NULL` (all current).

4. Simulate a change — update one customer in Snowflake Web UI → Worksheets:

```sql
UPDATE OLIST_DB.RAW.customers
SET customer_city = 'SNAPSHOT_TEST_CITY',
    customer_state = 'ZZ'
WHERE customer_id = (
    SELECT customer_id FROM OLIST_DB.RAW.customers LIMIT 1
);
```

5. Run snapshot again to capture the change:

```bash
dbt snapshot
```

6. Query the history:

```sql
SELECT
    customer_id,
    customer_city,
    customer_state,
    dbt_valid_from,
    dbt_valid_to
FROM OLIST_DB.SNAPSHOTS.customers_snapshot
WHERE customer_city = 'SNAPSHOT_TEST_CITY'
   OR customer_id = (
       SELECT customer_id FROM OLIST_DB.RAW.customers
       WHERE customer_city = 'SNAPSHOT_TEST_CITY'
   )
ORDER BY dbt_valid_from;
```

You should see 2 rows for the same customer — the old version (with `dbt_valid_to` set) and the new version (with `dbt_valid_to = NULL`).

---

## Lab 2: Integration Testing (45 min)

**Why:** `dbt build` runs seeds, models, snapshots, and tests in DAG order — one command to validate the entire pipeline end-to-end.

### Steps

1. Run the complete pipeline:

```bash
dbt build
```

Expected: Seeds load, staging views build, mart tables build, snapshot executes, all tests run. Output should show ~20 steps with PASS/WARN results.

2. Verify all objects in Snowflake Web UI:

```sql
-- Staging views
SHOW VIEWS IN SCHEMA OLIST_DB.ANALYTICS;

-- Mart tables
SHOW TABLES IN SCHEMA OLIST_DB.ANALYTICS;

-- Snapshot table
SHOW TABLES IN SCHEMA OLIST_DB.SNAPSHOTS;
```

Expected objects:
- **Views:** stg_customers, stg_orders, stg_order_items, stg_payments, stg_products
- **Tables:** fct_orders, fct_sales, products_with_categories, product_categories (seed)
- **Snapshots:** customers_snapshot

3. Run only specific parts to confirm selection works:

```bash
dbt build --select staging
```

This runs staging models and their tests only.
