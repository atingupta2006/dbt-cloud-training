# 01 — ref() Function

## Objective

Use ref() to build model dependencies and allow dbt to control execution order.
Replace hard-coded table names with ref() calls.

---

## What is ref()

ref() is a dbt function used inside SQL models to reference another dbt model.

Instead of writing:

```sql
FROM analytics.stg_orders
```

You write:

```sql
FROM {{ ref('stg_orders') }}
```

ref() resolves to the correct database.schema.table at runtime.

dbt also records this relationship and builds a dependency graph.

---

## Why ref() Exists

Hard-coded table names create problems:

* Execution order must be managed manually
* Renaming models breaks downstream SQL
* No DAG
* No lineage

ref() solves all of these.

---

## Example: Staging Model

```sql
-- models/staging/stg_customers.sql
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM {{ source('olist_raw', 'customers') }}
```

---

## Example: Using ref() in Downstream Model

```sql
-- models/marts/dim_customers.sql
SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
FROM {{ ref('stg_customers') }}
```

---

## DAG Created Automatically

```
stg_customers
      |
      v
dim_customers
```

No ordering flags required.

---

## Multiple ref() Calls in One Model

```sql
-- models/marts/fct_orders.sql
SELECT
    o.order_id,
    o.customer_id,
    c.customer_city,
    o.order_status
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('stg_customers') }} c
    ON o.customer_id = c.customer_id
```

---

## DAG with Multiple Dependencies

```
stg_customers      stg_orders
        \            /
         \          /
          v        v
           fct_orders
```

---

## ref() Resolves Physical Names

During execution, dbt expands:

```sql
{{ ref('stg_orders') }}
```

Into something like:

```sql
training_db.dbt_atin.stg_orders
```

Students never hard-code these names.

---

## Rename Safety

When you rename a model file, only update the ref() call. No other changes needed.

---

## Missing Model Error

If you reference a non-existent model:

```sql
FROM {{ ref('unknown_model') }}
```

dbt fails at compilation with "Model not found" error.

---

## ref() Inside CTEs

```sql
WITH payments AS (
    SELECT order_id, payment_value
    FROM {{ ref('stg_payments') }}
),
orders AS (
    SELECT order_id, order_status
    FROM {{ ref('stg_orders') }}
)
SELECT o.order_id, o.order_status, p.payment_value
FROM orders o
LEFT JOIN payments p ON o.order_id = p.order_id
```

---

## ref() vs Hard-Coded Names

| Item                  | Hard-coded Table | ref() |
| --------------------- | ---------------- | ----- |
| Renaming safe         | No               | Yes   |
| DAG built             | No               | Yes   |
| Environment aware     | No               | Yes   |
| Dependency validation | No               | Yes   |

---

## When NOT to Use ref()

* Raw CSV files
* External tables
* Tables not managed by dbt

Those use `source()` instead.

---

## Summary

* ref() links dbt models together
* ref() builds the dependency graph automatically
* ref() resolves to physical table names at runtime
* Every inter-model dependency must use ref()

---
