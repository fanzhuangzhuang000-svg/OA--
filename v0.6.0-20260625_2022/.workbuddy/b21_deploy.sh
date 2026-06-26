#!/bin/bash
# B2.1 一键部署到 117: 推 4 个脚本 + 设 cron
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

HOST=192.168.3.117
USER=nbcy
REMOTE_DIR=/home/nbcy/oa-scripts

echo "==== B2.1 部署到 117 ===="

# 1. 推 4 个脚本
mkdir -p /tmp/oa-deploy
cp "$SCRIPT_DIR/oa_daily_backup.sh" /tmp/oa-deploy/
cp "$SCRIPT_DIR/oa_alert.sh" /tmp/oa-deploy/
cp "$SCRIPT_DIR/oa_alert_send.sh" /tmp/oa-deploy/
cp "$SCRIPT_DIR/oa_cert_renew.sh" /tmp/oa-deploy/
cp "$SCRIPT_DIR/oa_harden.sh" /tmp/oa-deploy/

scp -o ConnectTimeout=5 /tmp/oa-deploy/*.sh ${USER}@${HOST}:/tmp/oa-deploy/
ssh -o ConnectTimeout=5 ${USER}@${HOST} "
  sudo -n mkdir -p ${REMOTE_DIR} && \\
  sudo -n mv /tmp/oa-deploy/*.sh ${REMOTE_DIR}/ && \\
  sudo -n chown nbcy:nbcy ${REMOTE_DIR}/*.sh && \\
  sudo -n chmod 755 ${REMOTE_DIR}/*.sh && \\
  echo '✓ 4 脚本已部署到 ${REMOTE_DIR}/'
  ls -la ${REMOTE_DIR}/
"

# 2. 设 cron
echo ""
echo "==== 设置 cron ===="
ssh -o ConnectTimeout=5 ${USER}@${HOST} "
  crontab -l 2>/dev/null > /tmp/cron.bak || true
  # 清掉旧 oa-cron 行
  grep -v 'oa-daily-backup\\|oa-alert\\|oa-cert-renew' /tmp/cron.bak > /tmp/cron.new 2>/dev/null || touch /tmp/cron.new
  # 加 5 个 cron 项
  cat >> /tmp/cron.new <<'EOF'
# B2.1 OA 运维 cron
# 每日 02:00 full 备份
0 2 * * * /home/nbcy/oa-scripts/oa_daily_backup.sh >> /var/log/oa-backup.log 2>&1
# 每 15min 监控告警采集
*/15 * * * * /home/nbcy/oa-scripts/oa_alert.sh >> /var/log/oa-monitor.log 2>&1
# 每 5min 告警发送 (去重 15min)
*/5 * * * * /home/nbcy/oa-scripts/oa_alert_send.sh >> /var/log/oa-alert.log 2>&1
# 每日 03:00 证书续期检查
0 3 * * * /home/nbcy/oa-scripts/oa_cert_renew.sh >> /var/log/oa-certbot.log 2>&1
# 每 6h 拉一次同步 (oa:sync-actual-costs 已存在, 这里只是兜底)
0 */6 * * * cd /var/www/oa-api && sudo -n php -d opcache.enable=0 artisan schedule:run >> /var/log/oa-schedule.log 2>&1
EOF
  crontab /tmp/cron.new
  echo '✓ cron 已设置:'
  crontab -l
"

# 3. 跑一次加固
echo ""
echo "==== 跑加固 ===="
ssh -o ConnectTimeout=5 ${USER}@${HOST} "sudo -n /home/nbcy/oa-scripts/oa_harden.sh"

# 4. 跑一次 backup (验证)
echo ""
echo "==== 验证: 跑一次备份 ===="
ssh -o ConnectTimeout=5 ${USER}@${HOST} "/home/nbcy/oa-scripts/oa_daily_backup.sh"

# 5. 跑一次 alert (验证)
echo ""
echo "==== 验证: 跑一次监控告警 ===="
ssh -o ConnectTimeout=5 ${USER}@${HOST} "/home/nbcy/oa-scripts/oa_alert.sh; echo '--- alert log ---'; tail -3 /var/log/oa-monitor.log"

echo ""
echo "✅ B2.1 部署完成"
