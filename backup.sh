#!/bin/bash
NODE_ID="node0"
DATA_DIR="./data"
BACKUP_DIR="./backup/$(date +%Y%m%d-%H%M%S)"

mkdir -p "$BACKUP_DIR"

# Copy in recommended order
cp -r $DATA_DIR/${NODE_ID}/snapshots "$BACKUP_DIR/"
cp -r $DATA_DIR/${NODE_ID}/dbs "$BACKUP_DIR/"
cp -r $DATA_DIR/${NODE_ID}/wal "$BACKUP_DIR/"
cp -r $DATA_DIR/${NODE_ID}/catalog "$BACKUP_DIR/"
cp $DATA_DIR/${NODE_ID}/_catalog_checkpoint "$BACKUP_DIR/"
echo "Backup created at $BACKUP_DIR"

# Compress the backup directory
tar -czf "${BACKUP_DIR}.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
echo "Compressed backup archive created at ${BACKUP_DIR}.tar.gz"

# Remove the temporary backup directory
rm -rf "$BACKUP_DIR"
echo "Temporary backup directory removed"
