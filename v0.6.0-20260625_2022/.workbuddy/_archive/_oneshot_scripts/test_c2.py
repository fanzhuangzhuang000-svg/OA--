"""Test C2: create role -> check audit log"""
import urllib.request, json, urllib.parse
BASE = 'http://172.20.0.139:3001'
def call(method, path, token=None, body=None):
    # Encode URL for non-ASCII chars
    parts = urllib.parse.urlparse(path)
    encoded_path = urllib.parse.quote(parts.path, safe='/=&?')
    if parts.query:
        encoded_path += '?' + urllib.parse.quote(parts.query, safe='=&')
    url = f'{BASE}{encoded_path}'
    data = json.dumps(body).encode() if body is not None else None
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    if token: headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# Login
code, body = call('POST', '/api/auth/login', body={'username': 'admin', 'password': 'admin123'})
token = json.loads(body)['data']['token']
print(f'LOGIN: {code}')

# Create a role (triggers Observer)
import time
role_name = f'审计测试角色_{int(time.time())}'
code, body = call('POST', '/api/roles', token=token, body={
    'name': role_name,
    'description': '用于触发审计 Observer',
    'color': '#000000',
    'permissions': [],
})
print(f'CREATE ROLE [{role_name}]: {code} {body}')
try:
    new_id = json.loads(body)['data']['id']
except Exception:
    new_id = None
    print('  -> create failed, aborting remaining tests')
    raise SystemExit(1)

# Update role
code, body = call('PUT', f'/api/roles/{new_id}', token=token, body={'description': '已更新描述'})
print(f'UPDATE ROLE: {code} {body}')

# Wait a bit
time.sleep(1)

# Check audit logs (no filter first to see all)
code, body = call('GET', '/api/audit-logs?per_page=50', token=token)
print(f'GET /api/audit-logs (latest 50): {code}')
data = json.loads(body)['data']
print(f'  total: {data["total"]}')
for r in data['data'][:8]:
    print(f'  - [{r["action"]}] [{r["module"]}] {r["description"]} by {r["operator"]} (resp={r["response"]})')

# Delete role
code, body = call('DELETE', f'/api/roles/{new_id}', token=token)
print(f'DELETE ROLE: {code} {body}')

time.sleep(1)

# Final check
code, body = call('GET', '/api/audit-logs?per_page=10', token=token)
data = json.loads(body)['data']
print(f'\nFINAL AUDIT LOGS (latest 10): {data["total"]} entries total')
for r in data['data'][:6]:
    print(f'  - [{r["action"]}] [{r["module"]}] {r["description"]} by {r["operator"]}')
