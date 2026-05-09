FROM influxdb:3-core

# Copy the admin token file into the image with correct permissions
COPY --chmod=644 admin_token.json /var/lib/influxdb3/admin_token.json
