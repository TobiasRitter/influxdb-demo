from __future__ import annotations

from dataclasses import dataclass
import os
import requests

from influxdb_client_3 import InfluxDBClient3, Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd


HOST = os.getenv("INFLUX_HOST", "http://localhost:8181")
DATABASE = os.getenv("INFLUX_DATABASE", "demo")
TOKEN = os.getenv("INFLUX_TOKEN")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class Sample:
    value: float
    timestamp: int
    unit: str
    signal_id: str


def write_sample(
    client: InfluxDBClient3.InfluxDBClient3,
    measurement: str,
    sample: Sample,
) -> Point:
    point = (
        Point(measurement)
        .field("value", sample.value)
        .time(sample.timestamp)
        .tag("unit", sample.unit)
        .tag("signal_id", sample.signal_id)
    )
    client.write(point)
    return point


def read_samples(
    client: InfluxDBClient3.InfluxDBClient3, measurement: str
) -> pd.DataFrame | None:
    sql = f"SELECT * FROM {measurement} ORDER BY time DESC"

    try:
        df = client.query_dataframe(sql)
        return df
    except Exception as exc:
        print(f"Error reading samples: {exc}")
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


@app.get("/samples/{measurement}")
async def get_samples(measurement: str) -> str:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        df = read_samples(client, measurement)
        if df is not None:
            return df.to_json(orient="records")
        else:
            return "No samples available"


@app.post("/samples")
async def add_samples(
    measurement: str,
    samples: list[Sample],
) -> list[str]:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        inserted = [write_sample(client, measurement, sample) for sample in samples]
        return [str(point) for point in inserted]


@app.delete("/reset")
async def reset_endpoint() -> dict:
    result = reset_database()
    return {"status": "ok", "result": result}
