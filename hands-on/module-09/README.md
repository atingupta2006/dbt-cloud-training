# Module 09 – CLI vs Cloud, Scheduling & Orchestration

**Duration:** 6 hours (Sessions 16–18)

**Prerequisite:** Read [AIRFLOW-QUICKSTART.md](AIRFLOW-QUICKSTART.md) before starting Lab 4. It covers Airflow concepts (DAGs, operators, sensors, connections) from scratch — no prior Airflow experience required.

---

## Lab 1: Run Project in CLI and Cloud (25 min)

**Why:** Understanding both execution paths — CLI for local development, Cloud for production — is essential for real-world dbt workflows. Most teams develop in CLI and deploy via Cloud.

### Steps

1. Run project locally via CLI:

```bash
source .venv/bin/activate
dbt run --target dev
dbt test --target dev
```

2. Verify in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.STG_CUSTOMERS;
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS_DEV.FCT_ORDERS;
```

3. Open dbt Cloud → **Develop → Cloud IDE**

4. Select Development environment

5. Run in the Cloud IDE command bar:

```
dbt run
dbt test
```

6. Verify the same models were created in the Cloud dev schema (Snowflake Web UI).

Both CLI and Cloud produce identical results — the difference is where the execution happens.

---

## Lab 2: Create Production Job in dbt Cloud (30 min)

**Why:** Scheduled jobs ensure your warehouse is refreshed automatically. Without scheduling, someone has to manually run `dbt build` every day — that does not scale.

### Steps

1. In dbt Cloud, navigate to **Deploy → Jobs**
2. Click **Create Job**
3. Configure:

| Setting | Value |
|---------|-------|
| Job Name | Daily Production Build |
| Environment | Production |
| Commands | `dbt run` and `dbt test` (each on its own line) |
| Threads | 4 |

4. Set schedule:
   - Type: **Custom cron**
   - Expression: `0 6 * * *` (daily at 6:00 AM UTC)

5. Configure notifications:
   - **On Failure:** Email notification
   - Slack webhook (if available): **Account Settings → Integrations → Slack**

6. Save the job

---

## Lab 3: Manually Trigger and Monitor Job (20 min)

**Why:** Before trusting a schedule, always trigger a manual run to verify the job works. Monitoring logs and artifacts is how you debug production failures.

### Steps

1. Open the **Daily Production Build** job
2. Click **Run Now**
3. Watch the run progress:
   - **Logs** tab: real-time command output
   - **Results** tab: model pass/fail summary

4. After completion, verify in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.STG_CUSTOMERS;
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```

5. In dbt Cloud, check **Run Details → Artifacts**:
   - `run_results.json` — detailed results for each model
   - `manifest.json` — project metadata

---

## Lab 4: Trigger dbt Cloud Job from Airflow (45 min)

**Why:** In enterprise environments, dbt is one piece of a larger data pipeline. Airflow orchestrates ingestion, dbt transformation, and downstream reporting in sequence — no manual steps, full observability.

**Prerequisite:** You must have read [AIRFLOW-QUICKSTART.md](AIRFLOW-QUICKSTART.md) before this lab. It covers installation, core concepts, and operator basics.

### Part A: Verify Airflow Is Running (10 min)

1. If you completed the quickstart, Airflow should already be running. Verify by opening [http://localhost:8080](http://localhost:8080) in your browser.

2. If not running, start it:

```bash
cd ~/airflow-demo
source airflow_venv/bin/activate
export AIRFLOW_HOME=~/airflow-demo/airflow_home
airflow webserver --port 8080 &
airflow scheduler &
```

3. Install the dbt Cloud provider package (if not already installed):

```bash
pip install apache-airflow-providers-dbt-cloud
```

### Part B: Configure dbt Cloud Connection (10 min)

1. Get your dbt Cloud **Account ID**:
   - In dbt Cloud, look at the URL: `https://cloud.getdbt.com/deploy/{ACCOUNT_ID}/...`
   - Note this number

2. Generate an API token:
   - dbt Cloud → profile icon → **Account Settings → API Access → Service Tokens**
   - Click **+ New Token** → Name: `airflow-training` → Permissions: **Job Admin**
   - Copy the token

3. Get your **Job ID**:
   - dbt Cloud → **Deploy → Jobs** → click on **Daily Production Build** (created in Lab 2)
   - The Job ID is in the URL: `...jobs/{JOB_ID}`

4. Add the connection in Airflow UI:
   - Navigate to **Admin → Connections** → click **+**
   - Configure:

| Field | Value |
|-------|-------|
| Connection Id | `dbt_cloud_default` |
| Connection Type | `dbt Cloud` |
| Account ID | Your Account ID from step 1 |
| API Token | The token from step 2 |

5. Click **Save**

### Part C: Create the DAG (15 min)

1. Create `$AIRFLOW_HOME/dags/dbt_cloud_pipeline.py` in VSCode:

```python
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
        dbt_cloud_conn_id='dbt_cloud_default',
        job_id=12345,           # Replace with YOUR Job ID from Part B step 3
        check_interval=30,      # Poll dbt Cloud every 30 seconds
        timeout=3600,           # Fail if job takes longer than 1 hour
    )
```

> Replace `job_id=12345` with the actual Job ID you noted in Part B.

2. Wait 30 seconds for the scheduler to detect the new DAG file.

3. Refresh the Airflow UI. You should see **dbt_cloud_pipeline** in the DAG list.

### Part D: Trigger and Monitor (10 min)

1. Toggle the DAG **ON** (switch on the left of `dbt_cloud_pipeline`)

2. Click the **play button** (▶) → **Trigger DAG**

3. Click on the DAG name → **Graph** view. You see one task: `trigger_dbt_build`.

4. Click on the task → **Logs**. You should see:
   - `Triggering job run for job_id=...`
   - `Polling status every 30 seconds...`
   - `Job run completed with status: SUCCESS`

5. Verify in dbt Cloud → **Deploy → Jobs → Daily Production Build → Run History**. You should see a new run triggered by the API (not by schedule).

6. Verify the data in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```

### Discussion

- **When to use dbt Cloud scheduling vs Airflow:** Cloud scheduling is simpler. Airflow is for when dbt is one step in a larger pipeline (extract → transform → load → report).
- **What happens on failure?** Airflow retries based on `default_args.retries`. If all retries fail, the task shows red in the UI and sends an alert (if email is configured).
- **Can Airflow run dbt CLI directly?** Yes — use `BashOperator` with `bash_command='dbt run --target prod'`. This is an alternative to the Cloud API approach.
