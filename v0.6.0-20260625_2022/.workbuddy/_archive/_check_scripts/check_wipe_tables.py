"""检查 wipe-data 表都存在吗"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

# 1. 列出 DB 所有表
out = run("sudo -u postgres psql -d security_oa -tAc \"SELECT tablename FROM pg_tables WHERE schemaname='public'\" 2>&1")
tables_in_db = set([t.strip() for t in out.split('\n') if t.strip()])
print(f'DB 中实际有的表数: {len(tables_in_db)}')

# 2. wipeData 列表
wipe_tables = [
    'project_settlements', 'project_materials', 'construction_logs',
    'contract_payment_nodes', 'project_contracts', 'purchase_items', 'purchase_orders',
    'project_members', 'projects',
    'service_order_parts', 'service_order_logs', 'service_orders',
    'maintenance_contracts',
    'expense_items', 'expense_claims', 'approval_records',
    'payables', 'receivables',
    'stock_records', 'device_serial_numbers', 'inventory_items', 'warehouses',
    'vehicle_usage_requests', 'vehicle_maintenance_records', 'vehicle_insurance', 'vehicles',
    'attendance_records', 'leave_requests', 'overtime_requests',
    'follow_up_records', 'customer_devices', 'customer_contacts', 'customers',
    'certificates', 'employee_profiles',
    'disk_files', 'disk_folders',
    'knowledge_articles', 'knowledge_categories',
    'notifications',
]

print(f'\nwipeData 列表: {len(wipe_tables)} 张')
print('\nwipeData 表在 DB 中找不到的:')
missing = [t for t in wipe_tables if t not in tables_in_db]
for t in missing:
    print(f'  ❌ {t}')

print('\nDB 中有但 wipeData 没列的（业务表）:')
business_extra = [t for t in tables_in_db if t not in wipe_tables and not t.startswith(('pg_', 'cache', 'jobs', 'sessions', 'password_', 'personal_'))]
for t in sorted(business_extra):
    print(f'  ➕ {t}')

ssh.close()
