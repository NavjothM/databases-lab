# etl: Temporal workflow that loads a CSV into Postgres and publishes it to Iceberg

Standalone `uv` project (deps: `temporalio`, `psycopg[binary]`, `trino`). Runs on the host and talks to the Databases stack over localhost.

## Files
- `workflows.py`: `CsvToIceberg` workflow; runs two activities in order (2 min and 5 min timeouts).
- `activities.py`:
  - `load_csv_to_postgres(csv_path)`: creates `orders` if missing, `TRUNCATE`s, bulk inserts. Idempotent. DSN `postgresql://postgres:postgres@localhost:5432/app`.
  - `publish_to_iceberg()`: via Trino (`localhost:8080`, user `etl`): creates schema `iceberg.demo`, drops and recreates `iceberg.demo.orders` with `CREATE TABLE AS SELECT * FROM postgres.public.orders`.
- `worker.py`: Temporal worker on task queue `etl` (sync activities need the `ThreadPoolExecutor`).
- `run.py`: starts one workflow run and prints the result.
- `data/orders.csv`: sample data (5 rows).

## Run
```bash
uv sync
uv run python worker.py     # terminal 1, leave running
uv run python run.py        # terminal 2; expect "loaded 5 rows to Postgres, 5 rows in Iceberg"
```
Check: `docker compose exec trino trino --execute "SELECT * FROM iceberg.demo.orders"` (from `../`), and the run in the Temporal UI at http://localhost:8081.

## Notes
- Prereqs: the `../` Docker stack is up and Trino is healthy; the Trino `postgres` catalog exists (`../trino/catalog/postgres.properties`).
- Temporal retries failed activities by default (5 attempts here); a stuck workflow can be terminated from the UI.
- Task queue name (`etl`) must match in `worker.py` and `run.py`.
- Planned improvements: incremental loads instead of truncate/drop, data-quality checks as an activity, scheduled runs, and switching table creation to Alembic migrations.
