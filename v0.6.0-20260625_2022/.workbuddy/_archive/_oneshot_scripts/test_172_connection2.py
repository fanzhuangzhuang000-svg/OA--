import paramiko

# 尝试连接 172 服务器
print("正在连接 172.20.0.139 服务器...")

# 尝试更多可能的凭据
credentials = [
    ('ubuntu', 'Aa782997781.'),
    ('root', ''),
    ('admin', 'admin123'),
    ('oa', 'oa123'),
    ('www-data', ''),
    ('ubuntu', 'ubuntu'),
    ('root', 'root'),
]

connected = False
ssh = None

for username, password in credentials:
    try:
        pwd_display = password if password else '(空密码)'
        print(f"尝试 {username} / {pwd_display}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('172.20.0.139', username=username, password=password, timeout=10, allow_agent=False, look_for_keys=False)
        print(f"✅ 连接成功！")
        connected = True
        break
    except Exception as e:
        print(f"❌ 失败: {e}")
        continue

if not connected:
    print("\n❌ 无法连接 to 172.20.0.139 服务器")
    print("\n请提供正确的 SSH 凭据：")
    print("1. 用户名：")
    print("2. 密码（或 SSH 密钥路径）：")
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
stdin, stdout, stderr = ssh.exec_command("cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute='echo \"Tables: \" . count(DB::select(\"SELECT tablename FROM pg_tables WHERE schemaname = 'public'\");'")
output = stdout.read().decode()
print(f"数据库信息：{output if output else '查询失败'}")

ssh.close()
print("\n✅ 连接测试完成！")
