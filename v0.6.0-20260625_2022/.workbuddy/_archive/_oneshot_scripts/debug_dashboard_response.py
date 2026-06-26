import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 登录
cmd_login = "curl -s -X POST http://127.0.0.1/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'"
stdin, stdout, stderr = ssh.exec_command(cmd_login)
login_resp = stdout.read().decode()
print("=== LOGIN RESPONSE ===")
print(login_resp[:500])

try:
    token = json.loads(login_resp).get('data', {}).get('token', '') or json.loads(login_resp).get('token', '')
except:
    token = ''

# 尝试多种取 token 方式
try:
    lr = json.loads(login_resp)
    token = lr.get('data', {}).get('token') or lr.get('token') or lr.get('access_token', '')
    print(f"Token found: {bool(token)}, length: {len(token) if token else 0}")
except Exception as e:
    print(f"Parse error: {e}")
    print(f"Raw: {login_resp[:300]}")

# 2. 测试 stats 接口（带 token）
if token:
    auth = f"Authorization: Bearer {token}"
    for endpoint in ['stats', 'project-progress', 'todo', 'service-stats', 'revenue-trend']:
        cmd = f"curl -s http://127.0.0.1/api/dashboard/{endpoint} -H '{auth}'"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        resp = stdout.read().decode()
        try:
            r = json.loads(resp)
            print(f"\n=== /api/dashboard/{endpoint} ===")
            print(f"Top-level keys: {list(r.keys())}")
            print(f"code: {r.get('code')}")
            print(f"data: {str(r.get('data'))[:300]}")
        except Exception as e:
            print(f"\n=== /api/dashboard/{endpoint} ===")
            print(f"PARSE ERROR: {resp[:200]}")

ssh.close()
