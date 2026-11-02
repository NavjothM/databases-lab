import asyncio
import uuid
from pathlib import Path

from temporalio.client import Client

from workflows import CsvToIceberg


async def main():
    client = await Client.connect("localhost:7233")
    csv_path = str(Path(__file__).parent / "data" / "orders.csv")
    result = await client.execute_workflow(
        CsvToIceberg.run,
        csv_path,
        id=f"csv-to-iceberg-{uuid.uuid4()}",
        task_queue="etl",
    )
    print(result)


asyncio.run(main())
