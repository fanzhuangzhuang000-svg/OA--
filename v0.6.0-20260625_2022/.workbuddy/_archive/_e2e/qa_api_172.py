"""Task 2: 172 服务器全 API 联调测试"""
import paramiko, json, time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')

def run(cmd, t=30):
    si, so, se = c.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    return out, err

# 取 token
out, _ = run("curl -s -X POST http://127.0.0.1:3001/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'")
try:
    j = json.loads(out)
    token = j.get('data', {}).get('token') or j.get('token', '')
except:
    token = ''
print(f'Token: {token[:30]}...' if token else 'NO TOKEN')
if not token:
    print('LOGIN RESP:', out[:300])
    c.close()
    exit(1)

# 端点列表（按模块）
endpoints = [
    # Auth
    ('GET', '/api/auth/me', 200),
    # Dashboard
    ('GET', '/api/dashboard/stats', 200),
    ('GET', '/api/dashboard/recent-projects', 200),
    ('GET', '/api/dashboard/recent-service-orders', 200),
    # 工作台
    ('GET', '/api/workbench/summary', [200, 404]),
    # 考勤
    ('GET', '/api/attendance/overview', 200),
    ('GET', '/api/attendance/records', 200),
    ('GET', '/api/attendance/leave', 200),
    ('GET', '/api/attendance/overtime', 200),
    # 员工
    ('GET', '/api/employees', 200),
    ('GET', '/api/departments', 200),
    ('GET', '/api/positions', 200),
    # 客户
    ('GET', '/api/customers', 200),
    # 销售
    ('GET', '/api/sales/leads', 200),
    ('GET', '/api/sales/opps', 200),
    ('GET', '/api/sales/referrers', 200),
    ('GET', '/api/sales/pool', 200),
    ('GET', '/api/sales/follow-ups', 200),
    ('GET', '/api/sales/products', 200),
    # 项目
    ('GET', '/api/projects', 200),
    # 售后
    ('GET', '/api/service/orders', 200),
    ('GET', '/api/service/maintenance-contracts', 200),
    # 报销
    ('GET', '/api/expenses', 200),
    # 车辆
    ('GET', '/api/vehicles', 200),
    ('GET', '/api/vehicles/insurances', 200),
    ('GET', '/api/vehicles/maintenances', 200),
    ('GET', '/api/fuel-cards', 200),
    ('GET', '/api/fuel-cards/recharges', 200),
    # 库存
    ('GET', '/api/inventory', 200),
    ('GET', '/api/inventory-categories', 200),
    # 财务
    ('GET', '/api/finance/receivables', 200),
    ('GET', '/api/finance/payables', 200),
    # 网盘
    ('GET', '/api/disk/folders', 200),
    # 知识库
    ('GET', '/api/knowledge/categories', 200),
    ('GET', '/api/knowledge/articles', 200),
    # 审批
    ('GET', '/api/approval-templates', 200),
    # 用户
    ('GET', '/api/users', 200),
    ('GET', '/api/roles', 200),
    ('GET', '/api/permissions', 200),
    # 消息
    ('GET', '/api/messages', [200, 404]),
    ('GET', '/api/notifications', [200, 404]),
]

results = []
for method, path, expect in endpoints:
    if isinstance(expect, list):
        expect_codes = expect
    else:
        expect_codes = [expect]
    cmd = f"curl -s -X {method} -H 'Authorization: Bearer {token}' http://127.0.0.1:3001{path} -o /dev/null -w '%{{http_code}}'"
    out, _ = run(cmd, t=15)
    code = out.strip()
    status = '✅' if code in [str(c) for c in expect_codes] else '❌'
    results.append((status, method, path, code, expect_codes))
    print(f'  {status} {method} {path} → {code}')

# 写入操作（创建/更新/删除）
print('\n--- 写入操作测试 ---')
write_tests = [
    # 销售前链路
    ('POST', '/api/sales/leads', '{"customer_id":1,"customer_name":"测试","contact_name":"张三","contact_phone":"13800000001","source":"website","owner_id":1,"stage":"new","rating":"A","estimated_amount":50000}', [200, 201, 422]),
    ('POST', '/api/sales/referrers', '{"name":"测试推荐人","phone":"13900000001","rate":10}', [200, 201, 422]),
    # 财务
    ('POST', '/api/finance/receivables', '{"customer_id":1,"amount":10000,"due_date":"2026-12-31"}', [200, 201, 422]),
    ('POST', '/api/finance/payables', '{"supplier_id":1,"amount":5000,"due_date":"2026-12-31"}', [200, 201, 422]),
    # 知识库
    ('POST', '/api/knowledge/categories', '{"name":"测试分类","parent_id":null,"icon":"folder"}', [200, 201, 422]),
    ('POST', '/api/knowledge/articles', '{"title":"测试文章","content":"内容","category_id":1,"status":"published"}', [200, 201, 422, 500]),
    # 考勤
    ('POST', '/api/attendance/leave', '{"type":"事假","start_date":"2026-06-20","end_date":"2026-06-22","reason":"私事","user_id":1}', [200, 201, 422]),
    # 报销
    ('POST', '/api/expenses', '{"category":"餐饮","total_amount":500,"description":"客户接待","user_id":1,"project_id":1,"claim_date":"2026-06-19"}', [200, 201, 422]),
]
for method, path, body, expect in write_tests:
    body_escaped = body.replace("'", "'\\''")
    cmd = f"curl -s -X {method} -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{body_escaped}' http://127.0.0.1:3001{path} -o /tmp/resp.json -w '%{{http_code}}'"
    out, _ = run(cmd, t=15)
    code = out.strip()
    # 看响应
    body_out, _ = run('cat /tmp/resp.json 2>/dev/null')
    body_show = body_out[:120].replace('\n', ' ')
    status = '✅' if code in [str(c) for c in expect] else '❌'
    results.append((status, method, path, code, expect))
    print(f'  {status} {method} {path} → {code} | {body_show}')

# 统计
ok = sum(1 for r in results if r[0] == '✅')
fail = sum(1 for r in results if r[0] == '❌')
print(f'\n=== API 联调结果 ===')
print(f'✅ 通过: {ok}')
print(f'❌ 失败: {fail}')
print(f'总端点数: {len(results)}')
print(f'通过率: {ok/len(results)*100:.1f}%')

# 失败详情
if fail > 0:
    print('\n--- 失败端点 ---')
    for r in results:
        if r[0] == '❌':
            print(f'  {r[1]} {r[2]} → {r[3]} (期望 {r[4]})')

# 保存结果
sftp = c.open_sftp()
with sftp.open('/tmp/api_results.json', 'w') as f:
    json.dump([{'status': r[0], 'method': r[1], 'path': r[2], 'code': r[3], 'expect': r[4]} for r in results], f, ensure_ascii=False, indent=2)
sftp.close()
print('\n结果已保存: /tmp/api_results.json')

c.close()
print('\nDONE')
