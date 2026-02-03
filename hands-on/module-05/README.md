# Module 05 – Development Workflow & Selection Syntax

**Prerequisites:** Module 04 completed

**Duration:** ~90 minutes

**Instructor Note:** This module focuses on dbt workflow commands and model selection patterns. Students practice targeted execution and understand the DAG.

---

## Lab 1: Core Workflow Commands (30 min)

**Objective:** Execute core dbt commands and observe dependency behavior

### Overview

dbt provides several commands for different workflows:
- `dbt run`: Execute models (create tables/views)
- `dbt test`: Run data quality tests
- `dbt build`: Run models, tests, snapshots, seeds in DAG order
- `dbt compile`: Compile Jinja to SQL without running
- `dbt snapshot`: Execute snapshots only

### Tasks

#### 1. Run a single staging model

```bash
dbt run --select stg_customers
```

**Expected output:**
```
Completed successfully
Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

**What happened:** Only `stg_customers` view was created/updated

#### 2. Run model with all downstream dependencies

```bash
dbt run --select stg_customers+
```

**Expected output:**
- Runs `stg_customers` and all models that depend on it (downstream), e.g. `fct_orders`.
- Syntax: `model_name+` = model + all downstream

#### 3. Run model with all upstream dependencies

```bash
dbt run --select +fct_orders
```

**Expected output:**
- Runs all models that `fct_orders` depends on (upstream), plus `fct_orders` itself. E.g. `stg_customers`, `stg_orders`, then `fct_orders`.
- Syntax: `+model_name` = all upstream + model

#### 4. Test a single model

```bash
dbt test --select stg_orders
```

**Expected output:**
- Runs all tests configured for `stg_orders` (not_null, unique, relationships, accepted_values)

#### 5. Build entire project

```bash
dbt build
```

**Expected output:**
```
Completed with 1 warning
Done. PASS=19 WARN=1 ERROR=0 SKIP=0 TOTAL=20
```

**What happened:** 
- Loaded seed (product_categories)
- Ran all models in dependency order
- Executed snapshots
- Ran all tests

#### 6. Build only staging directory

```bash
dbt build --select staging
```

**Expected output:**
- Runs all models in the `staging` directory and their tests only.

### Success Criteria

- ✅ Single model execution works
- ✅ Dependency operators (+, +model) execute correctly
- ✅ `dbt build` runs full pipeline
- ✅ Understand execution order from logs

---

## Lab 2: Selection Syntax Patterns (25 min)

**Objective:** Practice model selectors and exclusion

### Overview

Selection syntax patterns:
- **Path selector:** `staging` or `marts` (directory name)
- **Wildcard:** `stg_*` (matches pattern)
- **Exclusion:** `--exclude model_name`
- **Graph operators:** `+model`, `model+`, `+model+`

### Tasks

#### 1. Run all staging models using path selector

```bash
dbt run --select staging
```

**Expected output:**
- Runs all 5 staging models:
	- stg_customers
	- stg_orders
	- stg_order_items
	- stg_payments
	- stg_products

#### 2. Run all marts models

```bash
dbt run --select marts
```

**Expected output:**
- Runs all 3 mart models:
	- fct_orders
	- fct_sales
	- products_with_categories

#### 3. Exclude specific model

```bash
dbt run --select marts --exclude fct_orders
```

**Expected output:**
- Runs only:
	- fct_sales
	- products_with_categories

**Why:** Skip expensive models during development

#### 4. Run snapshots only

```bash
dbt snapshot
```

**Expected output:**
- Executes `customers_snapshot` only

#### 5. Build staging with tests

```bash
dbt build --select staging
```

**Expected output:**
- Runs all 5 staging models and their 9 associated tests

### Success Criteria

- ✅ Path selectors work (staging, marts)
- ✅ Exclusion filters out models
- ✅ Different resource types can be targeted
- ✅ Build includes both models and tests

---

## Lab 3: Graph Operators & Wildcards (20 min)

**Objective:** Use advanced selection patterns

### Tasks

#### 1. Run model with all downstream (+ suffix)

```bash
dbt run --select stg_orders+
```

**Expected output:**
- Runs `stg_orders` and all downstream models:
	- fct_orders
	- fct_sales

**Why:** Both `fct_orders` and `fct_sales` depend on `stg_orders`

#### 2. Run model with all upstream (+ prefix)

```bash
dbt run --select +fct_sales
```

**Expected output:**
- Runs all upstream models and `fct_sales`:
	- stg_orders
	- stg_order_items
	- fct_sales

**Why:** `fct_sales` depends on those staging models

#### 3. Run model with 1 degree upstream

```bash
dbt run --select 1+fct_orders
```

**Expected output:**
- Runs only 1 degree upstream models and `fct_orders`:
	- stg_customers
	- stg_orders
	- fct_orders
- Syntax: `N+model` = N degrees of upstream ancestors

#### 4. Wildcard selector (all staging models)

```bash
dbt run --select stg_*
```

**Expected output:**
- Runs all models starting with `stg_`

#### 5. Combine selectors

```bash
dbt run --select stg_customers+ --exclude fct_sales
```

**Expected output:**
- Runs `stg_customers` and all downstream models except `fct_sales`:
	- stg_customers
	- fct_orders

### Success Criteria

- ✅ Graph operators work (+ prefix, suffix, degree)
- ✅ Wildcards match patterns
- ✅ Multiple selectors can be combined
- ✅ Understand DAG execution order

---

## Lab 4: Compile & Utility Commands (15 min)

**Objective:** Use dbt utility commands for debugging

### Tasks

#### 1. Compile models without running

```bash
dbt compile
```

**Expected output:**
- Generates SQL files in `target/compiled/` folder

**Why:** Review generated SQL before execution

#### 2. Inspect compiled SQL

Open file:
```bash
cat target/compiled/olist_dbt_project/models/marts/fct_orders.sql
```
**What to see:**
- Jinja rendered to plain SQL with {{ ref() }} resolved to actual table names

#### 3. Parse project (validate syntax)

```bash
dbt parse
```

**Expected output:**
- Creates `target/manifest.json` with project metadata

**Why:** Validate Jinja/YAML syntax without running models

#### 4. List models based on selection

```bash
dbt list --select +fct_orders
```

**Expected output:**
- Lists all resources that would be run with the selection, e.g.:
	- source:olist_dbt_project.olist_raw.customers
	- source:olist_dbt_project.olist_raw.orders
	- olist_dbt_project.stg_customers
	- olist_dbt_project.stg_orders
	- olist_dbt_project.fct_orders

**Why:** Preview what would run with a selection

#### 5. Show model information

```bash
dbt list --select fct_orders --output json
```

**Expected output:**
- JSON with model metadata (path, materialization, dependencies)

### Success Criteria

- ✅ `dbt compile` generates SQL without running
- ✅ Compiled SQL shows resolved references
- ✅ `dbt parse` validates syntax
- ✅ `dbt list` previews selections

---

## Module 05 Summary

### What You Practiced

**Workflow Commands:**
- `dbt run` - Execute models
- `dbt test` - Run tests
- `dbt build` - Run everything in DAG order
- `dbt compile` - Generate SQL
- `dbt parse` - Validate syntax
- `dbt snapshot` - Run snapshots
- `dbt list` - Preview selections

**Selection Syntax:**
- `--select model_name` - Single model
- `--select +model_name` - Upstream + model
- `--select model_name+` - Model + downstream
- `--select N+model_name` - N degrees upstream
- `--select path/` - Directory
- `--select pattern*` - Wildcard
- `--exclude model_name` - Exclude from selection

**Key Concepts:**
1. **DAG (Directed Acyclic Graph):** Dependencies determine execution order
2. **Graph Operators:** Navigate upstream (+) and downstream (+)
3. **Path Selectors:** Target entire directories
4. **Exclusion:** Skip specific models
5. **Compilation:** Preview SQL before execution

### Commands Reference

```bash
# Single model
dbt run --select stg_customers

# With dependencies
dbt run --select +fct_orders          # upstream + model
dbt run --select stg_customers+       # model + downstream
dbt run --select +fct_orders+         # upstream + model + downstream

# Directory
dbt run --select staging              # all in staging/
dbt run --select marts                # all in marts/

# Wildcards
dbt run --select stg_*                # all starting with stg_
dbt run --select *orders*             # all containing 'orders'

# Exclusion
dbt run --select marts --exclude fct_sales

# Combinations
dbt run --select stg_customers+ --exclude fct_sales

# Utilities
dbt compile                           # Generate SQL
dbt parse                             # Validate syntax
dbt list --select +fct_orders         # Preview selection
dbt build                             # Run everything
```

### Project Structure After Module 05

```
models/
├── staging/
│   ├── stg_customers.sql (view)
│   ├── stg_orders.sql (view)
│   ├── stg_order_items.sql (view)
│   ├── stg_payments.sql (view)
│   ├── stg_products.sql (view)
│   ├── sources.yml
│   └── schema.yml (9 tests)
├── marts/
│   ├── fct_orders.sql (table)
│   ├── fct_sales.sql (incremental)
│   └── products_with_categories.sql (view)
seeds/
└── product_categories.csv (7 rows)
snapshots/
└── customers_snapshot.sql (SCD Type 2)
tests/
└── assert_positive_order_totals.sql (custom test)
```

### Next Steps

Module 06 will cover:
- Debugging with `dbt debug`
- Variables and Jinja templating
- Creating reusable macros
- Advanced Jinja patterns
