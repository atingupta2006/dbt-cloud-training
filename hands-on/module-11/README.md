# Module 11 – Capstone Project: Complete Olist dbt Pipeline

**Duration:** 2 hours instruction (Session 20) + 4 hours hands-on assessment (the labs below constitute the assessment)

---

## Objective

Build a production-ready dbt project from scratch using the Olist dataset, demonstrating every concept from Modules 01–10. Work individually; instructor available for guidance.

---

## Part 0: Initialize the Project (10 min)

**Why:** The capstone is a from-scratch build. Creating a fresh project ensures you are not relying on leftover files from earlier modules — everything here is your own work.

### Tasks

1. In your terminal, navigate to a parent directory (outside the existing module project) and initialize a new dbt project:

```bash
cd ~
dbt init final_project
```

When prompted, select **snowflake** as the adapter.

2. Move into the new project directory:

```bash
cd final_project
```

3. Open this folder in VSCode.

4. Verify `~/.dbt/profiles.yml` has a `final_project` profile. If not, add one — use the same connection details from Module 01:

```yaml
final_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: DBT_USER
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: DBT_ROLE
      warehouse: COMPUTE_WH
      database: OLIST_DB
      schema: ANALYTICS_DEV
      threads: 4
```

5. Delete the example models that `dbt init` creates:

```bash
rm -rf models/example
```

6. Update `dbt_project.yml` — set the project name and model config:

```yaml
name: 'final_project'
version: '1.0.0'

profile: 'final_project'

models:
  final_project:
    staging:
      +materialized: view
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
```

7. Verify the project connects:

```bash
dbt debug
```

All checks should pass.

---

## Part 1: Setup & Sources (20 min)

**Why:** Every dbt project starts with declaring raw data as sources. This is the foundation — without it, nothing downstream can be built or tested.

### Tasks

1. Verify all 5 Olist tables exist in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.RAW.CUSTOMERS;
SELECT COUNT(*) FROM OLIST_DB.RAW.ORDERS;
SELECT COUNT(*) FROM OLIST_DB.RAW.ORDER_ITEMS;
SELECT COUNT(*) FROM OLIST_DB.RAW.PAYMENTS;
SELECT COUNT(*) FROM OLIST_DB.RAW.PRODUCTS;
```

2. Create `models/staging/sources.yml`:

```yaml
version: 2

sources:
  - name: olist_raw
    database: OLIST_DB
    schema: RAW
    tables:
      - name: customers
      - name: orders
        loaded_at_field: order_purchase_timestamp
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
      - name: order_items
      - name: payments
      - name: products
```

3. Test source freshness:

```bash
dbt source freshness
```

> **Note:** The freshness check will show ERROR because the Olist dataset is historical (2016–2018). This is expected behavior — in production, stale data would correctly trigger this alert.

---

## Part 2: Staging Layer (25 min)

**Why:** Staging models are the single source of truth for column naming, casting, and filtering. Every downstream model references staging — never raw.

### Tasks

1. Create 5 staging models as views in `models/staging/`. The table below shows the minimum key columns — include additional columns as needed:

| Model | Key Columns |
|-------|-------------|
| stg_customers.sql | customer_id, customer_city |
| stg_orders.sql | order_id, customer_id, order_status, order_purchase_timestamp |
| stg_order_items.sql | order_id, order_item_id, product_id, price, freight_value |
| stg_payments.sql | order_id, payment_sequential, payment_type, payment_value |
| stg_products.sql | product_id, product_category_name, product_name_length |

2. Each staging model pattern:

```sql
-- models/staging/stg_customers.sql
WITH source AS (
    SELECT * FROM {{ source('olist_raw', 'customers') }}
)

SELECT
    customer_id,
    customer_city
FROM source
```

3. Add `models/staging/schema.yml` with tests:

```yaml
version: 2

models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
  - name: stg_order_items
    columns:
      - name: order_item_id
        tests:
          - not_null
  - name: stg_payments
    columns:
      - name: order_id
        tests:
          - not_null
  - name: stg_products
    columns:
      - name: product_id
        tests:
          - unique
          - not_null
```

4. Run and test:

```bash
dbt run --select staging
dbt test --select staging
```

---

## Part 3: Intermediate & Marts (50 min)

**Why:** Intermediate models encapsulate reusable join logic. Marts expose business-facing tables — dimensions for descriptive attributes, facts for measurable events.

### Tasks

1. Create `models/intermediate/int_order_items_with_products.sql` (ephemeral):

```sql
{{ config(materialized='ephemeral') }}

SELECT
    CONCAT(oi.order_id, '-', oi.order_item_id) AS order_item_id,
    oi.order_id,
    oi.product_id,
    oi.price,
    oi.freight_value,
    p.product_category_name
FROM {{ ref('stg_order_items') }} oi
LEFT JOIN {{ ref('stg_products') }} p
    ON oi.product_id = p.product_id
```

2. Create `models/intermediate/int_order_payments_agg.sql` (ephemeral):

```sql
{{ config(materialized='ephemeral') }}

SELECT
    order_id,
    COUNT(*) AS payment_count,
    SUM(payment_value) AS total_payment_value
FROM {{ ref('stg_payments') }}
GROUP BY order_id
```

3. Create `models/marts/dim_customers.sql` (table):

```sql
{{ config(materialized='table') }}

SELECT
    c.customer_id,
    c.customer_city,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('stg_orders') }} o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_city
```

4. Create `models/marts/dim_products.sql` (table):

```sql
{{ config(materialized='table') }}

SELECT
    p.product_id,
    p.product_category_name,
    COUNT(DISTINCT oi.order_id) AS times_ordered,
    SUM(oi.price) AS total_revenue
FROM {{ ref('stg_products') }} p
LEFT JOIN {{ ref('stg_order_items') }} oi
    ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_category_name
```

5. Create `models/marts/fct_orders.sql` (table):

```sql
{{ config(materialized='table') }}

SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    pay.payment_count,
    COALESCE(pay.total_payment_value, 0) AS total_payment_value
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('int_order_payments_agg') }} pay
    ON o.order_id = pay.order_id
```

6. Create `models/marts/fct_sales.sql` (incremental):

```sql
{{ config(
    materialized='incremental',
    unique_key='order_item_id',
    on_schema_change='fail'
) }}

-- Note: If you have an existing fct_sales table from Module 02,
-- you may need to run with --full-refresh the first time:
-- dbt run --select fct_sales --full-refresh

SELECT
    oi.order_item_id,
    oi.order_id,
    oi.product_id,
    oi.price,
    oi.freight_value,
    oi.product_category_name,
    o.order_status,
    o.order_purchase_timestamp
FROM {{ ref('int_order_items_with_products') }} oi
LEFT JOIN {{ ref('stg_orders') }} o
    ON oi.order_id = o.order_id

{% if is_incremental() %}
WHERE o.order_purchase_timestamp > (SELECT MAX(order_purchase_timestamp) FROM {{ this }})
{% endif %}
```

7. Add `models/marts/schema.yml`:

```yaml
version: 2

models:
  - name: dim_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
  - name: dim_products
    columns:
      - name: product_id
        tests:
          - unique
          - not_null
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: total_payment_value
        tests:
          - not_null
  - name: fct_sales
    columns:
      - name: order_item_id
        tests:
          - unique
          - not_null
      - name: price
        tests:
          - not_null
```

8. Build:

```bash
dbt build --select intermediate marts
```

---

## Part 4: Advanced Features (40 min)

**Why:** Snapshots, macros, and hooks move a project from "works in dev" to "production-grade." These features handle change tracking, DRY code, and automated permissions.

### Tasks

1. Create `snapshots/customers_snapshot.sql`:

```sql
{% snapshot customers_snapshot %}

{{ config(
    target_schema='SNAPSHOTS',
    unique_key='customer_id',
    strategy='check',
    check_cols=['customer_city']
) }}

SELECT * FROM {{ source('olist_raw', 'customers') }}

{% endsnapshot %}
```

2. Run snapshot:

```bash
dbt snapshot
```

3. Create macro `macros/cents_to_dollars.sql`:

```sql
{% macro cents_to_dollars(amount_col) %}
    ({{ amount_col }} / 100.0)
{% endmacro %}
```

> This macro demonstrates reusable transformations. Olist data is in BRL, not cents — in production you would adapt the logic to your currency format.

4. Create macro `macros/get_payment_types.sql`:

```sql
{% macro get_payment_types() %}
    {{ return(["credit_card", "boleto", "voucher", "debit_card"]) }}
{% endmacro %}
```

5. Use `cents_to_dollars` in `fct_sales.sql` — add this column to the SELECT. Add a comma after the previous line (`o.order_purchase_timestamp`) and insert:

```sql
    {{ cents_to_dollars('oi.price') }} AS price_converted
```

6. Add a post-hook to `dbt_project.yml`:

```yaml
models:
  final_project:
    +post-hook:
      - "GRANT SELECT ON {{ this }} TO ROLE ACCOUNTADMIN"
```

7. Rebuild to verify hooks execute:

```bash
dbt run --select fct_orders
```

---

## Part 5: Documentation (20 min)

**Why:** A dbt project without documentation is a liability. Future developers (including your future self) need to understand what each model does and why.

### Tasks

1. Add descriptions to `models/staging/schema.yml`:

```yaml
models:
  - name: stg_customers
    description: "Cleaned customer records from Olist raw data"
    columns:
      - name: customer_id
        description: "Unique customer identifier"
```

2. Add descriptions to all mart models in `models/marts/schema.yml`.

3. Generate and serve docs:

```bash
dbt docs generate
dbt docs serve
```

4. In the browser, verify:
   - DAG shows complete lineage from sources → staging → intermediate → marts
   - All models have descriptions
   - Click on `fct_sales` and trace its upstream dependencies

---

## Part 6: Cloud Deployment (25 min)

**Why:** Local dbt is for development. Production pipelines run in dbt Cloud with scheduled jobs, alerting, and artifact management — no laptop required.

### Tasks

1. Initialize a Git repository and push to GitHub (from the project root directory):

```bash
git init
git add .
git commit -m "Capstone: complete Olist pipeline"
```

2. Create a new repository on GitHub (e.g., `final-project`), then connect and push:

```bash
git remote add origin https://github.com/<your-username>/final-project.git
git branch -M main
git push -u origin main
```

3. In dbt Cloud:
   - Connect Git repository
   - Navigate to **Orchestration → Environments**
   - Create **Development** environment → Snowflake connection → `ANALYTICS_DEV` schema
   - Create **Production** environment → `ANALYTICS` schema

4. Test in dbt Cloud:
   - Open the **Studio IDE** (click **Studio** in the left navigation) and run `dbt build`
   - Verify all models and tests pass

5. Create production job:

| Setting | Value |
|---------|-------|
| Name | Capstone Daily Build |
| Environment | Production |
| Commands | `dbt build` |
| Schedule | `0 6 * * *` |
| Notifications | Email on failure |

6. Trigger the job manually, verify successful completion.

---

## Part 7: Validation (10 min)

**Why:** Final validation ensures everything works end-to-end. A passing `dbt build` in production is the ultimate proof your pipeline is ready.

### Tasks

1. In Snowflake Web UI, verify production tables:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.DIM_CUSTOMERS;
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_SALES;
```

2. In dbt Cloud, verify:
   - Job run history shows green (success)
   - Docs are generated and accessible
   - DAG is complete

3. Run full test suite one final time:

```bash
dbt test
```

---

## Deliverables

| # | Item | Check |
|---|------|-------|
| 1 | 5 staging models (views) | |
| 2 | 2 intermediate models (ephemeral) | |
| 3 | 2 dimension tables + 2 fact tables (1 incremental) | |
| 4 | Sources with freshness checks | |
| 5 | 15+ tests passing | |
| 6 | 1 snapshot configured | |
| 7 | 2+ custom macros used in models | |
| 8 | All models documented with descriptions | |
| 9 | Deployed to dbt Cloud with dev + prod environments | |
| 10 | Production job scheduled and tested | |

### Submission

Provide to the instructor:

1. GitHub repository link
2. dbt Cloud project link (share access)
3. Screenshots: successful Cloud job run, DAG lineage, Snowflake production tables
