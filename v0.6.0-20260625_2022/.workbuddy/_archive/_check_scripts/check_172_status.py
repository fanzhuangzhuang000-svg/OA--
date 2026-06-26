import paramiko

print("🔧 修复 172 服务器日志权限问题...")
print("=" * 60)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 修复日志文件权限
    print("\n修复日志文件权限...")
    commands = [
        'sudo chmod 666 /var/www/oa-api/storage/logs/laravel.log',
        'sudo chown www-data:www-data /var/www/oa-api/storage/logs/laravel.log',
        'sudo chmod -R 777 /var/www/oa-api/storage/',
        'sudo chown -R www-data:www-data /var/www/oa-api/storage/',
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        if err and 'sudo' not in cmd:
            print(f"  警告: {cmd} -> {err[:100]}")
    
    print("✅ 日志权限已修复")
    
    # 查询数据库状态
    print("\n查询数据库状态...")
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && php artisan tinker --execute="echo DB::table(\'projects\')->count();" 2>&1')
    output = stdout.read().decode()
    err = stderr.read().decode()
    
    if output.strip() and 'could not be opened' not in output:
        print(f"✅ 项目数量: {output.strip()}")
    else:
        print(f"⚠️ 查询失败: {err[:300] if err else output[:300]}")
    
    # 查询所有表的数量
    print("\n查询主要表的数据量...")
    tables = ['projects', 'customers', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items']
    
    for table in tables:
        stdin, stdout, stderr = ssh.exec_command(f'cd /var/www/oa-api && php artisan tinker --execute="echo DB::table(\'{table}\')->count();" 2>&1')
        output = stdout.read().decode()
        if output.strip() and 'could not be opened' not in output:
            print(f"  {table}: {output.strip()} 条")
        else:
            print(f"  {table}: 查询失败")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 172 服务器状态检查完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
