# Stage 1: Get the InfluxDB binary
FROM influxdb:3-core AS influx-source

# Stage 2: Compress and Strip the binary
# We use debian-slim because it has the package manager needed for UPX
FROM debian:trixie AS compressor
RUN apt-get update && \
    apt-get install -y --no-install-recommends upx-ucl binutils && \
    rm -rf /var/lib/apt/lists/*

COPY --from=influx-source /usr/bin/influxdb3 /usr/bin/influxdb3-raw

# 'strip' removes debug symbols, and 'upx' compresses the binary itself
RUN strip --strip-all /usr/bin/influxdb3-raw && \
    upx --best --lzma -o /usr/bin/influxdb3 /usr/bin/influxdb3-raw

# Stage 3: Get the Python library
FROM python:3.13-slim-bookworm AS python-source

# Stage 4: Prepare the configuration directory
# This ensures the directory itself is owned by the nonroot user
FROM debian:bookworm-slim AS config-builder
RUN mkdir -p /etc/influxdb3 && chown 65532:65532 /etc/influxdb3
COPY --chmod=644 --chown=65532:65532 admin_token.json /etc/influxdb3/admin_token.json

# Stage 5: Final Distroless image
FROM gcr.io/distroless/cc-debian12

# 1. Copy required Python shared library to /lib 
COPY --from=python-source /usr/local/lib/libpython3.13.so.1.0 /lib/libpython3.13.so.1.0

# 2. Copy the COMPRESSED InfluxDB binary from Stage 2
COPY --from=compressor /usr/bin/influxdb3 /usr/bin/influxdb3

# 3. Copy the PRE-CONFIGURED directory from Stage 4
# This prevents "Permission denied" errors on folder metadata 
COPY --from=config-builder --chown=65532:65532 /etc/influxdb3 /etc/influxdb3

# 4. Set environment and execution context 
ENV INFLUXDB3_ADMIN_TOKEN_FILE=/etc/influxdb3/admin_token.json
WORKDIR /var/lib/influxdb3
USER 65532

# 5. Run the database using the JSON array format (exec form) [cite: 1, 2]
ENTRYPOINT ["/usr/bin/influxdb3"]
CMD ["serve", "--node-id=node0", "--object-store=file", "--data-dir=/var/lib/influxdb3"]
