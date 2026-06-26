import requests, json, time
BASE = 'http://127.0.0.1/api'

# 1) 登录
r = requests.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin123'})
print('登录:', r.status_code, r.json().get('code'))
token = r.json().get('data', {}).get('token', '')
if not token:
    print('登录失败 body:', r.text[:200])
    exit(1)
h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 2) 找一条 status=contacted 的 lead
r2 = requests.get(f'{BASE}/sales/leads', headers=h, params={'per_page': 50})
all_leads = r2.json().get('data', {}).get('data', [])
print(f'总线索数: {len(all_leads)}')

# 看 status 分布
from collections import Counter
status_counter = Counter(l['status'] for l in all_leads)
print(f'状态分布: {dict(status_counter)}')

contacted = next((l for l in all_leads if l['status'] == 'contacted'), None)
if not contacted:
    print('❌ 没找到 status=contacted 的 lead')
    exit(1)
print(f'\n测试 lead: id={contacted["id"]} status={contacted["status"]}')

# 3) 模拟看板拖动：contacted → qualified
print('\n--- 复现看板拖动 ---')
r3 = requests.patch(f'{BASE}/sales/leads/{contacted["id"]}/status', headers=h, json={'status': 'qualified'})
print(f'PATCH contacted→qualified:')
print(f'  HTTP {r3.status_code}')
print(f'  body: {r3.text[:300]}')

# 4) 再试一次 negotiated → qualified
neg = next((l for l in all_leads if l['status'] == 'negotiating'), None)
if neg:
    print(f'\n测试 lead: id={neg["id"]} status=negotiating')
    r4 = requests.patch(f'{BASE}/sales/leads/{neg["id"]}/status', headers=h, json={'status': 'qualified'})
    print(f'PATCH negotiating→qualified:')
    print(f'  HTTP {r4.status_code}')
    print(f'  body: {r4.text[:300]}')

# 5) 试一下：contacted → contacted (相同)
print(f'\n--- 边界：相同状态 ---')
r5 = requests.patch(f'{BASE}/sales/leads/{contacted["id"]}/status', headers=h, json={'status': 'contacted'})
print(f'PATCH contacted→contacted: HTTP {r5.status_code}')
print(f'  body: {r5.text[:200]}')
