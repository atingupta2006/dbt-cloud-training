# Module 03 Labs - Seeds & Testing Basics

All labs are instructor-led. Run commands exactly as shown.

---

## Lab 1: Load CSV Seed (20 min)

Objective: Create and load product categories seed

1. Move to project root

```bash
cd <your_dbt_project>
```

2. Create seeds directory

```bash
mkdir -p seeds
```

3. Create seeds/product_categories.csv

```bash
cat > seeds/product_categories.csv << 'EOF'
category_id,category_name,category_description
1,books,Printed and digital books
2,electronics,Electronic devices and accessories
3,home,Home and kitchen items
4,fashion,Clothing and apparel
5,toys,Toys and games
EOF
```

4. Inspect file

```bash
cat seeds/product_categories.csv
```

5. Run seed

```bash
dbt seed
```

6. Open Snowflake worksheet

7. Verify table

```sql
SELECT *
FROM product_categories;
```

8. Append two more categories

```bash
cat >> seeds/product_categories.csv << 'EOF'
6,beauty,Beauty and personal care
7,sports,Sports and fitness
EOF
```

9. Rerun seed

```bash
dbt seed
```

10. Verify updated rows

```sql
SELECT COUNT(*)
FROM product_categories;
```

Success: product_categories table exists with all rows

---

## Lab 2: Use Seed in Models (25 min)

Objective: Join seed data with staging models

1. Open staging products model

```bash
vi models/staging/stg_products.sql
```

2. Replace file content

```sql
WITH source_products AS (
    SELECT
        product_id,
        product_category_name,
        product_name_lenght,
        product_description_lenght,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    FROM {{ source('olist', 'products') }}
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

3. Create marts directory

```bash
mkdir -p models/marts
```

4. Create marts/products_with_categories.sql

```bash
cat > models/marts/products_with_categories.sql << 'EOF'
SELECT
    product_id,
    product_category_name,
    category_name,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM {{ ref('stg_products') }};
EOF
```

5. Run models

```bash
dbt run --select +products_with_categories
```

6. Verify in Snowflake

```sql
SELECT *
FROM products_with_categories
LIMIT 20;
```

Success: Products enriched with category_name column

---

## Lab 3: Apply Built-in Tests (30 min)

Objective: Add tests to models using schema.yml

1. Create staging schema file

```bash
cat > models/staging/schema.yml << 'EOF'
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
              values: ['delivered','shipped','processing','canceled','unavailable']
EOF
```

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

Success: All tests pass, 6+ tests executed

---

## Lab 4: Write Custom Test (25 min)

Objective: Create singular test for business logic

1. Create tests directory

```bash
mkdir -p tests
```

2. Create tests/assert_positive_order_totals.sql

```bash
cat > tests/assert_positive_order_totals.sql << 'EOF'
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
EOF
```

3. Run custom test

```bash
dbt test --select assert_positive_order_totals
```

4. Introduce failing scenario (temporary)

```bash
vi seeds/product_categories.csv
```

5. Save file without changes and rerun test

```bash
dbt test --select assert_positive_order_totals
```

6. Restore original state

```bash
dbt seed
```

7. Rerun custom test

```bash
dbt test --select assert_positive_order_totals
```

Success: Custom test executes and validates business rule
