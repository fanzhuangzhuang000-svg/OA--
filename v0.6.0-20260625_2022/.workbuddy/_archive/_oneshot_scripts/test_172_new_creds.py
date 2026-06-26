import paramiko

print("🔍 测试 172.20.0.139 新凭据...")
print("=" * 50)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 验证身份
    stdin, stdout, stderr = ssh.exec_command('whoami && pwd')
    output = stdout.read().decode()
    print(f"\n当前用户: {output.strip()}")
    
    # 检查 Laravel 项目
    stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/oa-api/artisan 2>&1')
    output = stdout.read().decode()
    if 'No such file' not in output:
        print("✅ Laravel 项目存在")
    else:
        print(f"⚠️ Laravel 项目不存在: {output}")
    
    # 检查数据库状态
    print("\n检查数据库状态...")
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && php artisan tinker --execute="echo DB::table(\'projects\')->count();" 2>&1')
    output = stdout.read().decode()
    err = stderr.read().decode()
    
    # 只显示前 500 个字符
    if output.strip():
        print(f"项目数量: {output.strip()[:200]}")
    else:
        print(f"查询失败，错误: {err[:300]}")
    
    ssh.close()
    print("\n" + "=" * 50)
    print("✅ 172.20.0.139 服务器连接正常！")
    print("\n正确凭据已确认:")
    print("  用户名: nbcy")
    print("  密码: admin123")
    
except paramiko.AuthenticationException:
    print("❌ 认证失败，凭据可能不正确")
except paramiko.SSHException as e:
    print(f"❌ SSH 错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")
    import traceback
    traceback.print_exc()
