#!/bin/bash

# --- Configuration ---
NODE_ID="node0"
HOST_DATA_ROOT="./data"
BACKUP_DIR="./backups"

# Check if an argument was provided
if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_filename.tar.gz>"
    echo "Available backups:"
    ls -1 $BACKUP_DIR/*.tar.gz 2>/dev/null
    exit 1
fi

BACKUP_FILE="$1"

# Ensure the backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file $BACKUP_FILE not found."
    exit 1
fi

echo "--- Warning: This will overwrite all current data in $HOST_DATA_ROOT ---"
read -p "Are you sure you want to proceed? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Restore cancelled."
    exit 1
fi

# 2. Clear current data
# We delete the node directory to ensure a completely clean state
echo "Clearing existing data..."
rm -rf "$HOST_DATA_ROOT/$NODE_ID"

# 3. Create a temporary extraction directory
TEMP_EXTRACT="./restore_tmp"
mkdir -p "$TEMP_EXTRACT"

# 4. Extract the backup
echo "Extracting backup archive..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_EXTRACT"

# 5. Move files to the production data directory
# The backup script creates a folder named 'influx_tmp_TIMESTAMP' inside the tar
# We use a wildcard to find that folder and move its contents
INNER_FOLDER=$(ls -1 "$TEMP_EXTRACT" | grep influx_tmp)

echo "Moving files to $HOST_DATA_ROOT..."
cp -r "$TEMP_EXTRACT/$INNER_FOLDER/$NODE_ID" "$HOST_DATA_ROOT/"

# 6. Cleanup
rm -rf "$TEMP_EXTRACT"

echo "------------------------------------------"
echo "Restore Completed Successfully!"
