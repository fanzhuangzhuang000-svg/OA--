#!/bin/bash
set -e

echo "=== 1. 备份 Nginx 配置 ==="
sudo cp /etc/nginx/sites-enabled/oa-api /etc/nginx/sites-enabled/oa-api.bak.$(date +%s)

echo ""
echo "=== 2. 在 oa-api 配置加 X-Debug-Auth 响应头 ==="
# 在 location /api { 块内加一行
sudo sed -i '/location \/api {/a\    add_header X-Debug-Auth "$http_authorization" always;' /etc/nginx/sites-enabled/oa-api

echo "验证修改:"
grep -A3 "location /api" /etc/nginx/sites-enabled/oa-api

echo ""
echo "=== 3. nginx -t ==="
sudo nginx -t 2>&1

echo ""
echo "=== 4. nginx reload ==="
sudo nginx -s reload 2>&1
sleep 1

echo ""
echo "=== 5. 测试登录（看 X-Debug-Auth 响应头）==="
curl -v -X POST http://127.0.0.1/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' 2>&1 | grep -i "X-Debug-Auth\|HTTP/"

echo ""
echo "=== 6. 获取 token 并测试 /api/vehicles ==="
LOGIN_RESP=$(curl -s -X POST http://127.0.0.1/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}')
TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('token',''))")
echo "Token: ${TOKEN:0:40}..."

echo ""
echo "请求 /api/vehicles（带 Authorization 头）:"
curl -v -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1/api/vehicles 2>&1 | grep -i "X-Debug-Auth\|HTTP/\|Authorization"

echo ""
echo "响应体:"
curl -s -w "\nHTTP %{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1/api/vehicles | head -10

echo ""
echo "=== 7. 检查 Laravel Sanctum 中间件配置 ==="
grep -n "auth:\|sanctum\|middleware" /var/www/oa-api/routes/api.php | head -20
