#!/usr/bin/env python3
"""从 172 服务器获取完整 API 路由（grep 过滤）"""
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

def parse_table_line(line):
    """解析 route:list 表格行"""
    # 去掉 ANSI 颜色码
    line = re.sub(r'\x1b\[[0-9;]*m', '', line)
    line = line.rstrip()
    
    if not line or line.startswith("+") or "Method" in line and "URI" in line:
        return None
    
    # 格式：METHOD  URI  Name  Action  Middleware
    # 用两个以上的空格分割
    parts = re.split(r'\s{2,}', line.strip())
    if len(parts) >= 2:
        method = parts[0].strip()
        uri = parts[1].strip()
        name = parts[2].strip() if len(parts) > 2 else ""
        action = parts[3].strip() if len(parts) > 3 else ""
        return {"method": method, "uri": uri, "name": name, "action": action}
    return None

def main():
    client = ssh_connect()
    
    print("📋 获取 API 路由（grep 过滤）...")
    # 用 grep 只拿 api 行，避免表格头部干扰
    code, out, err = run(client, 
        "cd /var/www/oa-api && php artisan route:list 2>/dev/null | grep -E '^\s+(GET|POST|PUT|DELETE|PATCH|HEAD)' | grep 'api/'",
        timeout=30)
    
    print(f"退出码: {code}, 输出行数: {len(out.split(chr(10)))}")
    
    # 解析
    routes = []
    for line in out.split("\n"):
        parsed = parse_table_line(line)
        if parsed and "api/" in parsed["uri"]:
            routes.append(parsed)
    
    print(f"\n解析到 {len(routes)} 个 API 端点")
    print("=" * 70)
    
    # 按模块分组
    modules = {}
    for r in routes:
        uri = r["uri"]
        m = re.match(r'api/([^/\{]+)', uri)
        if m:
            mod = m.group(1)
            if mod not in modules:
                modules[mod] = []
            modules[mod].append(r)
    
    # 输出
    for mod in sorted(modules.keys()):
        print(f"\n📦 {mod} ({len(modules[mod])} 个)")
        for r in sorted(modules[mod], key=lambda x: x["uri"]):
            print(f"    {r['method']:<18} {r['uri']}")
    
    # 保存 JSON
    out_file = "D:/work/website/OA/.workbuddy/_test/api_tests/api_routes_172.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已保存到: {out_file}")
    
    client.close()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
