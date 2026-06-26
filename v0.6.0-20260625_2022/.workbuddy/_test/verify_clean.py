import paramiko, sys, json
sys.path.insert(0, r'D:\work\website\OA\.workbuddy')
import importlib.util
spec = importlib.util.spec_from_file_location('deploy', r'D:\work\website\OA\.workbuddy\deploy_to_172.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ssh = m.ssh_connect()

# 1) login
si, so, se = ssh.exec_command(
    'curl -sS -X POST http://127.0.0.1/api/auth/login '
    '-H "Content-Type: application/json" '
    '-d \'{"username":"admin","password":"admin123"}\'',
    timeout=10
)
r = json.loads(so.read().decode() or '{}')
print(f'login: code={r.get("code")} token={"yes" if r.get("data",{}).get("token") else "no"}')
token = r.get('data', {}).get('token', '')

# 2) 各端点
endpoints = [
    ('/dashboard/stats', 'GET'),
    ('/inventory-categories', 'GET'),
    ('/purchase/payment-requests', 'GET'),
    ('/employees', 'GET'),
    ('/auth/me', 'GET'),
]
for ep, method in endpoints:
    cmd = f'''curl -sS -o /tmp/r.json -w "%{{http_code}}" -X {method} -H "Authorization: Bearer {token}" "http://127.0.0.1/api{ep}"'''
    si, so, se = ssh.exec_command(cmd, timeout=10)
    http = so.read().decode().strip()
    si, so, se = ssh.exec_command('cat /tmp/r.json | head -c 100; echo', timeout=5)
    body = so.read().decode().strip()[:80]
    print(f'  {method} {ep:35s} HTTP {http}  body={body}')

ssh.close()
