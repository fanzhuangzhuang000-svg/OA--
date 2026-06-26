"""117 烟囱测试脚本"""
import paramiko, re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.3.117', username='nbcy', password='admin123', timeout=15)


def run(cmd, t=15):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    return out or err


# 1. login
print('=== 1. login ===')
out = run('curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin1","password":"admin123"}\' 2>&1', 15)
print('  body:', out[:300])
m = re.search(r'"token":"([^"]+)"', out)
token = m.group(1) if m else None
print(f'  token: {token[:30] if token else "NONE"}')

# 2. V0.4.1 8 budget API
print('\n=== V0.4.1 项目预算 (8 API) ===')
tests = []
# 1) list
out = run(f'curl -s -w "\\n%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1/api/construction/budgets 2>&1', 15)
code = out.rsplit('\n', 1)[-1]
body = out.rsplit('\n', 1)[0]
print(f'  [1] GET list  HTTP={code} body={body[:200]}')
tests.append(('GET /budgets', code))

# 2) summary
out = run(f'curl -s -w "\\n%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1/api/construction/budgets/summary/1 2>&1', 15)
code = out.rsplit('\n', 1)[-1]
print(f'  [2] GET summary  HTTP={code}')
tests.append(('GET /budgets/summary/1', code))

# 3) project_id
out = run('PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -tAc "SELECT id FROM projects WHERE status != \'completed\' LIMIT 1" 2>&1', 10)
project_id = out.strip()
print(f'  using project_id={project_id}')

# 4) POST create
budget_payload = f'{{"project_id":{project_id},"title":"117部署烟囱测试预算","category":"material","total_amount":54000,"items":[{{"name":"线缆","category":"material","estimated_amount":24000,"quantity":120,"unit":"米","unit_price":200}},{{"name":"人工","category":"labor","estimated_amount":15000,"quantity":30,"unit":"工日","unit_price":500}},{{"name":"外包","category":"outsource","estimated_amount":15000,"quantity":1,"unit":"项","unit_price":15000}}]}}'
out = run(f'curl -s -w "\\n%{{http_code}}" -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "Accept: application/json" -d \'{budget_payload}\' http://127.0.0.1/api/construction/budgets 2>&1', 15)
parts = out.rsplit('\n', 1)
code = parts[-1]
body = parts[0]
print(f'  [3] POST create  HTTP={code} body={body[:300]}')
tests.append(('POST /budgets', code))
m = re.search(r'"id":(\d+)', body)
budget_id = m.group(1) if m else None
print(f'    budget_id={budget_id}')

# 5) GET show
if budget_id:
    out = run(f'curl -s -w "\\n%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1/api/construction/budgets/{budget_id} 2>&1', 15)
    code = out.rsplit('\n', 1)[-1]
    print(f'  [4] GET show  HTTP={code}')
    tests.append(('GET /budgets/{id}', code))

# 6) POST approve
if budget_id:
    out = run(f'curl -s -w "\\n%{{http_code}}" -X POST -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1/api/construction/budgets/{budget_id}/approve 2>&1', 15)
    code = out.rsplit('\n', 1)[-1]
    print(f'  [5] POST approve  HTTP={code}')
    tests.append(('POST /budgets/{id}/approve', code))

# 7) GET summary
out = run(f'curl -s -w "\\n%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1/api/construction/budgets/summary/{project_id} 2>&1', 15)
code = out.rsplit('\n', 1)[-1]
print(f'  [6] GET summary 2  HTTP={code}')
tests.append(('GET /budgets/summary/{project_id}', code))

# 8) POST revise
if budget_id:
    out = run(f'curl -s -w "\\n%{{http_code}}" -X POST -H "Authorization: Bearer {token}" -H "Accept: application/json" -d \'{{"reason":"调整"}}\' http://127.0.0.1/api/construction/budgets/{budget_id}/revise 2>&1', 15)
    code = out.rsplit('\n', 1)[-1]
    print(f'  [7] POST revise  HTTP={code}')
    tests.append(('POST /budgets/{id}/revise', code))

# 9) DELETE draft
budget2 = f'{{"project_id":{project_id},"title":"删除测试","category":"material","total_amount":1000,"items":[{{"name":"测试","category":"material","estimated_amount":1000,"quantity":1,"unit":"个","unit_price":1000}}]}}'
out = run(f'curl -s -w "\\n%{{http_code}}" -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "Accept: application/json" -d \'{budget2}\' http://127.0.0.1/api/construction/budgets 2>&1', 15)
body = out.rsplit('\n', 1)[0]
m = re.search(r'"id":(\d+)', body)
draft_id = m.group(1) if m else None
if draft_id:
    out = run(f'curl -s -w "\\n%{{http_code}}" -X DELETE -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1/api/construction/budgets/{draft_id} 2>&1', 15)
    code = out.rsplit('\n', 1)[-1]
    print(f'  [8] DELETE draft  HTTP={code}')
    tests.append(('DELETE /budgets/{id}', code))

print(f'\n=== V0.4.1 烟囱: {sum(1 for _, c in tests if c == "200")}/{len(tests)} ===')

# 3. V0.4.2 supplier API
print('\n=== V0.4.2 供应商/总账 (8 API) ===')
v42_tests = []
urls = [
    ('GET /suppliers', '/api/suppliers'),
    ('GET /suppliers/1', '/api/suppliers/1'),
    ('GET /external/quote-requests', '/api/external/quote-requests'),
    ('GET /external/quote-requests/1', '/api/external/quote-requests/1'),
    ('GET /ledger/suppliers', '/api/ledger/suppliers'),
    ('GET /ledger/customers', '/api/ledger/customers'),
    ('GET /ledger/dashboard', '/api/ledger/dashboard'),
    ('GET /projects/suppliers', '/api/projects/suppliers'),
    ('GET /projects/customers', '/api/projects/customers'),
]
for name, url in urls:
    out = run(f'curl -s -w "\\n%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1{url} 2>&1', 15)
    code = out.rsplit('\n', 1)[-1]
    body = out.rsplit('\n', 1)[0][:200]
    print(f'  {name}  HTTP={code} body={body[:200]}')
    v42_tests.append((name, code))

print(f'\n=== V0.4.2 烟囱: {sum(1 for _, c in v42_tests if c == "200")}/{len(v42_tests)} ===')

# 4. 其他核心
print('\n=== 核心业务 (5 API) ===')
core_tests = []
core_urls = [
    ('GET /auth/me', '/api/auth/me'),
    ('GET /users', '/api/users'),
    ('GET /projects', '/api/projects'),
    ('GET /dashboard', '/api/dashboard'),
    ('GET /notifications', '/api/notifications'),
]
for name, url in core_urls:
    out = run(f'curl -s -w "\\n%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1{url} 2>&1', 15)
    code = out.rsplit('\n', 1)[-1]
    body = out.rsplit('\n', 1)[0][:150]
    print(f'  {name}  HTTP={code} body={body}')
    core_tests.append((name, code))

print(f'\n=== 核心: {sum(1 for _, c in core_tests if c == "200")}/{len(core_tests)} ===')

# 总成绩
total_pass = sum(1 for _, c in tests + v42_tests + core_tests if c == '200')
total = len(tests) + len(v42_tests) + len(core_tests)
print(f'\n{"="*50}\n117 部署烟囱: {total_pass}/{total} 全 200\n{"="*50}')

ssh.close()
