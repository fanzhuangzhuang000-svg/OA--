#!/bin/bash
# 安防运维OA - 后端部署脚本（服务器端运行）
# 用法: sudo bash deploy_server.sh

set -e
APPDIR="/var/www/oa-api"
DBNAME="oa_db"
DBUSER="oa_user"
DBPASS="OaPass123!"

echo "========================================="
echo "  安防运维OA - 后端部署"
echo "========================================="

# Step 1: 确认环境
echo "[1/10] 确认环境..."
php -v | head -1
composer --version | head -1
nginx -v 2>&1 | head -1
mysql --version | head -1

# Step 2: 创建目录
echo "[2/10] 创建项目目录..."
mkdir -p "$APPDIR"
chown -R www-data:www-data "$(dirname $APPDIR)"
echo "  目录: $APPDIR"

# Step 3: 读取 debian-sys-maint 密码
echo "[3/10] 读取 MySQL 维护账号..."
DEB_USER=$(sudo grep '^user' /etc/mysql/debian.cnf | head -1 | cut -d= -f2 | tr -d ' ')
DEB_PASS=$(sudo grep '^password' /etc/mysql/debian.cnf | head -1 | cut -d= -f2 | tr -d ' ')
echo "  debian-sys-maint: $DEB_USER"

# Step 4: 创建数据库和用户
echo "[4/10] 配置 MySQL 数据库..."
mysql -u "$DEB_USER" -p"$DEB_PASS" -e "CREATE DATABASE IF NOT EXISTS ${DBNAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
mysql -u "$DEB_USER" -p"$DEB_PASS" -e "CREATE USER IF NOT EXISTS '${DBUSER}'@'localhost' IDENTIFIED BY '${DBPASS}';" 2>/dev/null
mysql -u "$DEB_USER" -p"$DEB_PASS" -e "GRANT ALL PRIVILEGES ON ${DBNAME}.* TO '${DBUSER}'@'localhost';" 2>/dev/null
mysql -u "$DEB_USER" -p"$DEB_PASS" -e "FLUSH PRIVILEGES;" 2>/dev/null
echo "  ✅ 数据库配置完成"

# Step 5: 写入 .env（等文件上传后再写）
echo "[5/10] 准备 .env 配置..."
cat > /tmp/oa_env_template.txt << 'ENVEOF'
APP_NAME=安防运维OA
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
echo "  ✅ .env 模板已准备（等待文件上传后写入）"

# Step 6: 配置 Nginx
echo "[6/10] 配置 Nginx..."
cat > /etc/nginx/sites-available/oa-api << 'NGINXEOF'
server {
    listen 80;
    server_name 172.20.0.139;
    root /var/www/oa-api/public;
    index index.php index.html;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

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

    error_log /var/log/nginx/oa-api_error.log;
    access_log /var/log/nginx/oa-api_access.log;
}
NGINXEOF

ln -sf /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api
rm -f /etc/nginx/sites-enabled/default
nginx -t 2>&1
echo "  ✅ Nginx 配置完成"

# Step 7: 启动 PHP-FPM
echo "[7/10] 启动 PHP-FPM..."
systemctl start php8.3-fpm
systemctl enable php8.3-fpm
echo "  ✅ PHP-FPM 已启动"

# Step 8: 重载 Nginx
echo "[8/10] 重载 Nginx..."
systemctl reload nginx
echo "  ✅ Nginx 已重载"

# Step 9: 测试
echo "[9/10] 测试访问..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
echo "  HTTP 状态码: $HTTP_CODE"

# Step 10: 完成
echo ""
echo "========================================="
echo "  ✅ 服务器端准备完成！"
echo "========================================="
echo ""
echo "📋 接下来需要："
echo "  1. 上传后端 PHP 文件到 $APPDIR"
echo "  2. 运行: cd $APPDIR && sudo -u www-data composer install"
echo "  3. 写入 .env 并运行: php artisan key:generate && php artisan migrate --force"
echo ""
echo "🌐 访问地址: http://172.20.0.139"
