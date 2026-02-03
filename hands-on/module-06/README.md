# Module 06 – Debugging, Variables & Macros

**Prerequisites:** Module 05 completed

**Duration:** ~90 minutes

**Instructor Note:** This module teaches debugging techniques, Jinja variables, and reusable macros. Focus on practical code reuse patterns.

---

## Lab 1: Debug Connection (15 min)

**Objective:** Use `dbt debug` to verify and troubleshoot connection

### Overview

`dbt debug` performs a series of checks:
- Python version compatibility
- profiles.yml syntax
- Database connection
- Required dependencies

### Tasks


### Task 1: Verify working connection

From project root:
```bash
dbt debug
```

**Expected output:**
```
Configuration:
  profiles.yml file [OK found and valid]
  dbt_project.yml file [OK found and valid]

Required dependencies:
  - git [OK found]

Connection:
  account: <Your-Snowflake-Acount-ID>
  user: DBT_USER
  database: OLIST_DB
  warehouse: COMPUTE_WH
  role: DBT_ROLE
  Connection test: [OK connection ok]

All checks passed!
```


### Task 2 (Optional): Simulate connection error

1. Open `.env` file in VSCode (located in project root).
2. Change `SNOWFLAKE_PASSWORD` to an incorrect value and save.
3. Run:
    ```bash
    dbt debug
    ```
    **Expected output:**
    - Connection test shows `[ERROR]`
4. Restore the correct password and verify again:
    ```bash
    dbt debug
    ```
    **Expected output:**
    - All checks passed

Open `.env` file in VSCode (located in project root):

Change `SNOWFLAKE_PASSWORD` to incorrect value, save.

Run debug again:
```bash
dbt debug
```

**Expected:** Connection test shows [ERROR]

Restore correct password and verify:
```bash
dbt debug
```

### Success Criteria

- ✅ `dbt debug` shows all checks passed
- ✅ Connection test returns [OK]
- ✅ Understand debug output structure

---

## Lab 2: Variables & Jinja Context (30 min)

**Objective:** Use `var()`, `target`, and `env_var()` functions

### Overview

dbt provides three ways to access dynamic values:
- **Variables (`var()`)**: Defined in `dbt_project.yml` or via CLI
- **Target context (`target`)**: Current environment (dev, prod)
- **Environment variables (`env_var()`)**: OS-level variables

### Tasks


### Task 1: Configure project variable

Open `~/olist_dbt_project/dbt_project.yml` in VSCode:

Verify the `vars` section exists (already added):
```yaml
# Variables for Module 06
vars:
  payment_methods: ['credit_card','debit_card']
```

**What this does:** Makes `payment_methods` list available to all models


### Task 2: Create model using variable

Create `~/olist_dbt_project/models/marts/payment_filter.sql` in VSCode:

Add content:
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

**What this does:** Uses Jinja for-loop to generate dynamic IN clause


### Task 3: Run model with default variable

```bash
dbt run --select payment_filter
```


**Expected output:**
- Compiles to `WHERE payment_type IN ('credit_card','debit_card')`

**Verify:** View created successfully in ANALYTICS schema

**Verify:** View created successfully in ANALYTICS schema


### Task 4: Override variable via CLI

```bash
dbt run --select payment_filter --vars "payment_methods: ['credit_card']"
```

**Expected output:**
- Now filters to only `credit_card`

**Why:** Testing single payment method without changing code


### Task 5: Use target and env_var

Update `payment_filter.sql`:
```sql
{{ config(materialized='view') }}

SELECT
    order_id,
    payment_type,
    payment_value,
    '{{ target.name }}' AS target_name,
    '{{ target.schema }}' AS target_schema
FROM {{ ref('stg_payments') }}
WHERE payment_type IN (
{% for m in var('payment_methods') %}
    '{{ m }}'{% if not loop.last %},{% endif %}
{% endfor %}
)
```

Run:
```bash
dbt run --select payment_filter
```

**Expected output:**
- Output includes `target_name` = 'dev' and `target_schema` = 'ANALYTICS'

### Success Criteria

- ✅ Variable defined in `dbt_project.yml`
- ✅ Jinja for-loop generates dynamic SQL
- ✅ CLI `--vars` overrides project variable
- ✅ `target` context accessible in models

---

## Lab 3: Reusable Macros (35 min)

**Objective:** Create and use custom macros for code reuse

### Overview

Macros are Jinja functions that generate SQL. Benefits:
- **DRY principle**: Write once, use everywhere
- **Consistency**: Centralized logic
- **Maintainability**: Update in one place

### Tasks


### Task 1: Create generate_alias macro

Create `~/olist_dbt_project/macros/generate_alias.sql` in VSCode:

Add content:
```jinja
{% macro generate_alias(table_name, prefix) %}
    {{ prefix }}_{{ table_name }}
{% endmacro %}
```

**What this does:** Takes two arguments, returns concatenated string


### Task 2: Create cents_to_dollars macro

Create `~/olist_dbt_project/macros/cents_to_dollars.sql` in VSCode:

Add content:
```jinja
{% macro cents_to_dollars(amount_col) %}
    ({{ amount_col }} / 100.0)
{% endmacro %}
```

**What this does:** Generates SQL division expression with parentheses


### Task 3: Use macros in model

Create `~/olist_dbt_project/models/marts/order_amounts.sql` in VSCode:

Add content:
```sql
{{ config(materialized='view') }}

SELECT
    order_id,
    {{ cents_to_dollars('payment_value') }} AS payment_amount,
    '{{ generate_alias('orders','fact') }}' AS alias_name
FROM {{ ref('stg_payments') }}
```

**What this does:** Uses both macros to generate SQL


### Task 4: Run and verify compilation

```bash
dbt run --select order_amounts
```

Check compiled SQL:
```bash
cat target/compiled/olist_dbt_project/models/marts/order_amounts.sql
```

**Expected output:**
```sql
SELECT
    order_id,
    (payment_value / 100.0) AS payment_amount,
    'fact_orders' AS alias_name
FROM OLIST_DB.ANALYTICS.STG_PAYMENTS
```
**Key observation:**
- Macros expanded to raw SQL


### Task 5: Create macro returning list

Create `~/olist_dbt_project/macros/get_payment_methods.sql` in VSCode:

Add content:
```jinja
{% macro get_payment_methods() %}
    {{ return(['credit_card','debit_card','voucher','boleto']) }}
{% endmacro %}
```

**What this does:** Returns Python list for use in tests


### Task 6: Use macro in test

Create `~/olist_dbt_project/models/marts/schema.yml` in VSCode:

Add content:
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

**What this does:** Test validates payment_type against macro list


### Task 7: Run test

```bash
dbt test --select payment_filter
```

**Expected output:**
- Test passes (values in macro list are valid)

### Success Criteria

- ✅ Three macros created (`generate_alias`, `cents_to_dollars`, `get_payment_methods`)
- ✅ Macros compile to correct SQL
- ✅ Macro used in test configuration
- ✅ Understand macro vs model distinction

---

## Lab 4: Date Spine Macro (25 min)

**Objective:** Generate calendar dimension using recursive macro

### Overview

Date spine = continuous sequence of dates. Used for:
- Filling gaps in time series data
- Creating calendar dimensions
- Date-based joins

### Tasks


### Task 1: Create date_spine macro

Create `~/olist_dbt_project/macros/date_spine.sql` in VSCode:

Add content:
```jinja
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

**What this does:** Generates recursive CTE with date sequence
**Note:**
- Snowflake requires `RECURSIVE` keyword


### Task 2: Create dim_date model

Create `~/olist_dbt_project/models/marts/dim_date.sql` in VSCode:

Add content:
```sql
{{ config(materialized='table') }}

{{ date_spine("'2016-01-01'", "'2018-12-31'") }}
```

**What this does:** Entire model is macro invocation


### Task 3: Run model

```bash
dbt run --select dim_date
```

**Expected output:**
- Creates table with ~1,095 rows (3 years of dates)


### Task 4: Verify date range

Query:
```bash
snowsql -a %SNOWFLAKE_ACCOUNT% -u %SNOWFLAKE_USER% --authenticator externalbrowser -d OLIST_DB -s ANALYTICS -q "SELECT MIN(date_day), MAX(date_day), COUNT(*) FROM dim_date"
```

**Expected output:**
- MIN: 2016-01-01
- MAX: 2018-12-31
- COUNT: 1095


### Task 5: Create join model using dim_date

Create `~/olist_dbt_project/models/marts/orders_with_date.sql` in VSCode:

Add content:
```sql
{{ config(materialized='table') }}

SELECT
    o.order_id,
    o.order_purchase_timestamp,
    d.date_day,
    o.order_status
FROM {{ ref('stg_orders') }} o
INNER JOIN {{ ref('dim_date') }} d
    ON DATE(o.order_purchase_timestamp) = d.date_day
```

**What this does:** Joins orders to calendar dimension


### Task 6: Run full model

```bash
dbt run --select orders_with_date
```

**Expected output:**
- Orders joined with date dimension

### Success Criteria

- ✅ `date_spine` macro creates recursive CTE
- ✅ `dim_date` table populated with date range
- ✅ Orders successfully join to date dimension
- ✅ Understand macro as reusable SQL generator

---

## Module 06 Summary

### What You Practiced

**Debugging:**
- `dbt debug` command validates setup
- Connection troubleshooting
- Profiles.yml verification

**Variables:**
- `var()` - Project variables in `dbt_project.yml`
- CLI override with `--vars`
- `target` context (name, schema, etc.)
- `env_var()` for OS environment variables

**Macros:**
- Custom macros for SQL generation
- String manipulation (`generate_alias`)
- Mathematical operations (`cents_to_dollars`)
- List returns (`get_payment_methods`)
- Recursive CTEs (`date_spine`)
- Macro usage in tests

**Jinja Concepts:**
- For-loops with `{% for %}`
- Conditionals with `{% if %}`
- Macro definitions with `{% macro %}`
- `{{ }}` for expression output

### Key Concepts

1. **Macros vs Models:**
   - Macros = Jinja functions that generate SQL
   - Models = SQL/Jinja files that create database objects

2. **Variable Precedence:**
   - CLI `--vars` > `dbt_project.yml vars` > macro defaults

3. **Compilation:**
   - Jinja rendered first → generates SQL → SQL executed

4. **Code Reuse Benefits:**
   - Single source of truth
   - Easier maintenance
   - Consistent business logic

### Project Structure After Module 06

```
macros/
├── generate_alias.sql       # String concatenation macro
├── cents_to_dollars.sql     # Math conversion macro
├── get_payment_methods.sql  # List return macro
└── date_spine.sql           # Recursive CTE macro

models/
├── marts/
│   ├── payment_filter.sql           # Uses var() and for-loop
│   ├── order_amounts.sql            # Uses multiple macros
│   ├── dim_date.sql                 # Date dimension (table)
│   ├── orders_with_date.sql         # Join to date dimension (table)
│   ├── fct_orders.sql               # From Module 04
│   ├── fct_sales.sql                # From Module 04
│   ├── products_with_categories.sql # From Module 04
│   └── schema.yml                   # Test using macro
└── staging/
    └── [5 models from Module 04]

dbt_project.yml
└── vars:
    └── payment_methods: ['credit_card','debit_card']
```

### Commands Reference

```bash
# Debugging
dbt debug                              # Verify connection and setup

# Variables
dbt run --select model_name --vars "var_name: value"

# Macros
dbt run --select model_using_macro
dbt compile                            # See rendered SQL in target/

# Date spine
dbt run --select dim_date              # Generate calendar
```

### Next Steps

Module 07 will cover:
- Documentation and metadata
- dbt docs generate/serve
- Column descriptions
- Model dependencies visualization
