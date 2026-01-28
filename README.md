# DBT Training Curriculum

**RJP INFOTEK Pvt Ltd** | [www.rjpinfotek.com](https://www.rjpinfotek.com)

**Duration:** 40 Hours + 4 Hours Assessment

---

## Repository Structure

This repository contains:

- **modules/** - 11 training modules with hands-on exercises
- **data/raw/** - Olist e-commerce dataset for exercises
- **references/** - Additional learning resources

**Training Approach:** Instructor-led demonstrations with guided hands-on practice.

---

## Prerequisites

- Working knowledge of SQL (joins, aggregations, CTEs)
- Basic Python knowledge (variables, functions)
- Familiarity with data warehousing (schemas, facts/dimensions)
- Basic Git usage (clone, commit, branch, push)

---

## 1. DBT Setup & Project Structure (Sessions 1–2, 4 Hours)

### Session 1 – Installing and Configuring DBT

**Concepts:**
- Why DBT (vs. traditional ETL/PySpark)
- DBT CLI vs DBT Cloud

**Hands-on:**
- Install DBT CLI, sign up for DBT Cloud
- Configure Snowflake connection using `profiles.yml`

**Outcome:** First `dbt run` connected to warehouse

### Session 2 – Understanding DBT Project Structure

**Concepts:**
- Anatomy of a project – `models/`, `tests/`, `seeds/`, `snapshots/`, `macros/`
- `dbt_project.yml` and its role

**Hands-on:**
- Create a new project in CLI and DBT Cloud
- Organize project folders for staging and marts

**Outcome:** Functional project skeleton with proper structure

---
## 2. Core DBT Concepts (Sessions 3–8, 12 Hours)

### Session 3 – Building Models

**Concepts:**
- Using `ref()` to define dependencies
- Materializations – table, view, incremental, ephemeral

**Hands-on:**
- Create staging model with `ref()`
- Build `fact_sales` as incremental model
- Building SQL transformations using `ref()`
### Session 4 – Sources

**Concepts:**
- Declaring upstream data as sources
- Testing and freshness checks

**Hands-on:**
- Configure sources in YAML
- Run freshness check for raw tables

### Session 5 – Seeds

**Concepts:**
- Role of seeds for reference data

**Hands-on:**
- Add a CSV seed (product lookup)
- Query and join seeded data with models
### Session 6 – Testing Basics

**Concepts:**
- Importance of testing in pipelines
- Built-in tests (unique, not_null, relationships)

**Hands-on:**
- Apply built-in tests to customer/order tables
- Write and run a simple custom test

### Session 7 – Snapshots

**Concepts:**
- Why snapshots (historical data tracking, SCD Type 2)

**Hands-on:**
- Create snapshot configuration
- Track changes in customer dimension
### Session 8 – Practice Lab on Core Concepts

**Hands-on:**
- Consolidation lab: Create sources, models, seeds, apply tests, implement a snapshot

**Outcome:** End-to-end small pipeline using all core features

---

## 3. DBT Workflow (Sessions 9–11, 6 Hours)
### Session 9 – Development Workflow

**Concepts:**
- `dbt run`, `dbt test`, `dbt build` – when to use each

**Hands-on:**
- Execute the run-test-build cycle

### Session 10 – Project Organization

**Concepts:**
- Layered approach – staging, intermediate, marts

**Hands-on:**
- Refactor existing models into layers

### Session 11 – Debugging and Configurations

**Concepts:**
- Using `dbt debug`
- Variables and configs in dbt

**Hands-on:**
- Debug broken model
- Implement variable to control schema

---
## 4. Advanced DBT Features (Sessions 12–15, 8 Hours)

### Session 12 – Macros & Jinja

**Concepts:**
- Introduction to Jinja templating
- Writing reusable macros
- Parameterization

**Hands-on:**
- Parameterize model logic with Jinja
- Create parameterized macro for standard joins
### Session 13 – Hooks & Operations

**Concepts:**
- Pre- and post-model hooks
- `dbt run-operation`

**Hands-on:**
- Implement a post-hook for auditing
- Run an operation to refresh schema

### Session 14 – Documentation & Lineage

**Concepts:**
- Documenting models
- Generating lineage graphs

**Hands-on:**
- Add documentation to models
- Generate docs site and explore lineage
### Session 15 – Environment Management

**Concepts:**
- Configuring dev/test/prod

**Hands-on:**
- Create multiple environments in DBT Cloud
- Demonstrate schema separation

---

## 5. Orchestration & Deployment (Sessions 16–18, 6 Hours)
### Session 16 – Running DBT Locally vs Cloud

**Concepts:**
- Differences between CLI and Cloud runs

**Hands-on:**
- Run project in both CLI and Cloud

### Session 17 – Scheduling Jobs in DBT Cloud

**Concepts:**
- Job scheduling basics

**Hands-on:**
- Create and schedule job for daily staging refresh

### Session 18 – Orchestration Integrations

**Concepts:**
- Options beyond DBT Cloud (Airflow, Prefect)

**Hands-on:**
- Demonstration of triggering DBT from Airflow
- Monitor jobs and set up notifications in Cloud

---
## 6. Review and Capstone (Sessions 19–20, 4 Hours)

### Session 19 – Review & Troubleshooting Lab

**Hands-on:**
- Debug broken model chains, test failures
- Apply fixes and rerun project

### Session 20 – Evaluation Lab (2.5 Hours + 1.5 Hours MCQ + 1-on-1 Viva)

**Evaluation Activities:**

Learners build a DBT project from scratch, covering major topics:

- Setup a new project
- Add sources, models, seeds
- Apply tests and snapshots
- Add macros and documentation
- Generate lineage site
- Deploy in DBT Cloud and schedule a job
- Present working pipeline at the end

---

*© RJP INFOTEK Pvt Ltd - All rights reserved*