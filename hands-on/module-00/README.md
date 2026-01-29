# Module 00 – Snowflake Setup

**Prerequisites:** ACCOUNTADMIN access to Snowflake

**Outcome:** Database, role, user, and sample data ready for dbt training

**Note:** Complete all parts in sequence before starting Module 01.

---

## Part 1: Create Role and User

```sql
USE ROLE ACCOUNTADMIN;

-- Create role for dbt
CREATE ROLE IF NOT EXISTS DBT_ROLE;

-- Create user with credentials
CREATE USER IF NOT EXISTS DBT_USER
  PASSWORD = 'StrongPassword@123'
  DEFAULT_ROLE = DBT_ROLE
  DEFAULT_WAREHOUSE = COMPUTE_WH
  MUST_CHANGE_PASSWORD = FALSE;

GRANT ROLE DBT_ROLE TO USER DBT_USER;
```

---

## Part 2: Grant Warehouse Access

```sql
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE DBT_ROLE;
GRANT OPERATE ON WAREHOUSE COMPUTE_WH TO ROLE DBT_ROLE;
```

---

## Part 3: Create Database and Schemas

```sql
CREATE DATABASE IF NOT EXISTS OLIST_DB;
USE DATABASE OLIST_DB;

CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;
CREATE SCHEMA IF NOT EXISTS SNAPSHOTS;
```

---

## Part 4: Grant Permissions

```sql
-- Grant database and schema permissions
GRANT ALL ON DATABASE OLIST_DB TO ROLE DBT_ROLE;
GRANT ALL ON ALL SCHEMAS IN DATABASE OLIST_DB TO ROLE DBT_ROLE;
GRANT ALL ON FUTURE SCHEMAS IN DATABASE OLIST_DB TO ROLE DBT_ROLE;

-- Grant schema-level permissions explicitly
GRANT USAGE ON SCHEMA OLIST_DB.RAW TO ROLE DBT_ROLE;
GRANT CREATE TABLE ON SCHEMA OLIST_DB.RAW TO ROLE DBT_ROLE;
GRANT USAGE ON SCHEMA OLIST_DB.ANALYTICS TO ROLE DBT_ROLE;
GRANT CREATE TABLE ON SCHEMA OLIST_DB.ANALYTICS TO ROLE DBT_ROLE;
GRANT CREATE VIEW ON SCHEMA OLIST_DB.ANALYTICS TO ROLE DBT_ROLE;
GRANT USAGE ON SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;
GRANT CREATE TABLE ON SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;

-- Grant table-level permissions to DBT_ROLE
GRANT ALL ON ALL TABLES IN SCHEMA OLIST_DB.RAW TO ROLE DBT_ROLE;
GRANT ALL ON ALL TABLES IN SCHEMA OLIST_DB.ANALYTICS TO ROLE DBT_ROLE;
GRANT ALL ON ALL TABLES IN SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;

GRANT ALL ON FUTURE TABLES IN SCHEMA OLIST_DB.RAW TO ROLE DBT_ROLE;
GRANT ALL ON FUTURE TABLES IN SCHEMA OLIST_DB.ANALYTICS TO ROLE DBT_ROLE;
GRANT ALL ON FUTURE TABLES IN SCHEMA OLIST_DB.SNAPSHOTS TO ROLE DBT_ROLE;

-- Grant view permissions for DBT_ROLE in ANALYTICS schema
GRANT SELECT ON ALL VIEWS IN SCHEMA OLIST_DB.ANALYTICS TO ROLE DBT_ROLE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA OLIST_DB.ANALYTICS TO ROLE DBT_ROLE;

-- Grant ACCOUNTADMIN ability to query DBT_ROLE objects (for validation/monitoring)
GRANT SELECT ON ALL TABLES IN SCHEMA OLIST_DB.ANALYTICS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON FUTURE TABLES IN SCHEMA OLIST_DB.ANALYTICS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON ALL VIEWS IN SCHEMA OLIST_DB.ANALYTICS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA OLIST_DB.ANALYTICS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA OLIST_DB.SNAPSHOTS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON FUTURE TABLES IN SCHEMA OLIST_DB.SNAPSHOTS TO ROLE ACCOUNTADMIN;
```

**What these permissions enable:**
- DBT_ROLE can create tables and views in all schemas
- DBT_ROLE has full access to manage objects it creates
- ACCOUNTADMIN can query (but not modify) DBT_ROLE's tables and views for monitoring
- Future objects automatically inherit these permissions

---

## Part 5: Create Tables

```sql
USE DATABASE OLIST_DB;
USE SCHEMA RAW;
```

### customers

```sql
CREATE OR REPLACE TABLE customers (
    customer_id STRING,
    customer_unique_id STRING,
    customer_zip_code_prefix STRING,
    customer_city STRING,
    customer_state STRING
);
```

### orders

```sql
CREATE OR REPLACE TABLE orders (
    order_id STRING,
    customer_id STRING,
    order_status STRING,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);
```

### order_items

```sql
CREATE OR REPLACE TABLE order_items (
    order_id STRING,
    order_item_id INTEGER,
    product_id STRING,
    seller_id STRING,
    shipping_limit_date TIMESTAMP,
    price NUMBER(10,2),
    freight_value NUMBER(10,2)
);
```

### payments

```sql
CREATE OR REPLACE TABLE payments (
    order_id STRING,
    payment_sequential INTEGER,
    payment_type STRING,
    payment_installments INTEGER,
    payment_value NUMBER(10,2)
);
```

### products

```sql
CREATE OR REPLACE TABLE products (
    product_id STRING,
    product_category_name STRING,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);
```

---

## Part 6: Create File Format and Stage

```sql
CREATE OR REPLACE FILE FORMAT csv_format
TYPE = 'CSV'
FIELD_DELIMITER = ','
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
NULL_IF = ('');

CREATE OR REPLACE STAGE olist_stage
FILE_FORMAT = csv_format;
```

---

## Part 7: Upload CSV Files

1. Open Snowflake Web UI
2. Navigate to **Data** → **Databases** → **OLIST_DB** → **RAW** → **Stages** → **OLIST_STAGE**
3. Click **+ Files** and upload all 5 files from `GH/data/raw/`

---


## Connection Credentials for Students

| Parameter | Value |
|-----------|-------|
| Account | `<your_snowflake_account>` |
| User | `DBT_USER` |
| Password | `StrongPassword@123` |
| Role | `DBT_ROLE` |
| Warehouse | `COMPUTE_WH` |
| Database | `OLIST_DB` |
| Schema | `ANALYTICS` |

---

**Setup Complete. Proceed to Module 01.**
