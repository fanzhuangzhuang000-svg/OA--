import paramiko

print("📊 查询 172 服务器数据库状态（使用 psql）...")
print("=" * 60)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 从 .env 文件读取数据库配置
    print("\n读取数据库配置...")
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/oa-api/.env | grep DB_')
    env_output = stdout.read().decode()
    
    # 解析数据库配置
    db_config = {}
    for line in env_output.split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            db_config[key.strip()] = value.strip()
    
    db_name = db_config.get('DB_DATABASE', 'security_oa')
    db_user = db_config.get('DB_USERNAME', 'oa_user')
    db_pass = db_config.get('DB_PASSWORD', '')
    
    print(f"  数据库: {db_name}")
    print(f"  用户: {db_user}")
    
    # 使用 psql 查询主要表的数据量
    print("\n查询主要表的数据量...")
    tables = [
        'projects', 'customers', 'leads', 'opportunities', 
        'attendance_records', 'vehicles', 'inventory_items',
        'users', 'work_orders', 'reimbursements',
        'project_stages', 'customer_followups', 'notifications'
    ]
    
    for table in tables:
        query = f"SELECT COUNT(*) FROM {table};"
        cmd = f'PGPASSWORD="{db_pass}" psql -h 127.0.0.1 -U {db_user} -d {db_name} -t -c "{query}"'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode().strip()
        err = stderr.read().decode()
        
        if output and 'ERROR' not in output:
            print(f"  {table}: {output} 条")
        else:
            if 'does not exist' in err:
                print(f"  {table}: 表不存在")
            else:
                print(f"  {table}: 查询失败")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 数据库状态查询完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
