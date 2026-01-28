# Organizing Project Folders

This file explains how to structure models so the project stays readable as it grows.

Poor organization causes confusion, slow reviews, and broken pipelines.

---

## Why Organization Matters

* Models grow quickly
* Teams grow
* Logic becomes complex

Structure prevents chaos.

---

## The Layered Approach

Most production projects use layers:

* staging
* intermediate
* marts

Each layer has a clear purpose.

---

## Staging Layer

Purpose:

* Mirror raw tables
* Clean column names
* Cast data types

Rules:

* One staging model per source table
* No joins

Example:

```
models/staging/stg_orders.sql
models/staging/stg_customers.sql
```

---

## Intermediate Layer

Purpose:

* Join staging models
* Apply business rules

Example:

```
models/intermediate/int_orders_enriched.sql
```

---

## Marts Layer

Purpose:

* Final tables
* Facts and dimensions

Example:

```
models/marts/fct_orders.sql
models/marts/dim_customers.sql
```

---

## Basic Folder Tree

```
models/
├── staging/
├── intermediate/
└── marts/
```

---

## Organizing by Business Domain

```
models/
├── staging/
│   ├── sales/
│   └── marketing/
├── intermediate/
│   ├── sales/
│   └── marketing/
└── marts/
    ├── sales/
    └── marketing/
```

---

## Organizing by Source System

```
models/staging/olist/
models/staging/shopify/
```

---

## Naming Conventions

* stg_ for staging
* int_ for intermediate
* fct_ for facts
* dim_ for dimensions

Use snake_case.

---

## YAML Per Folder

Example:

```
models/staging/schema.yml
```

```yaml
version: 2
models:
  - name: stg_orders
    description: Clean orders data
```

---

## Configure Schemas in dbt_project.yml

```yaml
models:
  training_project:
    staging:
      +schema: staging
    intermediate:
      +schema: intermediate
    marts:
      +schema: marts
```

---

## Migration Path

Projects often start flat and evolve:

```
models/orders.sql → models/staging/stg_orders.sql
```

---

## Best Practices

* Keep staging models thin
* Put business logic in intermediate layer
* Place final metrics in marts layer

---
