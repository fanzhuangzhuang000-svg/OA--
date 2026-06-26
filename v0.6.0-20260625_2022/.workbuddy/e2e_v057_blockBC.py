#!/usr/bin/env python3
"""V0.5.7 块B+C — 数据字典 + 系统监控 e2e"""
import requests
import json
import sys
import subprocess

API = 'http://192.168.3.117/api'

passed = failed = 0
def check(n, c, det=''):
    global passed, failed
    if c: passed += 1; print(f'  ✓ {n}')
    else:  failed += 1; print(f'  ✗ {n} {det}')

print('=' * 60)
print('V0.5.7 块B+C — 数据字典 + 系统监控 e2e')
print('=' * 60)

# 准备: 清测试数据
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM system_dicts;\""
], capture_output=True, text=True, timeout=10)

# admin 登录
T = requests.post(f'{API}/auth/login', json={'username': 'admin1', 'password': 'admin123'}).json()['data']['token']
H = {'Authorization': f'Bearer {T}'}

# ============= 块B: 数据字典 =============
print('\n[1] /dict/kinds (分类列表)')
r = requests.get(f'{API}/dict/kinds', headers=H, timeout=10)
d = r.json()
check('B1-1 kinds 200', r.status_code == 200)
check('B1-1 code=0', d.get('code') == 0)
kinds = d.get('data', {})
check('B1-1 至少 7 类', len(kinds) >= 7, f'got: {len(kinds)}')
for required in ['repair_method', 'customer_source', 'device_type', 'region', 'fault_type', 'urgency', 'payment_method', 'product_unit']:
    check(f'B1-1 kind {required}', required in kinds, f'missing')

# ============= 块B: seed defaults =============
print('\n[2] /dict/seed-defaults (一键导入)')
r = requests.post(f'{API}/dict/seed-defaults', headers=H, json={}, timeout=10)
d = r.json()
check('B2-1 seed 200', r.status_code == 200)
check('B2-1 code=0', d.get('code') == 0)
res = d.get('data', {})
check('B2-1 created >= 30', res.get('created', 0) >= 30, f'got: {res.get("created")}')

# 重复调用应 idempotent
r2 = requests.post(f'{API}/dict/seed-defaults', headers=H, json={}, timeout=10)
d2 = r2.json()
check('B2-1 重复 seed idempotent (created=0)', d2.get('data', {}).get('created', -1) == 0, f'got: {d2.get("data", {}).get("created")}')

# ============= 块B: grouped =============
print('\n[3] /dict/grouped (分组)')
r = requests.get(f'{API}/dict/grouped', headers=H, timeout=10)
d = r.json()
check('B3-1 grouped 200', r.status_code == 200)
groups = d.get('data', [])
check('B3-1 至少 8 组', len(groups) >= 8, f'got: {len(groups)}')
# 找 repair_method 组
rm_group = next((g for g in groups if g['kind'] == 'repair_method'), None)
check('B3-1 找到 repair_method 组', rm_group is not None)
if rm_group:
    check('B3-1 repair_method 5 项 (default)', rm_group['count'] == 5, f'got: {rm_group["count"]}')

# ============= 块B: index 按 kind 过滤 =============
print('\n[4] /dict?kind=repair_method')
r = requests.get(f'{API}/dict', params={'kind': 'repair_method'}, headers=H, timeout=10)
d = r.json()
arr = d.get('data', [])
check('B4-1 仅 repair_method', all(x['kind'] == 'repair_method' for x in arr))
check('B4-1 5 项', len(arr) == 5)
codes = [x['code'] for x in arr]
for c in ['free_warranty', 'free_contract', 'paid_repair', 'paid_replace', 'returned']:
    check(f'B4-1 含 {c}', c in codes)

# ============= 块B: store (新建) =============
print('\n[5] /dict POST (新建)')
r = requests.post(f'{API}/dict', headers=H, json={
    'kind': 'repair_method',
    'code': 'v057bc_test1',
    'label': '测试1',
    'color': 'info',
    'sort_order': 100,
}, timeout=10)
d = r.json()
check('B5-1 store 200', r.status_code == 200)
check('B5-1 code=0', d.get('code') == 0)
new_id = d.get('data', {}).get('id')
check('B5-1 返回 id', new_id is not None)

# 重复 code 应失败
r2 = requests.post(f'{API}/dict', headers=H, json={
    'kind': 'repair_method', 'code': 'v057bc_test1', 'label': '重复',
}, timeout=10)
check('B5-1 重复 code 422', r2.status_code == 422, f'code={r2.status_code}')

# ============= 块B: PATCH =============
print('\n[6] /dict/{id} PATCH (改)')
r = requests.patch(f'{API}/dict/{new_id}', headers=H, json={
    'label': '测试1改',
    'sort_order': 200,
}, timeout=10)
d = r.json()
check('B6-1 patch 200', r.status_code == 200)
check('B6-1 label 已改', d.get('data', {}).get('label') == '测试1改')
check('B6-1 sort_order 已改', d.get('data', {}).get('sort_order') == 200)

# ============= 块B: DELETE (软) =============
print('\n[7] /dict/{id} DELETE (软删)')
r = requests.delete(f'{API}/dict/{new_id}', headers=H, timeout=10)
d = r.json()
check('B7-1 delete 200', r.status_code == 200)
# 验证 is_active=false (用 is_active=false 过滤, 因为 is_active=true 默认不过滤 软删)
r2 = requests.get(f'{API}/dict', params={'kind': 'repair_method', 'is_active': 'false'}, headers=H, timeout=10)
items = r2.json().get('data', [])
test1 = next((x for x in items if x['code'] == 'v057bc_test1'), None)
check('B7-1 is_active=false', test1 and test1.get('is_active') is False, f'got: {test1}')

# ============= 块B: reorder =============
print('\n[8] /dict/reorder (批量改 sort_order)')
# 先拿到 repair_method 的 id
r = requests.get(f'{API}/dict', params={'kind': 'repair_method'}, headers=H, timeout=10)
items = r.json().get('data', [])
if len(items) >= 2:
    items_to_reorder = [
        {'id': items[0]['id'], 'sort_order': 999},
        {'id': items[1]['id'], 'sort_order': 888},
    ]
    r2 = requests.post(f'{API}/dict/reorder', headers=H, json={'items': items_to_reorder}, timeout=10)
    d2 = r2.json()
    check('B8-1 reorder 200', r2.status_code == 200)
    check('B8-1 updated=2', d2.get('data', {}).get('updated') == 2)

# ============= 块C: monitor 总览 =============
print('\n[9] /admin/monitor/metrics (总览)')
r = requests.get(f'{API}/admin/monitor/metrics', headers=H, timeout=10)
d = r.json()
check('C1-1 metrics 200', r.status_code == 200)
check('C1-1 code=0', d.get('code') == 0)
data = d.get('data', {})
check('C1-1 包含 disk', 'disk' in data)
check('C1-1 包含 db', 'db' in data)
check('C1-1 包含 services', 'services' in data)
check('C1-1 包含 errors', 'errors' in data)
check('C1-1 包含 backups', 'backups' in data)
check('C1-1 包含 timestamp', 'timestamp' in data)
# disk 字段
disk = data.get('disk', {})
check('C1-1 disk.mounts 是数组', isinstance(disk.get('mounts'), list))
check('C1-1 disk.mounts >= 1', len(disk.get('mounts', [])) >= 1)
# db 字段
db = data.get('db', {})
check('C1-1 db.active_connections 数字', isinstance(db.get('active_connections'), int))
check('C1-1 db.cache_hit_rate 数字', isinstance(db.get('cache_hit_rate'), (int, float)))
# services 字段
svcs = data.get('services', {})
check('C1-1 services.php_fpm_workers 数字', isinstance(svcs.get('php_fpm_workers'), int))
check('C1-1 services.php_version 含 .', '.' in str(svcs.get('php_version', '')))
# errors 字段
errs = data.get('errors', {})
check('C1-1 errors.total_24h 数字', isinstance(errs.get('total_24h'), int))
# backups 字段
bk = data.get('backups', {})
check('C1-1 backups.count 数字', isinstance(bk.get('count'), int))

# ============= 块C: 5 个分端点 =============
print('\n[10] /admin/monitor/{disk,db,services,errors,backups}')
for sub in ['disk', 'db', 'services', 'errors', 'backups']:
    r = requests.get(f'{API}/admin/monitor/{sub}', headers=H, timeout=10)
    check(f'C2-1 /admin/monitor/{sub} 200', r.status_code == 200)
    d = r.json()
    check(f'C2-1 {sub} code=0', d.get('code') == 0)

# ============= 块C: 鉴权 =============
print('\n[11] 鉴权')
r = requests.get(f'{API}/admin/monitor/metrics', timeout=10)
check('C3-1 无 token 401', r.status_code == 401)
r = requests.get(f'{API}/dict/kinds', timeout=10)
check('C3-2 dict 无 token 401', r.status_code == 401)

# ============= 块C: 路由 =============
print('\n[12] 路由注册')
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "cd /var/www/oa-api && php artisan route:list --path=admin/monitor 2>&1"
], capture_output=True, text=True, timeout=15)
for p in ['api/admin/monitor/metrics', 'api/admin/monitor/disk', 'api/admin/monitor/db',
          'api/admin/monitor/services', 'api/admin/monitor/errors', 'api/admin/monitor/backups']:
    check(f'C4 路由 {p}', p in out.stdout)

# ============= 清理 =============
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM system_dicts WHERE code LIKE 'v057bc_%';\""
], capture_output=True, text=True, timeout=10)
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -1"
], capture_output=True, text=True, timeout=10)

print('\n' + '=' * 60)
print(f'通过 {passed} / 失败 {failed}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
