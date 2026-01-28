# Hands-On Labs Validation Summary

## Project Name Changes

✅ **Changed**: `my_project` → `olist_dbt_project` throughout all modules

## Key Fixes Applied

### Module 01 - DBT Setup & Project Structure

**Fixed:**
- Virtual environment path: `~/.venv`
- Project name in profiles.yml: `olist_dbt_project`
- Project initialization: `dbt init olist_dbt_project`
- All file paths use `~/olist_dbt_project/...`
- Source reference: `source('olist_raw', 'customers')` (consistent)

**Validation Checklist:**
- [x] Profile name matches project name
- [x] All paths use home directory (~)
- [x] Source references use 'olist_raw' consistently
- [x] dbt_project.yml model config uses correct project name

### Module 02 - Building Models & Sources

**Fixed:**
- All paths: `~/olist_dbt_project/...`
- Removed hardcoded `RAW.tablename` → now uses `source('olist_raw', 'tablename')`
- Added `order_item_id` generation for incremental unique_key
- Fixed sources.yml path to use home directory
- Added proper file editing commands (nano/vi) instead of just showing code

**Validation Checklist:**
- [x] No hardcoded table references (RAW.table)
- [x] All source() calls use 'olist_raw'
- [x] fct_sales has proper unique_key with order_item_id
- [x] sources.yml declares TRAINING_DB.RAW
- [x] Lab 3 includes proper file editing steps

### Module 03 - Seeds & Testing

**Fixed:**
- All paths: `~/olist_dbt_project/...`
- Changed `cd ~/my_project` → `cd ~/olist_dbt_project`
- Source reference in stg_products: `source('olist_raw', 'products')`
- Test directory: `~/olist_dbt_project/tests/`
- Simplified Lab 4 test scenario (removed confusing vi edit step)

**Validation Checklist:**
- [x] Seeds created in correct directory
- [x] All source references consistent
- [x] Custom test in ~/olist_dbt_project/tests/
- [x] Test execution commands work from any directory

### Module 04 - Snapshots & Integration

**Fixed:**
- All paths: `~/olist_dbt_project/...`
- Snapshot sources: `source('olist_raw', ...)` (was 'raw')
- sources.yml: database=TRAINING_DB, schema=RAW, source_name=olist_raw
- All staging/intermediate/marts file paths use home directory
- Consistent source references throughout

**Validation Checklist:**
- [x] Snapshot uses olist_raw source
- [x] Integration lab has complete file paths
- [x] All model files reference olist_raw consistently
- [x] Directory structure properly created

### Module 05 - Development Workflow

**Fixed:**
- All paths: `~/olist_dbt_project/...`
- venv activation: `~/.venv/bin/activate`
- Source references: `source('olist_raw', ...)`
- All vi commands use full home directory paths

**Validation Checklist:**
- [x] Model selection commands work correctly
- [x] Tag example uses proper file path
- [x] Refactoring lab uses consistent source names
- [x] All dependencies reference correct models

### Module 06 - Debugging & Macros

**Fixed:**
- All paths: `~/olist_dbt_project/...`
- Model references: `ref('stg_payments')` instead of `ref('payments')`
- Model references: `ref('stg_orders')` instead of `ref('orders')`
- All macro files in `~/olist_dbt_project/macros/`
- All model files in `~/olist_dbt_project/models/`

**Validation Checklist:**
- [x] dbt debug references correct profile
- [x] Variables example works with proper refs
- [x] Macros created in correct directory
- [x] All ref() calls use staging models (stg_*)

## Naming Conventions Applied

### Project Structure
```
~/
├── .venv/                          # Python virtual environment
├── .dbt/
│   └── profiles.yml               # Profile: olist_dbt_project
└── olist_dbt_project/             # DBT project
    ├── dbt_project.yml            # Project name: olist_dbt_project
    ├── models/
    │   ├── sources.yml            # Source: olist_raw
    │   ├── staging/
    │   │   ├── sources.yml
    │   │   ├── schema.yml
    │   │   ├── stg_customers.sql
    │   │   ├── stg_orders.sql
    │   │   ├── stg_order_items.sql
    │   │   ├── stg_products.sql
    │   │   └── stg_payments.sql
    │   ├── intermediate/
    │   │   ├── int_orders_enriched.sql
    │   │   └── int_customer_orders.sql
    │   └── marts/
    │       ├── dim_customers.sql
    │       ├── dim_products.sql
    │       ├── dim_date.sql
    │       ├── fct_orders.sql
    │       └── fct_sales.sql
    ├── macros/
    │   ├── generate_alias.sql
    │   ├── cents_to_dollars.sql
    │   ├── get_payment_methods.sql
    │   └── date_spine.sql
    ├── seeds/
    │   └── product_categories.csv
    ├── snapshots/
    │   └── customers_snapshot.sql
    └── tests/
        └── assert_positive_order_totals.sql
```

### Naming Standards

**Source Name**: `olist_raw`
- Database: `TRAINING_DB`
- Schema: `RAW`
- Usage: `{{ source('olist_raw', 'customers') }}`

**Staging Models**: `stg_<table_name>`
- Examples: `stg_customers`, `stg_orders`, `stg_payments`
- Materialized: `view`

**Intermediate Models**: `int_<description>`
- Examples: `int_orders_enriched`, `int_customer_orders`
- Materialized: `ephemeral`

**Dimension Tables**: `dim_<entity>`
- Examples: `dim_customers`, `dim_products`, `dim_date`
- Materialized: `table`

**Fact Tables**: `fct_<entity>`
- Examples: `fct_orders`, `fct_sales`
- Materialized: `table` or `incremental`

## Student Workflow Validation

### Setup (Module 01)
```bash
# 1. Create virtual environment
python3 -m venv ~/.venv

# 2. Activate (works from any directory)
source ~/.venv/bin/activate

# 3. Install dbt
pip install dbt-core==1.9.8 dbt-snowflake==1.9.8

# 4. Configure profile
nano ~/.dbt/profiles.yml
# Profile name: olist_dbt_project

# 5. Initialize project
dbt init olist_dbt_project

# 6. Navigate to project
cd ~/olist_dbt_project

# 7. Test connection
dbt debug
```

### Daily Usage
```bash
# Activate environment (from anywhere)
source ~/.venv/bin/activate

# Navigate to project (from anywhere)
cd ~/olist_dbt_project

# Run commands
dbt run
dbt test
dbt build
```

### Key Benefits of Using ~
✅ Commands work from any directory
✅ No confusion about relative vs absolute paths
✅ Consistent across all students' machines
✅ Easy to copy-paste commands
✅ Resilient to directory navigation errors

## Issues Fixed

### Consistency Issues
- ❌ Mixed use of `my_project` and generic references
- ✅ Now consistently uses `olist_dbt_project`
- ❌ Inconsistent source names ('raw', 'olist', 'olist_raw')
- ✅ Now consistently uses `olist_raw`
- ❌ Mixed ref() to raw vs staging models
- ✅ Now always refs staging models (stg_*)

### Path Issues
- ❌ Relative paths that break when not in project dir
- ✅ Now uses `~` for all paths
- ❌ Missing home directory references
- ✅ All paths start with `~/`

### Data Reference Issues
- ❌ Hardcoded `FROM RAW.tablename`
- ✅ Now uses `{{ source('olist_raw', 'tablename') }}`
- ❌ Missing unique_key in incremental models
- ✅ Added proper order_item_id generation

### Lab Instructions
- ❌ Missing file editing commands
- ✅ Added nano/vi commands where needed
- ❌ Confusing test scenarios
- ✅ Simplified and clarified test examples

## Pre-Flight Check

Before running labs, ensure:
1. ✅ Snowflake account accessible
2. ✅ TRAINING_DB.RAW schema contains olist tables
3. ✅ Environment variables set (SNOWFLAKE_*)
4. ✅ Python 3.8+ installed
5. ✅ Students understand ~ means home directory

## Expected Success Criteria

Each module's commands should execute without modification when:
- Student is in any directory (thanks to ~)
- Virtual environment is activated
- Snowflake credentials are set
- Source data exists in TRAINING_DB.RAW

All `dbt run`, `dbt test`, `dbt build` commands should complete successfully with green output.
