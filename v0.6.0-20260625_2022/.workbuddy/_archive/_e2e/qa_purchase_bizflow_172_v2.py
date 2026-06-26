"""采购业务流 E2E 测试 v2 — 解决 quoting 地狱"""
import paramiko, json

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')

# 拿 token
si, so, se = c.exec_command(
    '''curl -s -X POST http://127.0.0.1:3001/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' ''',
    timeout=10
)
out = so.read().decode('utf-8', errors='ignore')
token = json.loads(out)['data']['token']
print(f'Token: {token[:30]}...')

def call(method, ep, body=None):
    sftp = c.open_sftp()
    if body:
        with sftp.open('/tmp/body.json', 'w') as f:
            f.write(body)
        full = f'curl -s -o /tmp/r.txt -w "%{{http_code}}" -X {method} -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d @/tmp/body.json http://127.0.0.1:3001{ep}'
    else:
        full = f'curl -s -o /tmp/r.txt -w "%{{http_code}}" -H "Authorization: Bearer {token}" http://127.0.0.1:3001{ep}'
    sftp.close()
    si, so, se = c.exec_command(full, timeout=15)
    code = so.read().decode('utf-8', errors='ignore').strip()
    sftp = c.open_sftp()
    body_out = sftp.open('/tmp/r.txt').read().decode('utf-8', errors='ignore')
    sftp.close()
    return code, body_out

print('\n=== 采购业务流 E2E ===')

# 1. 录需求
code, body = call('POST', '/api/purchase/requirements',
    json.dumps({"title":"摄像头采购","priority":"high","status":"draft",
                "quantity":20,"estimated_amount":30000,
                "material":"海康威视摄像头DS-2CD2T47","deadline":"2026-07-15"}))
print(f'  1.录需求 → {code}')
req_id = None
if code in ['200', '201']:
    try: req_id = json.loads(body)['data']['id']
    except: pass
    print(f'    需求 id={req_id}')

# 2. 创建计划
plan_body = json.dumps({"title":"采购计划-A","requirement_id":req_id or 1,
                        "supplier_id":1,"total_amount":30000})
code, body = call('POST', '/api/purchase/plans', plan_body)
print(f'  2.建计划 → {code}')
plan_id = None
if code in ['200', '201']:
    try: plan_id = json.loads(body)['data']['id']
    except: pass
    print(f'    计划 id={plan_id}')

# 3. 提交
if plan_id:
    code, body = call('POST', f'/api/purchase/plans/{plan_id}/submit',
                      json.dumps({"comment":"请审批"}))
    print(f'  3.提交审批 → {code}')

    # 4. 审批
    code, body = call('POST', f'/api/purchase/plans/{plan_id}/approve',
                      json.dumps({"comment":"同意"}))
    print(f'  4.审批通过 → {code}')

    # 5. 创建合同
    code, body = call('POST', '/api/purchase/contracts',
        json.dumps({"title":"采购合同-1","plan_id":plan_id,"supplier_id":1,
                    "contract_no":f"HT-2026-{plan_id}","total_amount":30000,
                    "sign_date":"2026-06-19"}))
    print(f'  5.建合同 → {code}')
    contract_id = None
    if code in ['200', '201']:
        try: contract_id = json.loads(body)['data']['id']
        except: pass
        print(f'    合同 id={contract_id}')

    # 6. 发货
    if contract_id:
        code, body = call('POST', f'/api/purchase/contracts/{contract_id}/ship',
                          json.dumps({"tracking_no":"SF1234567890"}))
        print(f'  6.发货 → {code}')
        # 7. 物流
        code, body = call('POST', f'/api/purchase/shipments/{contract_id}/logistics-update',
                          json.dumps({"status":"in_transit","location":"上海分拨中心"}))
        print(f'  7.物流更新 → {code}')

# 统计
print('\n=== 统计 ===')
for ep in ['/api/purchase/requirements', '/api/purchase/plans', '/api/purchase/contracts',
           '/api/purchase/payment-requests', '/api/purchase/payments', '/api/purchase/shipments',
           '/api/purchase/approvals']:
    code, body = call('GET', ep)
    try:
        total = json.loads(body).get('data', {}).get('total', '?')
    except: total = '?'
    print(f'  GET {ep:40s} → {code} (total={total})')

c.close()
print('\n=== DONE ===')
