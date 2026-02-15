# Airflow Quickstart for dbt Cloud

**Prerequisite:** This guide assumes you are running on **CentOS Stream 9** (like the provided Labs VM) or a similar Linux environment with **Python 3.9+**.

---

## 1. Environment Setup

Airflow 2.9.x requires a specific constraint file to ensure dependency stability. We will create a dedicated virtual environment.

### Step 1: Create Virtual Environment

```bash
cd ~
mkdir -p airflow-lab
cd airflow-lab
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Airflow 2.9.3

We typically use the constraint file for our specific Python version.

```bash
# Get Python version (e.g., 3.9, 3.11)
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"

# Install Airflow
pip install "apache-airflow==2.9.3" \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PYTHON_VERSION}.txt"
```

### Step 3: Initialize Airflow

Set the home directory and initialize the database (SQLite by default).

```bash
export AIRFLOW_HOME=~/airflow-lab/airflow_home
airflow db migrate
```

### Step 4: Create Admin User

```bash
airflow users create \
    --username admin \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org \
    --password admin
```

### Step 5: Start Services

You need two terminals (or run in background with `-D`).

**Terminal 1 (Scheduler):**
```bash
source ~/airflow-lab/venv/bin/activate
export AIRFLOW_HOME=~/airflow-lab/airflow_home
airflow scheduler
```

**Terminal 2 (Webserver):**
```bash
source ~/airflow-lab/venv/bin/activate
export AIRFLOW_HOME=~/airflow-lab/airflow_home
airflow webserver --port 8080
```

Access the UI at [http://localhost:8080](http://localhost:8080).

---

## 2. Install dbt Cloud Provider

To trigger dbt Cloud jobs, we need the official provider package.

```bash
# Stop the scheduler/webserver with Ctrl+C if running in foreground
# Or just run this in your active venv terminal

pip install "apache-airflow-providers-dbt-cloud" \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-${PYTHON_VERSION}.txt"
```

**Important:** After installing new packages, you must restart the Airflow Scheduler and Webserver.

---

## 3. Configure dbt Cloud Connection

1.  **Get Credentials:**
    *   **Account ID:** From your dbt Cloud URL (e.g., `cloud.getdbt.com/deploy/12345/projects...` -> `12345`).
    *   **API Token:** Go to **Account Settings** -> **API Access** -> **Service Tokens**. Create a new token with "Job Admin" permissions.

2.  **Add Connection in Airflow UI:**
    *   Go to **Admin** -> **Connections**.
    *   Click **+**.
    *   **Connection Id:** `dbt_cloud_default`
    *   **Connection Type:** `dbt Cloud`
    *   **Account ID:** `<YOUR_ACCOUNT_ID>`
    *   **API Token:** `<YOUR_API_TOKEN>`
    *   Click **Save**.

---

## 4. Troubleshooting common issues

### "Command not found: airflow"
Make sure you activated your virtual environment:
```bash
source ~/airflow-lab/venv/bin/activate
```

### "Provider not found"
If Airflow doesn't see `dbt_cloud_default` connection type:
1.  Verify installation: `pip list | grep dbt`
2.  Restart the Webserver.
