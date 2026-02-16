from __future__ import annotations
import os
import sys

# optional: load a local .env file if present (no hard dependency)
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    from influxdb_client_3 import InfluxDBClient3, Point
except Exception as e:
    print(
        "Missing dependency: install 'influxdb3-python' (pip install influxdb3-python)",
        file=sys.stderr,
    )
    raise

HOST = os.getenv("INFLUX_HOST", "http://localhost:8181")
TOKEN = os.getenv("INFLUX_TOKEN", "")
DATABASE = os.getenv("INFLUX_DATABASE", "demo")

if not TOKEN:
    print(
        "Warning: INFLUX_TOKEN is empty — the demo may fail if the server requires auth.",
        file=sys.stderr,
    )


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
        # convenience: returns a pandas DataFrame when pandas is installed
        df = client.query_dataframe(sql)

        # pretty-print if pandas available
        try:
            import pandas as pd  # noqa: F401

            print(df.to_markdown())
        except Exception:
            print(df)

    except Exception as exc:  # pragma: no cover - runtime network/credentials
        print("Query failed:", exc, file=sys.stderr)


def main() -> None:
    print(f"Connecting to InfluxDB host={HOST!r} database={DATABASE!r}")

    client = InfluxDBClient3(token=TOKEN, host=HOST, database=DATABASE)
    with client:
        print("Writing 3 sample points...")
        write_sample_points(client)
        print("Write complete.")

        query_and_print(client)


if __name__ == "__main__":
    main()
