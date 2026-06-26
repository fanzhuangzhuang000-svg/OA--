"""
Test C1 CRUD via curl
"""
import urllib.request, json

BASE = 'http://172.20.0.139:3001'

def call(method, path, token=None, body=None):
    url = f'{BASE}{path}'
    data = None
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if body is not None:
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# 1) Login
code, body = call('POST', '/api/auth/login', body={'username': 'admin', 'password': 'admin123'})
print(f'LOGIN: {code} {body[:120]}')
token = json.loads(body)['data']['token']

# 2) GET roles
code, body = call('GET', '/api/roles', token=token)
print(f'GET /api/roles: {code} count={len(json.loads(body)["data"]["data"])}')

# 3) POST role
code, body = call('POST', '/api/roles', token=token, body={
    'name': '测试角色',
    'description': 'API测试',
    'color': '#ff0000',
    'permissions': ['系统管理.系统参数配置'],
})
print(f'POST /api/roles: {code} {body}')

# 4) Sync perms
code, body = call('POST', '/api/roles/1/permissions', token=token, body={
    'permissions': ['系统管理.系统参数配置', '员工管理.员工列表查看', '考勤管理.打卡记录查看'],
})
print(f'POST /api/roles/1/permissions: {code} {body}')

# 5) PUT update
code, body = call('PUT', '/api/roles/1', token=token, body={
    'description': '超管（已通过 API 更新）',
})
print(f'PUT /api/roles/1: {code} {body}')

# 6) DELETE test role
code, body = call('GET', '/api/roles', token=token)
test_id = [r['id'] for r in json.loads(body)['data']['data'] if r['name'] == '测试角色'][0]
code, body = call('DELETE', f'/api/roles/{test_id}', token=token)
print(f'DELETE /api/roles/{test_id}: {code} {body}')

# 7) Verify final state
code, body = call('GET', '/api/roles', token=token)
data = json.loads(body)['data']
print(f'FINAL: {len(data["data"])} roles, super admin desc: {[r for r in data["data"] if r["id"]==1][0]["description"]}')

# 8) Test RBAC forbid (assign super to non-super - just check error path)
code, body = call('DELETE', '/api/roles/1', token=token)
print(f'DELETE /api/roles/1 (should fail - has members): {code} {body}')
