# Module 03 – Seeds & Testing Basics

**Duration:** 4 hours (Sessions 5–6)

---

## Lab 1: Load CSV Seed (20 min)

**Why:** Seeds let you version-control small reference datasets (lookups, mappings) directly in your dbt project. They load as tables with `dbt seed` — no Snowflake file uploads required.

### Steps

1. Create `seeds/product_categories.csv` in VSCode:

```csv
category_id,category_name,category_description
1,livros_interesse_geral,General interest books
2,informatica_acessorios,Computer accessories
3,utilidades_domesticas,Household utilities
4,cool_stuff,Cool and unique items
5,brinquedos,Toys and games
6,beleza_saude,Beauty and health
7,esporte_lazer,Sports and leisure
```

2. Load the seed:

```bash
dbt seed
```

3. Verify in Snowflake Web UI → Worksheets:

```sql
SELECT * FROM product_categories;
```

Expected: 7 rows.

---

## Lab 2: Use Seed in Models (25 min)

**Why:** Seeds are referenced with `ref()` just like models. This lets you enrich raw data with lookup values maintained in version control.

### Steps

1. Create `models/staging/stg_products.sql` in VSCode:

```sql
SELECT
    product_id,
    product_category_name,
    product_name_lenght,
    product_description_lenght,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM {{ source('olist_raw', 'products') }}
```

> Note: `product_name_lenght` is a typo in the source data — we keep it as-is in staging.

2. Create `models/marts/products_with_categories.sql`:

```sql
SELECT
    p.product_id,
    p.product_category_name,
    c.category_name,
    p.product_weight_g,
    p.product_length_cm
FROM {{ ref('stg_products') }} p
LEFT JOIN {{ ref('product_categories') }} c
    ON p.product_category_name = c.category_name
```

3. Run the chain:

```bash
dbt run --select +products_with_categories
```

4. Verify in Snowflake Web UI:

```sql
SELECT * FROM products_with_categories LIMIT 10;
```

---

## Lab 3: Apply Built-in Tests (30 min)

**Why:** Tests are data quality gates that run automatically. They catch duplicates, nulls, broken foreign keys, and unexpected values before bad data reaches your marts.

### Steps

1. Create `models/staging/schema.yml` in VSCode:

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

> The `accepted_values` test intentionally lists only 4 of 8 actual order statuses — it will WARN, showing unexpected values like 'unavailable', 'invoiced', 'created', and 'approved'.

2. Run all tests:

```bash
dbt test
```

Expected: 7 PASS, 1 WARN (the accepted_values test finds statuses not in the list).

---

## Lab 4: Write Custom Test (25 min)

**Why:** Generic tests cover common patterns, but business rules require custom SQL. A singular test passes when it returns zero rows — any returned row is a violation.

### Steps

1. Create `tests/assert_positive_order_totals.sql` in VSCode:

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
WHERE order_total <= 0
```

2. Run the custom test:

```bash
dbt test --select assert_positive_order_totals
```

Expected: PASS (no orders with zero or negative totals).

3. Run full test suite to confirm everything together:

```bash
dbt test
```
