from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

default_args = {
    'owner': 'data-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='dbt_cloud_pipeline',
    description='Trigger dbt Cloud production job',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule=None,              # Manual trigger only (no auto-schedule)
    catchup=False,
    tags=['dbt', 'training'],
) as dag:

    trigger_dbt_job = DbtCloudRunJobOperator(
        task_id='trigger_dbt_build',
        dbt_cloud_conn_id='dbt_cloud_default',  # Must match Connection ID in Airflow UI
        job_id=12345,           # REPLACE THIS with your actual Job ID from dbt Cloud
        check_interval=30,      # Poll dbt Cloud every 30 seconds
        timeout=3600,           # Fail if job takes longer than 1 hour
        wait_for_termination=True
    )
