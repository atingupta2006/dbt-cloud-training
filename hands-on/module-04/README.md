# Module 04 – Snapshots & Integration

**Prerequisites:** Module 03 completed

**Duration:** ~90 minutes

**Instructor Note:** This module introduces snapshots for slowly changing dimensions (SCD Type 2) and demonstrates full pipeline integration testing.

---

## Lab 1: Create Customer Snapshot (45 min)

**Objective:** Track customer dimension changes over time using SCD Type 2

### Overview

Snapshots in dbt capture historical changes to dimension tables. We'll use the **check strategy** to monitor specific columns for changes.

### Tasks

#### 1. Create `~/olist_dbt_project/snapshots/customers_snapshot.sql` in VSCode:

```sql
{% snapshot customers_snapshot %}

{{
    config(
      target_schema='SNAPSHOTS',
      unique_key='customer_id',
      strategy='check',
      check_cols=['customer_city', 'customer_state', 'customer_zip_code_prefix']
    )
}}

SELECT *
FROM {{ source('olist_raw', 'customers') }}

{% endsnapshot %}
```

**Configuration explained:**
- `target_schema='SNAPSHOTS'`: Where snapshot table will be created
- `unique_key='customer_id'`: Primary key for tracking records
- `strategy='check'`: Monitor specific columns for changes
- `check_cols=[...]`: Columns to monitor - snapshot triggers when these change

#### 4. Run initial snapshot (baseline)

```bash
dbt snapshot
```

**Expected output:**
```
Completed successfully
Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

This creates the snapshot table with all current customer records and adds these dbt columns:
- `dbt_valid_from`: When this version became active
- `dbt_valid_to`: When this version expired (NULL = current)
- `dbt_scd_id`: Unique identifier for this version

#### 5. Verify initial snapshot

Query in Snowflake:

```sql
-- Check row count
SELECT COUNT(*) FROM OLIST_DB.SNAPSHOTS.customers_snapshot;

-- View sample records
SELECT 
    customer_id,
    customer_city,
    customer_state,
    dbt_valid_from,
    dbt_valid_to
FROM OLIST_DB.SNAPSHOTS.customers_snapshot
LIMIT 10;
```

**Expected:** All records have `dbt_valid_to = NULL` (all current)

#### 6. Update a customer record

In Snowflake, update one customer to test change tracking:

```sql
UPDATE OLIST_DB.RAW.customers
SET customer_city = 'SNAPSHOT_TEST_CITY_XYZ',
    customer_state = 'ZZ'
WHERE customer_id = (
    SELECT customer_id 
    FROM OLIST_DB.RAW.customers 
    LIMIT 1
);
```

Verify the update:

```sql
SELECT customer_id, customer_city, customer_state
FROM OLIST_DB.RAW.customers 
WHERE customer_city = 'SNAPSHOT_TEST_CITY_XYZ';
```

**Expected:** 1 row with updated city and state

#### 7. Run snapshot again to capture change

```bash
dbt snapshot
```

**Expected output:**
```
Completed successfully
Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

#### 8. Query snapshot to see SCD Type 2 history

```sql
SELECT 
    customer_id,
    customer_city,
    customer_state,
    dbt_valid_from,
    dbt_valid_to,
    dbt_scd_id
FROM OLIST_DB.SNAPSHOTS.customers_snapshot
WHERE customer_city = 'SNAPSHOT_TEST_CITY_XYZ' 
   OR customer_id = (
       SELECT customer_id 
       FROM OLIST_DB.RAW.customers 
       WHERE customer_city = 'SNAPSHOT_TEST_CITY_XYZ'
   )
ORDER BY customer_id, dbt_valid_from;
```

**Expected:** 2 rows for the same customer_id
- **Row 1 (Old version):** Original city/state, `dbt_valid_to` = timestamp (expired)
- **Row 2 (New version):** Updated city/state, `dbt_valid_to` = NULL (current)

### Success Criteria

 - ✅ Snapshot table exists in SNAPSHOTS schema
 - ✅ Initial snapshot contains all customer records
 - ✅ After update, snapshot shows 2 versions for modified customer
 - ✅ Old version has `dbt_valid_to` timestamp
 - ✅ New version has `dbt_valid_to` = NULL

---

## Lab 2: Integration Testing (45 min)

**Objective:** Test the complete end-to-end pipeline built across Modules 01-04

### Overview

The `dbt build` command runs everything in dependency order:
1. Seeds (CSV files)
2. Models (staging → marts)
3. Snapshots
4. Tests

### Current Project Architecture

From Modules 01-03, you have:

```
OLIST_DB.RAW (source)
    ↓
Seeds (product_categories.csv)
    ↓
Staging Models (5 views)
├── stg_customers
├── stg_orders  
├── stg_order_items
├── stg_payments
└── stg_products
    ↓
Mart Models (3 models)
├── fct_orders (table)
├── fct_sales (incremental table)
└── products_with_categories (view)
    ↓
Snapshots (1 snapshot)
└── customers_snapshot (SCD Type 2)
    ↓
Tests (9 tests + 1 custom test)
```

### Tasks

#### 1. Review the full pipeline

Check your project structure:

```bash
# View all models
ls models/staging/
ls models/marts/

# View seeds
ls seeds/

# View snapshots
ls snapshots/

# View tests
ls tests/
```

#### 2. Run complete integration test

Execute the full pipeline:

```bash
dbt build
```

**Expected output:**
```
Running with dbt=1.9.2
Found 9 models, 9 tests, 1 seed, 1 snapshot, 5 sources

Concurrency: 4 threads

14:30:00  1 of 20 START seed file OLIST_DB.RAW.product_categories ............. [RUN]
14:30:01  1 of 20 OK loaded seed file OLIST_DB.RAW.product_categories .......... [INSERT 7 in 1.2s]
14:30:01  2 of 20 START sql view model OLIST_DB.ANALYTICS.stg_customers ........ [RUN]
14:30:01  3 of 20 START sql view model OLIST_DB.ANALYTICS.stg_orders ........... [RUN]
...
14:30:15  20 of 20 PASS test assert_positive_order_totals ...................... [PASS in 0.5s]

Finished running 5 view models, 3 table models, 9 tests, 1 seed, 1 snapshot in 15.2s

Completed with 1 warning:

Warning in test accepted_values_stg_orders_order_status__delivered__shipped__canceled__processing (models/staging/schema.yml)
  Got 1 result, configured to warn if != 0

Done. PASS=19 WARN=1 ERROR=0 SKIP=0 TOTAL=20
```

**Note:** The 1 warning is intentional (from Module 03) - it's a teaching example of test failures.

#### 3. Verify objects in Snowflake

Check each schema:

```sql
-- RAW schema (source + seeds)
SHOW TABLES IN SCHEMA OLIST_DB.RAW;

-- ANALYTICS schema (models)
SHOW VIEWS IN SCHEMA OLIST_DB.ANALYTICS;
SHOW TABLES IN SCHEMA OLIST_DB.ANALYTICS;

-- SNAPSHOTS schema
SHOW TABLES IN SCHEMA OLIST_DB.SNAPSHOTS;
```

**Expected objects:**

**RAW:**
- customers (source table)
- orders (source table)
- order_items (source table)
- payments (source table)
- products (source table)
- product_categories (seed)

**ANALYTICS:**
- Views: stg_customers, stg_orders, stg_order_items, stg_payments, stg_products
- Tables: fct_orders, fct_sales
- View: products_with_categories

**SNAPSHOTS:**
- Table: customers_snapshot

#### 4. Test selection syntax (preview of Module 05)

Run specific parts of the pipeline:

```bash
# Run only staging models
dbt build --select staging.*

# Run a specific model and its downstream dependencies
dbt build --select stg_customers+

# Run only marts
dbt build --select marts.*

# Run only tests
dbt test

# Run tests for specific model
dbt test --select stg_orders
```

#### 5. View lineage graph

Generate documentation:

```bash
dbt docs generate
dbt docs serve
```

Navigate to the lineage graph and explore:
- Source → staging → mart dependencies
- Model details
- Test results

### Success Criteria

 - ✅ `dbt build` completes successfully (19 PASS, 1 WARN)
 - ✅ All schemas contain expected objects
 - ✅ Staging models created as views
 - ✅ Mart models created as tables/incremental tables
 - ✅ Snapshot table exists with historical data
 - ✅ Tests execute and report results
 - ✅ Selection syntax works for targeted runs

---

## Common Issues & Solutions

### Issue: "Insufficient privileges to operate on table 'CUSTOMERS_SNAPSHOT'"

**Cause:** DBT_ROLE lacks permissions on SNAPSHOTS schema

**Fix:** Run in Snowflake as ACCOUNTADMIN:

```sql
USE ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;
GRANT CREATE TABLE ON SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;
```

### Issue: Can't query snapshot table as ACCOUNTADMIN

**Cause:** DBT_ROLE owns the snapshot table; ACCOUNTADMIN doesn't have automatic access

**Fix:** Grant permissions to ACCOUNTADMIN:

```sql
USE ROLE ACCOUNTADMIN;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA OLIST_DB.SNAPSHOTS TO ROLE ACCOUNTADMIN;
```

### Issue: Snapshot doesn't detect changes

**Cause:** Check columns might not be configured correctly

**Verify:** Ensure `check_cols` includes columns that actually changed in your UPDATE

---

## Key Concepts Covered

1. **Snapshots**
   - SCD Type 2 implementation
   - Check strategy vs timestamp strategy
   - dbt snapshot metadata columns

2. **Integration Testing**
   - Full pipeline execution with `dbt build`
   - Dependency resolution (DAG)
   - End-to-end validation

3. **Pipeline Architecture**
   - Layered approach: source → staging → marts
   - Seeds for reference data
   - Tests for data quality

4. **Selection Syntax** (preview)
   - Targeting specific models
   - Upstream/downstream dependencies
   - Selective testing

---

## Next Steps

In Module 05, you'll learn:
- Advanced workflow commands
- Selection syntax patterns
- Tags and resource management
- Debugging techniques
