from __future__ import annotations

import os

from influxdb_client_3 import InfluxDBClient3, Point
from fastapi import FastAPI
import pandas as pd


app = FastAPI()


def add_sample(
    client: InfluxDBClient3.InfluxDBClient3, location: str, temperature: float
) -> None:
    point = (
        Point("demo_measurement")
        .tag("location", location)
        .field("temperature", temperature)
    )
    client.write(point)


def get_samples(client: InfluxDBClient3.InfluxDBClient3) -> pd.DataFrame | None:
    sql = "SELECT * FROM demo_measurement ORDER BY time DESC"
    print(f"\nRunning SQL query: {sql}\n")

    try:
        df = client.query_dataframe(sql)
        return df
    except Exception as exc:
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
        add_sample(client, "office", 22.5)
        add_sample(client, "lab", 23.0)
        add_sample(client, "warehouse", 19.8)
        print("Write complete.")

        df = get_samples(client)
        if df is not None:
            print(df.to_markdown())


if __name__ == "__main__":
    main()


@app.get("/")
async def root() -> str:
    return "Hello, World!"


@app.get("/greet/{name}")
async def greet(name: str) -> str:
    return f"Hello, {name}!"
