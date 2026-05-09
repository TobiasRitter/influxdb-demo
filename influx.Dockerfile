# Stage 1: Get the InfluxDB binary
FROM influxdb:3-core AS influx-source

# Stage 2: Get the Python library
FROM python:3.13-slim-bookworm AS python-source

# Stage 3: Build the final Distroless image
# 'cc-debian12' contains the necessary glibc for Rust/Python
FROM gcr.io/distroless/cc-debian12

# 1. Copy the required Python shared library
# We place it in /lib so the binary finds it without needing ldconfig
COPY --from=python-source /usr/local/lib/libpython3.13.so.1.0 /lib/libpython3.13.so.1.0

# 2. Copy the InfluxDB binary
COPY --from=influx-source /usr/bin/influxdb3 /usr/bin/influxdb3

# 3. Copy your admin token
# Note: Distroless uses UID 65532 for its built-in 'nonroot' user
COPY --chmod=644 --chown=65532:65532 admin_token.json /etc/influxdb3/admin_token.json

# 4. Set environment and execution context
ENV INFLUXDB3_ADMIN_TOKEN_FILE=/etc/influxdb3/admin_token.json
WORKDIR /var/lib/influxdb3
USER 65532

# 5. Run the database
# Distroless has no shell, so you MUST use the JSON array format (exec form)
ENTRYPOINT ["/usr/bin/influxdb3"]
CMD ["serve", "--node-id=node0", "--object-store=file", "--data-dir=/var/lib/influxdb3"]
