#!/bin/bash
# B2.1-3 监控告警 — 4 维度
#   1. CPU/内存/磁盘 (117 本机)
#   2. PHP-FPM / NGINX / PG / Redis 健康
#   3. API /api/health 200?
#   4. 备份是否在 25h 内完成
# 告警: 写入 /tmp/oa-alert-pending (后台 cron 每 5min 发送)
set -uo pipefail

TS=$(date '+%Y-%m-%d %H:%M:%S')
LOG="${HOME}/oa-monitor.log"
ALERT_FILE="/tmp/oa-alert-pending"
HOSTNAME_S=$(hostname)

touch "$LOG" 2>/dev/null || LOG="/tmp/oa-monitor-$(whoami).log"

issues=0
report=""

# ===== 1. 磁盘 =====
DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_PCT" -gt 90 ]; then
  report+="[CRIT] disk / ${DISK_PCT}%\n"
  issues=$((issues+1))
elif [ "$DISK_PCT" -gt 80 ]; then
  report+="[WARN] disk / ${DISK_PCT}%\n"
fi

# ===== 2. 内存 =====
MEM_PCT=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')
if [ "$MEM_PCT" -gt 90 ]; then
  report+="[CRIT] memory ${MEM_PCT}%\n"
  issues=$((issues+1))
elif [ "$MEM_PCT" -gt 80 ]; then
  report+="[WARN] memory ${MEM_PCT}%\n"
fi

# ===== 3. CPU load (5min) =====
LOAD5=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $2}' | tr -d ' ')
CORES=$(nproc)
LOAD_THRESH=$(echo "$CORES * 2" | bc 2>/dev/null || echo "4")
if [ "$(echo "$LOAD5 > $LOAD_THRESH" | bc 2>/dev/null || echo 0)" = "1" ]; then
  report+="[WARN] load5=$LOAD5 (>${LOAD_THRESH} for $CORES cores)\n"
fi

# ===== 4. 服务存活 =====
for svc in php8.5-fpm nginx postgresql redis-server; do
  if ! systemctl is-active --quiet "$svc"; then
    report+="[CRIT] service $svc is DOWN\n"
    issues=$((issues+1))
  fi
done

# ===== 5. API health =====
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:8081/api/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" != "200" ]; then
  report+="[CRIT] /api/health returned $HTTP_CODE\n"
  issues=$((issues+1))
fi

# ===== 6. 备份新鲜度 (25h 内必须有) =====
LATEST_BACKUP=$(find /var/backups/oa/full -mindepth 1 -maxdepth 1 -type d -mmin -1500 2>/dev/null | head -1)
if [ -z "$LATEST_BACKUP" ]; then
  LATEST_DIR=$(find /var/backups/oa/full -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -r | head -1)
  if [ -n "$LATEST_DIR" ]; then
    LATEST_AGE_HOURS=$(( ($(date +%s) - $(stat -c %Y "$LATEST_DIR" 2>/dev/null || echo $(date +%s)) / 1) / 3600 ))
    if [ "$LATEST_AGE_HOURS" -gt 25 ]; then
      report+="[CRIT] latest backup is ${LATEST_AGE_HOURS}h old (>25h)\n"
      issues=$((issues+1))
    fi
  fi
fi

# ===== 7. 证书 (仅 117 有 HTTPS 才有 /etc/letsencrypt) =====
if [ -d /etc/letsencrypt/live ]; then
  CERT_DAYS=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/*/cert.pem 2>/dev/null | head -1 | sed 's/notAfter=//' | xargs -I '{}' date -d '{}' +%s 2>/dev/null)
  if [ -n "$CERT_DAYS" ]; then
    DAYS_LEFT=$(( (CERT_DAYS - $(date +%s)) / 86400 ))
    if [ "$DAYS_LEFT" -lt 14 ]; then
      report+="[CRIT] SSL cert expires in ${DAYS_LEFT} days\n"
      issues=$((issues+1))
    elif [ "$DAYS_LEFT" -lt 30 ]; then
      report+="[WARN] SSL cert expires in ${DAYS_LEFT} days\n"
    fi
  fi
fi

# ===== 输出 =====
if [ "$issues" -gt 0 ] || [ -n "$report" ]; then
  LINE="[${TS}] [${HOSTNAME_S}] issues=${issues}\n${report}"
  echo "[$TS] issues=$issues" >> "$LOG"
  if [ "$issues" -gt 0 ]; then
    printf "%b" "$LINE" | tee -a "$ALERT_FILE"
  else
    echo "[$TS] warnings only (no alert)" >> "$LOG"
    printf "%b" "$LINE" >> "$LOG"
  fi
fi

# 抑制重复告警 (15min 内相同 issues 数)
exit $issues
