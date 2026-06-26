#!/bin/bash
# 备份 storage/app 和 disk_files
set -euo pipefail
BACKUP_DIR="/var/backups/oa/files"
DATE=$(date +%Y-%m-%d)
FILENAME="oa-files-${DATE}.tar.gz"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"
cd /var/www/oa-api
tar -czf "$BACKUP_DIR/$FILENAME" \
  --exclude='storage/framework/cache/data' \
  --exclude='storage/framework/sessions' \
  --exclude='storage/framework/views' \
  --exclude='storage/logs/*.log' \
  storage/app/

echo "[$(date)] Files backup: $BACKUP_DIR/$FILENAME"
ls -lh "$BACKUP_DIR/$FILENAME"

find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
