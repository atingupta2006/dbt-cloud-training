# 03 — Incremental Models

## Objective

Create models that load only new or changed data.
Use incremental materialization correctly on Snowflake.

---

## What Is an Incremental Model

An incremental model builds a table once.
Subsequent runs insert or merge only new rows.

Avoids full table rebuild.

---

## Why Incremental Models

* Fact tables grow continuously
* Full rebuilds become slow
* Warehouse cost increases

Incremental solves this.

---

## When To Use

Use incremental when:

* Table exceeds millions of rows
* Data arrives over time
* Rows have a stable key

Do not use for:

* Small dimensions
* Static lookup tables

---

## Basic Structure

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

First run → full load
Next runs → incremental

---

## is_incremental() Macro

is_incremental() returns true only during incremental runs.

---

### Pattern

```sql
WHERE order_purchase_timestamp > (
    SELECT MAX(order_purchase_timestamp)
    FROM {{ this }}
)
```

Guarded by:

```sql
{% if is_incremental() %}
WHERE ...
{% endif %}
```

---

## Complete Example

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
FROM {{ ref('stg_orders') }}

{% if is_incremental() %}
WHERE order_purchase_timestamp > (
    SELECT MAX(order_purchase_timestamp)
    FROM {{ this }}
)
{% endif %}
```

---

## Full Refresh

Forces complete rebuild using `--full-refresh` flag.

---

## unique_key

unique_key identifies a row.

Examples:

```yaml
unique_key: order_id
```

Composite key:

```yaml
unique_key: ['order_id','product_id']
```

---

## Snowflake Incremental Strategies

| Strategy         | Description           |
| ---------------- | --------------------- |
| merge            | Default upsert        |
| append           | Only inserts          |
| delete+insert    | Replace matching keys |
| insert_overwrite | Partition replace     |

---

## Setting Strategy

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_id'
) }}
```

---

## Append vs Upsert

**Append** - Only inserts new rows:
```sql
incremental_strategy='append'
```

**Upsert (Merge)** - Updates existing rows, inserts new:
```sql
incremental_strategy='merge', unique_key='order_id'
```

Use merge when rows can change over time.

---

## Best Practices

* Always define `unique_key` for merge strategies
* Keep filter logic simple
* Use staging models as source
* Test incremental logic thoroughly

---
