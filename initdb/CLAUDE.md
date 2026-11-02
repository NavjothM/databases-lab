# initdb: Postgres first-boot SQL

Mounted read-only at `/docker-entrypoint-initdb.d` in the `postgres` container. Scripts run in filename order, **only when the data volume is empty** (first start or after `docker compose down -v`).

- `01-create-dbs.sql`: creates databases `app` and `iceberg_catalog`.
- `02-iceberg-catalog.sql`: connects to `iceberg_catalog` (`\c`) and creates `iceberg_tables` and `iceberg_namespace_properties`, the tables Trino's Iceberg JDBC catalog requires.

Editing these files does nothing to a running database. To apply a change to an existing one, run the SQL manually (`docker compose exec -T postgres psql -U postgres -d <db>`) or reset with `down -v` (destroys data; ask first). Keep scripts idempotent (`IF NOT EXISTS`). Do not put table definitions for `app` here; those belong in Alembic migrations.
