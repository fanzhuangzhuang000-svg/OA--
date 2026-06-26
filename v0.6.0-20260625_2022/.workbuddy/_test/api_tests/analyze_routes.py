#!/usr/bin/env python3
"""从 172 服务器下载 routes/api.php 并分析 API 端点"""
import paramiko
import re

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
    
    print("📥 下载 routes/api.php...")
    sftp = client.open_sftp()
    try:
        with open("D:/work/website/OA/pc-api/routes/api_copy.php", "w", encoding="utf-8") as f:
            # 用 sftp get
            import io
            with sftp.open("/var/www/oa-api/routes/api.php", "r") as remote_f:
                content = remote_f.read()
            f.write(content)
            print(f"  ✅ 下载完成 ({len(content)} 字符)")
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        # 尝试用 cat 命令
        code, out, err = run(client, "cat /var/www/oa-api/routes/api.php")
        with open("D:/work/website/OA/pc-api/routes/api_copy.php", "w", encoding="utf-8") as f:
            f.write(out)
        print(f"  ✅ 用 cat 下载完成 ({len(out)} 字符)")
    finally:
        sftp.close()
    
    client.close()
    
    # 解析路由文件
    print("\n📋 解析 API 路由...")
    with open("D:/work/website/OA/pc-api/routes/api_copy.php", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取所有 Route:: 定义
    # 匹配：Route::get/post/put/delete('uri', ...)
    pattern = r"Route::(GET|POST|PUT|DELETE|PATCH|any)\s*\(\s*['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    api_routes = [m for m in matches if m[1].startswith('/api') or m[1].startswith('api')]
    
    print(f"共找到 {len(matches)} 个路由定义，其中 API 路由 {len(api_routes)} 个")
    print("=" * 70)
    
    # 按模块分组
    modules = {}
    for method, uri in api_routes:
        # 标准化 uri（去掉 /api 前缀）
        clean_uri = uri[4:] if uri.startswith('/api') else uri
        parts = clean_uri.strip('/').split('/')
        module = parts[0] if parts else 'root'
        
        if module not in modules:
            modules[module] = []
        modules[module].append((method, uri))
    
    for mod in sorted(modules.keys()):
        print(f"\n📦 {mod} ({len(modules[mod])} 个)")
        for method, uri in sorted(modules[mod], key=lambda x: x[1]):
            print(f"    {method:<10} {uri}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
