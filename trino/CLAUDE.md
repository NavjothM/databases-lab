# trino: catalog configuration

`catalog/` is mounted read-only at `/etc/trino/catalog` in the `trino` container. Each `*.properties` file defines one catalog; Trino reads them at startup, so run `docker compose restart trino` after any change.

- `catalog/iceberg.properties`: Iceberg connector with a **JDBC catalog** stored in Postgres database `iceberg_catalog` (needs the tables from `../initdb/02-iceberg-catalog.sql`). Warehouse is `s3://warehouse/` on MinIO (`http://minio:9000`, path-style access, region `us-east-1`).
- `catalog/postgres.properties`: PostgreSQL connector to the `app` database, so Trino can query `postgres.public.*` (used for the `CREATE TABLE AS SELECT` into Iceberg).

Credentials use `${ENV:POSTGRES_USER}`, `${ENV:POSTGRES_PASSWORD}`, `${ENV:MINIO_ROOT_USER}`, `${ENV:MINIO_ROOT_PASSWORD}`, which come from `../.env` via the compose `env_file`. Don't hardcode secrets here.

Quick checks:
```bash
docker compose exec trino trino --execute "SHOW CATALOGS"
docker compose exec trino trino --execute "SHOW SCHEMAS FROM iceberg"
docker compose logs trino | grep -i "caused by" | tail
```
Errors involving `iceberg_tables`, S3, or `minio` almost always trace back to this folder's config, the init SQL, or the `warehouse` bucket not existing.
