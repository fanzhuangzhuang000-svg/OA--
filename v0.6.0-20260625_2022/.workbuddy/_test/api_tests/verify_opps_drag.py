import requests, json
BASE = 'http://127.0.0.1/api'

r = requests.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 找 requirement 状态的 opp
r2 = requests.get(f'{BASE}/sales/opps', headers=h, params={'per_page': 5, 'stage': 'requirement'})
opps = r2.json().get('data', {}).get('data', [])
if not opps:
    # 拿任意
    r2 = requests.get(f'{BASE}/sales/opps', headers=h, params={'per_page': 5})
    opps = r2.json().get('data', {}).get('data', [])
print(f'opps: {len(opps)}')
if not opps:
    exit(0)

# 用 SQL 强制 reset
import subprocess
oid = opps[0]['id']
print(f'测试 opp id={oid}')

# 7 段值（前端看板）
tests = [
    ('inquiry', 'requirement'),
    ('qualification', 'solution'),
    ('proposal', 'negotiation'),
    ('negotiating', 'negotiation'),
    ('quoted', 'contracting'),
    ('requirement', 'requirement'),
]
for board_val, expected_db in tests:
    # SQL 重置
    subprocess.run(['psql', '-U', 'oa_user', '-d', 'security_oa', '-c',
                    f"UPDATE opportunities SET stage='requirement' WHERE id={oid};"],
                   env={'PGPASSWORD': 'oapass', 'PATH': '/usr/bin:/usr/local/bin'},
                   capture_output=True, text=True)
    r3 = requests.patch(f'{BASE}/sales/opps/{oid}/stage', headers=h, json={'stage': board_val})
    code = r3.json().get('code')
    db = r3.json().get('data', {}).get('stage', '?') if code == 0 else '-'
    msg = r3.json().get('message', '')[:50] if code != 0 else ''
    mark = '✅' if code == 0 and db == expected_db else '❌'
    print(f'  {mark} PATCH {board_val:14s} → HTTP {r3.status_code} code={code} db={db} (期望 {expected_db}) {msg}')
