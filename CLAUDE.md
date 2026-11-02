# Databases: local data stack for learning databases and ETL

Docker Compose stack plus two small `uv` projects (`alembic/`, `etl/`). Git repo: `NavjothM/databases-lab` (private).

## Services (`docker-compose.yml`)
| Service | Image | Notes |
|---|---|---|
| `postgres` | `postgres:17` | Port 5432. Databases: `app`, `iceberg_catalog`, plus Temporal's own. Volume `pgdata`. |
| `minio` | `pgsty/silo` (MinIO fork) | S3 API 9000, console 9001. Volume `miniodata`. Service is still *named* `minio`. |
| `minio-init` | `amazon/aws-cli` | One-shot: creates the `warehouse` bucket. |
| `trino` | `trinodb/trino` | Port 8080. Catalogs in `trino/catalog/`. |
| `temporal` | `temporalio/auto-setup` | gRPC 7233, stores data in Postgres. |
| `temporal-ui` | `temporalio/ui` | Port 8081 (mapped from 8080). |

Images are pinned by digest (`tag@sha256:...`). To upgrade: remove the digest, `docker compose pull`, test, re-pin.

## How the data flows
CSV -> Temporal workflow (`etl/`) -> Postgres `app.public.orders` -> Trino `CREATE TABLE AS SELECT` -> Iceberg table `iceberg.demo.orders`. Iceberg metadata is a JDBC catalog stored in Postgres (`iceberg_catalog` DB); data files are Parquet in `s3://warehouse/` on MinIO.

## Commands
```bash
docker compose up -d
until docker compose exec -T trino trino --execute "SELECT 1" >/dev/null 2>&1; do sleep 3; done   # Trino needs ~30s
docker compose exec trino trino                     # SQL shell
docker compose exec postgres psql -U postgres -d app
docker compose logs trino | grep -i "caused by"     # first place to look for Trino errors
docker compose stop        # pause, keeps data
docker compose down -v     # DESTROYS all data. Ask first.
```
UIs: Trino http://localhost:8080 (any username, no password), Temporal http://localhost:8081, MinIO http://localhost:9001 (`minioadmin`/`minioadmin`).

## Gotchas
- `initdb/*.sql` only run when Postgres starts with an **empty** volume. Changes there need `down -v` to take effect (or run the SQL manually with `psql`).
- The Iceberg JDBC catalog needs the `iceberg_tables` and `iceberg_namespace_properties` tables to exist; `initdb/02-iceberg-catalog.sql` creates them. Without them Trino fails with "Cannot check and eventually update SQL schema".
- MinIO's official Docker images were removed from Docker Hub/Quay (Sept 2026), hence the fork. If it breaks, alternatives are SeaweedFS or Garage.
- Credentials come from `.env` (git-ignored; `.env.example` has placeholders) and are also hardcoded in `docker-compose.yml` for Temporal and `minio-init`; keep them in sync if changed.
- `docker-compose.yml.bak` is a stale backup from the pinning step; safe to delete.
- Other folders (`../Backend`, `../ML`) connect to these services over localhost or the `databases_default` Docker network.
