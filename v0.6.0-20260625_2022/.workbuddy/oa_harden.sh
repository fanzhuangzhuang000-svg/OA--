#!/bin/bash
# B2.1-4 117 上线加固 4 件套 (幂等, 可重复跑)
set -uo pipefail

LOG="${HOME}/oa-hardening.log"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
fail=0

# ===== 1. APP_DEBUG=false (生产环境必须) =====
log "[1/4] APP_DEBUG=false"
ENV_FILE="/var/www/oa-api/.env"
if grep -q '^APP_DEBUG=true' "$ENV_FILE" 2>/dev/null; then
  if sed -i 's/^APP_DEBUG=true/APP_DEBUG=false/' "$ENV_FILE"; then
    log "  ✓ APP_DEBUG 已改为 false"
  else
    log "  ✗ 改 APP_DEBUG 失败"
    fail=1
  fi
else
  log "  ✓ APP_DEBUG 已是 false"
fi

# ===== 2. PHP 错误显示关 (双保险) =====
log "[2/4] display_errors=Off"
PHP_INI="/etc/php/8.5/fpm/php.ini"
if [ -f "$PHP_INI" ]; then
  if grep -q '^display_errors = On' "$PHP_INI"; then
    sed -i 's/^display_errors = On/display_errors = Off/' "$PHP_INI"
    log "  ✓ display_errors 已改为 Off"
    systemctl restart php8.5-fpm
    log "  ✓ php8.5-fpm 已重启"
  else
    log "  ✓ display_errors 已是 Off"
  fi
else
  log "  ✗ $PHP_INI 不存在"
fi

# ===== 3. Laravel log 权限 (www-data 可写) =====
log "[3/4] storage 权限"
STORAGE="/var/www/oa-api/storage"
if [ -d "$STORAGE" ]; then
  chown -R www-data:www-data "$STORAGE" 2>/dev/null
  find "$STORAGE" -type d -exec chmod 775 {} + 2>/dev/null
  find "$STORAGE" -type f -exec chmod 664 {} + 2>/dev/null
  log "  ✓ storage 权限已修"
else
  log "  ✗ $STORAGE 不存在"
  fail=1
fi

# ===== 4. 防火墙 (UFW) =====
log "[4/4] UFW 防火墙"
if command -v ufw >/dev/null 2>&1; then
  ufw --version >/dev/null 2>&1 || true
  # 允许 SSH / HTTP / API
  ufw allow 22/tcp comment 'SSH' 2>/dev/null || true
  ufw allow 80/tcp comment 'HTTP' 2>/dev/null || true
  ufw allow 443/tcp comment 'HTTPS' 2>/dev/null || true
  ufw allow 8081/tcp comment 'OA-API' 2>/dev/null || true
  # 启用
  if ufw status | grep -q "Status: inactive"; then
    echo "y" | ufw --force enable 2>&1 | tee -a "$LOG" >/dev/null
    log "  ✓ UFW 已启用 (22/80/443/8081)"
  else
    log "  ✓ UFW 已启用"
  fi
  ufw status numbered 2>/dev/null | head -10 >> "$LOG"
else
  log "  ⚠ UFW 未安装, 跳过 (生产建议装)"
fi

# ===== 5. .env 不应被 web 访问 =====
log "[bonus] .env 保护"
NGINX_OA="/etc/nginx/sites-enabled/oa"
if grep -q "location.*\\.env" "$NGINX_OA" 2>/dev/null; then
  log "  ✓ .env 已被 nginx 屏蔽"
else
  log "  ⚠ .env 未显式屏蔽, 建议在 nginx 加 'location ~ /\\.env { deny all; }'"
fi

if [ "$fail" -eq 0 ]; then
  log "✓ 加固完成"
else
  log "✗ 有失败, 请检查"
fi
exit $fail
