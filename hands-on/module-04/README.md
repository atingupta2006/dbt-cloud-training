# Module 04 – Snapshots & Integration

**Prerequisites:** Module 03 completed

**Duration:** ~120 minutes

**Instructor Note:** This module introduces snapshots for slowly changing dimensions and builds a complete integration pipeline.

---

## Lab 1: Create Customer Snapshot (30 min)

Objective: Track customer record changes over time

### Tasks

1. Create snapshots directory

```bash
mkdir -p ~/olist_dbt_project/snapshots
```

2. Create snapshot file

```bash
touch ~/olist_dbt_project/snapshots/customers_snapshot.sql
```

3. Add snapshot (timestamp strategy using derived updated_at)

```sql
{% snapshot customers_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

WITH customers AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_city,
        customer_state
    FROM {{ source('olist_raw', 'customers') }}
),

orders AS (
    SELECT
        customer_id,
        MAX(order_purchase_timestamp) AS updated_at
    FROM {{ source('olist_raw', 'orders') }}
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.updated_at
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id

{% endsnapshot %}
```

4. Run snapshot

```bash
dbt snapshot
```

5. Update one customer record in raw table

```sql
UPDATE OLIST_DB.RAW.customers
SET customer_city = 'test_city'
WHERE customer_id = (
    SELECT customer_id FROM OLIST_DB.RAW.customers LIMIT 1
);
```

6. Run snapshot again

```bash
dbt snapshot
```

7. Query snapshot table

```sql
SELECT
    customer_id,
    customer_city,
    dbt_valid_from,
    dbt_valid_to
FROM snapshots.customers_snapshot
ORDER BY customer_id, dbt_valid_from;
```

Success: Snapshot table shows multiple versions for same customer_id

---

## Lab 2: Integration Project (90 min)

Objective: Build complete end-to-end pipeline

Pipeline Architecture

```
sources (5 raw tables)
    ↓
staging (5 views)
    ↓
intermediate (2 ephemeral)
    ↓
marts (3 tables)
```

---

### Tasks

1. Declare sources

```bash
touch ~/olist_dbt_project/models/sources.yml
```

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

2. Create staging models

```bash
mkdir -p ~/olist_dbt_project/models/staging
```

```bash
touch ~/olist_dbt_project/models/staging/stg_customers.sql
```

```sql
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM {{ source('olist_raw', 'customers') }}
```

```bash
touch ~/olist_dbt_project/models/staging/stg_orders.sql
```

```sql
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
FROM {{ source('olist_raw', 'orders') }}
```

```bash
touch ~/olist_dbt_project/models/staging/stg_order_items.sql
```

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

```bash
touch ~/olist_dbt_project/models/staging/stg_products.sql
```

```sql
SELECT
    product_id,
    product_category_name
FROM {{ source('olist_raw', 'products') }}
```

```bash
touch ~/olist_dbt_project/models/staging/stg_payments.sql
```

```sql
SELECT
    order_id,
    payment_type,
    payment_value
FROM {{ source('olist_raw', 'payments') }}
```

3. Add staging tests

```bash
touch ~/olist_dbt_project/models/staging/schema.yml
```

```yaml
version: 2

models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests: [not_null, unique]

  - name: stg_orders
    columns:
      - name: order_id
        tests: [not_null, unique]
```

4. Create intermediate models

```bash
mkdir -p ~/olist_dbt_project/models/intermediate
```

```bash
touch ~/olist_dbt_project/models/intermediate/int_orders_enriched.sql
```

```sql
{{ config(materialized='ephemeral') }}

SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    p.payment_type,
    p.payment_value
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('stg_payments') }} p
    ON o.order_id = p.order_id
```

```bash
touch ~/olist_dbt_project/models/intermediate/int_customer_metrics.sql
```

```sql
{{ config(materialized='ephemeral') }}

SELECT
    customer_id,
    COUNT(order_id) AS total_orders
FROM {{ ref('stg_orders') }}
GROUP BY customer_id
```

5. Create marts

```bash
mkdir -p ~/olist_dbt_project/models/marts
```

```bash
touch ~/olist_dbt_project/models/marts/dim_customers.sql
```

```sql
SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    m.total_orders
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('int_customer_metrics') }} m
    ON c.customer_id = m.customer_id
```

```bash
touch ~/olist_dbt_project/models/marts/dim_products.sql
```

```sql
SELECT
    product_id,
    product_category_name
FROM {{ ref('stg_products') }}
```

```bash
touch ~/olist_dbt_project/models/marts/fct_sales.sql
```

```sql
{{ config(materialized='incremental', unique_key='order_item_id') }}

SELECT
    CONCAT(oi.order_id, '-', oi.product_id) AS order_item_id,
    oi.order_id,
    oi.order_item_id AS original_order_item_id,
    oi.product_id,
    oi.price,
    oi.freight_value
FROM {{ ref('stg_order_items') }} oi
```

6. Add mart tests

```bash
touch ~/olist_dbt_project/models/marts/schema.yml
```

```yaml
version: 2

models:
  - name: dim_customers
    columns:
      - name: customer_id
        tests: [not_null, unique]

  - name: fct_sales
    columns:
      - name: order_id
        tests: [not_null]
```

7. Create snapshot for dim_customers

Reuse customers_snapshot.sql

8. Run full pipeline

```bash
dbt build
```

Success: All models run, tests pass, snapshot exists
