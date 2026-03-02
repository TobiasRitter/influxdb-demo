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

echo "Backup completed to $BACKUP_DIR"
