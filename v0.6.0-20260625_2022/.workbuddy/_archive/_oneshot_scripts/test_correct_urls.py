import urllib.request, urllib.error, json

req = urllib.request.Request(
    'http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']

# 测试所有正确URL（按 api/modules.ts 中的定义）
tests = [
    ('/expenses', 'GET'),
    ('/expenses/stats', 'GET'),
    ('/expenses/1', 'GET'),
    ('/projects', 'GET'),
    ('/projects/1', 'GET'),
    ('/projects/1/tracking', 'GET'),
    ('/inventory', 'GET'),
    ('/inventory/stats', 'GET'),
    ('/inventory/1', 'GET'),
    ('/inventory-categories', 'GET'),
    ('/inventory-categories/tree', 'GET'),
    ('/inventory/warehouses', 'GET'),
    ('/inventory/low-stock', 'GET'),
    ('/finance/accounts', 'GET'),
    ('/finance/accounts/1/transactions', 'GET'),
    ('/customers/health', 'GET'),
    ('/customers/1/profile', 'GET'),
    ('/disk/folders', 'GET'),
    ('/disk/files', 'GET'),
    ('/approvals/center', 'GET'),
    ('/approvals/center/1', 'GET'),
    ('/approvals/center/stats', 'GET'),
    ('/sales/leads', 'GET'),
    ('/sales/leads/board', 'GET'),
    ('/sales/opps/board', 'GET'),
    ('/system-logs', 'GET'),
    ('/vehicles/insurances', 'GET'),
    ('/vehicles/maintenances', 'GET'),
    ('/vehicles/1', 'GET'),
    ('/vehicles/1/insurances', 'GET'),  # 嵌套
    ('/positions', 'GET'),
    ('/positions/tree', 'GET'),
]

print(f'Token: {token[:20]}...\n')
ok, fail = [], []
for url, method in tests:
    try:
        req = urllib.request.Request(
            f'http://172.20.0.139:3001/api{url}',
            headers={'Authorization': f'Bearer {token}'}
        )
        resp = urllib.request.urlopen(req, timeout=8)
        ok.append((url, resp.status))
        print(f'  [{resp.status}] {url}')
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:120]
        fail.append((url, e.code, body))
        print(f'  [{e.code}] {url} - {body}')

print(f'\n=== OK: {len(ok)} / FAIL: {len(fail)} ===')
