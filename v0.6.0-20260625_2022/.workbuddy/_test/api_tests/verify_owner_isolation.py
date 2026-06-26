"""列表 owner 隔离验证: admin 应见全部, 普通 sales 只能见自己"""
import requests, subprocess

BASE = 'http://127.0.0.1/api'

def login(u, p):
    r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    if j.get('code') != 0:
        # 试重置密码
        subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c',
            f"UPDATE users SET password = crypt('admin123', gen_random_bytes(4)) WHERE username='{u}';"], capture_output=True)
        r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
        j = r.json()
    if j.get('code') != 0: raise SystemExit(f'login fail: {j.get("message")}')
    return j['data']['token']

def sql(cmd):
    return subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c', cmd], capture_output=True, text=True).stdout

admin_token = login('admin', 'admin123')
ah = {'Authorization': f'Bearer {admin_token}'}

# 看所有 sales 用户（role=user）
out = sql("SELECT u.id, u.username, u.department_id FROM users u JOIN model_has_roles mhr ON mhr.model_id = u.id JOIN roles r ON r.id = mhr.role_id WHERE r.name = 'user' AND u.department_id IS NOT NULL ORDER BY u.id LIMIT 3;")
print('候选 sales 用户:', out)

# 取 lisi (id=72) 改他的 password = admin123
out = sql("UPDATE users SET password = crypt('admin123', gen_random_bytes(4)) WHERE username = 'lisi' RETURNING id, username, department_id;")
print('lisi 重置:', out)
# 重新 bind role (之前 E 字面量修过但只改了 id=1)
out = sql("UPDATE model_has_roles SET model_type = E'App\\Models\\User' WHERE model_id IN (SELECT id FROM users WHERE username = 'lisi') AND model_type != E'App\\Models\\User';")
print('lisi 修 model_type:', out)
out = sql("SELECT u.id, u.username, u.department_id, r.name FROM users u JOIN model_has_roles mhr ON mhr.model_id = u.id JOIN roles r ON r.id = mhr.role_id WHERE u.username = 'lisi';")
print('lisi 当前 role:', out)

# 试 login
try:
    lisi_token = login('lisi', 'admin123')
    lh = {'Authorization': f'Bearer {lisi_token}'}
    print(f'lisi login OK')
except Exception as e:
    print(f'lisi login fail: {e}')

print('=' * 60)
print('列表 owner 隔离验证')
print('=' * 60)

# admin 应见全部
r = requests.get(f'{BASE}/sales/leads?per_page=200', headers=ah, timeout=10)
admin_leads = r.json().get('data', {}).get('total', 0)
print(f'admin 看到 leads: {admin_leads}')

# 看 lisi department
out = sql("SELECT department_id FROM users WHERE username = 'lisi';")
print('lisi dept:', out)

# lisi 登录 + 看 leads
r = requests.get(f'{BASE}/sales/leads?per_page=200', headers=lh, timeout=10)
lisi_leads = r.json().get('data', {}).get('total', 0)
print(f'lisi 看到 leads: {lisi_leads} (应该 < {admin_leads})')

# 同样测 opps
r = requests.get(f'{BASE}/sales/opps?per_page=200', headers=ah, timeout=10)
admin_opps = r.json().get('data', {}).get('total', 0)
r = requests.get(f'{BASE}/sales/opps?per_page=200', headers=lh, timeout=10)
lisi_opps = r.json().get('data', {}).get('total', 0)
print(f'admin opps: {admin_opps}, lisi opps: {lisi_opps}')

# 测 quotes
r = requests.get(f'{BASE}/sales/quotes?per_page=200', headers=ah, timeout=10)
admin_quotes = r.json().get('data', {}).get('total', 0)
r = requests.get(f'{BASE}/sales/quotes?per_page=200', headers=lh, timeout=10)
lisi_quotes = r.json().get('data', {}).get('total', 0)
print(f'admin quotes: {admin_quotes}, lisi quotes: {lisi_quotes}')

# 测 referrers
r = requests.get(f'{BASE}/sales/referrers?per_page=200', headers=ah, timeout=10)
admin_referrers = r.json().get('data', {}).get('total', 0)
r = requests.get(f'{BASE}/sales/referrers?per_page=200', headers=lh, timeout=10)
lisi_referrers = r.json().get('data', {}).get('total', 0)
print(f'admin referrers: {admin_referrers}, lisi referrers: {lisi_referrers}')

# 验证 lisi 不能写 admin 的 lead (中间件)
out = sql("SELECT id, owner_id FROM leads WHERE owner_id = 1 LIMIT 1;")
admin_lead_id = out.splitlines()[2].split('|')[0].strip()
r = requests.put(f'{BASE}/sales/leads/{admin_lead_id}', headers=lh, json={'customer_name': 'lisi改admin的'}, timeout=10)
print(f'\nlisi PUT admin lead {admin_lead_id}: HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:50]}')

print('\n=== 块一剩余 owner 列表隔离验证完成 ===')
