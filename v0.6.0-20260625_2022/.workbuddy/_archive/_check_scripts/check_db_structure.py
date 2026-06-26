import paramiko

print("🔍 检查 172 服务器数据库表结构...")
print("=" * 60)

try:
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 从 .env 文件读取数据库配置
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
    
    print(f"\n数据库配置:")
    print(f"  数据库: {db_name}")
    print(f"  用户: {db_user}")
    
    # 检查主要表的结构
    print("\n检查主要表的结构...")
    tables = ['users', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items', 'projects', 'customers']
    
    for table in tables:
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -t -c \"{query}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if output and 'ERROR' not in output:
            print(f"\n📋 表 {table} 的结构:")
            for line in output.strip().split('\n'):
                if line.strip():
                    print(f"  {line.strip()}")
        else:
            if 'does not exist' in err:
                print(f"\n⚠️ 表 {table} 不存在")
            else:
                print(f"\n⚠️ 表 {table} 查询失败: {err[:200]}")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 数据库表结构检查完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
