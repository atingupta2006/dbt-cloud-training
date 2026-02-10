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

## Lab 4: Trigger dbt Cloud Job from Airflow (15 min)

**Why:** In enterprise environments, dbt is one piece of a larger data pipeline. Airflow (or similar tools) orchestrates ingestion, dbt transformation, and downstream dashboards in sequence.

### Steps

This lab is an instructor-led demonstration. Students observe and discuss.

1. Instructor shows example Airflow DAG code with:
   - `DbtCloudRunJobOperator` — triggers a dbt Cloud job
   - `DbtCloudJobRunSensor` — waits for job completion

2. Key parameters:
   - `account_id` — your dbt Cloud account
   - `job_id` — the job to trigger
   - API token for authentication

3. DAG flow: Airflow task triggers dbt Cloud job → sensor waits → downstream tasks proceed only after dbt succeeds

4. Discussion: When to use Cloud scheduling vs. external orchestration.
