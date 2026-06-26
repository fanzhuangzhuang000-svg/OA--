import paramiko

# 尝试连接 172 服务器
print("正在连接 172.20.0.139 服务器...")

# 尝试多个可能的凭据
credentials = [
    ('ubuntu', 'Aa782997781.'),
    ('root', 'admin123'),
    ('www-data', ''),
]

connected = False
ssh = None

for username, password in credentials:
    try:
        print(f"\n尝试 {username} / {password if password else '(无密码)'}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('172.20.0.139', username=username, password=password, timeout=10)
        print(f"✅ 连接成功！")
        connected = True
        break
    except Exception as e:
        print(f"❌ 失败: {e}")
        continue

if not connected:
    print("\n❌ 无法连接 to 172.20.0.139 服务器")
    print("\n可能的原因：")
    print("1. 服务器 IP 已变更（从 memory 看，172 可能是内网地址）")
    print("2. SSH 凭据已变更")
    print("3. 服务器已关机或不可达")
    print("\n建议：")
    print("1. 确认 172.20.0.139 是否仍然是测试服务器 IP")
    print("2. 提供正确的 SSH 凭据")
    print("3. 或者继续使用 152.136.115.121 服务器")
    exit(1)

# 检查 Laravel 项目是否存在
print("\n检查 Laravel 项目...")
stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/oa-api/ 2>&1 | head -10')
output = stdout.read().decode()
print(f"Laravel 项目检查：\n{output}")

# 检查数据库状态
print("\n检查数据库状态...")
stdin, stdout, stderr = ssh.exec_command("cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute='echo Project::count();'")
output = stdout.read().decode()
err = stderr.read().decode()
print(f"项目数量：{output if output else '查询失败'}")
if err:
    print(f"错误：{err[:300]}")

# 检查表数量
print("\n检查数据库表数量...")
stdin, stdout, stderr = ssh.exec_command("cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute='echo DB::connection()->getDatabaseName();'")
output = stdout.read().decode()
print(f"数据库名：{output if output else '未知'}")

ssh.close()
print("\n✅ 连接测试完成！")
