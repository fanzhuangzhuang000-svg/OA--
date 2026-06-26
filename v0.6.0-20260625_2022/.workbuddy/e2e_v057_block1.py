#!/usr/bin/env python3
"""V0.5.7 块1 — 项目/工单/返修互锁 e2e"""
import requests
import json
import sys
import subprocess

API = 'http://192.168.3.117/api'

def login(u):
    r = requests.post(f'{API}/auth/login', json=u, timeout=10)
    r.raise_for_status()
    d = r.json()['data']
    return d['token']

def get(t, path, **kw):
    return requests.get(f'{API}{path}', headers={'Authorization': f'Bearer {t}'}, timeout=10, **kw)

def post(t, path, data=None):
    return requests.post(f'{API}{path}', json=data, headers={'Authorization': f'Bearer {t}'}, timeout=10)

passed = failed = 0
def check(name, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  ✓ {name}')
    else:
        failed += 1
        print(f'  ✗ {name} {detail}')

print('=' * 60)
print('V0.5.7 块1 — 项目/工单/返修互锁 e2e')
print('=' * 60)

token = login({'username': 'admin1', 'password': 'admin123'})
print(f'\n[登录] admin1')

# 找 2 个项目: 一个 settlement/warranty 阶段, 一个 construction 阶段
print('\n[1] 找测试项目')
r = get(token, '/projects', params={'per_page': 100})
projects = r.json().get('data', {}).get('data', [])
settle_proj = None
constr_proj = None
for p in projects:
    stage = p.get('stage', '')
    if not settle_proj and stage in ('settlement', 'warranty'):
        settle_proj = p
    if not constr_proj and stage in ('construction', 'purchase'):
        constr_proj = p
    if settle_proj and constr_proj:
        break

# 如果没现成, 用任意 2 个
if not settle_proj and projects: settle_proj = projects[0]
if not constr_proj and len(projects) > 1: constr_proj = projects[1]

check('找到测试项目', settle_proj is not None, f'total={len(projects)}')
if settle_proj:
    print(f'  settle_proj: id={settle_proj["id"]} no={settle_proj.get("project_no")} stage={settle_proj.get("stage")}')
if constr_proj:
    print(f'  constr_proj: id={constr_proj["id"]} no={constr_proj.get("project_no")} stage={constr_proj.get("stage")}')

# 清空之前的测试工单
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM repair_orders WHERE code LIKE 'WO2027-%' OR code LIKE 'V057-%'; DELETE FROM work_orders WHERE code LIKE 'WO2027-%' OR code LIKE 'V057-%';\""
], capture_output=True, text=True, timeout=10)

# A1: GET /projects/{id}/maintenance (任何项目都 200)
print('\n[2] GET /projects/{id}/maintenance')
if settle_proj:
    r = get(token, f'/projects/{settle_proj["id"]}/maintenance')
    d = r.json().get('data', {})
    check('A1 maintenance 端点 200', r.status_code == 200)
    check('A1 返回 project_id', d.get('project_id') == settle_proj['id'])
    check('A1 返回 can_create_maintenance', 'can_create_maintenance' in d)
    check('A1 返回 items 数组', 'items' in d and isinstance(d['items'], list))
    check('A1 返回 stats', 'stats' in d and 'work_order_count' in d['stats'])

# A2: settlement 阶段项目 can_create=true
if settle_proj:
    r = get(token, f'/projects/{settle_proj["id"]}/maintenance')
    d = r.json().get('data', {})
    can = d.get('can_create_maintenance', {})
    print(f'  can_create: {can}')
    if settle_proj.get('stage') in ('settlement', 'warranty'):
        check('A2 settlement 阶段允许创建', can.get('allowed') is True)
    else:
        check('A2 该阶段不允许创建', can.get('allowed') is False, f'allowed={can.get("allowed")}')

# A3: construction 阶段项目 can_create=false
if constr_proj:
    r = get(token, f'/projects/{constr_proj["id"]}/maintenance')
    d = r.json().get('data', {})
    can = d.get('can_create_maintenance', {})
    if constr_proj.get('stage') in ('construction', 'purchase', 'contract', 'inquiry', 'initiation'):
        check('A3 construction 阶段拒绝创建', can.get('allowed') is False, f'allowed={can.get("allowed")}')
        if not can.get('allowed'):
            check('A3 拒绝原因含阶段名', '阶段' in (can.get('reason') or ''))

# A4: 给非 settlement 项目 POST /work-orders 带 project_id 应 422
print('\n[3] POST /work-orders 项目阶段校验')
if constr_proj and constr_proj.get('stage') not in ('settlement', 'warranty'):
    r = post(token, '/work-orders', {
        'project_id': constr_proj['id'],
        'contact_name': 'test',
        'fault_description': '阶段校验测试',
    })
    check('A4 construction 阶段 POST 工单 422', r.status_code == 422, f'code={r.status_code}')
    if r.status_code == 422:
        d = r.json()
        check('A4 错误信息含阶段', '阶段' in (d.get('message') or ''), d.get('message', '')[:100])

# A5: 给 settlement 项目 POST /work-orders 应成功
if settle_proj and settle_proj.get('stage') in ('settlement', 'warranty'):
    r = post(token, '/work-orders', {
        'project_id': settle_proj['id'],
        'contact_name': '互锁测试',
        'fault_description': 'V0.5.7 互锁测试工单',
    })
    check('A5 settlement 阶段 POST 工单 200', r.status_code == 200, f'code={r.status_code}')
    if r.status_code == 200 and r.json().get('code') == 0:
        wo_id = r.json()['data']['id']
        print(f'  ✓ created work_order id={wo_id}')

# A6: 返修单阶段校验
print('\n[4] POST /repair-orders 项目阶段校验')
if constr_proj and constr_proj.get('stage') not in ('settlement', 'warranty'):
    r = post(token, '/repair-orders', {
        'project_id': constr_proj['id'],
        'contact_name': 'test',
        'fault_description': '返修阶段校验',
    })
    check('A6 construction 阶段 POST 返修 422', r.status_code == 422, f'code={r.status_code}')

# A7: 跨阶段 — settlement 项目建工单 → 返修端点 maintenance items 应该看到
print('\n[5] 端点联动')
if settle_proj:
    r = get(token, f'/projects/{settle_proj["id"]}/maintenance')
    items = r.json().get('data', {}).get('items', [])
    has_wo = any(i.get('type') == 'work_order' for i in items)
    check('A7 项目详情看到 work_order', has_wo, f'item count={len(items)}')

# 总结
print('\n' + '=' * 60)
print(f'通过 {passed} / 失败 {failed}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
