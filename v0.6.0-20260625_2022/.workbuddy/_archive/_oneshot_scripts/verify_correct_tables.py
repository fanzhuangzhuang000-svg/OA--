import paramiko

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 查询所有主要表的记录数
print('\n查询所有主要表的记录数...')
tables = [
    'users',
    'customers',
    'leads',
    'opportunities',
    'attendance_records',
    'vehicles',
    'projects',
    'inventory_items',
    'follow_up_records',
    'sales_follow_ups',
    'service_orders',
    'expense_claims',
    'vehicle_usage_requests',
    'audit_logs',
    'notifications'
]

for table in tables:
    stdin, stdout, stderr = ssh.exec_command(
        f'psql -U oa_user -d security_oa -t -c "SELECT COUNT(*) FROM {table};" 2>&1'
    )
    output = stdout.read().decode().strip()
    err = stderr.read().decode()
    
    if output and (output.isdigit() or output == '0'):
        print(f'  {table}: {output} 条记录')
    else:
        if 'does not exist' in err:
            print(f'  {table}: 表不存在')
        else:
            print(f'  {table}: 查询失败')

ssh.close()
print('\n✅ 完成！')
