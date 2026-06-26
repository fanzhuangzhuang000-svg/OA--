#!/usr/bin/env python3
"""V0.5.7 块2 — 维修过程照片 e2e"""
import requests
import json
import io
import sys
import subprocess

API = 'http://192.168.3.117/api'

def login(u):
    r = requests.post(f'{API}/auth/login', json=u, timeout=10)
    r.raise_for_status()
    return r.json()['data']['token']

def get(t, p, **kw):
    return requests.get(f'{API}{p}', headers={'Authorization': f'Bearer {t}'}, timeout=10, **kw)

def post(t, p, d=None, files=None):
    h = {'Authorization': f'Bearer {t}'}
    if files:
        return requests.post(f'{API}{p}', data=d, files=files, headers=h, timeout=10)
    return requests.post(f'{API}{p}', json=d, headers=h, timeout=10)

def delete_photo(t, p):
    return requests.delete(f'{API}{p}', headers={'Authorization': f'Bearer {t}'}, timeout=10)

passed = failed = 0
def check(n, c, det=''):
    global passed, failed
    if c: passed += 1; print(f'  ✓ {n}')
    else:  failed += 1; print(f'  ✗ {n} {det}')

print('=' * 60)
print('V0.5.7 块2 — 维修过程照片 e2e')
print('=' * 60)

token = login({'username': 'admin1', 'password': 'admin123'})
print(f'\n[登录] admin1')

# 清旧数据
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM work_orders WHERE code LIKE 'V057P-%'; DELETE FROM repair_step_photos WHERE target_id IN (SELECT id FROM work_orders WHERE code LIKE 'V057P-%');\""
], capture_output=True, text=True, timeout=10)

# 创建一个 settlement 阶段项目的工单 (用 settlement proj)
r = get(token, '/projects', params={'per_page': 100, 'stage': 'settlement'})
projects = r.json().get('data', {}).get('data', [])
if not projects:
    projects = r.json().get('data', {}).get('data', [])
if not projects:
    r = get(token, '/projects', params={'per_page': 100})
    projects = r.json().get('data', {}).get('data', [])
    for p in projects:
        if p.get('stage') == 'settlement':
            projects = [p]; break

# 找测试项目
settle_proj = None
for p in projects:
    if p.get('stage') in ('settlement', 'warranty'):
        settle_proj = p; break
if not settle_proj and projects:
    settle_proj = projects[0]
check('找到测试项目', settle_proj is not None, '没有项目')

# 创建工单
r = post(token, '/work-orders', {
    'project_id': settle_proj['id'] if settle_proj else None,
    'contact_name': '块2测试',
    'fault_description': 'V0.5.7 块2 过程照片测试',
})
if r.status_code == 200 and r.json().get('code') == 0:
    wo_id = r.json()['data']['id']
    print(f'  ✓ 工单 id={wo_id}')
else:
    # 已存在, 取
    out = subprocess.run([
        'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
        "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -tA -c \"SELECT id FROM work_orders WHERE code='V057P-001';\""
    ], capture_output=True, text=True, timeout=10)
    wo_id = int(out.stdout.strip() or 0)
check('工单就绪', wo_id > 0, f'wo_id={wo_id}')

# A1: GET step-photos (空)
r = get(token, '/step-photos', params={'target_type': 'work_order', 'target_id': wo_id})
d = r.json().get('data', {})
check('A1 GET step-photos 200', r.status_code == 200 and r.json().get('code') == 0)
check('A1 返回 STEPS 列表', 'steps' in d and 'diagnose' in d['steps'])
check('A1 初始 0 张', d.get('counts', {}).get('total') == 0)

# A2: 上传 3 张不同 step 的照片
png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\x86\xa3i\x00\x00\x00\x00IEND\xaeB`\x82'
uploaded_ids = []
for step in ['diagnose', 'replace', 'test']:
    files = {'file': (f'{step}.png', io.BytesIO(png), 'image/png')}
    r = post(token, '/step-photos', {
        'target_type': 'work_order',
        'target_id': str(wo_id),
        'step': step,
        'description': f'测试 {step}',
    }, files=files)
    if r.status_code == 200 and r.json().get('code') == 0:
        uploaded_ids.append(r.json()['data']['id'])
        check(f'A2 上传 {step}', True, r.text[:100])
    else:
        check(f'A2 上传 {step}', False, f'code={r.status_code} body={r.text[:200]}')

# A3: GET 列表, 应有 3 张
r = get(token, '/step-photos', params={'target_type': 'work_order', 'target_id': wo_id})
d = r.json().get('data', {})
check('A3 列表 3 张', d.get('counts', {}).get('total') == 3, f'got {d.get("counts")}')
check('A3 by_step 分组', 'diagnose' in d.get('by_step', {}) and 'replace' in d.get('by_step', {}))
check('A3 步骤 label 中文', d['items'][0].get('step_label', '').startswith('🔍') or
      d['items'][0].get('step_label', '').startswith('🔄') or
      d['items'][0].get('step_label', '').startswith('✅'))

# A4: 删除一张
if uploaded_ids:
    r = delete_photo(token, f'/step-photos/{uploaded_ids[0]}')
    check('A4 DELETE 照片', r.status_code == 200 and r.json().get('code') == 0, r.text[:100])

# A5: 列表应剩 2 张
r = get(token, '/step-photos', params={'target_type': 'work_order', 'target_id': wo_id})
d = r.json().get('data', {})
check('A5 删除后剩 2 张', d.get('counts', {}).get('total') == 2, f'got {d.get("counts")}')

# A6: 参数校验
r = get(token, '/step-photos', params={'target_type': 'invalid', 'target_id': wo_id})
check('A6 target_type 错误返 422', r.status_code == 422, f'code={r.status_code}')

# A7: 工单 type + 返修 type 共用
# 找返修单
r = get(token, '/repair-orders', params={'per_page': 5})
ros = r.json().get('data', {}).get('data', [])
if ros:
    ro_id = ros[0]['id']
    files = {'file': ('rep_test.png', io.BytesIO(png), 'image/png')}
    r = post(token, '/step-photos', {
        'target_type': 'repair_order',
        'target_id': str(ro_id),
        'step': 'package',
    }, files=files)
    check('A7 返修单上传', r.status_code == 200 and r.json().get('code') == 0, r.text[:100])

print('\n' + '=' * 60)
print(f'通过 {passed} / 失败 {failed}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
