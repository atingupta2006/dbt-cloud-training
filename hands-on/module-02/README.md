# Module 02 Labs — Building Models & Sources

---

## Lab 1 — Staging Models with ref() (25 min)

**Objective**: Build staging models and downstream model using ref().

### Tasks

1. Create staging directory

```bash
mkdir -p models/staging
```

2. Create staging models

```bash
touch models/staging/stg_customers.sql
touch models/staging/stg_orders.sql
touch models/staging/stg_order_items.sql
```

3. Edit stg_customers.sql

```sql
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM RAW.customers
```

4. Edit stg_orders.sql

```sql
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
FROM RAW.orders
```

5. Edit stg_order_items.sql

```sql
SELECT
    order_id,
    product_id,
    price,
    freight_value
FROM RAW.order_items
```

6. Create marts directory

```bash
mkdir -p models/marts
```

7. Create downstream model

```bash
touch models/marts/fct_orders.sql
```

8. Edit fct_orders.sql

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

9. Run models

```bash
dbt run
```

### Success

Logs show staging models run before fct_orders

---

## Lab 2 — Build Incremental Fact Table (35 min)

**Objective**: Create fct_sales incremental model.

### Tasks

1. Create model

```bash
touch models/marts/fct_sales.sql
```

2. Edit fct_sales.sql

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

3. Run first time

```bash
dbt run --select fct_sales
```

4. Insert one new row into RAW.orders (in Snowflake)

5. Run again

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

## Lab 3 — Declare Sources in YAML (20 min)

**Objective**: Configure sources and switch staging models to source().

### Tasks

1. Create file

```bash
touch models/staging/sources.yml
```

2. Edit sources.yml

```yaml
version: 2

sources:
  - name: olist_raw
    database: TRAINING_DB
    schema: RAW
    tables:
      - name: customers
      - name: orders
      - name: order_items
      - name: products
      - name: payments
```

3. Update stg_customers.sql

```sql
FROM {{ source('olist_raw','customers') }}
```

4. Update stg_orders.sql

```sql
FROM {{ source('olist_raw','orders') }}
```

5. Update stg_order_items.sql

```sql
FROM {{ source('olist_raw','order_items') }}
```

6. Run staging only

```bash
dbt run --select staging
```

7. Inspect compiled SQL

```bash
ls target/compiled
```

### Success

Compiled SQL shows source() resolved

---

## Lab 4 — Configure and Run Source Freshness (20 min)

**Objective**: Add freshness configuration and run checks.

### Tasks

1. Edit models/staging/sources.yml

```yaml
sources:
  - name: olist_raw
    database: TRAINING_DB
    schema: RAW
    freshness:
      warn_after:
        count: 12
        period: hour
      error_after:
        count: 24
        period: hour
    tables:
      - name: orders
        loaded_at_field: order_purchase_timestamp
      - name: customers
        loaded_at_field: customer_id
      - name: order_items
        loaded_at_field: order_id
```

2. Run freshness

```bash
dbt source freshness
```

### Success

Freshness output shows PASS/WARN per table
