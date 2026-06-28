#!/bin/bash
BACKUP_DIR=/vol1/docker/oa-system/backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
docker compose exec -T postgres pg_dump -U oa_user oa_security | gzip > $BACKUP_DIR/oa_$DATE.sql.gz
# 保留最近 30 天
find $BACKUP_DIR -name '*.gz' -mtime +30 -delete
echo "Backup completed: oa_$DATE.sql.gz"
