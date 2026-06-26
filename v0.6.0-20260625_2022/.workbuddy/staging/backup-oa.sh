#!/bin/bash
# OA 数据库每日全量备份
# 保留 30 天,异地 SFTP 到 /var/backups/oa-offsite
set -euo pipefail

BACKUP_DIR="/var/backups/oa/db"
DATE=$(date +%Y-%m-%d)
FILENAME="oa-${DATE}.sql.gz"
RETENTION_DAYS=30
OFFSITE="/var/backups/oa-offsite"  # 第二块盘或第二台机器,占位

mkdir -p "$BACKUP_DIR" "$OFFSITE"
chmod 700 "$BACKUP_DIR" "$OFFSITE"

# 用 oa_user dump (有权限)
PGPASSWORD='oa_pg_pwd_782997781' pg_dump -h 127.0.0.1 -U oa_user -d security_oa -Fc -Z 9 -f "$BACKUP_DIR/$FILENAME"

# 验证备份可读
pg_restore -l "$BACKUP_DIR/$FILENAME" > /dev/null

# 异地同步 (rsync 到第二台机器占位)
if [ -d "$OFFSITE" ]; then
  rsync -a --delete "$BACKUP_DIR/" "$OFFSITE/" || true
fi

# 清理 30 天前的
find "$BACKUP_DIR" -type f -name 'oa-*.sql.gz' -mtime +$RETENTION_DAYS -delete
find "$OFFSITE" -type f -name 'oa-*.sql.gz' -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# 输出统计
echo "[$(date)] Backup OK: $BACKUP_DIR/$FILENAME"
ls -lh "$BACKUP_DIR/$FILENAME"
