---
name: data-engineering
description: Use for data engineering work in this repo: ETL and ELT pipelines, dbt models and tests, Airflow DAGs, Snowflake SQL and performance, AWS Glue, and data-quality checks. Trigger on requests to build, test, or debug a pipeline, a transformation, or a data-quality rule.
---

# Data engineering

Follow `CLAUDE.md` §3 and §5. Use this checklist.

## 1. Understand the data first
- Write down the source, grain (one row per what?), keys, expected volume, and freshness requirement.
- Confirm ambiguous business rules before coding them. Record the assumptions in the POC README.

## 2. Build in layers
- Ingest raw data unchanged. Transform in separate steps. Keep each step testable.
- Make transformations idempotent: re-running a load must not duplicate rows.
- Keep environment-specific values (connections, schemas, dates) in configuration, not code.

## 3. Data-quality checks
For each table, cover at least:
- Schema: required columns are present, and their types are correct.
- Nulls on required keys.
- Uniqueness of primary keys.
- Referential integrity between related tables.
- Valid ranges and allowed values.
- Freshness: the latest record is recent enough.
- Volume: row count within the expected band.

Write checks as code, with a test that feeds in known-bad data and expects the check to fire.

## 4. dbt and Airflow
- dbt: every model has a schema YAML with tests on its keys. Run `dbt build` locally before proposing changes.
- Airflow: keep DAGs thin. Put logic in importable functions. Set retries, and set a timeout on every task.
- Do not hardcode credentials. Use the connection and secrets store.

## 5. Performance
- Measure before optimising. Record the query, row counts and runtime.
- Check clustering, warehouse size and predicate pushdown before adding new tables.

## 6. Validation and reporting
- Run the tests and quality checks, and record the real results in `docs/VALIDATION.md`.
- State clearly which runs used synthetic data and which used real data (real data only with approval).
