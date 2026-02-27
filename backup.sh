#!/usr/bin/env bash
# backup.sh - simple online backup for the demo InfluxDB 3 instance
#
# Usage:
#   ./backup.sh [measurement] [output-file]
#
# If no measurement is provided the entire database is exported using
# `SELECT * FROM <measurement>` and you will be prompted for a table name.
# The script writes line-protocol by default but you can change the format
# by editing the --format flag.  It requires the following environment
# variables to be set (just like the Python demo):
#
#   INFLUX_HOST   e.g. http://localhost:8181
#   INFLUX_TOKEN  your admin or read token
#   INFLUX_DATABASE  the database to dump (\"demo\" in the example repo)
#
# Examples:
#   export INFLUX_HOST=http://localhost:8181
#   export INFLUX_TOKEN=...
#   export INFLUX_DATABASE=demo
#   ./backup.sh demo_measurement backup.parquet

# detect if sourced (causes your shell to exit due to set -euo pipefail)
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
    echo "This script should be executed, not sourced." >&2
    return 1 2>/dev/null || exit 1
fi

set -euo pipefail

token=${INFLUX_TOKEN:?"INFLUX_TOKEN environment variable not set; export a token before running the script"}
host=${INFLUX_HOST:-http://localhost:8181}
db=${INFLUX_DATABASE:-demo}

measurement=${1:-}
outfile=${2:-}

if [[ -z \"$measurement\" ]]; then
  echo "Measurement not supplied. Please enter the table/measurement name:" >&2
  read -r measurement
fi

if [[ -z "$outfile" ]]; then
  outfile="${measurement}_$(date +%F_%H%M%S).parquet"
  echo "No output file given, writing to $outfile" >&2
fi

sql="SELECT * FROM ${measurement}"

# perform query and write to file in the requested format
influxdb3 query \
  --host "$host" \
  --token "$token" \
  --database "$db" \
  --format parquet \
  --output "$outfile" \
  "$sql"

echo "Backup of $measurement written to $outfile" >&2
