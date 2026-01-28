# 05 — Sources

## Objective

Declare raw tables as dbt sources and reference them using source().

---

## What Are Sources

Sources represent upstream data not built by dbt.

Examples:

* Raw CSV tables
* Ingested warehouse tables

In this course: Olist raw tables.

---

## Why Declare Sources

* Central metadata
* Lineage
* Testing
* Freshness

---

## Source YAML File

Declare sources in `models/sources.yml`:

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
```

---

## Referencing Sources

```sql
SELECT customer_id, customer_city
FROM {{ source('olist_raw','customers') }}
```

Syntax: `{{ source('source_name','table_name') }}`

---

## source() vs ref()

| Item       | source() | ref() |
| ---------- | -------- | ----- |
| Raw data   | Yes      | No    |
| dbt models | No       | Yes   |
| DAG node   | Yes      | Yes   |

---

## Multiple Sources

You can declare multiple source systems:

```yaml
sources:
  - name: olist_raw
    schema: RAW
  - name: external_sales
    schema: EXT
```

---

## Database and Schema

If `database` is omitted, dbt uses the target database.

Explicit specification is recommended for clarity.

---

## Summary

* Staging models should always use `source()` instead of hard-coded table names
* Sources provide lineage, documentation, and testing capabilities
* Central metadata makes raw data dependencies explicit

---
