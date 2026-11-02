from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import load_csv_to_postgres, publish_to_iceberg


@workflow.defn
class CsvToIceberg:
    @workflow.run
    async def run(self, csv_path: str) -> str:
        loaded = await workflow.execute_activity(
            load_csv_to_postgres, csv_path, start_to_close_timeout=timedelta(minutes=2)
        )
        published = await workflow.execute_activity(
            publish_to_iceberg, start_to_close_timeout=timedelta(minutes=5)
        )
        return f"loaded {loaded} rows to Postgres, {published} rows in Iceberg"
