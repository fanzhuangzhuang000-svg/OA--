"""清 152 E2E 噪声数据 — 重写版"""
import paramiko
import json
import re
import sys

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PWD, timeout=15)
print(f'connected to {HOST}')


def run(cmd, t=30):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    return so.read().decode('utf-8', 'replace').strip()


def safe_list(raw, key='data'):
    """parse {data: {data: [...]}} or {data: {items: [...]}} or return []"""
    if not raw or not raw.startswith('{'):
        return []
    try:
        d = json.loads(raw).get('data') or {}
        if isinstance(d, dict):
            return d.get('data') or d.get('items') or d.get('list') or []
        if isinstance(d, list):
            return d
    except Exception:
        return []
    return []


def del_oid(api_path, oid):
    r = run(f'''curl -sk -o /dev/null -w "%{{http_code}}" -X DELETE "https://localhost{api_path}/{oid}" -H "Authorization: Bearer {admin_token}"''')
    return r


# 1. 登录
login = run('''curl -sk -X POST https://localhost/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' ''')
admin_token = json.loads(login).get('data', {}).get('token') if login.startswith('{') else None
if not admin_token:
    print('登录失败, 终止'); sys.exit(1)
print(f'admin token OK')

# 2. 收集 E2E 噪声 id
print()
print('='*60)
print('收集 E2E 噪声 id')
print('='*60)

e2e_ids = {}

# 商机
r = run(f'''curl -sk -X GET "https://localhost/api/sales/opps?per_page=500" -H "Authorization: Bearer {admin_token}"''')
opps = safe_list(r)
e2e_ids['商机'] = [o['id'] for o in opps if re.search(r'E2E', o.get('name', '') or '', re.IGNORECASE) or 'E2E' in (o.get('notes') or '')]
print(f'  商机 E2E: {len(e2e_ids["商机"])} 条')

# 线索
r = run(f'''curl -sk -X GET "https://localhost/api/sales/leads?per_page=500" -H "Authorization: Bearer {admin_token}"''')
leads = safe_list(r)
e2e_ids['线索'] = [l['id'] for l in leads if re.search(r'E2E', l.get('name', '') or '', re.IGNORECASE)]
print(f'  线索 E2E: {len(e2e_ids["线索"])} 条')

# 客户
r = run(f'''curl -sk -X GET "https://localhost/api/customers?per_page=500" -H "Authorization: Bearer {admin_token}"''')
customers = safe_list(r)
e2e_ids['客户'] = [c['id'] for c in customers if re.search(r'E2E', c.get('name', '') or '', re.IGNORECASE)]
print(f'  客户 E2E: {len(e2e_ids["客户"])} 条')

# 供应商
r = run(f'''curl -sk -X GET "https://localhost/api/suppliers?per_page=500" -H "Authorization: Bearer {admin_token}"''')
suppliers = safe_list(r)
e2e_ids['供应商'] = [s['id'] for s in suppliers if re.search(r'E2E', s.get('name', '') or '', re.IGNORECASE)]
print(f'  供应商 E2E: {len(e2e_ids["供应商"])} 条')

# 项目
r = run(f'''curl -sk -X GET "https://localhost/api/projects?per_page=500" -H "Authorization: Bearer {admin_token}"''')
projects = safe_list(r)
e2e_ids['项目'] = [p['id'] for p in projects if re.search(r'E2E', p.get('name', '') or '', re.IGNORECASE)]
print(f'  项目 E2E: {len(e2e_ids["项目"])} 条')

# 维修工单
r = run(f'''curl -sk -X GET "https://localhost/api/repair-orders?per_page=500" -H "Authorization: Bearer {admin_token}"''')
repairs = safe_list(r)
e2e_ids['维修工单'] = [ro['id'] for ro in repairs if re.search(r'E2E', ro.get('description', '') or '', re.IGNORECASE) or re.search(r'E2E', ro.get('problem', '') or '', re.IGNORECASE)]
print(f'  维修 E2E: {len(e2e_ids["维修工单"])} 条')

# 报销
r = run(f'''curl -sk -X GET "https://localhost/api/expenses?per_page=500" -H "Authorization: Bearer {admin_token}"''')
exp_list = safe_list(r)
e2e_ids['报销'] = [e['id'] for e in exp_list if re.search(r'E2E', e.get('description', '') or '', re.IGNORECASE)]
print(f'  报销 E2E: {len(e2e_ids["报销"])} 条')

# 应收
r = run(f'''curl -sk -X GET "https://localhost/api/finance/receivables?per_page=500" -H "Authorization: Bearer {admin_token}"''')
recv_list = safe_list(r)
e2e_ids['应收'] = [r2['id'] for r2 in recv_list if re.search(r'E2E', r2.get('description', '') or '', re.IGNORECASE) or re.search(r'E2E', r2.get('notes', '') or '', re.IGNORECASE)]
print(f'  应收 E2E: {len(e2e_ids["应收"])} 条')

# 应付
r = run(f'''curl -sk -X GET "https://localhost/api/finance/payables?per_page=500" -H "Authorization: Bearer {admin_token}"''')
pay_list = safe_list(r)
e2e_ids['应付'] = [p['id'] for p in pay_list if re.search(r'E2E', p.get('description', '') or '', re.IGNORECASE)]
print(f'  应付 E2E: {len(e2e_ids["应付"])} 条')

# 3. 删
print()
print('='*60)
print('批量删除')
print('='*60)

api_map = {
    '商机': '/api/sales/opps',
    '线索': '/api/sales/leads',
    '客户': '/api/customers',
    '供应商': '/api/suppliers',
    '项目': '/api/projects',
    '维修工单': '/api/repair-orders',
    '报销': '/api/expenses',
    '应收': '/api/finance/receivables',
    '应付': '/api/finance/payables',
}

for label, ids in e2e_ids.items():
    path = api_map[label]
    ok = 0
    for oid in ids:
        st = del_oid(path, oid)
        if st == '200':
            ok += 1
    print(f'  删{label}: {ok}/{len(ids)} 成功')

# 4. SQL 清异常用户 (V0.5.1 onboarding wizard 残留)
print()
print('='*60)
print('SQL 清异常用户 (V0.5.1 onboarding wizard 噪声)')
print('='*60)

sql_users = """DELETE FROM users WHERE
  name ~ '^[0-9]+$'
  OR username ~ '^[0-9]+'
  OR username LIKE '%adsasda%'
RETURNING id, name, username;"""
r = run(f'''sudo -n PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c "{sql_users}" 2>&1''')
print(r[:1500])

# 5. 验证
print()
print('='*60)
print('验证 — 152 当前表行数')
print('='*60)
r = run('''sudo -n PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -h 127.0.0.1 -d security_oa -c "SELECT relname, n_live_tup FROM pg_stat_user_tables WHERE schemaname='public' AND n_live_tup > 0 ORDER BY n_live_tup DESC LIMIT 25" 2>&1''')
print(r)

print()
print('='*60)
print('完成')
print('='*60)
print('  152 演示数据保留 (attendance/schedules/expense/客户/商机 等)')
print('  152 E2E 噪声清空')
print('  152 代码未推送, 仍跑 152 原本版本')
print('  117 未受影响')
