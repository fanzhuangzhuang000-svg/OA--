import paramiko, requests

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 从服务器角度访问 API
print("=" * 60)
print("1. 从服务器测试完整 API 流程")
print("=" * 60)

# 登录
login_cmd = """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}'"""
stdin, stdout, stderr = ssh.exec_command(login_cmd)
login_resp = stdout.read().decode()
print(f"Login response: {login_resp[:500]}")

import json
try:
    data = json.loads(login_resp)
    token = data.get('data', {}).get('token') or data.get('token')
    if token:
        print(f"\nToken 获取成功: {token[:30]}...")

        # 测试 dashboard 接口
        print("\n2. 测试 dashboard 各接口:")
        for ep in ['/api/dashboard/stats', '/api/dashboard/project-progress', '/api/dashboard/revenue-trend', '/api/dashboard/service-stats', '/api/dashboard/todo']:
            stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost{ep} -H 'Authorization: Bearer {token}'")
            resp = stdout.read().decode()
            try:
                d = json.loads(resp)
                if d.get('code') == 0:
                    data = d.get('data', [])
                    if isinstance(data, list):
                        print(f"  OK {ep}: {len(data)} 条")
                    else:
                        print(f"  OK {ep}: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}")
                else:
                    print(f"  ERR {ep}: {d.get('message', 'unknown')[:100]}")
            except Exception as e:
                print(f"  PARSE_ERR {ep}: {resp[:200]}")
except Exception as e:
    print(f"Login parse error: {e}")

# 2. 从外网角度访问首页
print("\n" + "=" * 60)
print("3. 从外网角度访问首页")
print("=" * 60)
try:
    r = requests.get('http://172.20.0.139', timeout=10)
    print(f"  Status: {r.status_code}")
    print(f"  Content length: {len(r.text)}")
    print(f"  First 200 chars: {r.text[:200]}")
except Exception as e:
    print(f"  ERR: {e}")

# 3. 检查 DashboardController 是否有最近的修改
print("\n" + "=" * 60)
print("4. 检查 DashboardController 文件时间戳")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php")
print(stdout.read().decode())

# 4. 检查前端构建时间
print("\n" + "=" * 60)
print("5. 检查前端 assets 目录时间")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/oa-web/assets/ | head -10")
print(stdout.read().decode())

ssh.close()
print("done")
