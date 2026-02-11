# Apache Airflow — Quickstart for dbt Users

**Duration:** 60–90 minutes (self-paced prerequisite — complete before Module 09, Lab 4)

---

## What Is Airflow?

Apache Airflow is an open-source platform for **orchestrating workflows**. Think of it as a scheduler on steroids — it does not move or transform data itself, but it tells other tools (like dbt, Python scripts, APIs) **when** to run, **in what order**, and **what to do if something fails**.

**Why it matters for dbt:** In production, dbt is rarely the only tool. A typical pipeline looks like:

```
Extract (Fivetran/Airbyte) → Transform (dbt) → Load dashboards (Looker/Tableau)
```

Airflow orchestrates this entire chain. It triggers the extract, waits for it to finish, then triggers dbt, waits again, then refreshes dashboards — all automatically, with retries and alerts.

---

## Core Concepts

### 1. DAG (Directed Acyclic Graph)

A DAG is a workflow defined as Python code. It describes:
- **What tasks** to run
- **In what order** (dependencies)
- **When** to run (schedule)

"Acyclic" means no circular dependencies — Task A can trigger Task B, but Task B cannot trigger Task A.

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Extract  │────▶│  dbt Run  │────▶│  Refresh  │
│   Data    │     │  & Test   │     │ Dashboard │
└──────────┘     └──────────┘     └──────────┘
```

Each box is a **Task**. The arrows are **Dependencies**.

### 2. Task

A single unit of work. Examples:
- Run a SQL query
- Execute a bash command
- Trigger a dbt Cloud job
- Send a Slack notification

### 3. Operator

An Operator is a **template** for creating tasks. You do not write task logic from scratch — you pick the right Operator and configure it.

| Operator | What It Does |
|----------|-------------|
| `BashOperator` | Runs a shell command |
| `PythonOperator` | Runs a Python function |
| `DbtCloudRunJobOperator` | Triggers a dbt Cloud job |
| `DbtCloudJobRunSensor` | Waits for a dbt Cloud job to finish |
| `SnowflakeOperator` | Runs a SQL query in Snowflake |
| `EmailOperator` | Sends an email |
| `SlackWebhookOperator` | Sends a Slack message |

### 4. Sensor

A special type of Operator that **waits** for something to happen before proceeding. Examples:
- Wait for a file to appear in S3
- Wait for a dbt Cloud job to complete
- Wait for a specific time of day

### 5. Connection

Airflow stores credentials (database passwords, API tokens) as **Connections** in its metadata database. DAGs reference connections by ID — credentials are never hardcoded in Python files.

### 6. Variable

Key-value pairs stored in Airflow for runtime configuration. Example: `dbt_cloud_job_id = 12345`. DAGs read variables instead of hardcoding values.

---

## Install Airflow Locally

**Why:** Running Airflow locally lets you write and test DAGs before deploying to a production Airflow server.

### Option A: pip install (simplest for learning)

> [!CAUTION]
> **CRITICAL: AIRFLOW VERSION PINNING**  
> **DO NOT** run `pip install apache-airflow` without a version pin. As of February 2025, running a plain install will attempt to install **Airflow 3.0 (Alpha/Beta)**, which is NOT compatible with these labs and will cause environment conflicts. Always use version `2.9.3` as shown below.

1. Create a dedicated virtual environment (separate from dbt):

```bash
cd ~
mkdir airflow-demo && cd airflow-demo
python3 -m venv airflow_venv
source airflow_venv/bin/activate
```

2. Set the Airflow home directory:

```bash
export AIRFLOW_HOME=~/airflow-demo/airflow_home
```

3. Install Airflow (pinned to a compatible version):

```bash
# Automatically detect Python version for constraints
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"

pip install "apache-airflow==2.9.3" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PYTHON_VERSION}.txt"
```

> This takes 2–5 minutes. The `--constraint` flag ensures compatible dependency versions.

4. **Verify Version (CRITICAL):**
```bash
airflow version
# Expected Output: 2.9.3 (Anything starting with 3.x is INCORRECT)
```

5. Initialize the metadata database:

```bash
airflow db migrate
```

5. Create an admin user:

```bash
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

6. Start the web server (in one terminal):

```bash
airflow webserver --port 8080
```

7. Open a second terminal, activate the same venv, and start the scheduler:

```bash
cd ~/airflow-demo
source airflow_venv/bin/activate
export AIRFLOW_HOME=~/airflow-demo/airflow_home
airflow scheduler
```

8. Open browser → [http://localhost:8080](http://localhost:8080)

9. Log in with `admin` / `admin`.

You should see the Airflow dashboard with example DAGs listed.

### Option B: Docker Compose (production-like setup)

If you have Docker installed, this is faster and more realistic:

1. Create a project directory:

```bash
cd ~
mkdir airflow-docker && cd airflow-docker
```

2. Download the official Docker Compose file:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.9.3/docker-compose.yaml'
```

3. Create required directories:

```bash
mkdir -p ./dags ./logs ./plugins ./config
```

4. Set the Airflow user ID:

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

5. Initialize Airflow:

```bash
docker compose up airflow-init
```

6. Start all services:

```bash
docker compose up -d
```

7. Open browser → [http://localhost:8080](http://localhost:8080)

8. Log in with `airflow` / `airflow`.

---

## Your First DAG

**Why:** The best way to learn Airflow is to write a DAG. This example uses `BashOperator` to run simple commands — the same pattern you will use to trigger dbt CLI commands.

### Step 1: Create the DAG file

Create `$AIRFLOW_HOME/dags/my_first_dag.py` (or `./dags/my_first_dag.py` if using Docker):

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments applied to every task in this DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='my_first_dag',
    description='A simple demo DAG',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='@daily',          # Run once per day
    catchup=False,              # Do not backfill past dates
    tags=['demo'],
) as dag:

    # Task 1: Print a greeting
    task_hello = BashOperator(
        task_id='say_hello',
        bash_command='echo "Hello from Airflow! Today is $(date)"',
    )

    # Task 2: Print working directory
    task_info = BashOperator(
        task_id='show_info',
        bash_command='echo "Running on $(hostname) as $(whoami)"',
    )

    # Task 3: Simulate a dbt run
    task_dbt = BashOperator(
        task_id='simulate_dbt_run',
        bash_command='echo "dbt run --target prod would execute here"',
    )

    # Define execution order (dependencies)
    task_hello >> task_info >> task_dbt
```

### Step 2: Verify Airflow picks it up

Wait 30 seconds (the scheduler scans the `dags/` folder periodically), then refresh the Airflow UI. You should see **my_first_dag** in the list.

### Step 3: Trigger the DAG

1. Toggle the DAG **ON** (the switch on the left)
2. Click the **play button** (▶) → **Trigger DAG**
3. Click on the DAG name to see the run
4. Switch to **Graph** view — you see three boxes connected by arrows
5. Click on `say_hello` → **Logs** to see the output

### Step 4: Understand the code

| Code Element | Purpose |
|-------------|---------|
| `with DAG(...) as dag:` | Defines the workflow container |
| `default_args` | Shared settings (retries, owner) for all tasks |
| `schedule='@daily'` | When to run. Other options: `@hourly`, `@weekly`, cron strings |
| `catchup=False` | If the DAG was paused, do NOT run missed schedules |
| `BashOperator(...)` | Creates a task that runs a shell command |
| `task_hello >> task_info >> task_dbt` | Sets execution order using the `>>` (bitshift) operator |

---

## Key Operators Explained

### BashOperator — Run shell commands

```python
from airflow.operators.bash import BashOperator

run_dbt = BashOperator(
    task_id='dbt_run',
    bash_command='cd /path/to/dbt/project && dbt run --target prod',
)
```

Use this to run dbt CLI commands directly from Airflow.

### PythonOperator — Run Python functions

```python
from airflow.operators.python import PythonOperator

def my_python_task():
    print("Running Python logic")
    # Any Python code: API calls, data validation, etc.

python_task = PythonOperator(
    task_id='run_python',
    python_callable=my_python_task,
)
```

### DbtCloudRunJobOperator — Trigger dbt Cloud jobs

```python
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

trigger_dbt = DbtCloudRunJobOperator(
    task_id='trigger_dbt_cloud',
    dbt_cloud_conn_id='dbt_cloud_default',  # Connection ID in Airflow
    job_id=12345,                            # Your dbt Cloud Job ID
    check_interval=30,                       # Poll every 30 seconds
    timeout=3600,                            # Fail after 1 hour
)
```

> **Pre-requisite:** Install the dbt Cloud provider package. Use constraints to avoid accidental Airflow upgrades:
> ```bash
> PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
> pip install "apache-airflow-providers-dbt-cloud" \
>   --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PYTHON_VERSION}.txt"
> ```

### DbtCloudJobRunSensor — Wait for dbt Cloud job completion

```python
from airflow.providers.dbt.cloud.sensors.dbt import DbtCloudJobRunSensor

wait_for_dbt = DbtCloudJobRunSensor(
    task_id='wait_for_dbt',
    dbt_cloud_conn_id='dbt_cloud_default',
    run_id="{{ task_instance.xcom_pull(task_ids='trigger_dbt_cloud', key='return_value') }}",
    timeout=3600,
)
```

### EmailOperator — Send notifications

```python
from airflow.operators.email import EmailOperator

send_alert = EmailOperator(
    task_id='send_success_email',
    to='team@example.com',
    subject='dbt Pipeline Completed',
    html_content='<p>All models built and tested successfully.</p>',
)
```

---

## Setting Up Connections

**Why:** Operators need credentials to talk to external systems. Airflow Connections store these securely.

### Add a dbt Cloud Connection

1. In the Airflow UI → **Admin → Connections**
2. Click **+ (Add new record)**
3. Configure:

| Field | Value |
|-------|-------|
| Connection Id | `dbt_cloud_default` |
| Connection Type | `dbt Cloud` |
| Account ID | Your dbt Cloud account ID (found in URL: `cloud.getdbt.com/deploy/{account_id}/...`) |
| API Token | Your dbt Cloud API token |

4. Click **Save**

### Generate a dbt Cloud API Token

1. In dbt Cloud → click your profile icon → **Account Settings**
2. Navigate to **API Access → Service Tokens**
3. Click **+ New Token**
4. Name: `airflow-integration`
5. Permissions: **Job Admin** (minimum: ability to trigger and read jobs)
6. Copy the token — you will not see it again

### Add a Snowflake Connection (optional)

1. In Airflow UI → **Admin → Connections**
2. Click **+**
3. Configure:

| Field | Value |
|-------|-------|
| Connection Id | `snowflake_default` |
| Connection Type | `Snowflake` |
| Host | `<your_account>.snowflakecomputing.com` |
| Schema | `ANALYTICS` |
| Login | `DBT_USER` |
| Password | `StrongPassword@123` |
| Extra | `{"database": "OLIST_DB", "warehouse": "COMPUTE_WH", "role": "DBT_ROLE"}` |

4. Click **Save**

---

## Building a dbt Pipeline DAG

**Why:** This is the pattern you will see in Module 09, Lab 4. It ties together everything above — operators, connections, and dependencies — into a real dbt orchestration workflow.

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from airflow.operators.email import EmailOperator

default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'email_on_failure': True,
    'email': ['data-team@example.com'],
}

with DAG(
    dag_id='dbt_production_pipeline',
    description='Trigger dbt Cloud production job daily',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='0 6 * * *',       # Daily at 6:00 AM UTC
    catchup=False,
    tags=['dbt', 'production'],
) as dag:

    # Step 1: Trigger the dbt Cloud job
    run_dbt = DbtCloudRunJobOperator(
        task_id='trigger_dbt_build',
        dbt_cloud_conn_id='dbt_cloud_default',
        job_id=12345,               # Replace with your Job ID
        check_interval=30,
        timeout=3600,
    )

    # Step 2: Notify on success
    notify_success = EmailOperator(
        task_id='send_success_email',
        to='data-team@example.com',
        subject='dbt Production Build — SUCCESS',
        html_content='<p>All dbt models built and tested. Check dbt Cloud for details.</p>',
    )

    # Dependencies
    run_dbt >> notify_success
```

### How this works step by step:

1. **6:00 AM UTC** — Airflow scheduler detects it is time to run
2. `trigger_dbt_build` calls the dbt Cloud API to start Job #12345
3. The operator polls every 30 seconds until the job finishes
4. If the job succeeds → `send_success_email` runs
5. If the job fails → Airflow retries twice (from `default_args`), then sends a failure email

---

## Airflow CLI Reference

| Command | Purpose |
|---------|---------|
| `airflow dags list` | List all discovered DAGs |
| `airflow dags trigger <dag_id>` | Manually trigger a DAG |
| `airflow tasks test <dag_id> <task_id> <date>` | Run a single task (for debugging) |
| `airflow dags test <dag_id>` | Run entire DAG without recording to DB |
| `airflow db migrate` | Apply database migrations |
| `airflow webserver` | Start the web UI |
| `airflow scheduler` | Start the scheduler |
| `airflow connections list` | List all configured connections |
| `airflow info` | Show Airflow environment info |

---

## Airflow vs dbt Cloud Scheduling — When to Use Each

| Scenario | Use dbt Cloud Scheduling | Use Airflow |
|----------|-------------------------|-------------|
| dbt is your only tool | Yes | Overkill |
| dbt runs after an Airbyte/Fivetran extract | Possible (webhook) | Better — Airflow manages the chain |
| Multiple teams share a pipeline | Difficult | Yes — Airflow is the central orchestrator |
| You need conditional logic (if X fails, do Y) | Limited | Yes — Airflow has branching, sensors, XCom |
| You want approval gates before prod deploy | No | Yes — manual triggers and sensors |
| Quick setup, no infrastructure team | Yes | No — Airflow needs hosting |

---

## Glossary

| Term | Definition |
|------|-----------|
| **DAG** | Directed Acyclic Graph — a workflow defined in Python |
| **Task** | A single unit of work inside a DAG |
| **Operator** | A class that defines what a task does (Bash, Python, dbt Cloud, etc.) |
| **Sensor** | An operator that waits for a condition to be met |
| **Connection** | Stored credentials for external systems (dbt Cloud, Snowflake, etc.) |
| **Variable** | Key-value config stored in Airflow metadata |
| **XCom** | Cross-communication — tasks pass small data to downstream tasks |
| **Scheduler** | Background process that triggers DAGs on schedule |
| **Executor** | How tasks are run (SequentialExecutor for local, CeleryExecutor for distributed) |
| **DAG Run** | A single execution instance of a DAG |
| **Task Instance** | A single execution of a task within a DAG Run |
| **Backfill** | Running a DAG for past dates that were missed |
| **Catchup** | Whether Airflow should backfill when a DAG is unpaused (usually `False`) |
| **Provider** | Installable package adding operators for external systems (`apache-airflow-providers-dbt-cloud`) |

---

## Verification Checklist

Before proceeding to Module 09 Lab 4, confirm:

- [ ] You understand what a DAG is (workflow as Python code)
- [ ] You can explain the difference between a Task and an Operator
- [ ] You know that `>>` sets task dependencies (execution order)
- [ ] You understand that Connections store credentials securely
- [ ] You can describe how `DbtCloudRunJobOperator` triggers a dbt Cloud job
- [ ] You know the difference between dbt Cloud scheduling and Airflow orchestration
