import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 读取 .env 获取数据库密码
stdin, stdout, stderr = ssh.exec_command("cat /var/www/oa-api/.env | grep DB_PASSWORD")
db_pwd = stdout.read().decode().strip().split('=', 1)[1].strip().strip('"').strip("'")

# 在服务器上用 PHP 自身的 bcrypt 生成
stdin, stdout, stderr = ssh.exec_command("php -r \"echo password_hash('admin123', PASSWORD_BCRYPT);\" 2>&1")
hash_out = stdout.read().decode().strip()
print("Hash:", hash_out)

# 用 $$ ... $$ dollar quoting 避免引号问题
# 这样 psql 不会把 $ 误认为变量
sql = f"""UPDATE users SET password = $crypt${hash_out}$crypt$ WHERE username = 'admin';"""

# 把 SQL 写到 /tmp 然后用 psql -f 读文件
with open(r'D:\work\website\OA\.workbuddy\update.sql', 'w') as f:
    f.write(sql + '\n')

sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\.workbuddy\update.sql', '/tmp/update.sql')
sftp.close()

psql_cmd = f"export PGPASSWORD='{db_pwd}' && psql -U oa_user -d security_oa -f /tmp/update.sql 2>&1"
stdin, stdout, stderr = ssh.exec_command(psql_cmd)
print("\nUPDATE RESULT:")
print(stdout.read().decode())

# 验证
stdin2, stdout2, stderr2 = ssh.exec_command(f"export PGPASSWORD='{db_pwd}' && psql -U oa_user -d security_oa -c \"SELECT username, length(password) as pwd_len, substring(password,1,10) as prefix FROM users WHERE username = 'admin';\" 2>&1")
print("VERIFY:", stdout2.read().decode())

# 清理
stdin3, stdout3, stderr3 = ssh.exec_command('sudo rm /tmp/update.sql && sudo truncate -s 0 /var/www/oa-api/storage/logs/laravel.log')

ssh.close()
print("\n✅ DONE - 请用 admin / admin123 重新登录")
