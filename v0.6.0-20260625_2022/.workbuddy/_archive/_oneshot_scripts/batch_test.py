import urllib.request, urllib.error, json

# 登录
req = urllib.request.Request(
    'http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']
print(f'Token: {token[:30]}...')

BASE = 'http://172.20.0.139:3001/api'

endpoints = [
    'departments', 'departments/tree',
    'positions', 'positions/tree',
    'skill-tags', 'skill-tags/categories',
    'employees', 'employees/1', 'employees/statistics',
    'customers', 'customers/1', 'customers/statistics',
    'customers/1/follow-ups', 'customers/1/health', 'customers/1/profile',
    'projects', 'projects/1', 'projects/dashboard-summary',
    'projects/1/tracking', 'projects/stages', 'projects/payment-calendar',
    'service-tickets', 'service-tickets/1', 'service-stages', 'service-statistics',
    'after-sales/statistics',
    'reimbursements', 'reimbursements/1', 'reimbursements/statistics',
    'vehicles', 'vehicles/1', 'vehicles/statistics',
    'vehicles/1/insurances', 'vehicles/1/maintenances', 'vehicles/1/fuel-cards',
    'fuel-cards', 'fuel-cards/stats',
    'inventory/items', 'inventory/items/1', 'inventory/statistics',
    'inventory/categories', 'inventory/categories/tree',
    'finance/accounts', 'finance/accounts/1/transactions',
    'finance/receivables', 'finance/payables',
    'finance/invoices', 'finance/overview', 'finance/summary', 'finance/payments',
    'drive/folders', 'drive/files',
    'knowledge/categories', 'knowledge/articles',
    'messages', 'messages/unread-count',
    'approvals/finance', 'approvals/operation', 'approvals/project',
    'attendance/records', 'attendance/leave-requests', 'attendance/overtime-requests',
    'attendance/schedules', 'attendance/settings',
    'attendance/statistics', 'attendance/today',
    'system/roles', 'system/permissions', 'system/menus',
    'system/audit-logs', 'system/login-logs',
    'system/data-stats', 'system/users',
    'dashboard/overview', 'dashboard/workbench',
    'training/plans', 'training/certificates', 'training/statistics',
    'users/profile', 'users/permissions',
]

results = {'ok': [], 'fail': []}

for ep in endpoints:
    try:
        req = urllib.request.Request(
            f'{BASE}/{ep}',
            headers={'Authorization': f'Bearer {token}'}
        )
        resp = urllib.request.urlopen(req, timeout=8)
        results['ok'].append((ep, resp.status))
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        results['fail'].append((ep, e.code, body))
    except Exception as e:
        results['fail'].append((ep, 'EXC', str(e)[:200]))

print(f"\n=== OK: {len(results['ok'])} / FAIL: {len(results['fail'])} ===\n")
print('FAIL列表:')
for ep, code, body in results['fail']:
    print(f'  [{code}] /{ep}')
    print(f'         {body}')
