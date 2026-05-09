# Stage 1: Get the InfluxDB binary
FROM influxdb:3-core AS influx-source

# Stage 2: Get the Python library
FROM python:3.13-slim-bookworm AS python-source

# Stage 3: Build the final tiny image
FROM debian:bookworm-slim

# 1. Install tini (essential for signal handling)
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1001 influxuser

# 2. Copy ONLY the required Python shared library
# This satisfies the 'libpython3.13.so.1.0' dependency without the full Python install
COPY --from=python-source /usr/local/lib/libpython3.13.so.1.0 /usr/local/lib/libpython3.13.so.1.0

# 3. Tell the system where to find that library
RUN ldconfig

# 4. Copy the InfluxDB binary
COPY --from=influx-source /usr/bin/influxdb3 /usr/bin/influxdb3

# 5. Set up directories and permissions
RUN mkdir -p /var/lib/influxdb3 /etc/influxdb3 && \
    chown -R 1001:1001 /var/lib/influxdb3 /etc/influxdb3

ENV INFLUXDB3_ADMIN_TOKEN_FILE=/etc/influxdb3/admin_token.json
COPY --chmod=644 --chown=1001:1001 admin_token.json /etc/influxdb3/admin_token.json

WORKDIR /var/lib/influxdb3
USER 1001

ENTRYPOINT ["/usr/bin/tini", "--", "influxdb3"]
CMD ["serve", "--node-id=node0", "--object-store=file", "--data-dir=/var/lib/influxdb3"]
