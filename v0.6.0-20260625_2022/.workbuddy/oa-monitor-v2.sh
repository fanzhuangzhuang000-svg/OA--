#!/bin/bash
# OA 监控 v2 (2026-06-21)
# - 本机: PHP-FPM / Nginx / PG / /api/health / 磁盘 / 内存 / 端口
# - 跨机: 172.20.0.139 主服务器 + 本机 152 + 公网连通性
# - 详细日志到 /var/log/oa-monitor-detail.log
# - 告警去重 30min
set -uo pipefail

TS=$(date '+%Y-%m-%d %H:%M:%S')
LOG="/var/log/oa-monitor.log"
DLOG="/var/log/oa-monitor-detail.log"
ALERT_FILE="/tmp/oa-alert-pending"

# === 本机 152 自检 ===
fail=0
report=""
check_metric() {
  local name="$1" val="$2" threshold="$3" unit="$4" op="$5"
  if [ "$op" = "gt" ] && [ "$val" -gt "$threshold" ]; then
    report+="[WARN] ${name}=${val}${unit} (阈值 ${threshold}${unit})\n"
  elif [ "$op" = "ne" ] && [ "$val" != "$threshold" ]; then
    report+="[CRIT] ${name}=${val} (期望 ${threshold})\n"
    fail=1
  fi
}

# 1. PHP-FPM
if ! systemctl is-active --quiet php8.3-fpm; then
  report+="[CRIT] php8.3-fpm down\n"; fail=1
fi
# 2. Nginx
if ! systemctl is-active --quiet nginx; then
  report+="[CRIT] nginx down\n"; fail=1
fi
# 3. PostgreSQL
if ! sudo -u postgres pg_isready -h 127.0.0.1 > /dev/null 2>&1; then
  report+="[CRIT] postgres down\n"; fail=1
fi
# 4. /api/health (152 走 nginx 80, 172 走 3001)
MY_IP=$(hostname -I | awk '{print $1}')
if [ "$MY_IP" = "10.2.0.8" ]; then
  HEALTH_URL="http://127.0.0.1/api/health"
else
  HEALTH_URL="http://127.0.0.1:3001/api/health"
fi
HTTP_HEALTH=$(curl -s -o /tmp/health_resp.json -w '%{http_code}' --max-time 5 "$HEALTH_URL" || echo 000)
if [ "$HTTP_HEALTH" != "200" ]; then
  report+="[CRIT] /api/health returned $HTTP_HEALTH (${HEALTH_URL})\n"; fail=1
fi
# 5. 磁盘
DISK_USE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
[ "${DISK_USE:-0}" -gt 80 ] && report+="[WARN] disk=${DISK_USE}%\n"
# 6. 内存
MEM_USE=$(free | grep Mem | awk '{print int($3/$2*100)}')
[ "${MEM_USE:-0}" -gt 90 ] && report+="[WARN] mem=${MEM_USE}%\n"
# 7. CPU 负载
LOAD=$(cat /proc/loadavg | awk '{print int($1)}')
CPU_N=$(nproc)
[ "$LOAD" -gt $((CPU_N * 2)) ] && report+="[WARN] load=${LOAD} (cpu=${CPU_N})\n"

# === 关键端口监听 (按部署模式) ===
# 152 用 unix socket, 172 用 3001, 都监听 80 + 5432
MY_IP=$(hostname -I | awk '{print $1}')
if [ "$MY_IP" = "10.2.0.8" ]; then
  # 152 演示服: unix socket, 不监听 3001
  PORTS="80 5432"
  if [ -S /run/php/php8.3-fpm.sock ]; then
    : # fpm socket 存在
  else
    report+="[CRIT] fpm socket /run/php/php8.3-fpm.sock 缺失\n"; fail=1
  fi
else
  # 172 测试服: 监听 3001
  PORTS="80 3001 5432"
fi
for p in $PORTS; do
  if ! ss -tln 2>/dev/null | grep -q ":$p "; then
    report+="[CRIT] port $p 未监听\n"; fail=1
  fi
done

# === 跨机监测: 172.20.0.139 主服务器 ===
PRIMARY="172.20.0.139"
PRIMARY_LOST_FILE="/tmp/oa-primary-lost-count"
LOST=0
PRIMARY_DETAIL=""

# 1. ping 3 次
if ! ping -c 3 -W 2 "$PRIMARY" > /dev/null 2>&1; then
  PRIMARY_DETAIL+="ping失败 "
  LOST=1
fi
# 2. SSH 端口
if ! timeout 3 bash -c "</dev/tcp/$PRIMARY/22" 2>/dev/null; then
  PRIMARY_DETAIL+="ssh:22 不可达 "
  LOST=1
fi
# 3. HTTP /api/health
P_HEALTH=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://$PRIMARY/api/health" || echo 000)
if [ "$P_HEALTH" != "200" ]; then
  PRIMARY_DETAIL+="/api/health=$P_HEALTH "
  LOST=1
fi
# 4. HTTP /login (检测 web)
P_LOGIN=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://$PRIMARY/login" || echo 000)
if [ "$P_LOGIN" != "200" ]; then
  PRIMARY_DETAIL+="/login=$P_LOGIN "
  LOST=1
fi

# 累加 lost count
if [ "$LOST" -eq 1 ]; then
  CURR=$(cat "$PRIMARY_LOST_FILE" 2>/dev/null || echo 0)
  CURR=$((CURR + 1))
  echo "$CURR" > "$PRIMARY_LOST_FILE"
  # 第一次发现故障: 立即告警; 后续: 5 次后才告警 (防网络抖动)
  if [ "$CURR" -eq 1 ] || [ "$CURR" -eq 5 ] || [ "$((CURR % 30))" -eq 0 ]; then
    report+="[CRIT] 172 主服务器 不可达 (连续 ${CURR} 次): ${PRIMARY_DETAIL}\n"
    fail=1
  fi
else
  # 恢复
  PREV=$(cat "$PRIMARY_LOST_FILE" 2>/dev/null || echo 0)
  if [ "$PREV" -gt 0 ]; then
    report+="[RECOVER] 172 主服务器 恢复 (之前 ${PREV} 次不可达)\n"
  fi
  echo "0" > "$PRIMARY_LOST_FILE"
fi

# === 写日志 ===
# detail log: 每次都记 (含原始指标)
{
  echo "[$TS] health=$HTTP_HEALTH disk=${DISK_USE}% mem=${MEM_USE}% load=${LOAD} primary_lost=$(cat $PRIMARY_LOST_FILE 2>/dev/null || echo 0) primary_detail='${PRIMARY_DETAIL:-OK}'"
} >> "$DLOG"

# main log: 故障/恢复才记
if [ "$fail" -eq 0 ] && [ -z "$report" ]; then
  echo "[$TS] OK" >> "$LOG"
  rm -f "$ALERT_FILE"
else
  echo "[$TS] ISSUES:" >> "$LOG"
  echo -e "$report" >> "$LOG"
  # 告警去重 30min
  if [ ! -f "$ALERT_FILE" ] || [ -n "$(find "$ALERT_FILE" -mmin +30 2>/dev/null)" ]; then
    echo -e "$report" > "$ALERT_FILE"
    echo "[$TS] ALERT raised"
    # 占位 webhook
    # curl -s -X POST "$WEBHOOK_URL" -H "Content-Type: application/json" \
    #   -d "{\"msgtype\":\"text\",\"text\":{\"content\":\"OA告警: $report\"}}" > /dev/null
  fi
fi
