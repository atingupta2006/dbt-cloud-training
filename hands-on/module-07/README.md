# Module 07 – Documentation & Hooks

**Prerequisites:** Module 06 completed

**Duration:** ~90 minutes

**Instructor Note:** This module teaches how to generate and serve dbt documentation, add descriptions to models/columns, and use hooks for automation.

---

## Lab 1: Generate and Serve Documentation (25 min)

**Objective:** Generate interactive documentation website and explore DAG

### Overview

`dbt docs generate` creates documentation:
- Model descriptions and columns
- Data lineage (DAG visualization)
- Source freshness checks
- Test results
- Compiled SQL

`dbt docs serve` launches local web server to view docs.

### Tasks


### Task 1: Generate documentation

```bash
dbt docs generate
```

**Expected output:**
```
Building catalog
Catalog written to target/catalog.json
```

**What happened:**
- Created `target/manifest.json` (project metadata)
- Created `target/catalog.json` (database schema)
- Created `target/index.html` (docs website)


### Task 2: Serve documentation locally

```bash
dbt docs serve
```

**Expected output:**
```
Serving docs at 8080
To access from your browser, navigate to: http://localhost:8080
```

**Note:** Server runs in foreground. Open browser to `http://localhost:8080`


### Task 3: Explore documentation website

Navigate through:
- **Project Overview:** Summary of models, sources, tests
- **Database Tab:** Browse schemas and tables
- **DAG Tab:** Visual lineage graph

Click on `fct_orders`:
- View model SQL
- See upstream dependencies (stg_customers, stg_orders, stg_order_items, stg_payments)
- See downstream consumers (none yet)
- View column list


### Task 4: Explore DAG (Directed Acyclic Graph)

Click **DAG** tab or click graph icon next to model name.

**What to observe:**
- Sources (blue boxes) → Staging models (green) → Marts (purple)
- Arrows show data flow direction
- Seeds appear as yellow boxes
- Click nodes to highlight dependencies


### Task 5: Stop documentation server

Press `Ctrl+C` in terminal to stop server.

### Success Criteria

- ✅ Documentation generated successfully
- ✅ Website accessible on localhost:8080
- ✅ DAG shows model relationships
- ✅ Can navigate between models

---

## Lab 2: Add Model & Column Descriptions (35 min)

**Objective:** Document models and columns with descriptions

### Overview

Documentation uses `description` property in `schema.yml` files.

Best practices:
- Describe business logic and purpose
- Document column definitions
- Note data quality rules
- Explain transformations

### Tasks


### Task 1: Document staging models

Update `~/olist_dbt_project/models/staging/schema.yml`:

```yaml
version: 2

models:
  - name: stg_customers
    description: Staging table for customer dimension. One row per customer with location data.
    columns:
      - name: customer_id
        description: Primary key for customers
        tests:
          - not_null
          - unique

      - name: customer_city
        description: City where customer is located

      - name: customer_state
        description: Two-letter state code where customer is located

  - name: stg_orders
    description: Staging table for orders fact. One row per order with status and timestamps.
    columns:
      - name: order_id
        description: Primary key for orders
        tests:
          - not_null
          - unique

      - name: customer_id
        description: Foreign key to stg_customers
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id

      - name: order_status
        description: Current status of the order (delivered, shipped, processing, canceled, unavailable)
        tests:
          - not_null
          - accepted_values:
              values: ['delivered', 'shipped', 'processing', 'canceled']

      - name: order_purchase_timestamp
        description: Timestamp when order was placed by customer
```


### Task 2: Document marts models

Create or update `~/olist_dbt_project/models/marts/schema.yml`:

```yaml
version: 2

models:
  - name: fct_orders
    description: |
      Order fact table with aggregated metrics.
      
      One row per order with calculated totals from order items and payments.
      Includes customer context for analysis.
    columns:
      - name: order_id
        description: Primary key - unique order identifier

      - name: customer_id
        description: Foreign key to customer dimension

      - name: order_status
        description: Current order status

      - name: order_purchase_timestamp
        description: When customer placed the order

      - name: total_order_value
        description: Sum of all item prices for this order (excludes freight)

      - name: total_freight_value
        description: Sum of all freight charges for this order

      - name: total_payment_value
        description: Total amount paid for this order

  - name: fct_sales
    description: |
      Incremental sales fact table at order item level.
      
      Processes only new orders on each run using incremental strategy.
      Use --full-refresh flag to rebuild entire table.
    columns:
      - name: order_item_id
        description: Unique identifier for this order line item (surrogate key)

      - name: order_id
        description: Order this item belongs to

      - name: customer_id
        description: Customer who placed the order

      - name: order_purchase_timestamp
        description: When order was placed

      - name: price
        description: Item price (excludes freight)

      - name: freight_value
        description: Shipping cost for this item

  - name: products_with_categories
    description: |
      Product dimension enriched with category names.
      
      Joins staging products with seed data to provide category descriptions.
    columns:
      - name: product_id
        description: Primary key for products

      - name: product_category_name
        description: Raw category name from source system

      - name: category_name
        description: Enriched category name from seed data

      - name: product_weight_g
        description: Product weight in grams

  - name: payment_filter
    description: Filtered payment transactions based on project variable payment_methods
    columns:
      - name: order_id
        description: Order identifier
        tests:
          - not_null

      - name: payment_type
        description: Payment method used (filtered by var payment_methods)
        tests:
          - accepted_values:
              values: "{{ get_payment_methods() }}"

      - name: payment_value
        description: Payment amount in cents
```


### Task 3: Document sources

Update `~/olist_dbt_project/models/staging/sources.yml` to add descriptions (keep existing freshness, identifier, and loaded_at_field):

```yaml
version: 2

sources:
  - name: olist_raw
    description: Raw data from Brazilian ecommerce platform Olist
    schema: RAW
    freshness:
      warn_after:
        count: 12
        period: hour
      error_after:
        count: 24
        period: hour
    tables:
      - name: customers
        description: Customer master data with location information
        identifier: customers
        loaded_at_field: customer_id
        columns:
          - name: customer_id
            description: Unique customer identifier

      - name: orders
        description: Order header records with status and timestamps
        identifier: orders
        loaded_at_field: order_purchase_timestamp
        columns:
          - name: order_id
            description: Unique order identifier

      - name: order_items
        description: Line items for each order with pricing
        identifier: order_items
        loaded_at_field: order_id
        columns:
          - name: order_id
            description: Order this item belongs to

      - name: products
        description: Product master data with dimensions
        identifier: products
        columns:
          - name: product_id
            description: Unique product identifier

      - name: payments
        description: Payment transactions for orders
        identifier: payments
        columns:
          - name: order_id
            description: Order this payment applies to
```


### Task 4: Regenerate documentation

```bash
dbt docs generate
```


### Task 5: Serve and review

```bash
dbt docs serve
```


Open browser and navigate to:
- `fct_orders` model - see full description
- Click columns - see column descriptions
- Navigate to sources - see source descriptions

### Success Criteria

- ✅ All models have descriptions
- ✅ Key columns documented
- ✅ Descriptions appear in docs website
- ✅ Source tables documented

---

## Lab 3: Pre-Hooks and Post-Hooks (30 min)

**Objective:** Use hooks to run SQL before/after model execution

### Overview

Hooks run SQL at specific times:
- **pre-hook**: Before model builds
- **post-hook**: After model builds

Common uses:
- Grant permissions
- Log metadata
- Create indexes
- Clean up temp tables
- Validate row counts

### Tasks


### Task 1: Add post-hook to grant permissions

Update `~/olist_dbt_project/dbt_project.yml`:

```yaml
models:
  olist_dbt_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
      +post-hook:
        - "GRANT SELECT ON {{ this }} TO ROLE ACCOUNTADMIN"
```

**What this does:** Grants SELECT permission to ACCOUNTADMIN after each marts table is created


### Task 2: Run model to test hook

```bash
dbt run --select fct_orders
```

**Expected output (in logs):**
```
Running 1 post-hook for model olist_dbt_project.fct_orders
GRANT SELECT ON OLIST_DB.ANALYTICS.FCT_ORDERS TO ROLE ACCOUNTADMIN
```


### Task 3: Add model-specific pre-hook

**Step 1:** Create log table in Snowflake:

```sql
USE DATABASE OLIST_DB;
USE SCHEMA ANALYTICS;

CREATE TABLE IF NOT EXISTS model_run_log (
    model_name VARCHAR,
    run_timestamp TIMESTAMP
);

-- Grant permissions
GRANT SELECT ON TABLE OLIST_DB.ANALYTICS.model_run_log TO ROLE DBT_ROLE;
GRANT INSERT ON TABLE OLIST_DB.ANALYTICS.model_run_log TO ROLE DBT_ROLE;
```


**Step 2:** Create `~/olist_dbt_project/models/marts/fct_orders_with_log.sql`:

```sql
{{ config(
    materialized='table',
    pre_hook="INSERT INTO {{ target.schema }}.model_run_log (model_name, run_timestamp) VALUES ('{{ this.name }}', CURRENT_TIMESTAMP())",
    post_hook="GRANT SELECT ON {{ this }} TO ROLE ACCOUNTADMIN"
) }}

-- Same SQL as fct_orders
WITH orders AS (
    SELECT *
    FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT *
    FROM {{ ref('stg_customers') }}
),

order_items AS (
    SELECT *
    FROM {{ ref('stg_order_items') }}
),

payments AS (
    SELECT *
    FROM {{ ref('stg_payments') }}
),

order_totals AS (
    SELECT
        oi.order_id,
        SUM(oi.price) AS total_order_value,
        SUM(oi.freight_value) AS total_freight_value
    FROM order_items oi
    GROUP BY oi.order_id
),

payment_totals AS (
    SELECT
        p.order_id,
        SUM(p.payment_value) AS total_payment_value
    FROM payments p
    GROUP BY p.order_id
),

final AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.customer_city,
        c.customer_state,
        o.order_status,
        o.order_purchase_timestamp,
        ot.total_order_value,
        ot.total_freight_value,
        pt.total_payment_value
    FROM orders o
    LEFT JOIN customers c
        ON o.customer_id = c.customer_id
    LEFT JOIN order_totals ot
        ON o.order_id = ot.order_id
    LEFT JOIN payment_totals pt
        ON o.order_id = pt.order_id
)

SELECT * FROM final
```


### Task 4: Run model with hooks

```bash
dbt run --select fct_orders_with_log
```

**Expected output:**
- Pre-hook inserts log entry
- Model builds
- Post-hook grants permission


### Task 5: Verify log table

Run in Snowflake:

```sql
SELECT * FROM OLIST_DB.ANALYTICS.model_run_log;
```

**Expected output:**
- Row with model name and timestamp

### Success Criteria

- ✅ Post-hook grants executed after marts models
- ✅ Pre-hook logs model execution
- ✅ Log table populated with run metadata
- ✅ Understand hook execution order

---

## Module 07 Summary

### What You Practiced

**Documentation:**
- `dbt docs generate` - Build documentation artifacts
- `dbt docs serve` - Launch documentation website
- Model descriptions in schema.yml
- Column descriptions
- Source documentation
- DAG visualization

**Hooks:**
- Project-level post-hooks in dbt_project.yml
- Model-specific pre-hooks and post-hooks
- Using `{{ this }}` to reference current model
- GRANT statements for permissions
- Logging and auditing patterns

### Key Concepts

1. **Documentation as Code:** Descriptions in schema.yml files alongside models
2. **DAG Visualization:** Interactive graph showing model dependencies
3. **Hooks:** SQL that runs automatically before/after model builds
4. **Artifacts:** manifest.json (metadata), catalog.json (schema), index.html (website)

### Commands Learned

```bash
# Documentation
dbt docs generate              # Build documentation artifacts
dbt docs serve                 # Launch docs website on localhost:8080
dbt docs serve --port 8081     # Use different port

# Regenerate after changes
dbt docs generate              # Rebuild after adding descriptions
```

### Project Structure After Module 07

```
models/
├── staging/
│   ├── schema.yml              # Updated with descriptions
│   └── sources.yml             # Updated with descriptions
└── marts/
    ├── schema.yml              # New file with model/column docs
    ├── fct_orders_with_log.sql # New model with hooks
    └── [other models from Module 06]

dbt_project.yml                 # Updated with post-hook
target/
├── manifest.json               # Project metadata
├── catalog.json                # Database schema info
└── index.html                  # Documentation website
```

### Hook Configuration Levels

1. **Project-level** (dbt_project.yml):
   ```yaml
   models:
     project_name:
       marts:
         +post-hook: "SQL here"
   ```

2. **Directory-level** (dbt_project.yml):
   ```yaml
   models:
     project_name:
       marts:
         finance:
           +pre-hook: "SQL here"
   ```

3. **Model-level** (in .sql file):
   ```sql
   {{ config(
       pre_hook="SQL here",
       post_hook=["SQL 1", "SQL 2"]
   ) }}
   ```

### Hook Execution Order

```
1. pre-hook runs
2. Model SQL executes (CREATE/INSERT)
3. post-hook runs
```

### Best Practices

**Documentation:**
- Document all public models (marts layer)
- Explain complex transformations and business logic
- Keep docs updated with model changes
- Use `|` for multi-line descriptions

**Hooks:**
- Post-hooks: Permissions, indexes, grants
- Pre-hooks: Setup tasks, temp tables
- Keep hooks simple; complex logic belongs in models
- Test in dev before production

### Next Steps

Module 08 will cover:
- Multiple environments (dev, staging, prod)
- Target context ({{ target.name }})
- Environment-specific configurations
- dbt Cloud overview and comparison
