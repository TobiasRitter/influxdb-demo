from __future__ import annotations

import os
import requests

from influxdb_client_3 import InfluxDBClient3, Point
from fastapi import FastAPI, HTTPException
import pandas as pd


HOST = os.getenv("INFLUX_HOST", "http://localhost:8181")
TOKEN = os.getenv("INFLUX_TOKEN")
DATABASE = os.getenv("INFLUX_DATABASE", "demo")

app = FastAPI()


def write_sample(
    client: InfluxDBClient3.InfluxDBClient3, location: str, temperature: float
) -> Point:
    point = (
        Point("demo_measurement")
        .tag("location", location)
        .field("temperature", temperature)
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
            return df.to_markdown()
        else:
            return "No samples available"


@app.post("/sample")
async def add_sample(location: str, temperature: float) -> str:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        return str(write_sample(client, location, temperature))


@app.post("/reset")
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
        write_sample(client, "office", 22.5)
        write_sample(client, "lab", 23.0)
        write_sample(client, "warehouse", 19.8)
        print("Write complete.")

        df = read_samples(client)
        if df is not None:
            print(df.to_markdown())


if __name__ == "__main__":
    main()
