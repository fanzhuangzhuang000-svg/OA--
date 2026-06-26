"""用 admin token 测 idle-config 端点"""
import paramiko, json
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=10)

# 登录拿 token
login_cmd = """curl -s -X POST -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' http://127.0.0.1:3001/api/auth/login"""
si, so, se = ssh.exec_command(login_cmd)
login_resp = json.loads(so.read().decode())
token = login_resp.get('data', {}).get('token') or login_resp.get('token')
if not token:
    print('LOGIN FAILED:', login_resp)
    raise SystemExit(1)
print('TOKEN OK:', token[:20] + '...')

# 调 idle-config
si, so, se = ssh.exec_command(f"curl -s -H 'Authorization: Bearer {token}' http://127.0.0.1:3001/api/settings/idle-config")
print('IDLE CONFIG:')
print(so.read().decode())

# 测 PUT 更新
si, so, se = ssh.exec_command(f"curl -s -X PUT -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{{\"idle_timeout_minutes\":45,\"idle_warning_seconds\":90,\"idle_enabled\":true}}' http://127.0.0.1:3001/api/settings")
print('PUT SETTINGS:')
print(so.read().decode()[:600])

# 再读一次
si, so, se = ssh.exec_command(f"curl -s -H 'Authorization: Bearer {token}' http://127.0.0.1:3001/api/settings/idle-config")
print('IDLE CONFIG (after PUT):')
print(so.read().decode())

ssh.close()
