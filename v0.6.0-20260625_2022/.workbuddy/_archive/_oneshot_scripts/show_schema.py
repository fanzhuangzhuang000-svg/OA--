import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123')
for tbl in ['attendance_records', 'vehicles', 'employee_profiles', 'expense_claims', 'leave_requests', 'maintenance_contracts', 'certificates', 'projects', 'service_orders', 'receivables']:
    cmd = f'cd /var/www/oa-api && php artisan tinker --execute="echo json_encode(DB::select(\\"SHOW COLUMNS FROM ' + tbl + '\\"));" 2>&1'
    si, so, se = ssh.exec_command(cmd)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    body = out or err
    print('===', tbl, '===')
    if 'Base table or view not found' in body or "doesn't exist" in body:
        print('  (table missing)')
    else:
        # 提取 Field/Type 两列
        import re, json
        try:
            arr = json.loads(body.strip())
            for c in arr:
                print(f"  {c['Field']:25s} {c['Type']:35s} null={c['Null']} default={c['Default']}")
        except Exception as e:
            print('  PARSE:', body[:300])
ssh.close()
