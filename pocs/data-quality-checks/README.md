# POC: data-quality checks on synthetic retail orders

**Status:** implemented and tested on synthetic data. Not connected to any real data source or warehouse.

## What it does
Runs a set of deterministic data-quality checks over a generated `orders` table and a `customers` table, then writes a JSON report and prints a summary. Each check returns one of three statuses:

- `pass`: the rule was evaluated and held
- `fail`: the rule was evaluated and found a problem
- `skipped`: the rule could not be evaluated, for example because a column is missing. A skipped check is never reported as a pass.

## Checks

| Check | Rule |
|---|---|
| `orders.schema` | Required columns are present |
| `not_null:<col>` | Required keys are present and non-blank |
| `unique:order_id` | No duplicate order IDs (every member of a duplicate group is counted) |
| `non_negative:amount` | Amounts are numeric and not negative |
| `allowed_values:status` | Status is one of the allowed values |
| `valid_dates:order_date` | Dates parse as ISO-8601 (catches impossible dates such as 2026-02-31) |
| `freshness:order_date` | The latest order is within `max_age_days` (default 2) of the reference date |
| `referential:customer_id->customer_id` | Every order's customer exists in `customers` |
| `row_count_band` | Row count is within 3 standard deviations of the historical counts. Needs at least 3 history values. |
| `customers.schema`, `not_null`, `unique` | Basic checks on the customers table |

The reference date is fixed (`2026-11-20`), not today's date, so runs are reproducible.

## Run it

```bash
cd pocs/data-quality-checks
uv sync                                  # creates .venv (gitignored)
uv run python -m dq.run                  # clean synthetic data -> exit code 0
uv run python -m dq.run --inject-defects # known defects -> exit code 1
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
```

Output is written to `output/dq_report.json` (gitignored).

## Known defects
`--inject-defects` modifies fixed rows, so the tests can check exactly which checks fire:

| Row | Defect | Expected check |
|---|---|---|
| 3 | `order_id` null | `not_null:order_id` (1 row) |
| 10 | `order_id` copied from row 9 | `unique:order_id` (2 rows) |
| 20 | `amount` = -15.0 | `non_negative:amount` (1 row) |
| 30 | `status` = "lost" | `allowed_values:status` (1 row) |
| 40 | `customer_id` = C9999 | `referential:customer_id->customer_id` (1 row) |
| 50 | `order_date` = 2026-02-31 | `valid_dates:order_date` (1 row) |

## Design notes
- Plain Python rules, no LLM. An LLM could later explain the failures, using this report as structured input. See `memory/TECHNICAL_DECISIONS.md` TD-004.
- Checks never raise on bad input. Missing columns and empty inputs produce `fail` or `skipped` results.
- Synthetic data only. Real data would need approval and a separate config (see `CLAUDE.md` §3).

## Limitations
- Row-count band uses only five hard-coded history values. A real pipeline would read history from a metrics store.
- Freshness uses a single date column.
- pandas holds the data in memory. This is fine for a POC, not for large tables.
- No scheduling, alerting or persistence of results beyond the JSON file.
