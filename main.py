from __future__ import annotations

import os
import sys

from influxdb_client_3 import InfluxDBClient3, Point
from fastapi import FastAPI, Request
import pandas as pd


app = FastAPI()


def write_sample_points(client: InfluxDBClient3.InfluxDBClient3) -> None:
    p1 = Point("demo_measurement").tag("location", "office").field("temperature", 22.5)
    p2 = Point("demo_measurement").tag("location", "lab").field("temperature", 23.0)
    p3 = (
        Point("demo_measurement")
        .tag("location", "warehouse")
        .field("temperature", 19.8)
    )

    client.write(p1)
    client.write(p2)
    client.write(p3)


def query_and_print(client: InfluxDBClient3.InfluxDBClient3) -> pd.DataFrame | None:
    sql = "SELECT * FROM demo_measurement ORDER BY time DESC"
    print(f"\nRunning SQL query: {sql}\n")

    try:
        df = client.query_dataframe(sql)
        print(df.to_markdown())
        return df
    except Exception as exc:
        print("Query failed:", exc, file=sys.stderr)
        return None


def main() -> None:
    HOST = os.getenv("INFLUX_HOST", "http://localhost:8181")
    TOKEN = os.getenv("INFLUX_TOKEN")
    DATABASE = os.getenv("INFLUX_DATABASE", "demo")

    if not TOKEN:
        raise ValueError(
            "INFLUX_TOKEN environment variable is required for authentication. Please set it and try again."
        )

    print(f"Connecting to InfluxDB host={HOST!r} database={DATABASE!r}")

    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        print("Writing 3 sample points...")
        write_sample_points(client)
        print("Write complete.")
        query_and_print(client)


if __name__ == "__main__":
    main()


@app.get("/")
async def root() -> str:
    return "Hello, World!"


@app.get("/greet/{name}")
async def greet(name: str) -> str:
    return f"Hello, {name}!"
