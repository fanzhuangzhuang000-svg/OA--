import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run_sql(sql):
    cmd = f'mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db -e "{sql}"'
    stdin, stdout, stderr = ssh.exec_command(f'echo admin123 | sudo -S {cmd}', timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    return out

# Check key tables
tables = ['employee_profiles', 'skill_tags', 'customer_devices', 'follow_up_records',
          'projects', 'service_orders', 'expense_claims', 'vehicles', 'warehouses', 'stock_records', 'system_logs']

for t in tables:
    print(f'=== {t} ===')
    out = run_sql(f'SHOW COLUMNS FROM {t}')
    if out:
        for line in out.split('\n'):
            if 'enum(' in line.lower() or line.strip():
                print(f'  {line}')
    else:
        print('  (empty or no such table)')
    print()

ssh.close()
