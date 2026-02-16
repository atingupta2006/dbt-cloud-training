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

**Why:** In mature data platforms, dbt is rarely an island. It depends on upstream loaders (Fivetran/Airbyte) and feeds downstream dashboards (Tableau/Looker). An orchestrator like **Airflow** manages these dependencies, ensuring dbt runs only *after* raw data arrives.

**Concepts:**
- **DAG (Directed Acyclic Graph):** A workflow defined in Python.
- **Operator:** A task template (e.g., `BashOperator` runs scripts, `DbtCloudRunJobOperator` talks to dbt Cloud API).
- **Connection:** Securely stores API tokens and credentials, keeping them out of your code.

### Prerequisite: Airflow Environment
This lab uses the **Remote VM** where Airflow 2.9.3 is pre-installed in `~/airflow-lab`.

### Part A: Start Airflow Services (10 min)

1. Connect to the Remote VM via SSH.

2. Activate the Airflow environment and start services:

```bash
# Terminal 1: Start Scheduler
source ~/airflow-lab/venv/bin/activate
export AIRFLOW_HOME=~/airflow-lab/airflow_home
airflow scheduler
```

3. Open a **new terminal** to the VM and start the Webserver:

```bash
# Terminal 2: Start Webserver
source ~/airflow-lab/venv/bin/activate
export AIRFLOW_HOME=~/airflow-lab/airflow_home
airflow webserver --port 8080
```

4. Open your browser to `http://<VM_IP>:8080`.
   - **Username:** `admin`
   - **Password:** `admin`

### Part B: Install dbt Cloud Provider (5 min)

The `apache-airflow-providers-dbt-cloud` package allows Airflow to communicate with dbt Cloud's API.

1. In a **new terminal** (or stop the scheduler with Ctrl+C), run:

```bash
source ~/airflow-lab/venv/bin/activate
pip install "apache-airflow-providers-dbt-cloud" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.9.txt"
```

> **Note:** If you stopped the scheduler, restart it now (`airflow scheduler`).

### Part C: Configure dbt Cloud Connection (10 min)

Airflow needs your dbt Cloud API token to trigger jobs.

1. **Get Account ID:**
   - URL: `https://cloud.getdbt.com/next/orchestration/12345/...` -> Account ID is `12345`.

2. **Get API Token:**
   - In dbt Cloud: **Profile Icon** → **Account Settings** → **API Access**.
   - Create New Token: Name `airflow-lab`, Permissions `Job Admin`. Copy the token.

3. **Get Job ID:**
   - In dbt Cloud: **Deploy** → **Jobs** → Select "Daily Production Build".
   - URL: `.../jobs/98765` -> Job ID is `98765`.

4. **Add Connection in Airflow:**
   - Go to **Admin** → **Connections** → **+ (Add)**
   - **Connection Id:** `dbt_cloud_default` (Recommended default name)
   - **Connection Type:** `dbt Cloud`
   - **Account ID:** `<Your Account ID>`
   - **API Token:** `<Your API Token>`
   - Click **Save**.

### Part D: Create the DAG (15 min)

We'll define a DAG that runs daily and triggers your dbt Cloud job.

1. Create the DAG file in the Airflow DAGs folder:

```bash
nano ~/airflow-lab/airflow_home/dags/dbt_cloud_pipeline.py
```

2. Paste the following code (replace `job_id` with yours):

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

# Default arguments for all tasks in the DAG
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
    schedule=None,              # Manual trigger (no cron schedule)
    catchup=False,
    tags=['dbt', 'training'],
) as dag:

    trigger_dbt_job = DbtCloudRunJobOperator(
        task_id='trigger_dbt_build',
        dbt_cloud_conn_id='dbt_cloud_default', # Matches Connection ID from Part C
        job_id=12345,           # <--- REPLACE WITH YOUR JOB ID
        check_interval=30,      # Poll dbt Cloud status every 30s
        timeout=3600,           # Fail if job takes > 1 hour
        wait_for_termination=True # Wait for job to finish before marking task success
    )
```

3. Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

4. Wait 30 seconds for Airflow to parse the file. Refresh the DAGs list in the UI.

### Part E: Trigger and Monitor (5 min)

1. Toggle the **dbt_cloud_pipeline** DAG to **Unpause** (slide the toggle to blue).

2. Click the **Play Button** (▶) → **Trigger DAG**.

3. Click the DAG name → **Grid View** (or Graph View).
   - A green square indicates success.
   - A spinning circle is running.

4. **Verify in dbt Cloud:**
   - Go to **Deploy** → **Jobs** → **Daily Production Build**.
   - You should see a "Running" job triggered by "API".

5. **Verify in Snowflake:**
   - Check the `LAST_ALTERED` timestamp of your tables.

### Discussion

1.  **Why use `wait_for_termination=True`?**
    - If `False`, Airflow just "fires and forgets" — marking the task successful as soon as dbt Cloud receives the request.
    - If `True` (default), Airflow keeps the task running until dbt Cloud finishes. This is crucial if downstream tasks (e.g., "Refresh Tableau") depend on dbt success.

2.  **Handling Secrets:** Note how the API Token is *never* in the Python code. It's stored securely in the Airflow metadata database via the Connection.
