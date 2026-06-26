import requests, json
BASE = 'http://127.0.0.1/api'

r = requests.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = r.json().get('data', {}).get('token', '')
h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 拿一些测试线索
r2 = requests.get(f'{BASE}/sales/leads', headers=h, params={'per_page': 100})
leads = r2.json().get('data', {}).get('data', [])
print(f'总线索数: {len(leads)}')

from collections import Counter
print(f'状态分布: {dict(Counter(l["status"] for l in leads))}')

# 7 段列名 → 看板 7 段值（用户拖动用的值）
# 5 段值 → DB 真实 status
# 测试每个迁移：拿 5 段值相同的 lead，PATCH 成目标
print('\n=== 5 段值内部迁移测试（合法）===')
# 从 new 拿一个
new_lead = next((l for l in leads if l['status'] == 'new'), None)
contacting_lead = next((l for l in leads if l['status'] == 'contacting'), None)
qualified_lead = next((l for l in leads if l['status'] == 'qualified'), None)
converted_lead = next((l for l in leads if l['status'] == 'converted'), None)
discarded_lead = next((l for l in leads if l['status'] == 'discarded'), None)

tests = []
if new_lead:
    tests.append((new_lead['id'], 'contacting', 'new → contacting'))
    tests.append((new_lead['id'], 'qualified', 'new → qualified'))
    tests.append((new_lead['id'], 'discarded', 'new → discarded'))
if contacting_lead:
    tests.append((contacting_lead['id'], 'qualified', 'contacting → qualified'))
    tests.append((contacting_lead['id'], 'discarded', 'contacting → discarded'))
    tests.append((contacting_lead['id'], 'new', 'contacting → new'))
if qualified_lead:
    tests.append((qualified_lead['id'], 'converted', 'qualified → converted'))
    tests.append((qualified_lead['id'], 'discarded', 'qualified → discarded'))
if converted_lead:
    tests.append((converted_lead['id'], 'contacting', 'converted → contacting (非法, 应 409)'))
if discarded_lead:
    tests.append((discarded_lead['id'], 'contacting', 'discarded → contacting (非法, 应 409)'))

print('\n--- 5 段值直接迁移 ---')
# 每个测试都重新拿一个目标状态的 lead（避免状态污染）
def get_one(status_val):
    # 重新拉取（不缓存），保证拿到当前 status
    r2 = requests.get(f'{BASE}/sales/leads', headers=h, params={'per_page': 100, 'status': status_val})
    arr = r2.json().get('data', {}).get('data', [])
    return arr[0] if arr else None

for lid, dst, desc in tests:
    # 重新从 dst 状态拿一个 lead（如果目标期望是合法的，需要 dst 状态的源）
    src_status = desc.split('→')[0].strip().replace('(非法, 应 409)', '').strip()
    if '应 409' not in desc:
        lead = get_one(src_status)
        if not lead:
            print(f'  ⚠️ {desc}: 找不到 {src_status} 状态的 lead，跳过')
            continue
        lid = lead['id']
    r = requests.patch(f'{BASE}/sales/leads/{lid}/status', headers=h, json={'status': dst})
    j = r.json()
    code = j.get('code')
    msg = j.get('message', '')[:50]
    new_db = j.get('data', {}).get('status', '?') if code == 0 else '-'
    expect_ok = '应 409' not in desc
    mark = '✅' if (code == 0 if expect_ok else code == 1) else '❌'
    print(f'  {mark} {desc}: HTTP {r.status_code} code={code} db_status={new_db} msg={msg}')

# 测试 7 段值（前端的看板列名）
print('\n--- 7 段看板值（前端的列名）---')
# 每个测试都从 fresh 的源状态拿一个 lead
test_cases = [
    ('contacted', 'contacting', 'new'),       # new → contacted (→ contacting)
    ('proposal', 'qualified', 'new'),         # new → proposal (→ qualified)
    ('negotiating', 'qualified', 'contacting'),  # contacting → negotiating (→ qualified)
    ('won', 'converted', 'qualified'),        # qualified → won (→ converted)
    ('lost', 'discarded', 'new'),             # new → lost (→ discarded)
]
for new_val, expected_db, src_status in test_cases:
    lead = get_one(src_status)
    if not lead:
        print(f'  ⚠️ 没有 {src_status} 状态的 lead，跳过 {new_val}')
        continue
    r = requests.patch(f'{BASE}/sales/leads/{lead["id"]}/status', headers=h, json={'status': new_val})
    j = r.json()
    code = j.get('code')
    db = j.get('data', {}).get('status', '?') if code == 0 else '-'
    mark = '✅' if code == 0 and db == expected_db else '❌'
    print(f'  {mark} {src_status:11s} 拖到 {new_val:12s}: HTTP {r.status_code} code={code} db={db} (期望 {expected_db})')
