# Why dbt Exists

## The Problem with Traditional Data Pipelines

Most legacy data pipelines were built around ETL:

* Extract data from source systems
* Transform data in a separate processing layer
* Load transformed data into a warehouse

Typical tools:

* Informatica
* Talend
* SSIS
* Custom Python jobs
* Spark / PySpark

These systems share the same structural problems.

---

## Pain #1 – Transformations Outside the Warehouse

In ETL, transformations happen before data reaches the warehouse.

That means:

* Business logic lives in external tools
* Warehouse only stores final outputs
* Raw data is often lost

Consequences:

* Hard to debug
* Hard to change
* Hard to audit

If a number looks wrong:

* You must inspect multiple tools
* Logs are scattered
* SQL cannot show you lineage

---

## Pain #2 – Black Box Transformations

Many ETL tools store logic in:

* GUIs
* XML
* Proprietary formats

You cannot:

* Code review properly
* Use git effectively
* Run transformations locally

Version control becomes weak.

---

## Pain #3 – Slow Change Cycles

Adding a new column often requires:

* Modify ETL job
* Redeploy pipeline
* Wait for scheduler

Even simple changes become slow.

---

## Pain #4 – Scaling Cost

Traditional systems scale compute and storage together.

When transformations grow:

* You buy bigger clusters
* Costs explode

---

## The Modern ELT Approach

ELT flips the model:

* Extract
* Load
* Transform

Raw data is loaded first.

Transformations run **inside the warehouse** using SQL.

---

## Why This Matters

Modern warehouses (Snowflake, BigQuery, Redshift) provide:

* Massive parallelism
* Cheap storage
* Separation of compute and storage

SQL engines are extremely powerful.

We should use them.

---

## What dbt Is

dbt stands for:

**data build tool**

In practice:

* A SQL transformation framework
* A compiler
* A runner
* A dependency manager

You write SELECT statements.

dbt turns them into tables and views in your warehouse.

---

## What dbt Is NOT

❌ Not an orchestrator
❌ Not an ingestion tool
❌ Not a streaming engine
❌ Not a warehouse

It sits in the transformation layer only.

---

## Core Idea

Each model is a SELECT statement.

Example:

```sql
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp
FROM raw.orders
```

Saved as a file.

dbt builds it as a table or view.

---

## How dbt Works

You write SQL files in `models/` directory.

dbt compiles them into DDL statements like:

```sql
CREATE OR REPLACE VIEW analytics.stg_orders AS ...
```

---

## dbt vs Traditional ETL Tools

| Area               | Traditional ETL   | dbt        |
| ------------------ | ----------------- | ---------- |
| Language           | GUI / Proprietary | SQL        |
| Version Control    | Weak              | Git-native |
| Execution Location | External Engine   | Warehouse  |
| Testing            | Limited           | Built-in   |
| Lineage            | Manual            | Automatic  |

---

## dbt vs PySpark

| Area           | PySpark          | dbt                |
| -------------- | ---------------- | ------------------ |
| Language       | Python           | SQL                |
| Runtime        | Spark Cluster    | Warehouse          |
| Learning Curve | High             | Low                |
| Best For       | Heavy processing | Analytics modeling |

---

## When PySpark Makes Sense

* Unstructured data
* Complex ML feature engineering
* Heavy text processing

---

## When dbt Makes Sense

* Analytics models
* Reporting tables
* Business metrics
* Dimensional models

Most analytics transformations belong in dbt.

---

## Key dbt Features

* Model dependencies
* Incremental models
* Tests
* Documentation
* Snapshots
* Macros
* Environment separation

You will learn these gradually.

---

## Why SQL-First Matters

* Everyone on analytics team knows SQL
* Easier hiring
* Easier reviews
* Easier debugging

---

## Why dbt Became Popular

* Cloud warehouses became powerful
* Git became standard
* Analytics engineering emerged

---

## Mental Model

Think of dbt as a **Makefile for SQL**:

* Files describe transformations
* dbt figures out order
* dbt runs them

---

## Summary

* dbt transforms data using SQL inside the warehouse
* It's not an orchestrator, ingestion tool, or warehouse
* Each model is a SELECT statement compiled into tables/views
* dbt handles dependencies automatically
* Provides testing, documentation, and lineage out of the box

---
