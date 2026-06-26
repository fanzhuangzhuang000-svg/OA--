import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 读取 .env 获取数据库密码
stdin, stdout, stderr = ssh.exec_command("cat /var/www/oa-api/.env | grep DB_PASSWORD")
env_out = stdout.read().decode().strip()
print("DB_PASSWORD line:", env_out)

# 提取密码（去掉 DB_PASSWORD= 前缀）
db_pwd = env_out.split('=', 1)[1].strip().strip('"').strip("'")
print("DB Password length:", len(db_pwd))

# 用 psql 直接更新密码（用刚才生成的 bcrypt 哈希）
bcrypt_hash = "$2y$10$Wk1wbZmC.fHeJlyn6oMKJeh.vIO/SXzxshGtKnf9pQWadZBuBAWKS"

# 注意：哈希中有 $ 符号，需要转义
psql_cmd = f"""psql -U oa_user -d security_oa -c "UPDATE users SET password = '{bcrypt_hash}' WHERE username = 'admin';" 2>&1"""

stdin, stdout, stderr = ssh.exec_command(f"export PGPASSWORD='{db_pwd}' && {psql_cmd}")
out = stdout.read().decode()
err = stderr.read().decode()
print("UPDATE RESULT:")
print(out)
if err.strip():
    print("STDERR:", err[:500])

# 验证
stdin2, stdout2, stderr2 = ssh.exec_command(f"export PGPASSWORD='{db_pwd}' && psql -U oa_user -d security_oa -c \"SELECT username, substring(password,1,20) as pwd FROM users WHERE username = 'admin';\" 2>&1")
print("VERIFY:", stdout2.read().decode())

ssh.close()
print("done")
