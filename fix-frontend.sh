#!/bin/bash
cd /vol1/docker/oa-system

echo "📁 创建 dist 目录..."
mkdir -p pc-web/dist

echo "🚀 启动 node 容器..."
docker compose up -d node

echo "⏳ 等待 node 启动..."
sleep 10

echo "📦 安装前端依赖..."
docker compose exec node npm install

echo "🔨 构建前端..."
docker compose exec node npm run build

echo "🚀 启动 nginx..."
docker compose up -d nginx

echo "📊 服务状态:"
docker compose ps

echo ""
echo "✅ 完成！"
echo "🌐 访问: http://192.168.50.50:3001"

