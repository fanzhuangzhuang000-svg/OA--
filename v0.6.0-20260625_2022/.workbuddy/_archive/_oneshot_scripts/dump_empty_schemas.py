import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 直接 dump 那 11 张空表的 schema
tables = ['jobs','failed_jobs','sessions','cache_locks','role_has_permissions',
          'model_has_permissions','password_reset_tokens','purchase_logistics',
          'purchase_payment_requests','purchase_payments','purchase_shipment_items',
          'purchase_shipments']

out_lines = []
for t in tables:
    stdin, stdout, stderr = ssh.exec_command(
        f"export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c \"\\d {t}\""
    )
    out_lines.append(f"=== {t} ===")
    out_lines.append(stdout.read().decode())
    out_lines.append(stderr.read().decode())

with open(r'D:\work\website\OA\.workbuddy\empty_tables_schema.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

# 同时再 dump 几张 sparse 表（待填满的）
sparse = ['project_contracts','construction_logs','project_materials',
          'process_templates','approval_records','knowledge_articles',
          'fuel_cards','vehicle_insurances','vehicle_maintenances',
          'process_instances','attendance_approvals','vehicle_fuel_records',
          'inventory_items','employee_certificates','customer_contacts',
          'reimbursement_items','contract_payment_nodes','quotation_items',
          'maintenance_records','opportunities','leads','employee_skills',
          'service_orders','tickets','training_records']
sparse_lines = []
for t in sparse:
    stdin, stdout, stderr = ssh.exec_command(
        f"export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c \"\\d {t}\" 2>&1 | head -25"
    )
    sparse_lines.append(f"=== {t} ===")
    sparse_lines.append(stdout.read().decode())
    sparse_lines.append('')

with open(r'D:\work\website\OA\.workbuddy\sparse_tables_schema.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sparse_lines))

print("schemas dumped")
ssh.close()
