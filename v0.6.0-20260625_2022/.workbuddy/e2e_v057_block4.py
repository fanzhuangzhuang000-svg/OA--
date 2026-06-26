#!/usr/bin/env python3
"""V0.5.7 块4 — 维修成本归集 e2e (4 维度 + dashboard 卡片)"""
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
print('V0.5.7 块4 — 维修成本归集 e2e')
print('=' * 60)

# ============= 准备测试数据 (直接 SQL 强插 3 单) =============
print('\n[0] 准备测试数据 (SQL 强插)')

# 清旧测试返修单
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM repair_orders WHERE code LIKE 'RN2026-B4%';\""
], capture_output=True, text=True, timeout=10)

# 强插 3 单 + 标 closed (用真实存在的 customer_id/project_id)
# 先查出有效 ID
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -t -c \"SELECT id FROM customers ORDER BY id LIMIT 5; SELECT id FROM projects ORDER BY id LIMIT 5;\""
], capture_output=True, text=True, timeout=10)
ids = [int(x.strip()) for x in out.stdout.split('\n') if x.strip() and x.strip().isdigit()]
print(f'  [准备] customers ids={ids[:5]}, projects ids={ids[5:10]}')
c1, c2 = ids[0], ids[1] if len(ids) > 1 else ids[0]
p1, p2 = ids[5], ids[6] if len(ids) > 6 else ids[5]

# 强插 3 单
insert_sql = f"""
INSERT INTO repair_orders (code, source_type, customer_id, project_id, contact_name, contact_phone, equipment_brand, equipment_model, fault_description, status, parts_cost, labor_cost, shipping_cost, total_cost, is_warranty, method_type, received_at, created_at, updated_at) VALUES
('RN2026-B4001', 'customer', {c1}, {p1}, '客户甲', '13800000001', '品牌A', 'M-100', 'B4测试1', 'closed', 200, 200, 100, 500, false, 'paid_repair', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '1 days'),
('RN2026-B4002', 'customer', {c2}, {p1}, '客户乙', '13800000002', '品牌B', 'M-200', 'B4测试2', 'closed', 100, 50, 50, 200, true, 'free_warranty', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '1 days'),
('RN2026-B4003', 'customer', {c1}, {p2}, '客户甲', '13800000001', '品牌C', 'M-300', 'B4测试3', 'closed', 1000, 300, 200, 1500, false, 'paid_replace', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', NOW() - INTERVAL '1 days');
"""
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    f"PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"{insert_sql}\""
], capture_output=True, text=True, timeout=10)

out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -t -c \"SELECT count(*) FROM repair_orders WHERE code LIKE 'RN2026-B4%';\""
], capture_output=True, text=True, timeout=10)
cnt = int(out.stdout.strip() or '0')
print(f'  [准备] 已插入 B4 测试单 {cnt} 单 (期望 3)')
if cnt != 3:
    print('  ✗ 测试数据准备失败, 退出')
    sys.exit(1)

# 清 dashboard cache
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -1"
], capture_output=True, text=True, timeout=10)

# admin 登录
T = requests.post(f'{API}/auth/login', json={'username': 'admin1', 'password': 'admin123'}).json()['data']['token']
H = {'Authorization': f'Bearer {T}'}

# ============= 1. overview 端点 =============
print('\n[1] /repair-cost/overview (概览 KPI)')
r = requests.get(f'{API}/repair-cost/overview', headers=H, timeout=10)
d = r.json()
check('B4-1 overview 200', r.status_code == 200)
check('B4-1 code=0', d.get('code') == 0)
data = d.get('data', {})
check('B4-1 包含 completed_orders', 'completed_orders' in data)
check('B4-1 包含 total_cost', 'total_cost' in data)
check('B4-1 包含 warranty_cost', 'warranty_cost' in data)
check('B4-1 包含 paid_cost', 'paid_cost' in data)
check('B4-1 包含 total_hours', 'total_hours' in data)
# B4 数据 至少 3 单
check('B4-1 completed_orders >= 3', data.get('completed_orders', 0) >= 3, f'got: {data.get("completed_orders")}')
# B4-001+002+003 总成本 = 500+200+1500 = 2200
check('B4-1 total_cost >= 2200', data.get('total_cost', 0) >= 2200, f'got: {data.get("total_cost")}')

# ============= 2. by-month 端点 =============
print('\n[2] /repair-cost/by-month (月度)')
r = requests.get(f'{API}/repair-cost/by-month?months=6', headers=H, timeout=10)
d = r.json()
check('B4-2 by-month 200', r.status_code == 200)
check('B4-2 code=0', d.get('code') == 0)
arr = d.get('data', [])
check('B4-2 数组非空', len(arr) > 0, f'got {len(arr)} rows')
if arr:
    row = arr[0]
    check('B4-2 行有 month', 'month' in row)
    check('B4-2 行有 total_cost', 'total_cost' in row)
    check('B4-2 行有 orders_count', 'orders_count' in row)

# 时间区间过滤
r2 = requests.get(f'{API}/repair-cost/by-month?months=12&from=2020-01-01&to=2020-12-31', headers=H, timeout=10)
check('B4-2 时间过滤 200', r2.status_code == 200)
arr2 = r2.json().get('data', [])
check('B4-2 2020 范围应空', len(arr2) == 0, f'got {len(arr2)} rows')

# ============= 3. by-project 端点 =============
print('\n[3] /repair-cost/by-project (项目)')
r = requests.get(f'{API}/repair-cost/by-project', headers=H, timeout=10)
d = r.json()
check('B4-3 by-project 200', r.status_code == 200)
arr = d.get('data', [])
check('B4-3 数组非空', len(arr) > 0, f'got {len(arr)} rows')
# 找 P1 (500+200=700) 和 P2 (1500)
p1_row = next((x for x in arr if x.get('project_id') == p1), None)
p2_row = next((x for x in arr if x.get('project_id') == p2), None)
check(f'B4-3 找到 project_id={p1}', p1_row is not None)
check(f'B4-3 找到 project_id={p2}', p2_row is not None)
if p1_row:
    check(f'B4-3 P1 总额 = 700', p1_row['total_cost'] == 700, f'got: {p1_row["total_cost"]}')
if p2_row:
    check(f'B4-3 P2 总额 = 1500', p2_row['total_cost'] == 1500, f'got: {p2_row["total_cost"]}')

# ============= 4. by-customer 端点 =============
print('\n[4] /repair-cost/by-customer (客户)')
r = requests.get(f'{API}/repair-cost/by-customer', headers=H, timeout=10)
d = r.json()
check('B4-4 by-customer 200', r.status_code == 200)
arr = d.get('data', [])
check('B4-4 数组非空', len(arr) > 0, f'got {len(arr)} rows')
# C1 (500+1500=2000), 付费=2000, 免费=0
c1_row = next((x for x in arr if x.get('customer_id') == c1), None)
c2_row = next((x for x in arr if x.get('customer_id') == c2), None)
check(f'B4-4 找到 customer_id={c1}', c1_row is not None)
check(f'B4-4 找到 customer_id={c2}', c2_row is not None)
if c1_row:
    check(f'B4-4 C1 总额 = 2000', c1_row['total_cost'] == 2000, f'got: {c1_row["total_cost"]}')
    check(f'B4-4 C1 paid = 2000', c1_row['paid_cost'] == 2000)
    check(f'B4-4 C1 warranty = 0', c1_row['warranty_cost'] == 0)
if c2_row:
    check(f'B4-4 C2 paid = 0', c2_row['paid_cost'] == 0)
    check(f'B4-4 C2 warranty = 200', c2_row['warranty_cost'] == 200, f'got: {c2_row["warranty_cost"]}')

# ============= 5. by-method 端点 =============
print('\n[5] /repair-cost/by-method (维修方式)')
r = requests.get(f'{API}/repair-cost/by-method', headers=H, timeout=10)
d = r.json()
check('B4-5 by-method 200', r.status_code == 200)
arr = d.get('data', [])
check('B4-5 数组非空', len(arr) > 0, f'got {len(arr)} rows')
methods = {x['method_type']: x for x in arr}
check('B4-5 包含 paid_repair', 'paid_repair' in methods)
check('B4-5 包含 free_warranty', 'free_warranty' in methods)
check('B4-5 包含 paid_replace', 'paid_replace' in methods)
# 占比字段
for row in arr:
    check(f'B4-5 {row["method_type"]} 有 percentage', 'percentage' in row)
    check(f'B4-5 {row["method_type"]} percentage 0-100', 0 <= row.get('percentage', -1) <= 100)

# ============= 6. dashboard widget 集成 =============
print('\n[6] /dashboard/maintenance-stats (成本卡片)')
r = requests.get(f'{API}/dashboard/maintenance-stats', headers=H, timeout=10)
d = r.json()
check('B4-6 maintenance-stats 200', r.status_code == 200)
cost = d.get('data', {}).get('cost', {})
check('B4-6 cost.this_month_total 字段存在', 'this_month_total' in cost)
check('B4-6 cost.this_month_warranty 字段存在', 'this_month_warranty' in cost)
check('B4-6 cost.this_month_paid 字段存在', 'this_month_paid' in cost)
check('B4-6 cost.total_contract 字段存在', 'total_contract' in cost)
check('B4-6 cost.cost_ratio_pct 字段存在', 'cost_ratio_pct' in cost)
check('B4-6 旧字段 monthly 仍存在', 'monthly' in cost)

# ============= 7. 公开端点不能访问 =============
print('\n[7] 公开端点鉴权')
r = requests.get(f'{API}/repair-cost/overview', timeout=10)
check('B4-7 无 token 返 401', r.status_code == 401, f'code={r.status_code}')
r = requests.get(f'{API}/repair-cost/by-month', timeout=10)
check('B4-7 by-month 无 token 返 401', r.status_code == 401)
r = requests.get(f'{API}/repair-cost/by-project', timeout=10)
check('B4-7 by-project 无 token 返 401', r.status_code == 401)

# ============= 8. 路由注册检查 =============
print('\n[8] 路由完整性')
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "cd /var/www/oa-api && php artisan route:list --path=repair-cost 2>&1"
], capture_output=True, text=True, timeout=15)
expected_routes = [
    'api/repair-cost/overview',
    'api/repair-cost/by-month',
    'api/repair-cost/by-project',
    'api/repair-cost/by-customer',
    'api/repair-cost/by-method',
]
for p in expected_routes:
    check(f'B4-8 路由 {p} 已注册', p in out.stdout, f'in routes output')

# ============= 清理 =============
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM repair_orders WHERE code LIKE 'RN2026-B4%';\""
], capture_output=True, text=True, timeout=10)
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -1"
], capture_output=True, text=True, timeout=10)

print('\n' + '=' * 60)
print(f'通过 {passed} / 失败 {failed}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
