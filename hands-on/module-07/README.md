# Module 07 – Hooks & Documentation

**Duration:** 4 hours (Sessions 13–14)

---

## Lab 1: Post-Hooks for Permissions (25 min)

**Why:** After dbt creates a table, other roles need SELECT access to query it. Post-hooks automate this — every time a marts model rebuilds, permissions are re-applied automatically.

### Steps

1. Add a post-hook to `dbt_project.yml` for all marts models:

```yaml
models:
  olist_dbt_project:
    staging:
      +materialized: view
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +post-hook:
        - "GRANT SELECT ON {{ this }} TO ROLE ACCOUNTADMIN"
```

2. Run a marts model:

```bash
dbt run --select fct_orders
```

Check the logs — you should see `GRANT SELECT ON ... TO ROLE ACCOUNTADMIN` executing after the model builds.

> In production, you would grant to a reporting or analyst role (e.g., `REPORTING_ROLE`). We use ACCOUNTADMIN here because it already exists in every Snowflake account.

3. Verify in Snowflake Web UI:

```sql
SHOW GRANTS ON TABLE OLIST_DB.ANALYTICS.FCT_ORDERS;
```

---

## Lab 2: Run Operation (20 min)

**Why:** `dbt run-operation` executes macros directly without building models. Useful for ad-hoc tasks like checking row counts, refreshing metadata, or running maintenance SQL.

### Steps

1. Create `macros/check_row_counts.sql` in VSCode:

```sql
{% macro check_row_counts() %}
    {% set tables = ['stg_customers', 'stg_orders', 'stg_order_items', 'stg_payments', 'stg_products'] %}

    {% for table in tables %}
        {% set query %}
            SELECT COUNT(*) AS cnt FROM {{ ref(table) }}
        {% endset %}

        {% set results = run_query(query) %}
        {% if execute %}
            {{ log(table ~ ": " ~ results.columns[0].values()[0] ~ " rows", info=True) }}
        {% endif %}
    {% endfor %}
{% endmacro %}
```

2. Run the operation:

```bash
dbt run-operation check_row_counts
```

Output prints row counts for each staging table.

---

## Lab 3: Document Models (30 min)

**Why:** Documentation-as-code keeps model descriptions next to the SQL. `dbt docs generate` builds a searchable website with lineage graphs — essential for onboarding new team members.

### Steps

1. Update `models/staging/schema.yml` to add descriptions. This is a complete replacement that includes all tests from Module 03 — copy this entire block:

```yaml
version: 2

models:
  - name: stg_customers
    description: "Customer dimension from Olist. One row per customer with location data."
    columns:
      - name: customer_id
        description: "Primary key"
        tests:
          - not_null
          - unique
      - name: customer_city
        description: "City where customer is located"
      - name: customer_state
        description: "Two-letter state code"

  - name: stg_orders
    description: "Order header records. One row per order with status and timestamps."
    config:
      tags: ['daily']
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - not_null
          - unique
      - name: customer_id
        description: "Foreign key to stg_customers"
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: order_status
        description: "Current status (delivered, shipped, processing, canceled)"
        tests:
          - not_null
          - accepted_values:
              values: ['delivered', 'shipped', 'processing', 'canceled']
```

2. Create or update `models/marts/schema.yml`:

```yaml
version: 2

models:
  - name: fct_orders
    description: "Order fact table joining orders with customer location."
    columns:
      - name: order_id
        description: "Primary key"
      - name: customer_city
        description: "Customer city at time of order"

  - name: fct_sales
    description: "Incremental sales fact at order-item level."
    columns:
      - name: order_item_id
        description: "Surrogate key (order_id + order_item_id)"
      - name: price
        description: "Item price excluding freight"
```

3. Generate documentation:

```bash
dbt docs generate
```

4. Serve locally:

```bash
dbt docs serve
```

Open `http://localhost:8080` in your browser. Navigate to models, view descriptions, and explore the DAG.

Press `Ctrl+C` to stop the server.

---

## Lab 4: Explore Lineage (15 min)

**Why:** The DAG (Directed Acyclic Graph) shows how data flows through your project. Use it for impact analysis — "if I change `stg_orders`, what breaks downstream?"

### Steps

1. In the documentation site, click the **Lineage Graph** button (or the graph icon next to a model name).

2. Click on `fct_sales` — observe all upstream dependencies:
   - Sources → stg_orders → fct_sales
   - Sources → stg_order_items → fct_sales

3. Click on `stg_orders` — observe all downstream consumers:
   - fct_orders, fct_sales, dim_customers_enhanced

4. This answers: "If I change `stg_orders`, which marts will be affected?"
