# 02 — Materializations Overview

## Objective

Understand dbt materialization types and choose the correct one per model.
Control how dbt builds tables in Snowflake.

---

## What Are Materializations

Materialization defines **how a model is persisted** in the warehouse.

Configured per model using:

```sql
{{ config(materialized='view') }}
```

If not specified, dbt uses **view**.

---

## Four Core Materializations

| Type        | Persisted Object | Rebuilt On Run        | Typical Usage                   |
| ----------- | ---------------- | --------------------- | ------------------------------- |
| view        | View             | Every query           | Staging, lightweight transforms |
| table       | Table            | Every run             | Small marts, dimensions         |
| incremental | Table            | Only new/changed rows | Large facts                     |
| ephemeral   | None             | Inlined as CTE        | Helper logic                    |

---

## View Materialization

### Behavior

* Creates Snowflake view
* SQL executed at query time
* No storage cost

### Configure

```sql
{{ config(materialized='view') }}

SELECT
    order_id,
    customer_id,
    order_status
FROM {{ ref('stg_orders') }}
```

### When To Use

* Staging models
* Simple column cleanup
* Renaming

### Pros / Cons

| Pros       | Cons                   |
| ---------- | ---------------------- |
| Fast build | Query-time cost        |
| No storage | Can be slow downstream |

---

## Table Materialization

### Behavior

* Creates physical table
* Fully rebuilt each run

### Configure

```sql
{{ config(materialized='table') }}

SELECT
    customer_id,
    customer_city,
    customer_state
FROM {{ ref('stg_customers') }}
```

### When To Use

* Dimensions
* Small marts

### Pros / Cons

| Pros            | Cons           |
| --------------- | -------------- |
| Fast queries    | Full rebuild   |
| Stable snapshot | Higher compute |

---

## Incremental Materialization

### Behavior

* Creates table
* Inserts or merges only new rows

### Configure

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

SELECT
    order_id,
    customer_id,
    order_purchase_timestamp
FROM {{ ref('stg_orders') }}
```

### When To Use

* Fact tables
* Large row counts

### Pros / Cons

| Pros        | Cons       |
| ----------- | ---------- |
| Fast reruns | More logic |
| Scales well | Needs keys |

---

## Ephemeral Materialization

### Behavior

* No table or view created in database
* SQL is compiled and inlined as CTE in downstream models
* Exists only during compilation, never materialized

### Configure In Model

```sql
{{ config(materialized='ephemeral') }}

SELECT
    order_id,
    payment_value,
    payment_value / 100.0 AS payment_value_dollars
FROM {{ ref('stg_payments') }}
```

### Configure In dbt_project.yml

To set ephemeral for entire folder:

```yaml
models:
  training_project:
    staging:
      helpers:
        +materialized: ephemeral
```

### How To Reference Ephemeral Models

Reference ephemeral models exactly like any other model using `ref()`:

```sql
{{ config(materialized='table') }}

-- This will inline the ephemeral model's SQL as a CTE
SELECT
    order_id,
    payment_value_dollars
FROM {{ ref('payment_helper') }}  -- payment_helper is ephemeral
WHERE payment_value_dollars > 100
```

**Compiled Result:**
```sql
WITH payment_helper AS (
    SELECT
        order_id,
        payment_value,
        payment_value / 100.0 AS payment_value_dollars
    FROM ANALYTICS.STG_PAYMENTS
)
SELECT
    order_id,
    payment_value_dollars
FROM payment_helper
WHERE payment_value_dollars > 100
```

### When To Use

* Small reusable transformations
* Helper calculations used by multiple models
* Intermediate logic that doesn't need to be queryable
* DRY (Don't Repeat Yourself) principle for shared logic

### When NOT To Use

* Large datasets (repeated computation cost)
* Models you need to query directly
* Complex transformations (hard to debug)
* Logic used by many downstream models (compile time increases)

### Pros / Cons

| Pros                          | Cons                                |
| ----------------------------- | ----------------------------------- |
| No storage cost               | Harder to debug (no table to query) |
| Faster builds (no DDL)        | Repeated computation in each model  |
| Cleaner warehouse (no clutter)| Cannot query directly               |
| Modular reusable logic        | Increases compile time              |

---

## Comparison Summary

| Use Case    | Recommended |
| ----------- | ----------- |
| Raw cleanup | view        |
| Dimensions  | table       |
| Large facts | incremental |
| Helpers     | ephemeral   |

---

## Setting Materialization Per Folder

In `dbt_project.yml`:

```yaml
models:
  training_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

Individual models can override with `{{ config(materialized='...') }}`.

---

## Performance Considerations

* **Views** - Push cost to query time, no storage cost
* **Tables** - Push cost to build time, faster queries
* **Incremental** - Shifts cost to first run, efficient for ongoing updates

---

## Typical Pattern

* staging → view
* dimensions → table
* facts → incremental

---
