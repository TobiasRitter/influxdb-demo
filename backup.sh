#!/bin/bash

# --- Configuration ---
NODE_ID="node0"
HOST_DATA_ROOT="./data" 
BACKUP_BASE_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
STAGING_DIR="$BACKUP_BASE_DIR/influx_tmp_$TIMESTAMP"
FINAL_ARCHIVE="$BACKUP_BASE_DIR/influx3_backup_$TIMESTAMP.tar.gz"

# The specific path to your catalog file
CATALOG_DB="$HOST_DATA_ROOT/$NODE_ID/catalog/catalog.sqlite"

echo "--- Starting Backup: $TIMESTAMP ---"

# 1. Ensure staging directory exists
mkdir -p "$STAGING_DIR/$NODE_ID/catalog"

# 2. Atomic Catalog Backup
# We perform this first to get a consistent point-in-time of the metadata
if [ -f "$CATALOG_DB" ]; then
    echo "Snapshotting Catalog..."
    sqlite3 "$CATALOG_DB" ".backup '$STAGING_DIR/$NODE_ID/catalog/catalog.sqlite'"
else
    echo "Warning: Catalog file not found at $CATALOG_DB. Skipping atomic snapshot."
fi

# 3. Copy Active/Immutable Data
# Using rsync here is safer than cp because it handles missing source 
# directories gracefully and preserves permissions.
echo "Syncing data folders..."

# Folders to check and sync
TARGETS=("wal" "dbs" "catalog/v2")

for folder in "${TARGETS[@]}"; do
    if [ -d "$HOST_DATA_ROOT/$NODE_ID/$folder" ]; then
        echo "Copying $folder..."
        mkdir -p "$STAGING_DIR/$NODE_ID/$folder"
        rsync -a "$HOST_DATA_ROOT/$NODE_ID/$folder/" "$STAGING_DIR/$NODE_ID/$folder/"
    fi
done

# Sync the checkpoint file if it exists
if [ -f "$HOST_DATA_ROOT/$NODE_ID/_catalog_checkpoint" ]; then
    cp "$HOST_DATA_ROOT/$NODE_ID/_catalog_checkpoint" "$STAGING_DIR/$NODE_ID/"
fi

# 4. Create the Archive
echo "Compressing into $FINAL_ARCHIVE..."
tar -czf "$FINAL_ARCHIVE" -C "$BACKUP_BASE_DIR" "influx_tmp_$TIMESTAMP"

# 5. Cleanup
rm -rf "$STAGING_DIR"

echo "------------------------------------------"
echo "Backup Completed: $FINAL_ARCHIVE"
