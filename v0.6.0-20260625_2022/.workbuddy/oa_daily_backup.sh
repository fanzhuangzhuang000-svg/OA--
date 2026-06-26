#!/bin/bash
# B2.1-1 每日 full 备份 (pg_dump + 代码 + dist) + 滚动 7 天
# 部署: 117 /var/www/oa-api  +  PG 数据库
# 保留: /var/backups/oa/full/ 最近 7 天
set -uo pipefail

TS=$(date +%Y%m%d_%H%M)
DOW=$(date +%u)  # 1=Mon ... 7=Sun
BACKUP_ROOT="/var/backups/oa/full"
TODAY_DIR="${BACKUP_ROOT}/${TS}"
DB_NAME="security_oa"
DB_USER="oa_user"
DB_PASS="oa_pg_pwd_782997781"
LOG="${HOME}/oa-backup.log"
ALERT_FILE="/tmp/oa-alert-pending"
ADMIN_EMAIL="${OA_ALERT_EMAIL:-admin@example.com}"

# 创建目录 (用 sudo 兜底, 因为 nbcy 默认没 /var/backups 权限)
sudo -n mkdir -p "$TODAY_DIR" 2>/dev/null || mkdir -p "$TODAY_DIR" 2>/dev/null || { echo "[FATAL] cannot create $TODAY_DIR" | tee -a "$LOG"; exit 1; }

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
fail=0

# ===== 1. PG 全量 dump =====
log "[1/3] pg_dump $DB_NAME"
DB_FILE="${TODAY_DIR}/db_${TS}.sql.gz"
if PGPASSWORD="$DB_PASS" pg_dump -U "$DB_USER" -h 127.0.0.1 "$DB_NAME" 2>>"$LOG" | gzip > "$DB_FILE"; then
  SIZE=$(du -h "$DB_FILE" | cut -f1)
  log "  ✓ db dump $SIZE"
else
  log "  ✗ db dump FAILED"
  fail=1
fi

# ===== 2. 代码目录 (排除 vendor/ node_modules/ storage 子目录) =====
log "[2/3] code backup"
CODE_FILE="${TODAY_DIR}/code_${TS}.tar.gz"
if tar -czf "$CODE_FILE" \
    --exclude='vendor' --exclude='node_modules' \
    --exclude='storage/logs' --exclude='storage/framework/cache' \
    --exclude='storage/framework/sessions' --exclude='storage/framework/testing' \
    --exclude='storage/framework/views' --exclude='storage/app/public' \
    -C /var/www oa-api oa-web 2>>"$LOG"; then
  SIZE=$(du -h "$CODE_FILE" | cut -f1)
  log "  ✓ code tar.gz $SIZE"
else
  log "  ✗ code tar FAILED"
  fail=1
fi

# ===== 3. 生成 MANIFEST =====
log "[3/3] manifest"
cat > "${TODAY_DIR}/MANIFEST.md" <<EOF
# OA 全量备份 ${TS}

- 数据库: ${DB_NAME} (PG 18)
- 文件大小: $(du -sh "$TODAY_DIR" | cut -f1)
- 备份内容:
  - db_${TS}.sql.gz: PG 全量
  - code_${TS}.tar.gz: oa-api + oa-web (排除 vendor/node_modules/storage)
- 恢复命令: 见 /var/backups/oa/README.md
EOF

# ===== 滚动清理 (保留最近 7 天) =====
DELETED=$(find "$BACKUP_ROOT" -maxdepth 1 -mindepth 1 -type d -mtime +7 -exec rm -rf {} + -print 2>/dev/null | wc -l)
if [ "$DELETED" -gt 0 ]; then
  log "  ✓ 清理 $DELETED 个过期目录 (>7天)"
fi

REMAIN=$(find "$BACKUP_ROOT" -maxdepth 1 -mindepth 1 -type d | wc -l)
log "当前保留: $REMAIN 个备份目录"

# ===== 失败告警 =====
if [ "$fail" -ne 0 ]; then
  MSG="[OA-BACKUP] 117 备份失败 @ ${TS}, 请检查 /var/log/oa-backup.log"
  echo "$MSG" >> "$ALERT_FILE"
  log "  ✗ 备份失败, 已加入告警队列"
  exit 1
fi

log "✓ 备份完成: $TODAY_DIR"
exit 0
