import paramiko

print("🚀 上传并运行测试数据 SQL 文件...")
print("=" * 60)

try:
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 上传 SQL 文件
    print("\n上传 SQL 文件...")
    sftp = ssh.open_sftp()
    local_file = r'D:\work\website\OA\.workbuddy\test_data_172.sql'
    remote_file = '/tmp/test_data_172.sql'
    sftp.put(local_file, remote_file)
    sftp.close()
    print("  ✅ 上传完成！")
    
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
    
    # 运行 SQL 文件
    print("\n运行 SQL 文件（可能需要几分钟）...")
    cmd = f'PGPASSWORD="{db_pass}" psql -h 127.0.0.1 -U {db_user} -d {db_name} -f {remote_file} 2>&1'
    
    # 实时输出
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    
    # 读取输出
    output = ""
    while True:
        line = stdout.readline()
        if not line:
            break
        output += line
        if 'INSERT' in line or 'BEGIN' in line or 'COMMIT' in line:
            print(line.strip())
    
    err = stderr.read().decode() if stderr else ''
    if err:
        print(f"\n⚠️ 错误输出: {err[:500]}")
    
    # 清理临时文件
    ssh.exec_command(f'rm {remote_file}')
    print("\n✅ 临时文件已清理")
    
    # 验证数据生成
    print("\n验证数据生成...")
    tables = ['users', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items']
    
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
    print("✅ 测试数据生成完成！")
    print("\n现在 172 服务器有大量测试数据，可以用于演示和测试。")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
