import urllib.request, urllib.error, json

# 登录
req = urllib.request.Request(
    'http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']

BASE = 'http://172.20.0.139:3001/api'

# 前端真实URL（去重、按模块排序）
real_apis = [
    # 考勤
    'attendance/records', 'attendance/statistics', 'attendance/today',
    # 客户
    'customers', 'customers/statistics', 'customers/{id}/health-score',
    # 部门/岗位
    'departments', 'departments/tree',
    'positions', 'positions/tree',
    # 员工
    'employees', 'employees/statistics',
    # 项目
    'projects', 'projects/dashboard-summary', 'projects/payment-calendar',
    'projects/{id}', 'projects/{id}/tracking', 'projects/stages',
    # 服务
    'service/orders', 'service/orders/stats',
    'service/maintenance-contracts',
    # 报销
    'expense', 'expense/statistics', 'expense/{id}',
    # 车辆
    'vehicles', 'vehicles/stats', 'vehicles/insurances', 'vehicles/maintenances',
    'vehicles/applies', 'vehicles/apply',
    'vehicles/{id}/insurances', 'vehicles/{id}/maintenances',
    # 油卡
    'fuel-cards', 'fuel-cards/stats',
    # 库存
    'inventory/items', 'inventory/items/{id}', 'inventory/statistics',
    'inventory/categories', 'inventory/categories/tree',
    'inventory/warehouses', 'inventory/warnings',
    'inventory/stock-in', 'inventory/stock-out', 'inventory/stock-records',
    # 财务
    'finance/accounts', 'finance/accounts/{id}/transactions',
    'finance/receivables', 'finance/payables',
    'finance/invoices', 'finance/overview', 'finance/summary', 'finance/payments',
    # 网盘
    'drive/folders', 'drive/files',
    # 知识库
    'knowledge/articles', 'knowledge/categories',
    # 消息
    'notifications', 'notifications/unread-count', 'notifications/mark-all-read',
    # 审批
    'approvals/finance', 'approvals/operation', 'approvals/project',
    'approvals/finance/{id}', 'approvals/operation/{id}', 'approvals/project/{id}',
    # 排班
    'schedules', 'schedules/groups', 'schedules/shifts', 'schedules/stats',
    # 系统
    'system/roles', 'system/permissions',
    'system/audit-logs', 'system/login-logs',
    'system/data-stats', 'system/business-stats', 'system/operation-stats',
    'system/users', 'system/permissions/tree',
    # 工作台/数据
    'dashboard/workbench', 'dashboard/summary', 'dashboard/kpi',
    # 销售
    'sales/leads', 'sales/leads/board', 'sales/leads/source-options',
    'sales/opps', 'sales/opps/board', 'sales/opps/funnel',
    # 采购
    'purchase/plans', 'purchase/requirements', 'purchase/contracts',
    'purchase/payment-requests', 'purchase/payments', 'purchase/shipments',
    # 用车
    'vehicle/fleet', 'vehicle/apply', 'vehicle/dispatch',
]

results = {'ok': [], 'fail4xx': [], 'fail5xx': [], 'exc': []}

for ep in real_apis:
    try:
        req = urllib.request.Request(
            f'{BASE}/{ep}',
            headers={'Authorization': f'Bearer {token}'}
        )
        resp = urllib.request.urlopen(req, timeout=8)
        results['ok'].append((ep, resp.status))
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:150]
        if e.code == 404:
            results['fail4xx'].append((ep, e.code, body))
        else:
            results['fail5xx'].append((ep, e.code, body))
    except Exception as e:
        results['exc'].append((ep, str(e)[:100]))

print(f"\n=== OK: {len(results['ok'])} / 4xx: {len(results['fail4xx'])} / 5xx: {len(results['fail5xx'])} / EXC: {len(results['exc'])} ===\n")

print('✅ 正常:')
for ep, code in results['ok']:
    print(f'  [{code}] /api/{ep}')
print('\n❌ 4xx错误:')
for ep, code, body in results['fail4xx']:
    print(f'  [{code}] /api/{ep}')
    print(f'         {body}')
print('\n❌ 5xx错误:')
for ep, code, body in results['fail5xx']:
    print(f'  [{code}] /api/{ep}')
    print(f'         {body}')
print('\n⚠️ 异常:')
for ep, msg in results['exc']:
    print(f'  /api/{ep} - {msg}')
