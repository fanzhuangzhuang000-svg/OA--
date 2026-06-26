import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 读取 .env 获取数据库密码
stdin, stdout, stderr = ssh.exec_command("cat /var/www/oa-api/.env | grep DB_PASSWORD")
db_pwd_line = stdout.read().decode().strip()
db_pwd = db_pwd_line.split('=', 1)[1].strip().strip('"').strip("'")
print("DB Password length:", len(db_pwd))

# 在服务器上用 PHP 自身的 bcrypt 生成（保证格式正确）
# 用 ssh.exec_command 跑一行 PHP
php_cmd = """php -r "echo password_hash('admin123', PASSWORD_BCRYPT);" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(php_cmd)
hash_out = stdout.read().decode().strip()
print("Server bcrypt hash:", hash_out[:30] + "...")
print("Hash length:", len(hash_out))

# 验证哈希是否以 $2y$ 开头（Laravel bcrypt 格式）
if not hash_out.startswith('$2y$'):
    print("WARN: hash does not start with $2y$!")

# 用 psql UPDATE 密码
psql_cmd = f"""export PGPASSWORD='{db_pwd}' && psql -U oa_user -d security_oa -c "UPDATE users SET password = '{hash_out}' WHERE username = 'admin';" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(psql_cmd)
print("\nUPDATE RESULT:")
print(stdout.read().decode())

# 验证
stdin2, stdout2, stderr2 = ssh.exec_command(f"export PGPASSWORD='{db_pwd}' && psql -U oa_user -d security_oa -c \"SELECT username, password FROM users WHERE username = 'admin';\" 2>&1")
print("VERIFY:", stdout2.read().decode())

# 清空日志，让用户重新测试
stdin3, stdout3, stderr3 = ssh.exec_command('sudo truncate -s 0 /var/www/oa-api/storage/logs/laravel.log')
print("LOG CLEARED")

ssh.close()
print("\n✅ DONE - 请用 admin / admin123 重新登录")
