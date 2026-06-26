"""采购业务流 E2E 测试 — 172.20.0.139"""
import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')

# 拿 token
cmd = '''curl -s -X POST http://127.0.0.1:3001/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' '''
si, so, se = c.exec_command(cmd, timeout=10)
out = so.read().decode('utf-8', errors='ignore')
j = json.loads(out)
token = j['data']['token']
print(f'Token: {token[:30]}...')

def call(method, ep, body=None):
    if body is None:
        full = f'''curl -s -o /tmp/r.txt -w "%{{http_code}}" -H "Authorization: Bearer {token}" http://127.0.0.1:3001{ep}'''
    else:
        body_escaped = body.replace('"', '\\"')
        full = f'''curl -s -o /tmp/r.txt -w "%{{http_code}}" -X {method} -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d "{body_escaped}" http://127.0.0.1:3001{ep}'''
    si, so, se = c.exec_command(full, timeout=15)
    code = so.read().decode('utf-8', errors='ignore').strip()
    sftp = c.open_sftp()
    try:
        body_out = sftp.open('/tmp/r.txt').read().decode('utf-8', errors='ignore')
    except:
        body_out = ''
    sftp.close()
    return code, body_out[:200]

print('\n=== 采购业务流 E2E ===')

# 1. 录需求
code, body = call('POST', '/api/purchase/requirements',
    '{"title":"摄像头需求-测试","priority":"high","status":"draft","quantity":20,"estimated_amount":30000}')
print(f'  1.录需求 POST /api/purchase/requirements → {code}')
print(f'    body: {body[:200]}')
req_id = None
try:
    req_id = json.loads(body).get('data', {}).get('id')
except: pass

# 2. 查询需求
code, body = call('GET', '/api/purchase/requirements')
print(f'  2.查需求 GET /api/purchase/requirements → {code}')

# 3. 创建计划
code, body = call('POST', '/api/purchase/plans',
    f'{{"title":"采购计划-A","requirement_id":{req_id or 1},"supplier_id":1,"total_amount":30000}}')
print(f'  3.建计划 POST /api/purchase/plans → {code}')
print(f'    body: {body[:200]}')
plan_id = None
try:
    plan_id = json.loads(body).get('data', {}).get('id')
except: pass

# 4. 提交审批
if plan_id:
    code, body = call('POST', f'/api/purchase/plans/{plan_id}/submit', '{"comment":"请审批"}')
    print(f'  4.提交 POST /api/purchase/plans/{plan_id}/submit → {code}')

    # 5. 审批
    code, body = call('POST', f'/api/purchase/plans/{plan_id}/approve', '{"comment":"同意"}')
    print(f'  5.审批 POST /api/purchase/plans/{plan_id}/approve → {code}')

# 6. 查询所有
for ep in ['/api/purchase/requirements', '/api/purchase/plans', '/api/purchase/contracts',
           '/api/purchase/payment-requests', '/api/purchase/payments', '/api/purchase/shipments',
           '/api/purchase/approvals']:
    code, _ = call('GET', ep)
    print(f'  查询 GET {ep} → {code}')

# 7. 物流跟踪
code, body = call('GET', '/api/purchase/shipments/1/track')
print(f'  7.物流跟踪 GET /api/purchase/shipments/1/track → {code}')
print(f'    body: {body[:200]}')

c.close()
print('\n=== DONE ===')
