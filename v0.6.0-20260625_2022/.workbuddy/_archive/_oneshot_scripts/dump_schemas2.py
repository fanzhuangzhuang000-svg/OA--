"""dump 剩余失败表的 schema"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

PG = "export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa"

tables = ['positions', 'stock_records', 'employee_onboardings',
          'employee_skills', 'device_serial_numbers', 'project_contracts',
          'construction_logs', 'sales_products', 'sales_follow_up_attachments',
          'fuel_cards', 'fuel_card_recharges', 'vehicle_insurance',
          'vehicle_maintenance_records', 'schedules', 'approval_records',
          'approval_templates', 'disk_folders', 'disk_files', 'disk_settings',
          'knowledge_articles', 'process_instances', 'process_inspections',
          'process_signatures', 'process_images', 'project_pool', 'referrers',
          'approval_records_v2', 'cache_locks']

for t in tables:
    cmd = f'{PG} -c "\\d {t}" 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    print(f'\n===== {t} =====')
    print(out)

ssh.close()
