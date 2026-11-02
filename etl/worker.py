import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

from activities import load_csv_to_postgres, publish_to_iceberg
from workflows import CsvToIceberg


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="etl",
        workflows=[CsvToIceberg],
        activities=[load_csv_to_postgres, publish_to_iceberg],
        activity_executor=ThreadPoolExecutor(4),
    )
    await worker.run()


asyncio.run(main())
