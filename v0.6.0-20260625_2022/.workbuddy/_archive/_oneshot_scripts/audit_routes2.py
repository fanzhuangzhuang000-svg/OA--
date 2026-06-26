import re

# 提取后端所有路由的"前缀路径"（不带id参数）
defined = []
with open('pc-api/routes/api.php', 'r', encoding='utf-8') as f:
    for line in f:
        m = re.search(r"Route::(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", line)
        if m:
            method = m.group(1).upper()
            path = m.group(2).rstrip('/').split('{')[0].rstrip('/')
            if path:
                defined.append((method, path))

# 测试中报404的端点
tested_404 = [
    'departments/tree', 'positions/tree', 'skill-tags', 'skill-tags/categories',
    'employees/statistics', 'customers/statistics', 'customers/1/health',
    'projects/1', 'projects/1/tracking', 'service-tickets', 'service-tickets/1',
    'service-stages', 'service-statistics', 'after-sales/statistics',
    'reimbursements', 'reimbursements/1', 'reimbursements/statistics',
    'vehicles/1', 'vehicles/statistics', 'vehicles/1/insurances',
    'vehicles/1/maintenances', 'vehicles/1/fuel-cards',
    'inventory/items', 'inventory/items/1', 'inventory/statistics',
    'inventory/categories', 'inventory/categories/tree',
    'drive/folders', 'drive/files', 'messages', 'messages/unread-count',
    'attendance/leave-requests', 'attendance/overtime-requests',
    'attendance/schedules', 'attendance/settings',
    'attendance/statistics',
    'system/roles', 'system/permissions', 'system/menus',
    'system/audit-logs', 'system/login-logs', 'system/data-stats', 'system/users',
    'dashboard/overview', 'dashboard/workbench',
    'training/plans', 'training/certificates', 'training/statistics',
    'users/profile', 'users/permissions',
]

print('=== 测试中404的端点 vs 后端真实路径 ===\n')
for ep in tested_404:
    # 模糊匹配
    base = ep.split('/')[0]
    matches = [d for d in defined if d[1].startswith(base)]
    print(f'/api/{ep}')
    if matches:
        for m, p in matches[:3]:
            print(f'  → 后端: {m} /api/{p}')
    else:
        print(f'  → 后端: 无任何 {base}/* 路由!')
    print()
