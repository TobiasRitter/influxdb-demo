from __future__ import annotations

import os
import requests

from influxdb_client_3 import InfluxDBClient3, Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd


HOST = "http://localhost:8181"
DATABASE = "demo"
TOKEN = os.getenv("INFLUX_TOKEN")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def write_sample(
    client: InfluxDBClient3.InfluxDBClient3,
    current: float,
    timestamp: int,
) -> Point:
    point = (
        Point("demo_measurement")
        .field("current", current)
        .time(timestamp)
        .tag("unit", "A")
    )
    client.write(point)
    return point


def read_samples(client: InfluxDBClient3.InfluxDBClient3) -> pd.DataFrame | None:
    sql = "SELECT * FROM demo_measurement ORDER BY time DESC"
    print(f"\nRunning SQL query: {sql}\n")

    try:
        df = client.query_dataframe(sql)
        return df
    except Exception as exc:
        return None


def reset_database() -> str:
    base = HOST.rstrip("/")
    headers = {"Authorization": f"Bearer {TOKEN}"}

    url = f"{base}/api/v3/configure/table"
    params = {"db": DATABASE, "table": "demo_measurement"}
    resp = requests.delete(url, headers=headers, params=params, timeout=10)

    if resp.status_code in (200, 204):
        return f"table demo_measurement deleted (status {resp.status_code})"

    if resp.status_code == 404:
        return f"table demo_measurement not found (status 404)"

    raise RuntimeError(f"failed to delete table: {resp.status_code} {resp.text}")


@app.get("/")
async def root() -> str:
    return "Hello, World!"


@app.get("/samples")
async def get_samples() -> str:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        df = read_samples(client)
        if df is not None:
            return df.to_json(orient="records")
        else:
            return "No samples available"


@app.post("/sample")
async def add_sample(
    current: float,
    timestamp: int,
) -> str:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        return str(write_sample(client, current, timestamp))


@app.delete("/reset")
async def reset_endpoint() -> dict:
    result = reset_database()
    return {"status": "ok", "result": result}


def main() -> None:
    if not TOKEN:
        raise ValueError(
            "INFLUX_TOKEN environment variable is required for authentication. Please set it and try again."
        )

    print(f"Connecting to InfluxDB host={HOST!r} database={DATABASE!r}")

    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        print("Writing 3 sample points...")
        write_sample(client, 1, 100000000)
        write_sample(client, 2, 200000000)
        write_sample(client, 3, 300000000)
        print("Write complete.")

        df = read_samples(client)
        if df is not None:
            print(df.to_markdown())


if __name__ == "__main__":
    main()
