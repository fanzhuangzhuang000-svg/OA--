import os, re

# 找出调用了缺失URL的前端文件 (按"页面"分组)
missing = ['attendance/statistics', 'customers/statistics', 'customers/{id}/health-score',
           'positions/tree', 'employees/statistics', 'projects/{id}', 'projects/{id}/tracking',
           'service/orders/stats', 'expense', 'expense/statistics', 'expense/{id}',
           'vehicles/applies', 'vehicles/apply', 'vehicles/{id}/insurances', 'vehicles/{id}/maintenances',
           'inventory/items', 'inventory/items/{id}', 'inventory/statistics',
           'inventory/categories', 'inventory/categories/tree', 'inventory/stock-in', 'inventory/stock-out',
           'finance/accounts/{id}/transactions', 'drive/folders', 'drive/files',
           'approvals/finance/{id}', 'approvals/operation/{id}', 'approvals/project/{id}',
           'system/roles', 'system/permissions', 'system/audit-logs', 'system/login-logs',
           'system/data-stats', 'system/business-stats', 'system/operation-stats',
           'system/users', 'system/permissions/tree',
           'dashboard/workbench', 'dashboard/summary', 'dashboard/kpi',
           'sales/leads/board', 'sales/opps/board',
           'vehicle/fleet', 'vehicle/apply', 'vehicle/dispatch']

pages_affected = {}  # url -> [files]
for root, dirs, files in os.walk('pc-web/src/views'):
    for fn in files:
        if not fn.endswith(('.vue', '.ts')):
            continue
        path = os.path.join(root, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            for url in missing:
                if url in content or url.replace('{id}', '1') in content or url.replace('{id}', '${id}') in content:
                    pages_affected.setdefault(url, set()).add(path.replace('pc-web/src/', ''))
        except:
            pass

print('=== 受影响的页面 (按页面分组) ===\n')
for url in sorted(pages_affected.keys()):
    files = pages_affected[url]
    print(f'/api/{url}')
    for f in sorted(files)[:5]:
        print(f'   ← {f}')
    if len(files) > 5:
        print(f'   ... +{len(files)-5} 更多')
    print()
