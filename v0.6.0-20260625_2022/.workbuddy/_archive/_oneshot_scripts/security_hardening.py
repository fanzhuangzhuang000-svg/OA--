import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

print("=" * 60)
print("A1. .env 权限收紧")
print("=" * 60)

# 1. 收紧 .env 权限
stdin, stdout, stderr = ssh.exec_command(
    "ls -la /var/www/oa-api/.env"
)
print("Before:", stdout.read().decode().strip())

stdin, stdout, stderr = ssh.exec_command(
    "sudo chmod 600 /var/www/oa-api/.env && sudo chown www-data:www-data /var/www/oa-api/.env"
)
stdout.read()
err = stderr.read().decode()
if err.strip():
    print(f"  warning: {err[:200]}")

stdin, stdout, stderr = ssh.exec_command(
    "ls -la /var/www/oa-api/.env"
)
print("After: ", stdout.read().decode().strip())

# 验证 nbcy 还能不能读
stdin, stdout, stderr = ssh.exec_command(
    "cat /var/www/oa-api/.env 2>&1 | head -3"
)
out = stdout.read().decode()
print(f"nbcy read test: {'OK (可读)' if 'APP_NAME' in out else 'BLOCKED (已锁定)'}")

print()
print("=" * 60)
print("A2. 创建 read-only 数据库账号")
print("=" * 60)

# 读 .env 拿密码（用 www-data 权限或者临时改回 600 跑一次）
# 现在 nbcy 读不了了，用 sudo 帮忙读
stdin, stdout, stderr = ssh.exec_command(
    "sudo grep DB_ /var/www/oa-api/.env | grep -v DB_CONNECTION"
)
db_info = stdout.read().decode()
print("DB config:")
for line in db_info.split('\n'):
    if line.strip():
        print(f"  {line}")

# 创建 read-only 用户
# 用 plsql 内部函数读密码不现实，改用 sudo 让 php 读 .env
create_sql = """
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'oa_reader') THEN
      CREATE ROLE oa_reader LOGIN PASSWORD 'oa_reader_readonly_782997781';
   END IF;
END
$$;

GRANT CONNECT ON DATABASE security_oa TO oa_reader;
GRANT USAGE ON SCHEMA public TO oa_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oa_reader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO oa_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO oa_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO oa_reader;
"""

# 写到 /tmp，pg_dump 风格用 psql -f
with open(r'D:\work\website\OA\.workbuddy\create_reader.sql', 'w') as f:
    f.write(create_sql)

sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\.workbuddy\create_reader.sql', '/tmp/create_reader.sql')
sftp.close()

# 用 oa_user 跑（它有 CREATE ROLE 权限）
stdin, stdout, stderr = ssh.exec_command(
    "export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -f /tmp/create_reader.sql 2>&1"
)
out = stdout.read().decode()
err = stderr.read().decode()
print("\nCreate reader output:")
print(out)
if err.strip() and 'NOTICE' not in err:
    print("STDERR:", err[:500])

# 验证 read-only 账号能登录
stdin, stdout, stderr = ssh.exec_command(
    "export PGPASSWORD='oa_reader_readonly_782997781' && "
    "psql -U oa_reader -d security_oa -c 'SELECT count(*) FROM users;' 2>&1"
)
print("\nRead-only test:")
print(stdout.read().decode())

# 验证不能写
stdin, stdout, stderr = ssh.exec_command(
    "export PGPASSWORD='oa_reader_readonly_782997781' && "
    "psql -U oa_reader -d security_oa -c \"UPDATE users SET password = 'hacked' WHERE username = 'admin';\" 2>&1"
)
out = stdout.read().decode()
err = stderr.read().decode()
print("\nWrite attempt (should fail):")
print(out)
if err.strip():
    print("STDERR:", err[:300])

# 清理
stdin, stdout, stderr = ssh.exec_command("rm /tmp/create_reader.sql")
stdout.read()

ssh.close()
print("\n=== done ===")
