"""验证172服务器上的修复"""
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

# 19个FAIL重测
tests = [
    ('GET', '/approvals', None),
    ('GET', '/attendance', None),
    ('POST', '/attendance/clock-in', {}),
    ('GET', '/attendance/stats', None),
    ('GET', '/customers/map', None),
    ('GET', '/finance/receipts', None),
    ('GET', '/finance/transfers', None),
    ('GET', '/purchase/logistics', None),
    ('GET', '/service/orders/stats', None),
    ('GET', '/vehicles/applies', None),
    ('GET', '/vehicles/apply', None),
    # 还存在的验证错误 (前端需要传参)
    ('GET', '/employee-resignations/settlement-preview?user_id=1&resign_date=2026-06-22', None),
    ('GET', '/follow-ups/calendar?month=2026-06', None),
    ('GET', '/schedules?start_date=2026-06-01&end_date=2026-06-30', None),
    ('POST', '/inventory/batch-delete', {'ids': []}),  # 仍422因为ids空数组
]

ok, fail = [], []
for method, url, data in tests:
    code, body = call(url, method, data)
    if code == 200:
        ok.append((method, url))
        print(f'  ✅ [{method} {code}] {url}')
    else:
        fail.append((method, url, code, body))
        print(f'  ❌ [{method} {code}] {url}')
        if isinstance(body, str): print(f'        {body[:150]}')

print(f'\n=== 修复验证: OK {len(ok)} / FAIL {len(fail)} ===')
