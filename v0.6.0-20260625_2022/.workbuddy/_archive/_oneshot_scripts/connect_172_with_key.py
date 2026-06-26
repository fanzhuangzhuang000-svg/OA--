import paramiko
import os

print("🔍 使用 SSH 密钥连接 172.20.0.139...")
print("=" * 60)

try:
    # 加载私钥
    key_path = os.path.expanduser('~/.ssh/id_rsa')
    print(f"加载私钥: {key_path}")
    
    if not os.path.exists(key_path):
        print(f"❌ 私钥文件不存在: {key_path}")
        exit(1)
    
    key = paramiko.RSAKey.from_private_key_file(key_path)
    print("✅ 私钥加载成功")
    
    # 连接服务器
    print("\n连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', pkey=key, timeout=10)
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
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="echo DB::table(\'projects\')->count();"')
    output = stdout.read().decode()
    err = stderr.read().decode()
    print(f"项目数量: {output.strip() if output.strip() else '查询失败'}")
    if err:
        print(f"错误: {err[:200]}")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 172.20.0.139 服务器连接正常！")
    print("\n正确连接方式:")
    print("  用户名: nbcy")
    print("  认证方式: SSH 密钥 (~/.ssh/id_rsa)")
    
except paramiko.AuthenticationException:
    print("❌ 密钥认证失败")
    print("可能原因:")
    print("  1. 服务器上的公钥已变更")
    print("  2. 私钥文件权限不正确")
    print("  3. 服务器禁用了密钥认证")
except paramiko.SSHException as e:
    print(f"❌ SSH 错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")
    import traceback
    traceback.print_exc()
