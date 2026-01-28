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

* No table or view created
* SQL inlined into downstream CTE

### Configure

```sql
{{ config(materialized='ephemeral') }}

SELECT
    order_id,
    payment_value
FROM {{ ref('stg_payments') }}
```

### When To Use

* Small reusable logic
* Helper calculations

### Pros / Cons

| Pros          | Cons             |
| ------------- | ---------------- |
| No storage    | Harder debugging |
| Faster builds | Repeated compute |

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
