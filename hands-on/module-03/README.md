# Module 03 Labs - Seeds & Testing Basics

**Prerequisites:** Module 02 completed

**Duration:** ~90 minutes

**Instructor Note:** Demonstrate how seeds provide reference data and how tests validate data quality.

---

## Lab 1: Load CSV Seed (20 min)

**Objective**: Create and load product categories seed

**Concept: Seeds**

Seeds are CSV files in your dbt project that get loaded as tables. Used for:
- Small reference/lookup data (categories, mappings, etc.)
- Data versioned in git alongside code
- Quick loading with `dbt seed` command

Not for large datasets—use sources instead.

### Tasks

1. Create `~/olist_dbt_project/seeds/product_categories.csv` in VSCode:

```csv
category_id,category_name,category_description
1,books,Printed and digital books
2,electronics,Electronic devices and accessories
3,home,Home and kitchen items
4,fashion,Clothing and apparel
5,toys,Toys and games
6,beauty,Beauty and personal care
7,sports,Sports and fitness
```

2. Run seed:

```bash
dbt seed
```

6. Open Snowflake worksheet

7. Verify table

```sql
SELECT *
FROM product_categories;
```

**Expected result:** 7 rows

8. Count records

```sql
SELECT COUNT(*) FROM product_categories;
```

**Expected:** COUNT = 7

### Success

product_categories table exists with all rows

---

## Lab 2: Use Seed in Models (25 min)

**Objective**: Join seed data with staging models

**Concept: Referencing Seeds**

Reference seeds using `{{ ref('seed_name') }}` just like models. Seeds become tables in your warehouse that you can join with other models.

### Tasks

1. Open `~/olist_dbt_project/models/staging/sources.yml` in VSCode and add products table to the existing sources configuration:

```yaml
      - name: products
        identifier: products
```

2. Create `~/olist_dbt_project/models/staging/stg_products.sql` in VSCode:

```sql
WITH source_products AS (
    SELECT
        product_id,
        product_category_name,
        product_name_length,
        product_description_length,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    FROM {{ source('olist_raw', 'products') }}
),

categories AS (
    SELECT
        category_id,
        category_name
    FROM {{ ref('product_categories') }}
),

final AS (
    SELECT
        p.product_id,
        p.product_category_name,
        c.category_name AS category_name,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM source_products p
    LEFT JOIN categories c
        ON p.product_category_name = c.category_name
)

SELECT *
FROM final;
```

3. Create `~/olist_dbt_project/models/marts/products_with_categories.sql` in VSCode:

```sql
SELECT
    product_id,
    product_category_name,
    category_name,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM {{ ref('stg_products') }};
```

4. Run models

```bash
dbt run --select +products_with_categories
```

6. Verify in Snowflake

```sql
SELECT *
FROM products_with_categories
LIMIT 20;
```

### Success

Products enriched with category_name column

---

## Lab 3: Apply Built-in Tests (30 min)

**Objective**: Add tests to models using schema.yml

**Concept: dbt Tests**

Tests validate data quality. Two types:
- **Generic tests**: Built-in (not_null, unique, relationships, accepted_values)
- **Singular tests**: Custom SQL queries (covered in Lab 4)

Tests defined in schema.yml files. Run with `dbt test`.

### Tasks

1. Create `~/olist_dbt_project/models/staging/schema.yml` in VSCode:

```yaml
version: 2

models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - not_null
          - unique

  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - not_null
          - unique

      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id

      - name: order_status
        tests:
          - not_null
          - accepted_values:
              values: ['delivered', 'shipped', 'processing', 'canceled']
```

**Note:** The 'unavailable' status is intentionally excluded from this list. This will cause the test to WARN, which is a teaching example of how tests can catch unexpected data values.

2. Run staging tests

```bash
dbt test --select staging
```

3. Observe test execution

```bash
dbt test --select stg_customers
```

4. Rerun all staging tests

```bash
dbt test --select stg_orders
```

### Success

All tests pass, 6+ tests executed

---

## Lab 4: Write Custom Test (25 min)

**Objective**: Create singular test for business logic

**Concept: Singular Tests**

Custom SQL queries stored in `tests/` directory. A test passes if it returns zero rows.

Use for:
- Complex business rules
- Multi-table validations
- Logic not covered by generic tests

### Tasks

1. Create `~/olist_dbt_project/tests/assert_positive_order_totals.sql` in VSCode:

```sql
WITH order_totals AS (
    SELECT
        oi.order_id,
        SUM(oi.price + oi.freight_value) AS order_total
    FROM {{ ref('stg_order_items') }} oi
    GROUP BY oi.order_id
)

SELECT
    order_id,
    order_total
FROM order_totals
WHERE order_total <= 0;
```

2. Run custom test

```bash
dbt test --select assert_positive_order_totals
```

**Expected output:**
```
14:30:00 | 1 of 1 START test assert_positive_order_totals .................... [RUN]
14:30:01 | 1 of 1 PASS assert_positive_order_totals ....................... [PASS in 0.8s]
```

### Success

✅ Custom test executes successfully
✅ Test passes (returns 0 rows - no negative order totals found)

---

## Lab 5: Run All Tests (10 min)

**Objective**: Execute complete test suite and interpret results

### Tasks

1. Run all tests

```bash
dbt test
```

**Expected output:**
```
14:30:00 | Running with dbt=1.9.2
14:30:00 | Found 9 models, 9 tests, 1 seed, 1 snapshot, 5 sources
14:30:00 | 
14:30:00 | Concurrency: 4 threads
14:30:00 | 
14:30:00 | 1 of 9 START test not_null_stg_customers_customer_id ............ [RUN]
14:30:00 | 2 of 9 START test unique_stg_customers_customer_id .............. [RUN]
14:30:00 | 3 of 9 START test not_null_stg_orders_order_id .................. [RUN]
14:30:00 | 4 of 9 START test unique_stg_orders_order_id .................... [RUN]
14:30:01 | 1 of 9 PASS not_null_stg_customers_customer_id .................. [PASS in 0.8s]
14:30:01 | 2 of 9 PASS unique_stg_customers_customer_id .................... [PASS in 0.8s]
14:30:01 | 3 of 9 PASS not_null_stg_orders_order_id ........................ [PASS in 0.9s]
14:30:01 | 4 of 9 PASS unique_stg_orders_order_id .......................... [PASS in 0.9s]
14:30:01 | 5 of 9 START test not_null_stg_orders_customer_id ............... [RUN]
14:30:01 | 6 of 9 START test relationships_stg_orders_customer_id .......... [RUN]
14:30:02 | 5 of 9 PASS not_null_stg_orders_customer_id ..................... [PASS in 0.7s]
14:30:02 | 6 of 9 PASS relationships_stg_orders_customer_id ................ [PASS in 0.8s]
14:30:02 | 7 of 9 START test not_null_stg_orders_order_status .............. [RUN]
14:30:02 | 8 of 9 START test accepted_values_stg_orders_order_status ....... [RUN]
14:30:03 | 7 of 9 PASS not_null_stg_orders_order_status .................... [PASS in 0.6s]
14:30:03 | 8 of 9 WARN accepted_values_stg_orders_order_status ............. [WARN 1 in 0.7s]
14:30:03 | 9 of 9 START test assert_positive_order_totals .................. [RUN]
14:30:04 | 9 of 9 PASS assert_positive_order_totals ........................ [PASS in 0.8s]
14:30:04 | 
14:30:04 | Finished running 9 tests in 4.2s
14:30:04 | 
14:30:04 | Completed with 1 warning:
14:30:04 | 
14:30:04 | Warning in test accepted_values_stg_orders_order_status (models/staging/schema.yml)
14:30:04 |   Got 1 result, configured to warn if != 0
14:30:04 | 
14:30:04 | Done. PASS=8 WARN=1 ERROR=0 SKIP=0 TOTAL=9
```

2. View test results breakdown

- **8 PASS**: Data quality checks passed
- **1 WARN**: Found 'unavailable' status not in accepted_values list (intentional teaching example)
- **0 ERROR**: No critical failures

### Success

✅ 9 tests executed
✅ 8 tests passed
✅ 1 test warned (expected - demonstrates test failure behavior)
✅ Test suite validates data quality

---

## Module 03 Summary

### What You Built

**Seeds (1):**
- product_categories.csv (7 rows of reference data)

**Staging Models (5):**
- stg_customers
- stg_orders
- stg_order_items
- stg_payments
- stg_products (new - joins with seed)

**Marts (3):**
- fct_orders
- fct_sales
- products_with_categories (new - uses seed data)

**Tests (9 total):**
- **Generic tests (8):**
  - not_null tests: 4
  - unique tests: 2
  - relationships test: 1
  - accepted_values test: 1 (with intentional warning)
  
- **Singular tests (1):**
  - assert_positive_order_totals (custom business logic)

### Key Concepts Mastered

1. **Seeds**: Load reference data from CSV files
2. **Generic Tests**: Built-in data quality validations
3. **Singular Tests**: Custom SQL test queries
4. **Test Interpretation**: Understanding PASS/WARN/ERROR results
5. **Data Quality**: Establishing validation rules for data pipelines

### Commands Learned

```bash
dbt seed                              # Load CSV files as tables
dbt seed --full-refresh               # Reload seeds from scratch
dbt test                              # Run all tests
dbt test --select <model_name>        # Test specific model
dbt test --select <test_name>         # Run specific test
dbt run --select +<model_name>        # Run model and upstream dependencies
```

### Test Results Interpretation

- **PASS**: Test passed - no issues found
- **WARN**: Test found issues but configured to warn (severity: warn)
- **ERROR**: Test failed - critical issues found (severity: error)
- **SKIP**: Test was skipped (e.g., disabled)

### Next Steps

Module 04 will cover:
- Snapshots for slowly changing dimensions (SCD Type 2)
- Integration testing with `dbt build`
- Full pipeline validation
- Working with historical data
