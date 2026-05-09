FROM influxdb:3-core AS builder

FROM python:3.13-slim-bookworm

# 1. Install tini and create our user
RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1001 influxuser

# 2. Create the data directory AND a config directory
RUN mkdir -p /var/lib/influxdb3 /etc/influxdb3 && \
    chown -R 1001:1001 /var/lib/influxdb3 /etc/influxdb3

COPY --from=builder /usr/bin/influxdb3 /usr/bin/influxdb3

# 3. Environment & Token (Updated Path)
ENV INFLUXDB3_ADMIN_TOKEN_FILE=/etc/influxdb3/admin_token.json
WORKDIR /var/lib/influxdb3

# 4. Copy the token to the NEW safe location
COPY --chmod=644 --chown=1001:1001 admin_token.json /etc/influxdb3/admin_token.json

USER 1001

ENTRYPOINT ["/usr/bin/tini", "--", "influxdb3"]
CMD ["serve", "--node-id=node0", "--object-store=file", "--data-dir=/var/lib/influxdb3"]
