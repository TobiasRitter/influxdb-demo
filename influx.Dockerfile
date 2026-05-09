FROM influxdb:3-core

# Include the admin token file in the image
COPY admin_token.json /var/lib/influxdb3/admin_token.json

# Ensure the config directory and permissions are set if needed
RUN mkdir -p /var/lib/influxdb3 && chmod 644 /var/lib/influxdb3/admin_token.json
