#!/bin/bash
# B2.1-5 验收清单 — 1 分钟跑完输出 PASS/FAIL
set -uo pipefail

RED="\033[31m"; GRN="\033[32m"; YEL="\033[33m"; NC="\033[0m"
pass=0; fail=0
check() {
  local name="$1" cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo -e "  ${GRN}✓${NC} $name"
    pass=$((pass+1))
  else
    echo -e "  ${RED}✗${NC} $name"
    fail=$((fail+1))
  fi
}

echo "=========================================="
echo "B2.1 生产环境验收清单"
echo "时间: $(date)"
echo "=========================================="
echo ""

echo "【1. 服务存活】"
check "php8.5-fpm active" "systemctl is-active --quiet php8.5-fpm"
check "nginx active"        "systemctl is-active --quiet nginx"
check "postgresql active"   "systemctl is-active --quiet postgresql"
check "redis-server active" "systemctl is-active --quiet redis-server"
echo ""

echo "【2. APP_DEBUG】"
check "APP_DEBUG=false" "grep -q '^APP_DEBUG=false' /var/www/oa-api/.env"
check "APP_ENV=production" "grep -q '^APP_ENV=production' /var/www/oa-api/.env"
check "LOG_CHANNEL=daily"  "grep -q '^LOG_CHANNEL=daily' /var/www/oa-api/.env"
echo ""

echo "【3. 资源指标】"
DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
MEM_PCT=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')
LOAD5=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $2}' | tr -d ' ')
echo "  磁盘:  ${DISK_PCT}%"
echo "  内存:  ${MEM_PCT}%"
echo "  load5: ${LOAD5}"
[ "$DISK_PCT" -lt 80 ] && echo -e "  ${GRN}✓ 磁盘 < 80%${NC}" || { echo -e "  ${YEL}⚠ 磁盘 >= 80%${NC}"; fail=$((fail+1)); }
[ "$MEM_PCT" -lt 80 ] && echo -e "  ${GRN}✓ 内存 < 80%${NC}" || { echo -e "  ${YEL}⚠ 内存 >= 80%${NC}"; fail=$((fail+1)); }
echo ""

echo "【4. API 健康】"
HTTP=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://127.0.0.1:8081/api/health)
check "/api/health = 200" "test '$HTTP' = '200'"
[ -n "$HTTP" ] && echo "  返回: $HTTP"
echo ""

echo "【5. Cron 设置】"
check "备份 cron 02:00"      "crontab -l | grep -q 'oa_daily_backup.sh'"
check "监控告警 */15"       "crontab -l | grep -q 'oa_alert.sh'"
check "告警发送 */5"         "crontab -l | grep -q 'oa_alert_send.sh'"
check "证书续期 03:00"      "crontab -l | grep -q 'oa_cert_renew.sh'"
check "schedule 每 6h"      "crontab -l | grep -q 'schedule:run'"
echo ""

echo "【6. 备份】"
if [ -d /var/backups/oa/full ]; then
  CNT=$(find /var/backups/oa/full -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
  LATEST=$(find /var/backups/oa/full -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -r | head -1)
  if [ -n "$LATEST" ]; then
    SIZE=$(du -sh "$LATEST" | cut -f1)
    AGE_MIN=$(( ($(date +%s) - $(stat -c %Y "$LATEST")) / 60 ))
    echo "  备份数: $CNT"
    echo "  最新:   $LATEST ($SIZE, ${AGE_MIN}min ago)"
    [ -f "$LATEST/MANIFEST.md" ] && echo -e "  ${GRN}✓ MANIFEST 存在${NC}" || { echo -e "  ${RED}✗ MANIFEST 缺失${NC}"; fail=$((fail+1)); }
    [ -f "$LATEST/db_"*.sql.gz ] && echo -e "  ${GRN}✓ DB dump 存在${NC}" || { echo -e "  ${RED}✗ DB dump 缺失${NC}"; fail=$((fail+1)); }
    [ -f "$LATEST/code_"*.tar.gz ] && echo -e "  ${GRN}✓ code tar 存在${NC}" || { echo -e "  ${RED}✗ code tar 缺失${NC}"; fail=$((fail+1)); }
  else
    echo -e "  ${YEL}⚠ 尚无备份 (刚部署, 等今晚 02:00 第一次自动备份)${NC}"
  fi
else
  echo -e "  ${RED}✗ 备份目录不存在${NC}"
  fail=$((fail+1))
fi
echo ""

echo "【7. 防火墙】"
if command -v ufw >/dev/null 2>&1; then
  if ufw status 2>/dev/null | grep -q "Status: active" || sudo -n ufw status 2>/dev/null | grep -q "Status: active"; then
    echo -e "  ${GRN}✓ UFW 已启用${NC}"
    sudo -n ufw status 2>/dev/null | grep -E "22|80|443|8081" | head -10
    pass=$((pass+1))
  else
    echo -e "  ${RED}✗ UFW 未启用${NC}"
    fail=$((fail+1))
  fi
else
  echo -e "  ${YEL}⚠ UFW 未安装${NC}"
fi
echo ""

echo "【8. 117 网络】"
EXT=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://192.168.3.117:8081/api/health 2>/dev/null || echo "000")
echo "  117:8081/api/health = $EXT"
[ "$EXT" = "200" ] && { echo -e "  ${GRN}✓ 117 服务可访问${NC}"; pass=$((pass+1)); } || { echo -e "  ${RED}✗ 117 不可达${NC}"; fail=$((fail+1)); }
echo ""

echo "=========================================="
echo -e "通过: ${GRN}${pass}${NC}    失败: ${RED}${fail}${NC}"
if [ "$fail" -eq 0 ]; then
  echo -e "${GRN}✅ 生产环境验收通过${NC}"
else
  echo -e "${YEL}⚠ 有 ${fail} 项需修复${NC}"
fi
echo "=========================================="
exit $fail
