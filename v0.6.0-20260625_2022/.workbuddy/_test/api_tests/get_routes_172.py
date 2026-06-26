#!/usr/bin/env python3
"""
从 172 服务器获取完整 API 路由表，输出为 JSON 方便分析
"""
import paramiko
import json
import sys

HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
    return client

def run(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err

def main():
    client = ssh_connect()
    
    print("📋 获取 API 路由表...")
    code, out, err = run(client, "cd /var/www/oa-api && php artisan route:list --format=json 2>/dev/null | grep -v '^INFO' | grep -v '^  ' | head -3000")
    
    # 尝试直接获取 JSON
    cmd = "cd /var/www/oa-api && php -r '\\$app = require_once \\\"/var/www/oa-api/public/index.php\\\";' 2>/dev/null || echo 'FAILED'"
    
    # 更简单的方法：直接写文件
    print("📝 写入临时路由文件...")
    code, out, err = run(client, "cd /var/www/oa-api && php artisan route:list --format=json > /tmp/routes.json 2>&1", timeout=30)
    print(f"  退出码: {code}")
    if err.strip():
        print(f"  stderr: {err[:200]}")
    
    # 下载路由文件
    print("📥 下载路由文件...")
    sftp = client.open_sftp()
    try:
        sftp.get("/tmp/routes.json", "D:/work/website/OA/.workbuddy/_test/api_tests/routes_172.json")
        print("  ✅ 路由文件下载成功")
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        # 尝试读取远程文件内容
        try:
            with sftp.open("/tmp/routes.json", "r") as f:
                content = f.read()
            with open("D:/work/website/OA/.workbuddy/_test/api_tests/routes_172.json", "w") as f:
                f.write(content)
            print("  ✅ 路由文件下载成功（备选方法）")
        except Exception as e2:
            print(f"  ❌ 备选方法也失败: {e2}")
    finally:
        sftp.close()
    
    client.close()
    
    # 解析并显示
    try:
        with open("D:/work/website/OA/.workbuddy/_test/api_tests/routes_172.json", "r", encoding="utf-8") as f:
            routes = json.load(f)
        
        print(f"\n📋 共 {len(routes)} 条路由")
        print("="*60)
        
        # 只显示 api 路由
        api_routes = [r for r in routes if 'api' in r.get('uri', '')]
        print(f"API 路由: {len(api_routes)} 条")
        print("\n所有 API 路由:")
        for r in api_routes:
            print(f"  {r.get('method','?'):<8} {r.get('uri','?')}")
        
        # 按模块分组
        print("\n按模块分组:")
        modules = {}
        for r in api_routes:
            uri = r.get('uri', '')
            # 提取模块名（第二段）
            parts = uri.split('/')
            if len(parts) >= 3:
                module = parts[1]  # /api/{module}/...
                if module not in modules:
                    modules[module] = []
                modules[module].append(r)
        
        for module, routes_list in sorted(modules.items()):
            print(f"\n  📦 {module} ({len(routes_list)} 个端点)")
            for r in routes_list:
                print(f"      {r.get('method','?'):<8} {r.get('uri','?')}")
        
    except Exception as e:
        print(f"❌ 解析路由文件失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
