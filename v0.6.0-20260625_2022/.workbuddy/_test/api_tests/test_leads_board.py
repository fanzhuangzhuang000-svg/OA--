import requests, json, time
BASE = 'http://127.0.0.1/api'

# 登录
s = requests.Session()
r = s.post(f'{BASE}/auth/login', json={'username': 'nbcy', 'password': 'admin123'})
print('登录:', r.status_code, r.json().get('code'))
token = r.json().get('data', {}).get('token', '')
h = {'Authorization': f'Bearer {token}'}

# 拿一个新建状态的线索
r = s.get(f'{BASE}/sales/leads', headers=h, params={'per_page': 50, 'status': 'new'})
leads = r.json().get('data', {}).get('data', [])
if not leads:
    # 取任意一个
    r = s.get(f'{BASE}/sales/leads', headers=h, params={'per_page': 50})
    leads = r.json().get('data', {}).get('data', [])
print('可用线索数:', len(leads))
if not leads:
    print('❌ 无可用线索')
    exit(1)

# 找一个 status=new 的
target = None
for l in leads:
    if l.get('status') == 'new':
        target = l
        break
if not target:
    target = leads[0]
print(f'使用线索: id={target["id"]} 当前 status={target.get("status")}')

# 模拟前端拖动：new → contacted（归一化为 contacting）
tests = [
    ('new', 'contacted'),       # 前端看板值
    ('contacting', 'qualified'),
    ('qualified', 'proposal'),
    ('qualified', 'negotiating'),
    ('qualified', 'won'),
    ('converted', 'lost'),
    ('discarded', 'new'),
]

cur = target['status']
for src, dst in tests:
    # 先把线索改回 src
    if cur != src:
        s.put(f'{BASE}/sales/leads/{target["id"]}/status', headers=h, json={'status': src})
        cur = src
    r = s.put(f'{BASE}/sales/leads/{target["id"]}/status', headers=h, json={'status': dst})
    j = r.json()
    msg = j.get('message', '')[:50]
    new_status = j.get('data', {}).get('status', '?') if j.get('code') == 0 else '-'
    ok = '✅' if j.get('code') == 0 else '❌'
    print(f'{ok} {src:12s} → {dst:12s} | HTTP {r.status_code} | code={j.get("code")} | new_db_status={new_status} | msg={msg}')
    if j.get('code') == 0:
        cur = new_status
    time.sleep(0.1)

print('\n完成')
