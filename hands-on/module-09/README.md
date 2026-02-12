# Module 09 – CLI vs Cloud, Scheduling & Orchestration

**Duration:** 6 hours (Sessions 16–18)

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

3. Open dbt Cloud → click **Studio** in the left navigation (this opens the Studio IDE)

4. Select your Development environment (check the bottom-right status button — it should show **Ready** in green)

5. Run in the Studio IDE command bar:

```
dbt run
dbt test
```

6. Verify the same models were created in the Cloud dev schema (Snowflake Web UI).

7. Compare both runs:
   - **Execution time:** Note the duration shown in CLI output vs the Studio IDE command log
   - **Logs:** CLI gives raw terminal output; Cloud gives a structured log viewer
   - **UI experience:** CLI requires a terminal + separate Snowflake tab; Cloud bundles editor, runner, and results in one browser window

8. Discuss trade-offs:
   - **CLI:** More flexibility (scripting, automation, custom flags), works offline, faster iteration for experienced users
   - **Cloud:** Better collaboration (shared project, version control UI), no local setup, built-in scheduling and artifacts

---

## Lab 2: Create Production Job in dbt Cloud (30 min)

**Why:** Scheduled jobs ensure your warehouse is refreshed automatically. Without scheduling, someone has to manually run `dbt build` every day — that does not scale.

### Prerequisite: Sync your CLI changes to Git
Before creating a job, ensure your dbt Cloud environment has the latest code:
1. If you made changes on the **Remote VM** or locally, `commit` and `push` them to your Git repository (GitHub/GitLab).
2. In dbt Cloud, ensure your **Environment** is pointed to the correct branch (e.g., `main`).

### Steps

1. In dbt Cloud, navigate to **Orchestration → Jobs**
2. Click **Create Job**
3. Configure:

| Setting | Value |
|---------|-------|
| Job Name | Daily Production Build |
| Environment | Production |
| Commands | `dbt build` |
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
   - **Results** tab: model pass/fail summary and execution times per model

4. After completion, verify in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.STG_CUSTOMERS;
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```

5. Review run summary: total models built, tests passed/failed, overall duration.

6. In dbt Cloud, check **Run Details → Artifacts**:
   - `run_results.json` — detailed results for each model (status, timing, rows affected)
   - `manifest.json` — project metadata

---

## Lab 4: Trigger dbt Cloud Job from Airflow (45 min)

**Why:** In enterprise environments, dbt is one piece of a larger data pipeline. Airflow orchestrates ingestion, dbt transformation, and downstream reporting in sequence — no manual steps, full observability.

**Prerequisite:** You must have read [AIRFLOW-QUICKSTART.md](AIRFLOW-QUICKSTART.md) before this lab. It covers installation, core concepts, and operator basics.

### Execution Mode: Remote VM vs Local (Choose one)

This lab can be performed on your local machine (if you have Airflow installed) OR on the provided **Remote CentOS VM**.

- **Remote VM:** SSH into `192.168.56.101` (password: `osboxes.org`), activate the Airflow venv, and set `AIRFLOW_HOME`.
- **Local:** Use your local Airflow installation from the quickstart.

### Part A: Verify Airflow Is Running (10 min)

1. If you completed the quickstart (or the VM bootstrap), Airflow services should be ready.

2. On the **Remote VM**, start the services:
   ```bash
   airflow webserver --port 8080 -D  # -D runs in background
   airflow scheduler -D
   ```

3. Verify by opening `localhost:8080` in your browser.

4. Install the dbt Cloud provider package:
   ```bash
   PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
   pip install "apache-airflow-providers-dbt-cloud" \
     --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PYTHON_VERSION}.txt"
   ```

### Part B: Configure dbt Cloud Connection (10 min)

1. Get your dbt Cloud **Account ID**:
   - In dbt Cloud, look at the URL: `https://cloud.getdbt.com/next/orchestration/{ACCOUNT_ID}/...`
   - Note this number

2. Generate an API token:
   - dbt Cloud → profile icon → **Account Settings → API Access → Service Tokens**
   - Click **+ New Token** → Name: `airflow-training` → Permissions: **Job Admin**
   - Copy the token

3. Get your **Job ID**:
   - dbt Cloud → **Orchestration → Jobs** → click on **Daily Production Build** (created in Lab 2)
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

5. Verify in dbt Cloud → **Orchestration → Jobs → Daily Production Build → Run History**. You should see a new run triggered by the API (not by schedule).

6. Verify the data in Snowflake Web UI:

```sql
SELECT COUNT(*) FROM OLIST_DB.ANALYTICS.FCT_ORDERS;
```

### Discussion

- **When to use dbt Cloud scheduling vs Airflow:** Cloud scheduling is simpler and sufficient when dbt is your only tool. Airflow is for when dbt is one step in a larger pipeline (extract → transform → load → report).
- **What happens on failure?** Airflow retries based on `default_args.retries`. If all retries fail, the task shows red in the UI and sends an alert (if email is configured).
- **Can Airflow run dbt CLI directly?** Yes — use `BashOperator` with `bash_command='dbt run --target prod'`. This is an alternative to the Cloud API approach.
