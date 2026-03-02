#!/usr/bin/env bash
# Simple backup helper for the influxdb3-core instance in this repo.
# Usage: ./backup.sh [output-dir]
# If no directory is supplied it defaults to "backup" in the current working
# directory.  The script tries to obtain a valid token from the environment
# variable INFLUXDB3_ADMIN_TOKEN or from the local admin_token.json file.

set -euo pipefail

OUTDIR=${1:-backup}
mkdir -p "$OUTDIR"

# determine token
if [[ -n "${INFLUXDB3_ADMIN_TOKEN:-}" ]]; then
    TOKEN="$INFLUXDB3_ADMIN_TOKEN"
elif [[ -f admin_token.json ]]; then
    # assume JSON has a field named "token"
    if command -v jq >/dev/null 2>&1; then
        TOKEN=$(jq -r '.token' admin_token.json)
    else
        echo "need jq to parse admin_token.json or set INFLUXDB3_ADMIN_TOKEN" >&2
        exit 1
    fi
else
    echo "no token found: set INFLUXDB3_ADMIN_TOKEN or provide admin_token.json" >&2
    exit 1
fi

# perform backup
influx backup \
    --host http://localhost:8181 \
    --token "$TOKEN" \
    --output "$OUTDIR"

echo "backup completed in $OUTDIR"
