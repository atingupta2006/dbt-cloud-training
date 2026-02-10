# Module 06 – Debugging, Variables & Macros

**Duration:** 4 hours (Sessions 11–12)

---

## Lab 1: Debug Connection (15 min)

**Why:** `dbt debug` is the first command you run when something breaks. It validates your profiles.yml, project config, and database connection in one shot.

### Steps

1. Verify working connection:

```bash
dbt debug
```

All checks should show `[OK]`.

2. Simulate a connection failure — change your password env var:

```bash
export SNOWFLAKE_PASSWORD="wrong_password"
dbt debug
```

Connection test shows `[ERROR]`.

3. Restore the correct password and verify:

```bash
export SNOWFLAKE_PASSWORD="StrongPassword@123"
dbt debug
```

---

## Lab 2: Variables & Jinja Context (30 min)

**Why:** Variables make models parameterizable. Instead of hardcoding values, you define them once and override per environment or at the CLI.

### Steps

1. Add a variable to `dbt_project.yml`:

```yaml
vars:
  payment_methods: ['credit_card', 'debit_card']
```

2. Create `models/marts/payment_filter.sql` in VSCode:

```sql
{{ config(materialized='view') }}

SELECT
    order_id,
    payment_type,
    payment_value
FROM {{ ref('stg_payments') }}
WHERE payment_type IN (
{% for m in var('payment_methods') %}
    '{{ m }}'{% if not loop.last %},{% endif %}
{% endfor %}
)
```

This uses a Jinja for-loop to generate a dynamic `IN` clause from the variable.

3. Run with the default variable:

```bash
dbt run --select payment_filter
```

4. Override the variable via CLI:

```bash
dbt run --select payment_filter --vars "payment_methods: ['credit_card']"
```

Now it filters to only `credit_card`.

5. Add target context — update `payment_filter.sql`:

```sql
{{ config(materialized='view') }}

SELECT
    order_id,
    payment_type,
    payment_value,
    '{{ target.name }}' AS environment,
    '{{ target.schema }}' AS target_schema
FROM {{ ref('stg_payments') }}
WHERE payment_type IN (
{% for m in var('payment_methods') %}
    '{{ m }}'{% if not loop.last %},{% endif %}
{% endfor %}
)
```

6. Run and verify the metadata columns appear:

```bash
dbt run --select payment_filter
```

---

## Lab 3: Reusable Macros (35 min)

**Why:** Macros are Jinja functions that generate SQL. They enforce DRY (Don't Repeat Yourself) — write transformation logic once, reuse it across all models.

### Steps

1. Create `macros/cents_to_dollars.sql` in VSCode:

```sql
{% macro cents_to_dollars(amount_col) %}
    ({{ amount_col }} / 100.0)
{% endmacro %}
```

> This macro demonstrates the pattern of reusable transformations. Olist data is already in BRL (Brazilian Real), not cents — in a real US-dollar dataset, this macro would convert cent values to dollars.

2. Create `macros/generate_alias.sql`:

```sql
{% macro generate_alias(table_name, prefix) %}
    {{ prefix }}_{{ table_name }}
{% endmacro %}
```

3. Create `models/marts/order_amounts.sql` to use both macros:

```sql
{{ config(materialized='view') }}

SELECT
    order_id,
    {{ cents_to_dollars('payment_value') }} AS payment_dollars,
    '{{ generate_alias("orders", "fact") }}' AS alias_name
FROM {{ ref('stg_payments') }}
```

4. Run and check the compiled output:

```bash
dbt run --select order_amounts
cat target/compiled/olist_dbt_project/models/marts/order_amounts.sql
```

The compiled SQL shows `(payment_value / 100.0)` — all Jinja is resolved to plain SQL.

5. Create a macro that returns a list — `macros/get_payment_methods.sql`:

```sql
{% macro get_payment_methods() %}
    {{ return(['credit_card', 'debit_card', 'voucher', 'boleto']) }}
{% endmacro %}
```

6. Use the macro in a test — create or update `models/marts/schema.yml`:

```yaml
version: 2

models:
  - name: payment_filter
    columns:
      - name: payment_type
        tests:
          - accepted_values:
              values: "{{ get_payment_methods() }}"
```

7. Run the test:

```bash
dbt test --select payment_filter
```

---

## Lab 4: Date Spine Macro (25 min)

**Why:** A date spine generates a continuous calendar dimension. This is essential for time-series analysis — filling gaps in data where no orders occurred on certain dates.

### Steps

1. Create `macros/date_spine.sql` in VSCode:

```sql
{% macro date_spine(start_date, end_date) %}
WITH RECURSIVE dates AS (
    SELECT {{ start_date }}::DATE AS d
    UNION ALL
    SELECT DATEADD(day, 1, d)
    FROM dates
    WHERE d < {{ end_date }}::DATE
)
SELECT d AS date_day
FROM dates
{% endmacro %}
```

2. Create `models/marts/dim_date.sql`:

```sql
{{ config(materialized='table') }}

{{ date_spine("'2016-01-01'", "'2018-12-31'") }}
```

3. Run:

```bash
dbt run --select dim_date
```

4. Verify in Snowflake Web UI:

```sql
SELECT MIN(date_day), MAX(date_day), COUNT(*) FROM dim_date;
```

Expected: 1,095 rows (3 years of dates).
