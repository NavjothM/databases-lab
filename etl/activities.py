import csv

import psycopg
import trino
from temporalio import activity

PG_DSN = "postgresql://postgres:postgres@localhost:5432/app"


@activity.defn
def load_csv_to_postgres(csv_path: str) -> int:
    with open(csv_path, newline="") as f:
        rows = [
            (int(r["order_id"]), r["customer"], r["amount"], r["order_date"])
            for r in csv.DictReader(f)
        ]
    with psycopg.connect(PG_DSN) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                   order_id   integer PRIMARY KEY,
                   customer   text,
                   amount     numeric(10,2),
                   order_date date)"""
        )
        conn.execute("TRUNCATE orders")
        with conn.cursor() as cur:
            cur.executemany("INSERT INTO orders VALUES (%s, %s, %s, %s)", rows)
    return len(rows)


@activity.defn
def publish_to_iceberg() -> int:
    conn = trino.dbapi.connect(host="localhost", port=8080, user="etl")
    cur = conn.cursor()

    def run(sql):
        cur.execute(sql)
        return cur.fetchall()

    run("CREATE SCHEMA IF NOT EXISTS iceberg.demo")
    run("DROP TABLE IF EXISTS iceberg.demo.orders")
    run("CREATE TABLE iceberg.demo.orders AS SELECT * FROM postgres.public.orders")
    return run("SELECT count(*) FROM iceberg.demo.orders")[0][0]
