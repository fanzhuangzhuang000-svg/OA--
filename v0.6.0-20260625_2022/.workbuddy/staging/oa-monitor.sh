#!/bin/bash
# 每 5 分钟检查: PHP-FPM, Nginx, PG, /api/health, 磁盘, 内存
set -uo pipefail
LOG="/var/log/oa-monitor.log"
ALERT_FILE="/tmp/oa-alert-pending"
TS=$(date '+%Y-%m-%d %H:%M:%S')

fail=0
report=""

# 1. PHP-FPM
if ! systemctl is-active --quiet php8.3-fpm; then
  report+="[CRIT] php8.3-fpm down\n"
  fail=1
fi

# 2. Nginx
if ! systemctl is-active --quiet nginx; then
  report+="[CRIT] nginx down\n"
  fail=1
fi

# 3. PostgreSQL
if ! sudo -u postgres pg_isready -h 127.0.0.1 > /dev/null 2>&1; then
  report+="[CRIT] postgres down\n"
  fail=1
fi

# 4. /api/health
HTTP=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3001/api/health || echo 000)
if [ "$HTTP" != "200" ]; then
  report+="[CRIT] /api/health returned $HTTP\n"
  fail=1
fi

# 5. 磁盘 > 80%
DISK_USE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USE" -gt 80 ]; then
  report+="[WARN] disk ${DISK_USE}%\n"
fi

# 6. 内存 > 90%
MEM_USE=$(free | grep Mem | awk '{print int($3/$2*100)}')
if [ "$MEM_USE" -gt 90 ]; then
  report+="[WARN] mem ${MEM_USE}%\n"
fi

if [ $fail -eq 0 ] && [ -z "$report" ]; then
  echo "[$TS] OK" >> "$LOG"
  rm -f "$ALERT_FILE"
else
  echo "[$TS] ISSUES:" >> "$LOG"
  echo -e "$report" >> "$LOG"
  # 防告警洪水: 同一问题 30 分钟内不重复
  if [ ! -f "$ALERT_FILE" ] || [ $(find "$ALERT_FILE" -mmin +30 2>/dev/null) ]; then
    echo -e "$report" > "$ALERT_FILE"
    # 这里可以接 webhook (企业微信/钉钉/邮件),现在先写文件占位
    echo "[$TS] ALERT raised"
  fi
fi
