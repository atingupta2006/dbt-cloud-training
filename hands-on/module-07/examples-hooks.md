
```
models:
  olist_dbt_project:
    +pre-hook:
      - "ALTER WAREHOUSE TRANSFORM_WH SET WAREHOUSE_SIZE = LARGE"
    +post-hook:
      - "ALTER WAREHOUSE TRANSFORM_WH SET WAREHOUSE_SIZE = XSMALL"
```

```
{{ config(
  post_hook="
    {% if target.name != 'prod' %}
      UPDATE {{ this }}
      SET email = 'masked@email.com'
    {% endif %}
  "
) }}
```

```
{{ config(
  pre_hook="SELECT GET_LOCK('orders_build', 300)"
) }}
```

```
{{ config(
  post_hook="SELECT RELEASE_LOCK('orders_build')"
) }}
```

```
GRANT ALL PRIVILEGES
ON ALL WAREHOUSES IN ACCOUNT
TO ROLE DBT_ROLE;
```

```
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE DBT_ROLE;
```