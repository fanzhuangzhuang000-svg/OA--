"""dump 关键表的实际列名"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

PG = "export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa"

tables = ['customer_devices', 'device_serial_numbers', 'employee_profiles',
          'employee_skills', 'certificates', 'construction_logs',
          'contract_payment_nodes', 'employee_onboardings', 'employee_resignations',
          'maintenance_contracts', 'project_contracts', 'project_materials',
          'project_settlements', 'purchase_contracts', 'purchase_items',
          'purchase_orders', 'purchase_plans', 'purchase_requirements',
          'quotations', 'quotation_items', 'sales_products', 'schedules',
          'service_order_parts', 'shift_groups', 'shift_group_members',
          'warehouses', 'stock_records', 'fuel_cards', 'fuel_card_recharges',
          'vehicle_insurance', 'vehicle_maintenance_records',
          'knowledge_articles', 'process_instances', 'process_inspections',
          'process_signatures', 'process_images', 'project_pool',
          'disk_files', 'disk_folders', 'referrers',
          'skill_tags', 'positions', 'departments']

for t in tables:
    cmd = f'{PG} -c "\\d {t}" 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    print(f'\n===== {t} =====')
    print(out)

ssh.close()
