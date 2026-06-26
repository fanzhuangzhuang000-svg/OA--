#!/usr/bin/env python3
"""
获取 172 服务器上的 API 路由（文本格式解析）
"""
import paramiko
import json
import re

HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
    return client

def run(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err

def parse_route_list(text):
    """解析 artisan route:list 文本输出"""
    routes = []
    lines = text.split("\n")
    
    # 跳过表头和分隔线
    started = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith("+") or line.startswith("| Method") or line.startswith("|"):
            if "Method" in line and "URI" in line:
                started = True
            continue
        if not started:
            continue
        
        # 解析：METHOD  uri  Name  Action  Middleware
        # 例如：  GET|HEAD  api/auth/me  auth.me  App\Http\Controllers\Api\AuthController@me  api,auth:sanctum
        parts = [p.strip() for p in line.split("  ") if p.strip()]
        if len(parts) >= 2:
            method = parts[0]
            uri = parts[1]
            name = parts[2] if len(parts) > 2 else ""
            action = parts[3] if len(parts) > 3 else ""
            middleware = parts[4] if len(parts) > 4 else ""
            
            if "api" in uri:
                routes.append({
                    "method": method,
                    "uri": uri,
                    "name": name,
                    "action": action,
                    "middleware": middleware,
                })
    
    return routes

def main():
    client = ssh_connect()
    
    print("📋 获取路由表（文本格式）...")
    code, out, err = run(client, "cd /var/www/oa-api && php artisan route:list 2>/dev/null", timeout=30)
    
    if err.strip() and "INFO" not in err:
        print(f"  ⚠️ stderr: {err[:200]}")
    
    # 解析
    routes = parse_route_list(out)
    api_routes = [r for r in routes if "api/" in r["uri"]]
    
    print(f"\n📋 共解析 {len(routes)} 条路由，其中 API 路由 {len(api_routes)} 条")
    print("=" * 70)
    
    # 按模块分组
    modules = {}
    for r in api_routes:
        uri = r["uri"]
        # 提取 /api/{module}/...
        m = re.match(r"api/([^/]+)", uri)
        if m:
            module = m.group(1)
            if module not in modules:
                modules[module] = []
            modules[module].append(r)
    
    # 输出分组
    for module in sorted(modules.keys()):
        routes_list = modules[module]
        print(f"\n📦 {module} ({len(routes_list)} 个端点)")
        for r in sorted(routes_list, key=lambda x: x["uri"]):
            methods = r["method"].replace("GET|HEAD", "GET").replace("POST", "POST")
            print(f"    {methods:<12} {r['uri']}")
    
    # 保存为 JSON
    output_file = "D:/work/website/OA/.workbuddy/_test/api_tests/routes_parsed.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(api_routes, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 路由已保存到: {output_file}")
    
    client.close()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
