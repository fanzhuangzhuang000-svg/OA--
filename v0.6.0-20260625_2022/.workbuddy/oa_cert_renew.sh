#!/bin/bash
# B2.1-2 HTTPS 证书续期 (certbot + 失败告警)
# 117 当前是 HTTP (oa.afjsw.cn 域名已备案, 但 117 nginx 暂未配 443)
# 当 117 切换到 HTTPS 后, 此脚本自动接管续期
set -uo pipefail

TS=$(date '+%Y-%m-%d %H:%M:%S')
LOG="${HOME}/oa-certbot.log"
ALERT_FILE="/tmp/oa-alert-pending"
DOMAIN="${OA_DOMAIN:-oa.afjsw.cn}"

touch "$LOG" 2>/dev/null || LOG="/tmp/oa-certbot-$(whoami).log"

log() { echo "[$TS] $*" | tee -a "$LOG"; }

# certbot 是否安装
if ! command -v certbot >/dev/null 2>&1; then
  log "[SKIP] certbot 未安装, 跳过 (HTTP-only 阶段无需续期)"
  exit 0
fi

# 是否有证书
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
  log "[SKIP] $DOMAIN 证书目录不存在, 跳过"
  exit 0
fi

# 检查证书到期
CERT_FILE="/etc/letsencrypt/live/$DOMAIN/cert.pem"
EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_FILE" 2>/dev/null | sed 's/notAfter=//')
EXPIRY_TS=$(date -d "$EXPIRY" +%s 2>/dev/null)
NOW_TS=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_TS - NOW_TS) / 86400 ))

log "证书 $DOMAIN 还有 ${DAYS_LEFT} 天到期"

# 30 天前续期 (certbot 默认就是 30 天, 触发条件)
if [ "$DAYS_LEFT" -gt 30 ]; then
  log "[OK] 不需要续期 (还 > 30 天)"
  exit 0
fi

log "[ACTION] 触发续期..."
if certbot renew --nginx --quiet 2>>"$LOG"; then
  log "[OK] 续期成功"
  # reload nginx
  systemctl reload nginx
  log "[OK] nginx 已 reload"
  exit 0
else
  RC=$?
  log "[FAIL] certbot renew 失败 (rc=$RC)"
  echo "[${TS}] [OA-CERTBOT] $DOMAIN 续期失败, 还有 ${DAYS_LEFT} 天" >> "$ALERT_FILE"
  exit 1
fi
