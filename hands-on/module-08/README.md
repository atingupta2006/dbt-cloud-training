# Module 08 – Environment Management (Labs)

---

## Lab 1 – Create Development Environment in dbt Cloud (25 min)

Objective: Create and validate a development environment in dbt Cloud

1. Open browser
2. Go to [https://cloud.getdbt.com](https://cloud.getdbt.com)
3. Create account or sign in
4. Create new project
5. Connect GitHub repository
6. Choose adapter: Snowflake
7. Open:
   Account Settings → Projects → <project> → Environments
8. Click: New Environment
9. Name: Development
10. Type: Development
11. dbt Version: 1.9.8
12. Threads: 4
13. Adapter: Snowflake
14. Database: OLIST_DB
15. Schema: ANALYTICS_DEV
16. Warehouse: COMPUTE_WH
17. Enter personal Snowflake user and password
18. Click Save
19. Open Cloud IDE
20. Run:

dbt debug

Success: Connection test returns OK

---

## Lab 2 – Create Production Environment in dbt Cloud (20 min)

Objective: Create separate production environment

1. Open:
   Account Settings → Projects → <project> → Environments
2. Click: New Environment
3. Name: Production
4. Type: Deployment
5. dbt Version: 1.9.8
6. Threads: 8
7. Adapter: Snowflake
8. Database: OLIST_DB
9. Schema: ANALYTICS
10. Warehouse: COMPUTE_WH
11. Enter production Snowflake user and password
12. Click Save
13. Click Test Connection

Success: Production environment saved and tested

---

## Lab 3 – Compare CLI Multi-Target vs Cloud Environments (20 min)

Objective: Observe schema change using CLI target and Cloud environment

1. Open ~/.dbt/profiles.yml in VSCode

2. Confirm dev target schema = ANALYTICS_DEV

3. Confirm prod target schema = ANALYTICS

4. From project root:

   dbt run --target dev

5. Open Snowflake UI → Worksheets

6. Run:

   SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.STG_CUSTOMERS;

7. From project root:

   dbt run --target prod

8. In Snowflake UI run:

   SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.STG_CUSTOMERS;

9. Open dbt Cloud IDE

10. Ensure Development environment selected

11. Run:

    dbt run --select stg_customers

Success: Same model created in two different schemas

---

## Lab 4 – Environment-Specific Logic (15 min)

Objective: Change model behavior based on environment

1. Create ./models/marts/orders_env_demo.sql in VSCode

2. Add:

   SELECT
   order_id,
   customer_id,
   order_status,
   order_purchase_timestamp
   FROM {{ ref('stg_orders') }}

   {% if target.name == 'dev' %}
   LIMIT 1000
   {% endif %}

3. Run locally:

   dbt run --select orders_env_demo --target dev

4. In Snowflake UI:

   SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.ORDERS_ENV_DEMO;

5. Run locally:

   dbt run --select orders_env_demo --target prod

6. In Snowflake UI:

   SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.ORDERS_ENV_DEMO;

Success: Dev table limited, prod table full size

---

End of Module 08 Labs
