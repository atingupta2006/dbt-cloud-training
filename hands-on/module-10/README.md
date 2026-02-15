# Module 10 – Review & Troubleshooting

**Duration:** 2 hours (Session 19)

---

## Lab 1: Debug Compilation Errors (25 min)

**Why:** Compilation errors are the most common roadblock in daily dbt work. Recognizing error patterns — bad refs, Jinja typos, circular dependencies — saves hours of frustration.

### Scenario A: Typo in ref()

1. Create a broken model:

```sql
-- models/staging/stg_broken_ref.sql
SELECT
    customer_id,
    customer_city
FROM {{ ref('stg_customer') }}  -- missing 's'
```

2. Compile:

```bash
dbt compile --select stg_broken_ref
```

3. Read the error:

```
Compilation Error in model stg_broken_ref
  node 'stg_customer' was not found
```

4. Fix: Open `models/staging/stg_broken_ref.sql` and change `stg_customer` to `stg_customers`. Re-compile to confirm.

5. Clean up:

```bash
rm models/staging/stg_broken_ref.sql
```

### Scenario B: Unclosed Jinja Tag

1. Create a broken model:

```sql
-- models/staging/stg_broken_jinja.sql
SELECT
    order_id,
    order_status
FROM {{ ref('stg_orders') }}
{% if target.name == 'prod' %
WHERE order_status = 'delivered'
{% endif %}
```

2. Compile:

```bash
dbt compile --select stg_broken_jinja
```

3. Error:

```
Compilation Error
  unexpected end of template, expected 'end of print statement'
```

4. Fix: Open `models/staging/stg_broken_jinja.sql`, locate line 6, and change `%` to `%}`. Re-compile to confirm.

5. Clean up:

```bash
rm models/staging/stg_broken_jinja.sql
```

### Scenario C: Circular Dependency

1. Create two models that reference each other:

```sql
-- models/staging/stg_circle_a.sql
SELECT * FROM {{ ref('stg_circle_b') }}
```

```sql
-- models/staging/stg_circle_b.sql
SELECT * FROM {{ ref('stg_circle_a') }}
```

2. Compile:

```bash
dbt compile --select stg_circle_a
```

3. Error:

```
Found a cycle: stg_circle_a --> stg_circle_b --> stg_circle_a
```

4. Fix: break the cycle — one model must reference a source or a different upstream model, not the other.

5. Clean up:

```bash
rm models/staging/stg_circle_a.sql models/staging/stg_circle_b.sql
```

---

## Lab 2: Resolve Test Failures (20 min)

**Why:** Failing tests are signals, not bugs. Learning to query the actual failing records and decide whether to fix the data, adjust the model, or update the test is core dbt skill.

### Scenario A: Unique Test Fails

1. Run tests:

```bash
dbt test --select stg_customers
```

2. If unique test on `customer_id` passes (clean data), simulate a duplicate by creating a model that introduces one:

```sql
-- models/staging/stg_customers_bad.sql
SELECT * FROM {{ ref('stg_customers') }}
UNION ALL
SELECT * FROM {{ ref('stg_customers') }} LIMIT 1
```

3. Add a test in `models/staging/schema.yml`. Append this to the existing `models:` list (watch your indentation):

```yaml
  - name: stg_customers_bad
    columns:
      - name: customer_id
        tests:
          - unique
```

4. Run:

```bash
dbt run --select stg_customers_bad
dbt test --select stg_customers_bad
```

5. Test fails. Query the compiled test SQL to see duplicates:

```bash
cat target/compiled/olist_dbt_project/models/staging/schema.yml/unique_stg_customers_bad_customer_id.sql
```

6. Copy that SQL, run in Snowflake Web UI to see the offending rows.

7. Fix: the model logic needs deduplication. Clean up:

```bash
rm models/staging/stg_customers_bad.sql
```

Remove the entire `stg_customers_bad` block from `models/staging/schema.yml`.

### Scenario B: Negative Amounts

1. Create a model with a potential data quality issue:

```sql
-- models/marts/fct_orders_check.sql
SELECT
    oi.order_id,
    oi.price,
    oi.freight_value,
    oi.price - oi.freight_value AS net_amount
FROM {{ ref('stg_order_items') }} oi
```

2. Add a custom test:

```sql
-- tests/assert_no_negative_net_amount.sql
SELECT *
FROM {{ ref('fct_orders_check') }}
WHERE net_amount < 0
```

3. Run:

```bash
dbt run --select fct_orders_check
dbt test --select fct_orders_check
```

4. If the test fails, check the rows in Snowflake Web UI. Decide: is this valid data (freight > price) or a bug?

5. Clean up:

```bash
rm models/marts/fct_orders_check.sql tests/assert_no_negative_net_amount.sql
```

---

## Lab 3: Optimize Slow Model (30 min)

**Why:** A model that runs in 2 minutes during development may run against 100x more data in production. Knowing how to profile, diagnose, and fix slow models is critical for production dbt projects.

### Steps

1. Create a deliberately expensive model (`models/marts/fct_sales_slow.sql`):

```sql
-- models/marts/fct_sales_slow.sql
{{ config(materialized='table') }}

SELECT
    CONCAT(oi.order_id, '-', oi.order_item_id) AS order_item_id,
    oi.order_id,
    oi.product_id,
    oi.price,
    oi.freight_value,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_city,
    p.product_category_name
FROM {{ ref('stg_order_items') }} oi
LEFT JOIN {{ ref('stg_orders') }} o ON oi.order_id = o.order_id
LEFT JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
LEFT JOIN {{ ref('stg_products') }} p ON oi.product_id = p.product_id
```

> We deliberately omit the payments join here. Joining payments directly to order_items creates a fan-out (3 items × 2 payments = 6 rows). In production, aggregate payments separately and join the result.

2. Run and note execution time:

```bash
dbt run --select fct_sales_slow
```

3. Inspect the compiled SQL:

```bash
cat target/compiled/olist_dbt_project/models/marts/fct_sales_slow.sql
```

4. Convert to incremental:

```sql
-- models/marts/fct_sales_slow.sql
{{ config(
    materialized='incremental',
    unique_key='order_item_id'
) }}

SELECT
    CONCAT(oi.order_id, '-', oi.order_item_id) AS order_item_id,
    oi.order_id,
    oi.product_id,
    oi.price,
    oi.freight_value,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_city,
    p.product_category_name
FROM {{ ref('stg_order_items') }} oi
LEFT JOIN {{ ref('stg_orders') }} o ON oi.order_id = o.order_id
LEFT JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
LEFT JOIN {{ ref('stg_products') }} p ON oi.product_id = p.product_id

{% if is_incremental() %}
WHERE o.order_purchase_timestamp > (SELECT MAX(order_purchase_timestamp) FROM {{ this }})
{% endif %}
```

5. Run full refresh, then incremental:

```bash
dbt run --select fct_sales_slow --full-refresh
dbt run --select fct_sales_slow
```

6. Compare execution times. Incremental run processes zero new rows — near-instant.

7. Add clustering (Snowflake-specific):

```sql
{{ config(
    materialized='incremental',
    unique_key='order_item_id',
    cluster_by=['order_purchase_timestamp']
) }}
```

8. Clean up:

```bash
rm models/marts/fct_sales_slow.sql
```

---

## Lab 4: Debug Production Issue (25 min)

**Why:** Production failures happen at 3 AM. Knowing the exact steps — check logs, isolate the failed model, fix, re-run only failures — turns a potential outage into a 10-minute fix.

### Steps

1. Use the `--debug` flag to get verbose output:

```bash
dbt --debug run --select stg_orders
```

2. Examine the log file:

```bash
cat logs/dbt.log | tail -50
```

3. Key things to look for in logs:
   - `Database Error` — connection or permission problem
   - `Compilation Error` — Jinja or ref issue
   - `Runtime Error` — SQL execution failure

4. Test connection:

```bash
dbt debug
```

This validates: Python version, profiles.yml, database connectivity, required schemas.

5. Simulate a selective re-run. Imagine `fct_orders` failed in a nightly job. Instead of running everything, use selection syntax to rebuild just that model and its downstream dependencies:

```bash
dbt run --select fct_orders+
```

6. In dbt Cloud, the equivalent is: **Deploy → Jobs → Run History** → select failed run → examine **Logs** tab → click on the failed model for error details.

7. Re-run only failed models from the last run:

```bash
dbt retry
```

`dbt retry` (available since dbt 1.6) re-executes all nodes that failed or were skipped in the most recent run, using the `run_results.json` in your `target/` directory.

8. Discussion: build a runbook for production incidents:
   - Check job logs (Cloud) or `logs/dbt.log` (CLI)
   - Identify failed model
   - Run `dbt debug` for connectivity
   - Test the single model in dev
   - Fix and re-deploy
