#!/bin/bash
cd /vol1/docker/oa-system

echo "📦 安装 git..."
docker compose exec -T app apk add --no-cache git

echo "📦 配置镜像..."
docker compose exec -T app composer config -g repos.packagist composer https://mirrors.cloud.tencent.com/composer/

echo "📦 运行 composer install..."
docker compose exec -T app composer install --no-dev --prefer-source --optimize-autoloader

echo "🔑 生成 APP_KEY..."
docker compose exec -T app php artisan key:generate --force

echo "🗄️ 运行数据库迁移..."
docker compose exec -T app php artisan migrate --force

echo "🌱 生成种子数据..."
docker compose exec -T app php artisan db:seed --force

echo "🔐 生成权限数据..."
docker compose exec -T app php artisan db:seed --class=PermissionRoleSeeder --force

echo "✅ 完成！访问: http://192.168.50.50:3002"

