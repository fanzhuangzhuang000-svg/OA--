import re

# 从后端routes/api.php提取所有真实路由（带方法）
defined = {}  # path-without-id -> {method: [path]}
with open('pc-api/routes/api.php', 'r', encoding='utf-8') as f:
    for line in f:
        m = re.search(r"Route::(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", line)
        if m:
            method = m.group(1).upper()
            path = m.group(2).rstrip('/')
            # 标准化为 base path (去掉 /{xxx})
            base = re.sub(r'/\{[^}]+\}', '', path).rstrip('/')
            defined.setdefault(base, set()).add(method)

# 列出 missing 端点对应后端有什么
missing = [
    'attendance/statistics',
    'customers/statistics', 'customers/{id}/health-score',
    'positions/tree',
    'employees/statistics',
    'projects/{id}', 'projects/{id}/tracking',
    'service/orders/stats',
    'expense', 'expense/statistics', 'expense/{id}',
    'vehicles/applies', 'vehicles/apply', 'vehicles/{id}/insurances', 'vehicles/{id}/maintenances',
    'inventory/items', 'inventory/items/{id}', 'inventory/statistics',
    'inventory/categories', 'inventory/categories/tree',
    'inventory/stock-in', 'inventory/stock-out',
    'finance/accounts/{id}/transactions',
    'drive/folders', 'drive/files',
    'approvals/finance/{id}', 'approvals/operation/{id}', 'approvals/project/{id}',
    'system/roles', 'system/permissions', 'system/audit-logs', 'system/login-logs',
    'system/data-stats', 'system/business-stats', 'system/operation-stats',
    'system/users', 'system/permissions/tree',
    'dashboard/workbench', 'dashboard/summary', 'dashboard/kpi',
    'sales/leads/board', 'sales/opps/board',
    'vehicle/fleet', 'vehicle/apply', 'vehicle/dispatch',
]

print(f'后端总路由base数: {len(defined)}\n')

for ep in missing:
    base = ep.split('/')[0]
    norm = re.sub(r'/\{[^}]+\}', '', ep)
    # 找相似的 base
    candidates = [b for b in defined.keys() if b.startswith(base + '/') or b == base]
    # 特殊: 找包含 norm 任一关键词的
    if not candidates:
        # 找包含同名词的
        for b in defined.keys():
            parts = norm.split('/')
            for p in parts:
                if p and len(p) > 2 and p in b:
                    candidates.append(b)
    print(f'/api/{ep} (norm={norm})')
    if candidates:
        for c in candidates[:5]:
            print(f'   后端有: {sorted(defined[c])} {c}')
    else:
        print(f'   ❌ 完全无 {base}/* 路由')
    print()
