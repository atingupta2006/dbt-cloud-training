# Module 02 Labs — Building Models & Sources

**Prerequisites:** Module 01 completed

**Duration:** ~80 minutes

**Instructor Note:** Walk through each lab step-by-step. Ensure students create all staging models before proceeding to marts.

---

## Lab 1 — Staging Models with ref() (25 min)

**Objective**: Build staging models and downstream model using ref().

### Tasks

1. Create staging directory

```bash
mkdir -p ~/olist_dbt_project/models/staging
```

2. Create sources.yml file

```bash
cat > ~/olist_dbt_project/models/staging/sources.yml << 'EOF'
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
EOF
```

**Note:** The database name (OLIST_DB) is inherited from your `profiles.yml` configuration.

3. Create staging models

```bash
touch ~/olist_dbt_project/models/staging/stg_customers.sql
touch ~/olist_dbt_project/models/staging/stg_orders.sql
touch ~/olist_dbt_project/models/staging/stg_order_items.sql
touch ~/olist_dbt_project/models/staging/stg_payments.sql
```

4. Edit stg_customers.sql

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

9. Create downstream model

```bash
touch ~/olist_dbt_project/models/marts/fct_orders.sql
```

10. Edit fct_orders.sql

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

### Tasks

1. Create model

```bash
touch ~/olist_dbt_project/models/marts/fct_sales.sql
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
        freight_value,
        CONCAT(order_id, '-', product_id) AS order_item_id
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

## Lab 3 — Source Freshness Configuration (20 min)

**Objective**: Add freshness checks to existing sources.

### Tasks

1. Edit ~/olist_dbt_project/models/staging/sources.yml

```bash
nano ~/olist_dbt_project/models/staging/sources.yml
```

2. Replace entire file with freshness configuration:

```yaml
version: 2

sources:
  - name: olist_raw
    schema: RAW
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

3. Run staging models

```bash
dbt run --select staging
```

4. Inspect compiled SQL

```bash
ls ~/olist_dbt_project/target/compiled
```

### Success

Compiled SQL shows source() resolved correctly

3. Update stg_customers.sql to use source function

```bash
nano ~/olist_dbt_project/models/staging/stg_customers.sql
```

Replace FROM clause with:

```sql
FROM {{ source('olist_raw','customers') }}
```

4. Update stg_orders.sql

```bash
nano ~/olist_dbt_project/models/staging/stg_orders.sql
```

Replace FROM clause with:

```sql
FROM {{ source('olist_raw','orders') }}
```

5. Update stg_order_items.sql

```bash
nano ~/olist_dbt_project/models/staging/stg_order_items.sql
```

Replace FROM clause with:

```sql
FROM {{ source('olist_raw','order_items') }}
```

3. Run staging only

```bash
dbt run --select staging
```

4. Inspect compiled SQL

```bash
ls target/compiled
```

### Success

Compiled SQL shows source() resolved

---

## Lab 4 — Configure and Run Source Freshness (20 min)

**Objective**: Add freshness configuration and run checks.

### Tasks

1. Edit ~/olist_dbt_project/models/staging/sources.yml

```bash
nano ~/olist_dbt_project/models/staging/sources.yml
```

Replace content with:

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
      - name: orders
        identifier: orders
        loaded_at_field: order_purchase_timestamp
      - name: customers
        identifier: customers
        loaded_at_field: customer_id
      - name: order_items
        identifier: order_items
        loaded_at_field: order_id
```

2. Run freshness

```bash
dbt source freshness
```

### Success

Freshness output shows PASS/WARN per table
