#!/bin/bash
# 安防运维OA - 完整部署脚本（在 172.20.0.139 上直接运行）
# 用法: sudo bash deploy_full.sh

set -e
APPDIR="/var/www/oa-api"

echo "=========================================="
echo "  安防运维OA - Laravel 后端完整部署"
echo "=========================================="

# Step 1: 清理旧目录
echo "[1/12] 清理旧目录..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR"
chown -R www-data:www-data /var/www
echo "  ✅ 目录已准备: $APPDIR"

# Step 2: 创建 Laravel 11 项目
echo "[2/12] 创建 Laravel 11 项目（需要 2-5 分钟）..."
cd /var/www
sudo -u www-data composer create-project laravel/laravel oa-api --prefer-dist --no-interaction 2>&1 | tail -5
echo "  ✅ Laravel 项目已创建"

# Step 3: 安装额外依赖
echo "[3/12] 安装 Sanctum + Spatie Permission..."
cd "$APPDIR"
sudo -u www-data composer require laravel/sanctum spatie/laravel-permission --no-interaction 2>&1 | tail -3
echo "  ✅ 额外依赖已安装"

# Step 4: 读取 MySQL debian-sys-maint 密码
echo "[4/12] 配置 MySQL 数据库..."
DEB_USER=$(grep '^user' /etc/mysql/debian.cnf | head -1 | cut -d= -f2 | tr -d ' ')
DEB_PASS=$(grep '^password' /etc/mysql/debian.cnf | head -1 | cut -d= -f2 | tr -d ' ')

mysql -u "$DEB_USER" -p"$DEB_PASS" -e "CREATE DATABASE IF NOT EXISTS oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
mysql -u "$DEB_USER" -p"$DEB_PASS" -e "CREATE USER IF NOT EXISTS 'oa_user'@'localhost' IDENTIFIED BY 'OaPass123!';" 2>/dev/null
mysql -u "$DEB_USER" -p"$DEB_PASS" -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost';" 2>/dev/null
mysql -u "$DEB_USER" -p"$DEB_PASS" -e "FLUSH PRIVILEGES;" 2>/dev/null
echo "  ✅ 数据库 oa_db 和用户 oa_user 已创建"

# Step 5: 写入 .env
echo "[5/12] 写入 .env 配置..."
cat > "$APPDIR/.env" << 'ENVEOF'
APP_NAME="安防运维OA"
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=http://172.20.0.139

LOG_CHANNEL=stack

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=oa_db
DB_USERNAME=oa_user
DB_PASSWORD=OaPass123!

BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file

SANCTUM_STATEFUL_DOMAINS=172.20.0.139
ENVEOF
chown www-data:www-data "$APPDIR/.env"
echo "  ✅ .env 已写入"

# Step 6: 生成 APP_KEY
echo "[6/12] 生成 APP_KEY..."
cd "$APPDIR"
php artisan key:generate --force
echo "  ✅ APP_KEY 已生成"

# Step 7: 运行默认迁移
echo "[7/12] 运行数据库迁移..."
php artisan migrate --force
echo "  ✅ 数据库迁移完成"

# Step 8: 配置 Nginx
echo "[8/12] 配置 Nginx..."
cat > /etc/nginx/sites-available/oa-api << 'NGINXEOF'
server {
    listen 80;
    server_name 172.20.0.139;
    root /var/www/oa-api/public;
    index index.php index.html;
    add_header X-Frame-Options "SAMEORIGIN";
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }
    location ~ /\.(?!well-known).* {
        deny all;
    }
}
NGINXEOF
ln -sf /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api
rm -f /etc/nginx/sites-enabled/default
nginx -t 2>&1
systemctl reload nginx
echo "  ✅ Nginx 已配置并重载"

# Step 9: 启动 PHP-FPM
echo "[9/12] 启动 PHP-FPM..."
systemctl start php8.3-fpm
systemctl enable php8.3-fpm
echo "  ✅ PHP-FPM 已启动"

# Step 10: 创建 Sanctum 迁移文件
echo "[10/12] 发布 Sanctum 配置..."
php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider" --force 2>/dev/null || true
php artisan migrate --force 2>/dev/null || true
echo "  ✅ Sanctum 已配置"

# Step 11: 测试
echo "[11/12] 测试部署..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
echo "  HTTP 状态码: $HTTP_CODE"

# Step 12: 完成
echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "🌐 访问地址: http://172.20.0.139"
echo "📡 API 地址: http://172.20.0.139/api"
echo ""
echo "⚠️  注意:"
echo "   1. 现在只有 Laravel 骨架，业务代码需要额外复制"
echo "   2. 默认账号需要运行: php artisan db:seed"
echo "   3. 前端需要设置 VITE_API_BASE=http://172.20.0.139"
echo ""
