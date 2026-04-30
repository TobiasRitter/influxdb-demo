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
    signal_id: str


def get_measurements(
    client: InfluxDBClient3.InfluxDBClient3,
) -> list[str] | None:
    sql = "SHOW TABLES"

    try:
        df = client.query_dataframe(sql)
        print(f"Measurements found: {df.head()}")
        return df["table_name"].tolist()
    except Exception as exc:
        print(f"Error reading measurements: {exc}")
        return None


def get_signals(
    client: InfluxDBClient3.InfluxDBClient3, measurement: str
) -> list[str] | None:
    quoted_measurement = measurement.replace('"', '""')
    sql = f'SELECT DISTINCT signal_id FROM "{quoted_measurement}"'

    try:
        df = client.query_dataframe(sql)
        print(f"Signals found for measurement {measurement}: {df.head()}")
        return df["signal_id"].tolist()
    except Exception as exc:
        print(f"Error reading signals: {exc}")
        return None


def read_samples(
    client: InfluxDBClient3.InfluxDBClient3,
    measurement: str,
    signal_id: str,
) -> pd.DataFrame | None:
    quoted_measurement = measurement.replace('"', '""')
    sql = (
        f'SELECT * FROM "{quoted_measurement}" '
        f"WHERE signal_id = '{signal_id}' "
        "ORDER BY time DESC"
    )

    try:
        df = client.query_dataframe(sql)
        return df
    except Exception as exc:
        print(f"Error reading samples: {exc}")
        return None


def write_samples(
    client: InfluxDBClient3.InfluxDBClient3,
    measurement: str,
    samples: list[Sample],
) -> list[Point]:
    points = [
        (
            Point(measurement)
            .field("value", sample.value)
            .time(sample.timestamp)
            .tag("signal_id", sample.signal_id)
        )
        for sample in samples
    ]
    client.write(points)
    return points


def drop_measurement(
    client: InfluxDBClient3.InfluxDBClient3,
    measurement: str,
) -> str | None:
    quoted_measurement = measurement.replace('"', '""')
    sql = f'DROP TABLE "{quoted_measurement}"'
    try:
        client.query(sql)
        return measurement
    except Exception as exc:
        print(f"Error deleting measurement: {exc}")
        return None


@app.get("/")
async def root() -> list[str] | None:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        return get_measurements(client)


@app.get("/{measurement}")
async def get_measurement_signals(measurement: str) -> list[str]:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        signals = get_signals(client, measurement)
        if signals is not None:
            return signals
        else:
            return []


@app.get("/{measurement}/{signal_id}")
async def get_samples(measurement: str, signal_id: str) -> str:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        df = read_samples(client, measurement, signal_id)
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
        inserted = write_samples(client, measurement, samples)
        return [str(point) for point in inserted]


@app.delete("/{measurement}")
async def delete_measurement(measurement: str) -> str | None:
    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        return drop_measurement(client, measurement)
