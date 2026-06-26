"""用正确方法测试：GET/POST/PUT/DELETE"""
import urllib.request, urllib.error, json

req = urllib.request.Request(
    'http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']
H = {'Authorization': f'Bearer {token}'}
BASE = 'http://172.20.0.139:3001/api'

def call(url, method='GET', data=None):
    try:
        r = urllib.request.Request(f'{BASE}{url}', headers=H, method=method)
        if data:
            r.data = json.dumps(data).encode()
            r.add_header('Content-Type', 'application/json')
        resp = urllib.request.urlopen(r, timeout=8)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as e:
        return 'EXC', str(e)[:150]

# 22个FAIL，用对应方法重测
tests = [
    ('GET', '/approvals', None),
    ('GET', '/attendance', None),
    ('POST', '/attendance/clock-in', {}),
    ('POST', '/attendance/clock-out', {}),
    ('GET', '/attendance/stats', None),
    ('GET', '/customers/map', None),
    ('GET', '/employee-resignations/settlement-preview?employee_id=1', None),
    ('GET', '/finance/receipts', None),
    ('GET', '/finance/transfers', None),
    ('GET', '/follow-ups/calendar?start=2026-06-01&end=2026-06-30', None),
    ('POST', '/inventory/batch-delete', {'ids': []}),
    ('POST', '/inventory/batch-export', {}),
    ('POST', '/inventory/batch-update', {}),
    ('POST', '/inventory/items/batch-import', {}),
    ('GET', '/inventory/items/export-template', None),
    ('GET', '/purchase/logistics', None),
    ('GET', '/schedules?start=2026-06-01&end=2026-06-30', None),
    ('POST', '/schedules/batch-by-group', {}),
    ('GET', '/schedules/smart-suggest?date=2026-06-22', None),
    ('GET', '/service/orders/stats', None),
    ('GET', '/vehicles/applies', None),
    ('GET', '/vehicles/apply', None),
]

print('=== 用正确方法重测 ===\n')
ok, fail = [], []
for method, url, data in tests:
    code, body = call(url, method, data)
    if code == 200:
        ok.append((method, url))
        print(f'  ✅ [{method} {code}] {url}')
    else:
        fail.append((method, url, code, body))
        print(f'  ❌ [{method} {code}] {url}')
        print(f'        {body[:150] if isinstance(body, str) else body}')

print(f'\n=== OK: {len(ok)} / FAIL: {len(fail)} ===')
