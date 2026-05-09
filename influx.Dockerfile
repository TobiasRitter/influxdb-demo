# Stage 1: Extraction
FROM influxdb:3-core AS builder

# Stage 2: Minimal Runtime with Python support
FROM python:3.13-slim-bookworm

# 1. Install tini for better signal handling (optional but recommended)
# and create a non-root user for security
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1001 influxuser

# 2. Copy the binary from the official image
COPY --from=builder /usr/bin/influxdb3 /usr/bin/influxdb3

# 3. Set up the environment and token
ENV INFLUXDB3_ADMIN_TOKEN_FILE=/var/lib/influxdb3/admin_token.json
WORKDIR /var/lib/influxdb3

# 4. Copy your admin token and fix permissions
# We use the 'influxuser' (1001) we created above
COPY --chmod=644 --chown=1001:1001 admin_token.json /var/lib/influxdb3/admin_token.json

# 5. Run as non-root
USER 1001

# Using tini as the entrypoint ensures that InfluxDB shuts down 
# cleanly when you stop the container.
ENTRYPOINT ["/usr/bin/tini", "--", "influxdb3"]
CMD ["serve", "--node-id=node0", "--object-store=file"]
