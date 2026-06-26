#!/usr/bin/env python3
"""V0.5.7 块A — 系统初始化向导 e2e (5 步 + summary)"""
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
print('V0.5.7 块A — 系统初始化向导 e2e')
print('=' * 60)

# ============= 准备: 清掉 setup_completed 标记 (从干净状态测) =============
print('\n[0] 重置 setup_completed (从干净状态测)')
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM system_settings WHERE key IN ('setup_completed','setup_completed_at','setup_completed_by');\""
], capture_output=True, text=True, timeout=10)

# admin 登录
T = requests.post(f'{API}/auth/login', json={'username': 'admin1', 'password': 'admin123'}).json()['data']['token']
H = {'Authorization': f'Bearer {T}'}

# ============= 1. summary 端点 =============
print('\n[1] /setup/summary')
r = requests.get(f'{API}/setup/summary', headers=H, timeout=10)
d = r.json()
check('A1-1 summary 200', r.status_code == 200)
check('A1-1 code=0', d.get('code') == 0)
data = d.get('data', {})
check('A1-1 包含 setup_completed 字段', 'setup_completed' in data)
check('A1-1 包含 score 字段', 'score' in data)
check('A1-1 包含 settings', 'settings' in data)
check('A1-1 包含 counts', 'counts' in data)
check('A1-1 包含 suggestions', 'suggestions' in data)
check('A1-1 setup_completed 初始为 false', data.get('setup_completed') is False)
check('A1-1 score 0-100', 0 <= data.get('score', -1) <= 100)
# counts 应有 10 个
counts = data.get('counts', {})
check('A1-1 counts >= 10 项', len(counts) >= 10, f'got: {len(counts)}')
check('A1-1 counts.users 数字', isinstance(counts.get('users'), int))
check('A1-1 counts.users >= 1', counts.get('users', 0) >= 1)
check('A1-1 counts.projects >= 1', counts.get('projects', 0) >= 1)

# ============= 2. step1 基础设置 =============
print('\n[2] /setup/step1 (基础设置)')
r = requests.post(f'{API}/setup/step1', headers=H, json={
    'system_name': 'Test OA System',
    'system_short_name': 'TestOA',
    'copyright': '© 2026 Test',
    'icp': 'TestICP备0001',
    'contact_email': 'test@example.com',
}, timeout=10)
d = r.json()
check('A2-1 step1 200', r.status_code == 200, f'code={r.status_code} body={r.text[:200]}')
check('A2-1 code=0', d.get('code') == 0)
check('A2-1 message 含 保存', '保存' in d.get('message', ''))

# 验证 summary 反映
r2 = requests.get(f'{API}/setup/summary', headers=H, timeout=10)
s = r2.json()['data']['settings']
check('A2-1 system_name 已保存', s.get('system_name', {}).get('value') == 'Test OA System')
check('A2-1 system_short_name 已保存', s.get('system_short_name', {}).get('value') == 'TestOA')
check('A2-1 copyright 已保存', s.get('copyright', {}).get('value') == '© 2026 Test')
check('A2-1 icp 已保存', s.get('icp', {}).get('value') == 'TestICP备0001')
check('A2-1 contact_email 已保存', s.get('contact_email', {}).get('value') == 'test@example.com')

# 校验失败
r3 = requests.post(f'{API}/setup/step1', headers=H, json={
    'system_name': 'X', 'system_short_name': 'X', 'copyright': 'X',
    'contact_email': 'invalid-email',
}, timeout=10)
check('A2-1 邮箱无效 422', r3.status_code == 422, f'code={r3.status_code}')
r4 = requests.post(f'{API}/setup/step1', headers=H, json={
    'system_name': 'X',
}, timeout=10)
check('A2-1 缺字段 422', r4.status_code == 422, f'code={r4.status_code}')

# ============= 3. step3 批量员工 =============
print('\n[3] /setup/step3 (批量员工)')
# 准备清理 V0.5.7A 测试员工
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM users WHERE username LIKE 'v057a_%';\""
], capture_output=True, text=True, timeout=10)

r = requests.post(f'{API}/setup/step3', headers=H, json={
    'employees': [
        {'name': '测试A1', 'username': 'v057a_test1', 'phone': '13700000001', 'email': 'a1@test.com', 'password': 'Pass1234', 'role': 'user'},
        {'name': '测试A2', 'username': 'v057a_test2', 'phone': '13700000002', 'email': 'a2@test.com', 'password': 'Pass1234', 'role': 'sales'},
        {'name': '测试A3', 'username': 'v057a_test3', 'phone': '13700000003', 'email': 'a3@test.com', 'password': 'Pass1234', 'role': 'technician'},
    ]
}, timeout=10)
d = r.json()
check('A3-1 step3 200', r.status_code == 200, f'body={r.text[:300]}')
check('A3-1 code=0', d.get('code') == 0)
stats = d.get('data', {}).get('stats', {})
check('A3-1 created=3', stats.get('created') == 3, f'got: {stats.get("created")}')
check('A3-1 skipped=0', stats.get('skipped') == 0, f'got: {stats.get("skipped")}')

# 重复创建应跳过
r2 = requests.post(f'{API}/setup/step3', headers=H, json={
    'employees': [
        {'name': '重复', 'username': 'v057a_test1', 'password': 'Pass1234', 'role': 'user'},
    ]
}, timeout=10)
d2 = r2.json()
check('A3-1 重复创建 skipped>=1', d2.get('data', {}).get('stats', {}).get('skipped', 0) >= 1)
# 错误列表中应包含 reason
errs = d2.get('data', {}).get('stats', {}).get('errors', [])
check('A3-1 错误信息含 reason', any('reason' in e for e in errs))

# 验证 user 真创建
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -t -c \"SELECT count(*) FROM users WHERE username LIKE 'v057a_%';\""
], capture_output=True, text=True, timeout=10)
cnt = int(out.stdout.strip() or '0')
check('A3-1 DB 实际有 3 个 v057a 用户', cnt == 3, f'got: {cnt}')

# 空数组 422
r3 = requests.post(f'{API}/setup/step3', headers=H, json={'employees': []}, timeout=10)
check('A3-1 空数组 422', r3.status_code == 422)

# ============= 4. step4 CSV 导入 =============
print('\n[4] /setup/step4 (CSV 导入)')
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM users WHERE username LIKE 'v057a_csv%';\""
], capture_output=True, text=True, timeout=10)

csv_text = "name,username,phone,email,password,role,department_id,position_id\n"
csv_text += "CSV测试1,v057a_csv1,13700001001,csv1@test.com,Pass1234,user,,\n"
csv_text += "CSV测试2,v057a_csv2,13700001002,csv2@test.com,Pass1234,sales,,\n"
r = requests.post(f'{API}/setup/step4', headers=H, json={'csv_text': csv_text}, timeout=10)
d = r.json()
check('A4-1 step4 200', r.status_code == 200, f'body={r.text[:300]}')
check('A4-1 code=0', d.get('code') == 0)
check('A4-1 created=2', d.get('data', {}).get('stats', {}).get('created') == 2)

# 验证
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -t -c \"SELECT count(*) FROM users WHERE username LIKE 'v057a_csv%';\""
], capture_output=True, text=True, timeout=10)
cnt = int(out.stdout.strip() or '0')
check('A4-1 DB 实际有 2 个 v057a_csv 用户', cnt == 2, f'got: {cnt}')

# 空 CSV 422
r2 = requests.post(f'{API}/setup/step4', headers=H, json={'csv_text': ''}, timeout=10)
check('A4-1 空 CSV 422', r2.status_code == 422)

# ============= 5. complete 标记 =============
print('\n[5] /setup/complete (标记完成)')
r = requests.post(f'{API}/setup/complete', headers=H, json={}, timeout=10)
d = r.json()
check('A5-1 complete 200', r.status_code == 200, f'body={r.text[:200]}')
check('A5-1 code=0', d.get('code') == 0)
check('A5-1 message 含 🎉', '🎉' in d.get('message', ''))

# 验证 summary 反映
r2 = requests.get(f'{API}/setup/summary', headers=H, timeout=10)
d2 = r2.json()['data']
check('A5-1 setup_completed=true', d2.get('setup_completed') is True)
check('A5-1 setup_completed_at 非空', d2.get('setup_completed_at') is not None)

# ============= 6. sample-csv 模板下载 =============
print('\n[6] /setup/sample-csv')
r = requests.get(f'{API}/setup/sample-csv', headers=H, timeout=10)
check('A6-1 sample-csv 200', r.status_code == 200)
check('A6-1 content-type csv', 'csv' in r.headers.get('content-type', ''))
check('A6-1 含表头', 'name,username' in r.text)
check('A6-1 含示例数据', '张三' in r.text)

# ============= 7. 鉴权 =============
print('\n[7] 鉴权')
r = requests.get(f'{API}/setup/summary', timeout=10)
check('A7-1 无 token 401', r.status_code == 401, f'code={r.status_code}')

# ============= 8. 路由注册 =============
print('\n[8] 路由完整性')
out = subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "cd /var/www/oa-api && php artisan route:list --path=setup 2>&1"
], capture_output=True, text=True, timeout=15)
expected = [
    'api/setup/summary',
    'api/setup/step1',
    'api/setup/step3',
    'api/setup/step4',
    'api/setup/complete',
    'api/setup/sample-csv',
]
for p in expected:
    check(f'A8 路由 {p} 已注册', p in out.stdout, '')

# ============= 清理 =============
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c \"DELETE FROM users WHERE username LIKE 'v057a_%'; DELETE FROM system_settings WHERE key IN ('setup_completed','setup_completed_at','setup_completed_by');\""
], capture_output=True, text=True, timeout=10)
subprocess.run([
    'ssh', '-o', 'ConnectTimeout=5', 'nbcy@192.168.3.117',
    "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -1"
], capture_output=True, text=True, timeout=10)

print('\n' + '=' * 60)
print(f'通过 {passed} / 失败 {failed}')
print('=' * 60)
sys.exit(0 if failed == 0 else 1)
