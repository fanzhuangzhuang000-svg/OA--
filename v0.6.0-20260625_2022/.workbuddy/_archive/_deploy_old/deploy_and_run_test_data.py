import paramiko
import time

print("🚀 部署并运行测试数据生成脚本...")
print("=" * 60)

try:
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 上传 PHP 脚本
    print("\n上传测试数据生成脚本...")
    sftp = ssh.open_sftp()
    local_file = r'D:\work\website\OA\.workbuddy\generate_test_data_172.php'
    remote_file = '/tmp/generate_test_data_172.php'
    sftp.put(local_file, remote_file)
    sftp.close()
    print("  ✅ 上传完成！")
    
    # 运行 PHP 脚本
    print("\n运行测试数据生成脚本（可能需要几分钟）...")
    stdin, stdout, stderr = ssh.exec_command(f'php {remote_file} 2>&1')
    
    # 实时输出
    output = ""
    while True:
        line = stdout.readline()
        if not line:
            break
        output += line
        print(line.strip())
    
    err = stderr.read().decode()
    if err:
        print(f"\n⚠️ 错误输出: {err[:500]}")
    
    # 清理临时文件
    ssh.exec_command(f'rm {remote_file}')
    print("\n✅ 临时文件已清理")
    
    # 验证数据生成
    print("\n验证数据生成...")
    tables = ['users', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items']
    
    for table in tables:
        stdin, stdout, stderr = ssh.exec_command(f'psql -U oa_user -d security_oa -t -c "SELECT COUNT(*) FROM {table};"')
        output = stdout.read().decode().strip()
        if output and 'ERROR' not in output:
            print(f"  {table}: {output} 条")
        else:
            print(f"  {table}: 查询失败")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 测试数据生成完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
