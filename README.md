# InfluxDB 3 — Python demo ✅

This workspace contains a small, self-contained example showing how to use
InfluxDB Core 3 from Python using the `influxdb3-python` client.

## What’s included
- `examples/demo_influxdb3.py` — minimal read/write/query demo
- `.env.example` — environment variable example
- `requirements.txt` — deps for the demo (`influxdb3-python`, `pandas`)

---

## Quick start (local)

1. Create & activate a virtualenv (you already have one in this workspace):

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start a local InfluxDB 3 Core (Docker):

   ```bash
   docker run --rm -p 8181:8181 \
     influxdb:3-core influxdb3 serve \
     --node-id=node0 --object-store=file \
     --data-dir=/var/lib/influxdb3/data --plugin-dir=/var/lib/influxdb3/plugins
   ```

   After it starts, create an auth token (use the UI or the `influxdb3` CLI) and
   set the values in environment variables or a `.env` file.

4. Configure credentials (example):

   ```bash
   export INFLUX_HOST=http://localhost:8181
   export INFLUX_TOKEN="<your-token>"
   export INFLUX_DATABASE=demo
   # or copy .env.example -> .env and edit the values
   ```

5. Run the demo:

   ```bash
   python examples/demo_influxdb3.py
   ```

You should see the script write three sample points and then print the last
rows queried from the `demo_measurement` measurement.

---

## Notes & tips 💡
- The demo uses `influxdb3-python` (the lightweight v3 client). The demo will
  also pretty-print results using `pandas` if available.
- Use `.env` for local testing (the demo will load it if `python-dotenv` is
  installed).
- If you need help creating a token, use the InfluxDB UI or the `influxdb3`
  CLI that ships with the server.

---

If you want, I can also: add a Docker Compose for InfluxDB 3, add more
examples (DataFrame writes / Parquet), or make a unit test for the demo. ✨
