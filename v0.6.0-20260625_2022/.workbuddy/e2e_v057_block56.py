#!/usr/bin/env python3
"""V0.5.7 块5+6 — Dashboard 4 widget + PWA e2e"""
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
print('V0.5.7 块5+6 — Dashboard widget + PWA e2e')
print('=' * 60)

# 准备: 强插 3 个 closed 返修单 + 不同 method/fault/工程师, 让所有 widget 有数据
print('\n[0] 准备测试数据')
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM repair_orders WHERE code LIKE 'RN2026-W%';\""
], capture_output=True, text=True, timeout=10)

# 拿真实 user_id (admin1 = 74)
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -t -c \"SELECT id FROM users WHERE id IN (74, 80, 82, 86) ORDER BY id;\""
], capture_output=True, text=True, timeout=10)
user_ids = [int(x.strip()) for x in out.stdout.split('\n') if x.strip() and x.strip().isdigit()]
print(f'  [准备] users = {user_ids}')

# 强插 3 单 (不同 method/fault/received_by)
insert_sql = f"""
INSERT INTO repair_orders (code, source_type, customer_id, contact_name, contact_phone, equipment_brand, equipment_model, fault_type, fault_description, status, parts_cost, labor_cost, shipping_cost, total_cost, is_warranty, method_type, received_by, received_at, updated_at) VALUES
('RN2026-W001', 'customer', 1, '客户W1', '13700000001', '品牌A', 'M-W1', 'power', 'W1电源故障', 'closed', 100, 50, 50, 200, false, 'paid_repair', {user_ids[0] if user_ids else 74}, NOW() - INTERVAL '10 days', NOW() - INTERVAL '5 days'),
('RN2026-W002', 'customer', 1, '客户W2', '13700000002', '品牌B', 'M-W2', 'network', 'W2网络故障', 'closed', 200, 100, 50, 350, true, 'free_warranty', {user_ids[1] if len(user_ids) > 1 else (user_ids[0] if user_ids else 74)}, NOW() - INTERVAL '15 days', NOW() - INTERVAL '8 days'),
('RN2026-W003', 'customer', 1, '客户W3', '13700000003', '品牌C', 'M-W3', 'image', 'W3图像问题', 'closed', 500, 200, 100, 800, false, 'paid_replace', {user_ids[0] if user_ids else 74}, NOW() - INTERVAL '20 days', NOW() - INTERVAL '12 days');
"""
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    f"PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"{insert_sql}\""
], capture_output=True, text=True, timeout=10)

out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -t -c \"SELECT count(*) FROM repair_orders WHERE code LIKE 'RN2026-W%';\""
], capture_output=True, text=True, timeout=10)
cnt = int(out.stdout.strip() or '0')
print(f'  [准备] 已插入 W 测试单 {cnt} 单')
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -1"
], capture_output=True, text=True, timeout=10)

# admin 登录
T = requests.post(f'{API}/auth/login', json={'username': 'admin1', 'password': 'admin123'}).json()['data']['token']
H = {'Authorization': f'Bearer {T}'}

# ============= 块5: 5 widget 端点 =============
print('\n[1] /dashboard/widget/method-distribution')
r = requests.get(f'{API}/dashboard/widget/method-distribution', headers=H, timeout=10)
d = r.json()
check('B5-1 method 200', r.status_code == 200)
check('B5-1 code=0', d.get('code') == 0)
data = d.get('data', {})
check('B5-1 至少 2 种方式', len(data) >= 2, f'got: {data}')
check('B5-1 含 paid_repair', 'paid_repair' in data)
check('B5-1 含 free_warranty', 'free_warranty' in data)
check('B5-1 含 paid_replace', 'paid_replace' in data)

# ============= 块5: cycle-percentile =============
print('\n[2] /dashboard/widget/cycle-percentile')
r = requests.get(f'{API}/dashboard/widget/cycle-percentile', headers=H, timeout=10)
d = r.json()
check('B5-2 cycle 200', r.status_code == 200)
data = d.get('data', {})
check('B5-2 包含 sample_count', 'sample_count' in data)
check('B5-2 包含 p50_days', 'p50_days' in data)
check('B5-2 包含 p90_days', 'p90_days' in data)
check('B5-2 包含 max_days', 'max_days' in data)
check('B5-2 包含 available', 'available' in data)
check('B5-2 sample_count >= 3', data.get('sample_count', 0) >= 3, f'got: {data.get("sample_count")}')
check('B5-2 available=true', data.get('available') is True)
check('B5-2 p50 > 0', data.get('p50_days', 0) > 0, f'got: {data.get("p50_days")}')
check('B5-2 p90 >= p50', data.get('p90_days', 0) >= data.get('p50_days', 0), f'p50={data.get("p50_days")} p90={data.get("p90_days")}')

# ============= 块5: fault-top =============
print('\n[3] /dashboard/widget/fault-top')
r = requests.get(f'{API}/dashboard/widget/fault-top', headers=H, timeout=10)
d = r.json()
check('B5-3 fault 200', r.status_code == 200)
arr = d.get('data', [])
check('B5-3 数组非空', len(arr) > 0, f'got: {len(arr)}')
if arr:
    row = arr[0]
    check('B5-3 行有 code', 'code' in row)
    check('B5-3 行有 label', 'label' in row)
    check('B5-3 行有 count', 'count' in row)
    check('B5-3 行有 percentage', 'percentage' in row)
    # 验证是 power/network/image 之一
    check(f'B5-3 首项 code 是测试之一', row['code'] in ['power', 'network', 'image'])

# ============= 块5: technician-rank =============
print('\n[4] /dashboard/widget/technician-rank')
r = requests.get(f'{API}/dashboard/widget/technician-rank', headers=H, timeout=10)
d = r.json()
check('B5-4 tech 200', r.status_code == 200)
arr = d.get('data', [])
check('B5-4 数组非空', len(arr) > 0, f'got: {len(arr)}')
if arr:
    row = arr[0]
    check('B5-4 行有 user_id', 'user_id' in row)
    check('B5-4 行有 name', 'name' in row)
    check('B5-4 行有 completed_count', 'completed_count' in row)
    check('B5-4 行有 avg_days', 'avg_days' in row)
    check('B5-4 行有 total_revenue', 'total_revenue' in row)
    check(f'B5-4 name 非空', isinstance(row.get('name'), str) and row['name'])

# ============= 块5: all =============
print('\n[5] /dashboard/widget/all (一锅端)')
r = requests.get(f'{API}/dashboard/widget/all', headers=H, timeout=10)
d = r.json()
check('B5-5 all 200', r.status_code == 200)
data = d.get('data', {})
check('B5-5 4 段都在', all(k in data for k in ['method_distribution', 'cycle_percentile', 'fault_top', 'technician_ranking']))
check('B5-5 updated_at 字段', 'updated_at' in data)

# ============= 块5: 鉴权 =============
print('\n[6] 鉴权')
r = requests.get(f'{API}/dashboard/widget/all', timeout=10)
check('B5-6 无 token 401', r.status_code == 401)

# ============= 块5: 路由 =============
print('\n[7] 路由注册')
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "cd /var/www/oa-api && php artisan route:list --path=dashboard/widget 2>&1"
], capture_output=True, text=True, timeout=15)
for p in ['api/dashboard/widget/method-distribution', 'api/dashboard/widget/cycle-percentile',
          'api/dashboard/widget/fault-top', 'api/dashboard/widget/technician-rank',
          'api/dashboard/widget/all']:
    check(f'B5-7 路由 {p}', p in out.stdout)

# ============= 块6: PWA 静态资源 =============
print('\n[8] PWA 静态资源')
r = requests.get('http://192.168.3.117/manifest.json', timeout=10)
check('B6-1 manifest 200', r.status_code == 200)
check('B6-1 manifest 包含 name', '"name"' in r.text)
check('B6-1 manifest 包含 start_url', '"start_url"' in r.text)
check('B6-1 manifest 包含 display', '"display"' in r.text)
check('B6-1 manifest 包含 icons', '"icons"' in r.text)
check('B6-1 manifest 包含 theme_color', '"theme_color"' in r.text)
# 验证是 JSON
try:
    m = r.json()
    check('B6-1 manifest 是合法 JSON', True)
except: check('B6-1 manifest 是合法 JSON', False, '')

r = requests.get('http://192.168.3.117/sw.js', timeout=10)
check('B6-2 sw.js 200', r.status_code == 200)
check('B6-2 sw.js 包含 CACHE_VERSION', 'CACHE_VERSION' in r.text)
check('B6-2 sw.js 包含 install', "'install'" in r.text)
check('B6-2 sw.js 包含 fetch', "'fetch'" in r.text)
check('B6-2 sw.js 包含 activate', "'activate'" in r.text)
# 是 JS content-type
check('B6-2 sw.js content-type 是 js', 'javascript' in r.headers.get('content-type', ''))

r = requests.get('http://192.168.3.117/offline.html', timeout=10)
check('B6-3 offline.html 200', r.status_code == 200)
check('B6-3 offline.html 含 您已离线', '您已离线'.encode('utf-8') in r.content)

r = requests.get('http://192.168.3.117/icons/icon-192.png', timeout=10)
check('B6-4 icon-192.png 200', r.status_code == 200)
check('B6-4 icon-192.png 是图片', 'image' in r.headers.get('content-type', ''))

r = requests.get('http://192.168.3.117/icons/icon-512.png', timeout=10)
check('B6-5 icon-512.png 200', r.status_code == 200)

# ============= 块6: index.html 集成 =============
print('\n[9] index.html PWA 集成')
r = requests.get('http://192.168.3.117/', timeout=10)
check('B6-6 index.html 200', r.status_code == 200)
check('B6-6 包含 manifest link', '/manifest.json' in r.text)
check('B6-6 包含 apple-touch-icon', 'apple-touch-icon' in r.text)
check('B6-6 包含 theme-color meta', 'theme-color' in r.text)
check('B6-6 包含 apple-mobile-web-app', 'apple-mobile-web-app-capable' in r.text)

# ============= 清理 =============
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM repair_orders WHERE code LIKE 'RN2026-W%';\""
], capture_output=True, text=True, timeout=10)
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -1"
], capture_output=True, text=True, timeout=10)

print('\n' + '=' * 60)
print(f'通过 {passed} / 失败 {failed}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
