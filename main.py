from __future__ import annotations

import os
import sys

from influxdb_client_3 import InfluxDBClient3, Point


def write_sample_points(client: InfluxDBClient3.InfluxDBClient3) -> None:
    p1 = Point("demo_measurement").tag("location", "office").field("temperature", 22.5)
    p2 = Point("demo_measurement").tag("location", "lab").field("temperature", 23.0)
    p3 = (
        Point("demo_measurement")
        .tag("location", "warehouse")
        .field("temperature", 19.8)
    )

    # write (client was created with a default database)
    client.write(p1)
    client.write(p2)
    client.write(p3)


def query_and_print(client: InfluxDBClient3.InfluxDBClient3) -> None:
    sql = "SELECT * FROM demo_measurement ORDER BY time DESC LIMIT 10"
    print(f"\nRunning SQL query: {sql}\n")

    try:
        df = client.query_dataframe(sql)
        print(df.to_markdown())
    except Exception as exc:
        print("Query failed:", exc, file=sys.stderr)


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
