# dbt CLI vs dbt Cloud

## Two Ways to Run dbt

dbt can be used in two primary ways:

1. Locally through the Command Line Interface (CLI)
2. Through the hosted dbt Cloud platform

Both execute the same dbt core engine.

The difference is **where** and **how** dbt runs.

---

## dbt CLI (Local Execution)

You install dbt on your machine.

Your laptop executes dbt and connects directly to your warehouse.

You manage all configuration and credentials.

---

## dbt CLI Capabilities

* Run models
* Run tests
* Compile SQL
* Generate docs
* Use packages
* Create snapshots

Same capabilities as Cloud.

---

## Pros of dbt CLI

 - ✅ Full control
 - ✅ No vendor lock-in
 - ✅ Works offline (except warehouse)
 - ✅ Easy integration with GitHub
 - ✅ Good for learning

---

## Cons of dbt CLI

❌ You manage scheduling
❌ You manage credentials
❌ No built-in UI

---

## dbt Cloud

dbt Cloud is a hosted service.

It provides:

* Browser IDE
* Managed execution
* Scheduler
* Logs
* Documentation hosting

You push code.

Cloud runs dbt.

---

## dbt Cloud Capabilities

* Run models
* Schedule jobs
* View lineage
* Build docs
* Monitor runs

---

## Pros of dbt Cloud

 - ✅ No local setup
 - ✅ Built-in scheduler
 - ✅ Web UI
 - ✅ Centralized logs

---

## Cons of dbt Cloud

❌ Cost
❌ Less flexible than CLI
❌ Harder to debug locally

---

## Feature Comparison

| Feature            | dbt CLI      | dbt Cloud   |
| ------------------ | ------------ | ----------- |
| Execution Location | Your machine | Cloud       |
| IDE                | Local editor | Browser IDE |
| Scheduler          | External     | Built-in    |
| Cost               | Free         | Paid tiers  |
| Debugging          | Excellent    | Moderate    |

---

## Pricing (High Level)

* dbt CLI: Free
* dbt Cloud: Free tier + Paid plans

Pricing changes frequently.

Check official site for details.

---

## When to Use dbt CLI

* Learning dbt
* Local development
* Small teams
* CI pipelines

---

## When to Use dbt Cloud

* Production scheduling
* Centralized management
* Large teams

---

## Common Team Pattern

Hybrid approach:

* Engineers develop locally using CLI
* Production runs in dbt Cloud

Same project.

Same code.

---

## Important Concept

The dbt project is identical.

Only the execution environment changes.

---

## Mental Model

Think of dbt Cloud as a hosted computer that runs dbt for you.

---

## Summary

You do not choose between two different dbts.

You choose where dbt runs.

---
