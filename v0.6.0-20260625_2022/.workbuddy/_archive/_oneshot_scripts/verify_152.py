"""完整验证 152 部署状态"""
import paramiko, json
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

def run(cmd):
    si, so, se = c.exec_command(cmd, timeout=30)
    return so.read().decode('utf-8', errors='ignore').strip()

# 登录
import subprocess
script = '''
curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
'''
raw = run(script)
print('LOGIN raw:', raw[:200])
try:
    j = json.loads(raw)
    token = j.get('data', {}).get('token') or j.get('token')
except:
    token = None
print('TOKEN:', token[:40] if token else 'EMPTY')

if not token:
    print('Login failed')
    c.close()
    exit(1)

urls = [
    '/api/auth/me', '/api/dashboard/summary', '/api/customers', '/api/projects',
    '/api/employees', '/api/sales/leads', '/api/sales/opps', '/api/sales/referrers',
    '/api/sales/pool', '/api/sales/follow-ups', '/api/sales/products',
    '/api/finance/receivables', '/api/finance/payables', '/api/inventory/items',
    '/api/knowledge/categories', '/api/knowledge/articles', '/api/disk/folders',
    '/api/vehicles', '/api/work-orders', '/api/approval-templates',
    '/api/attendance/records', '/api/expense', '/api/leave-requests',
    '/api/overtime-requests', '/api/vehicle-usages', '/api/insurance',
    '/api/maintenance', '/api/fuel-cards', '/api/fuel-card-recharges',
    '/api/inventory-categories', '/api/receivables', '/api/payables',
    '/api/contracts', '/api/construction-logs', '/api/maintenance-contracts',
    '/api/project-materials', '/api/project-settlements', '/api/purchase-orders',
    '/api/messages', '/api/files', '/api/users', '/api/departments',
    '/api/audit-logs', '/api/roles', '/api/permissions', '/api/notifications',
]
ok = 0
fail = 0
fail_list = []
for url in urls:
    code = run(f'curl -s -H "Authorization: Bearer {token}" "http://127.0.0.1{url}" -o /dev/null -w "%{{http_code}}"')
    if code in ('200', '422'):
        ok += 1
    else:
        fail += 1
        fail_list.append((url, code))

print(f'\n✅ 200/422: {ok}  ❌ 失败: {fail}')
for url, code in fail_list:
    print(f'  ❌ {url} → {code}')

# 前端
print('\n--- 前端 ---')
idx = run('curl -s http://127.0.0.1/ | grep -oE "assets/index-[A-Za-z0-9_-]+\\.js" | head -1')
print('index hash:', idx)

for path in ['/finance/receivable', '/finance/payable', '/purchase/requirement', '/approval/center', '/knowledge', '/disk', '/vehicle/fleet', '/finance/overview']:
    code = run(f'curl -s -L "http://127.0.0.1{path}" -o /dev/null -w "%{{http_code}}"')
    print(f'  {path} → {code}')

# 看几个关键 DB 表记录数
print('\n--- DB 数据 ---')
sql = "SELECT 'leads' AS t, count(*) AS n FROM leads UNION ALL SELECT 'opps', count(*) FROM opportunities UNION ALL SELECT 'quotes', count(*) FROM quotations UNION ALL SELECT 'referrers', count(*) FROM referrers UNION ALL SELECT 'pool', count(*) FROM project_pool UNION ALL SELECT 'follow_ups', count(*) FROM sales_follow_ups UNION ALL SELECT 'projects', count(*) FROM projects UNION ALL SELECT 'customers', count(*) FROM customers;"
out = run(f"PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -t -c \"{sql}\"")
print(out)

c.close()
print('\nDONE')
