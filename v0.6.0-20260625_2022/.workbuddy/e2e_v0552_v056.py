#!/usr/bin/env python3
"""V0.5.5.2 + V0.5.6 — 综合 e2e 验证"""
import requests
import json
import sys
from typing import Tuple

API = 'http://192.168.3.117/api'
admin = {'username': 'admin1', 'password': 'admin123'}

def login(u):
    r = requests.post(f'{API}/auth/login', json=u, timeout=10)
    r.raise_for_status()
    d = r.json()['data']
    return d['token'], d['user']

def get(t, path, **kw):
    return requests.get(f'{API}{path}', headers={'Authorization': f'Bearer {t}'}, timeout=10, **kw)

def post(t, path, data=None, files=None):
    h = {'Authorization': f'Bearer {t}'}
    return requests.post(f'{API}{path}', json=data, headers=h, timeout=10) if not files else \
           requests.post(f'{API}{path}', data=data, files=files, headers=h, timeout=10)

passed = 0
failed = 0

def check(name, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  ✓ {name}')
    else:
        failed += 1
        print(f'  ✗ {name} {detail}')

print('=' * 60)
print('V0.5.5.2 + V0.5.6 综合 e2e')
print('=' * 60)

token, user = login(admin)
print(f'\n[登录] admin1 (id={user["id"]})')

# ============ A 组: V0.5.5.2 ============
print('\n=== A 组: V0.5.5.2 维修中心小修小补 ===')

# A1: dashboard maintenance-stats
r = get(token, '/dashboard/maintenance-stats')
d = r.json().get('data', {})
check('A1 GET /dashboard/maintenance-stats', r.status_code == 200 and 'work_orders' in d,
      f'code={r.status_code}')
check('A1 work_orders 子节点', 'work_orders' in d and 'conv_rate' in d.get('work_orders', {}))
check('A1 repair_orders 子节点', 'repair_orders' in d and 'avg_cycle_days' in d.get('repair_orders', {}))
check('A1 by_method 分布', 'by_method' in d and 'paid_repair' in d.get('by_method', {}))

# A2: 看板数据 (work-orders list)
r = get(token, '/work-orders', params={'per_page': 5})
check('A2 看板取工单', r.status_code == 200 and r.json().get('code') == 0)
r = get(token, '/repair-orders', params={'per_page': 5})
check('A2 看板取返修', r.status_code == 200 and r.json().get('code') == 0)

# A3: customer_signature 字段在 work_orders
r = get(token, '/work-orders', params={'per_page': 1})
data = r.json().get('data', {}).get('data', [])
# 看 schema (从 show 拿)
# 用 select 1 with column_name 查询
import subprocess
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"SELECT column_name FROM information_schema.columns WHERE table_name='work_orders' AND column_name LIKE 'customer_sign%';\""
], capture_output=True, text=True, timeout=10)
has_col = 'customer_signature' in out.stdout
check('A4 work_orders.customer_signature 字段存在', has_col, out.stdout[:100])

# A5: source_type 字段
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"SELECT column_name FROM information_schema.columns WHERE table_name='repair_orders' AND column_name='source_type';\""
], capture_output=True, text=True, timeout=10)
check('A5 repair_orders.source_type 字段存在', 'source_type' in out.stdout, out.stdout[:100])

# A6: attachment upload
# 先创建一个返修单 (清空残留)
import subprocess
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"INSERT INTO work_orders (code, status, created_by, contact_name, fault_description, created_at, updated_at) VALUES ('WO2026-T1', 'pending', 74, 'test', 'test', now(), now()) ON CONFLICT DO NOTHING RETURNING id;\""
], capture_output=True, text=True, timeout=10)

# 取工单 id
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -tA -c \"SELECT id FROM work_orders WHERE code='WO2026-T1' LIMIT 1;\""
], capture_output=True, text=True, timeout=10)
wo_id = out.stdout.strip()
check('A6 测试工单创建', wo_id.isdigit(), f'got: {wo_id}')

# 创建一个返修单
r = post(token, '/repair-orders', {
    'code': 'RN2026-T1',
    'customer_id': 1,
    'equipment_brand': 'test',
    'equipment_model': 'test',
    'fault_description': 'attachment test',
    'status': 'received',
    'source_type': 'customer',
})
if r.status_code == 200 and r.json().get('code') == 0:
    ro_id = r.json()['data']['id']
    check('A6 测试返修单创建', True)
elif r.status_code == 200 and 'RN2026-T1' in str(r.json()):
    # 已存在, 取 id
    out = subprocess.run([
        'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
        f"PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -tA -c \"SELECT id FROM repair_orders WHERE code='RN2026-T1' LIMIT 1;\""
    ], capture_output=True, text=True, timeout=10)
    ro_id = out.stdout.strip()
    check('A6 测试返修单已存在', ro_id.isdigit())

# 测 attachments list
r = get(token, f'/repair-orders/{ro_id}/attachments')
check('A6 GET attachments 列表', r.status_code == 200 and r.json().get('code') == 0)

# 测 upload (用 1x1 png)
import io
png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\x86\xa3i\x00\x00\x00\x00IEND\xaeB`\x82'
files = {'file': ('test.png', io.BytesIO(png_data), 'image/png')}
r = post(token, f'/repair-orders/{ro_id}/attachments', data={'category': 'shipping'}, files=files)
check('A6 POST 上传附件', r.status_code == 200 and r.json().get('code') == 0, r.text[:200])

# 测 list 看到附件
r = get(token, f'/repair-orders/{ro_id}/attachments')
arr = r.json().get('data', [])
check('A6 列表含新附件', len(arr) >= 1, f'count={len(arr)}')

# 测 delete
if arr:
    aid = arr[0]['id']
    r = requests.delete(f'{API}/repair-orders/{ro_id}/attachments/{aid}',
                        headers={'Authorization': f'Bearer {token}'}, timeout=10)
    check('A6 DELETE 附件', r.status_code == 200 and r.json().get('code') == 0)

# ============ B 组: V0.5.6 ============
print('\n=== B 组: V0.5.6 服务迁移 ===')

# B1: migrate command exists
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "cd /var/www/oa-api && sudo -u www-data php artisan list 2>&1 | grep -i migrate"
], capture_output=True, text=True, timeout=10)
check('B1 migrate:work-orders 命令存在', 'migrate:work-orders' in out.stdout, out.stdout[:200])

# B1 dry-run
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "cd /var/www/oa-api && sudo -u www-data php artisan migrate:work-orders --dry-run 2>&1"
], capture_output=True, text=True, timeout=30)
check('B1 dry-run 可执行', '找到' in out.stdout or 'DRY' in out.stdout, (out.stdout + out.stderr)[-200:])

# B2: service_orders 标记字段
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"SELECT column_name FROM information_schema.columns WHERE table_name='service_orders' AND column_name LIKE 'migrated%';\""
], capture_output=True, text=True, timeout=10)
has_mig = 'migrated_to_work_order_id' in out.stdout and 'migrated_at' in out.stdout
check('B2 service_orders 迁移字段', has_mig, out.stdout[:200])

# B3: /service/orders index 包含 migration_banner
r = get(token, '/service/orders', params={'per_page': 1})
d = r.json()
has_banner = 'meta' in d and 'migration_banner' in d.get('meta', {})
check('B3 service/orders 返回 migration_banner', has_banner, f'resp keys: {list(d.keys())}')
if has_banner:
    b = d['meta']['migration_banner']
    check('B3 banner 包含 target_url', b.get('target_url') == '/maintenance/work-orders')

# B4: 老 service orders 写入返回 410
r = post(token, '/service/orders', data={'customer_id': 1, 'fault_description': 'test'})
check('B4 POST /service/orders 返 410', r.status_code == 410, f'code={r.status_code} body={r.text[:100]}')
r = requests.post(f'{API}/service/orders/1/assign', json={'assigned_to': 1},
                  headers={'Authorization': f'Bearer {token}'}, timeout=10)
check('B4 POST /service/orders/{id}/assign 返 410', r.status_code == 410)

# B5: field-masks preview (用真实存在的脱敏 module)
r = post(token, '/field-masks/preview', {
    'endpoint': '/api/finance/payables',
    'test_data': [{'amount': 1000, 'vendor_name': '测试供应商', 'phone': '13800138000'}],
    'as_user_id': user['id'],
})
d = r.json()
check('B5 preview 端点', r.status_code == 200 and d.get('code') == 0, r.text[:200])
check('B5 返回 matched_module', 'matched_module' in d.get('data', {}), d.get('message', '')[:200])

# 总结
print('\n' + '=' * 60)
print(f'通过 {passed} / 失败 {failed}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
