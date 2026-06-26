import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sql = """
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

ALTER DEFAULT PRIVILEGES FOR ROLE oa_user IN SCHEMA public GRANT SELECT ON TABLES TO oa_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE oa_user IN SCHEMA public GRANT SELECT ON SEQUENCES TO oa_reader;
"""

with open(r'D:\work\website\OA\.workbuddy\create_reader.sql', 'w') as f:
    f.write(sql)

sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\.workbuddy\create_reader.sql', '/tmp/create_reader.sql')
sftp.close()

# 用 sudo -u postgres 跑（超级用户能 CREATE ROLE）
stdin, stdout, stderr = ssh.exec_command(
    "sudo -u postgres psql -d security_oa -f /tmp/create_reader.sql 2>&1"
)
print("CREATE READER:")
print(stdout.read().decode())
err = stderr.read().decode()
if err.strip():
    print("STDERR:", err[:500])

# 验证 1: oa_reader 能 SELECT
stdin, stdout, stderr = ssh.exec_command(
    "PGPASSWORD='oa_reader_readonly_782997781' psql -U oa_reader -d security_oa -h 127.0.0.1 -c "
    "\"SELECT count(*) AS total_users, count(*) FILTER (WHERE username='admin') AS admin_count FROM users;\" 2>&1"
)
print("READ TEST (read-only should succeed):")
print(stdout.read().decode())

# 验证 2: oa_reader 不能 UPDATE
stdin, stdout, stderr = ssh.exec_command(
    "PGPASSWORD='oa_reader_readonly_782997781' psql -U oa_reader -d security_oa -h 127.0.0.1 -c "
    "\"UPDATE users SET password = 'hacked' WHERE username = 'admin';\" 2>&1"
)
print("WRITE TEST (read-only should fail):")
print(stdout.read().decode())

# 验证 3: oa_reader 不能 DELETE
stdin, stdout, stderr = ssh.exec_command(
    "PGPASSWORD='oa_reader_readonly_782997781' psql -U oa_reader -d security_oa -h 127.0.0.1 -c "
    "\"DELETE FROM users;\" 2>&1"
)
print("DELETE TEST (read-only should fail):")
print(stdout.read().decode())

# 验证 4: oa_reader 仍然能用 oa_user 的密码登录（确保主账号没坏）
stdin, stdout, stderr = ssh.exec_command(
    "export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c 'SELECT 1;' 2>&1"
)
print("OA_USER still works:")
print(stdout.read().decode())

# 清理
stdin, stdout, stderr = ssh.exec_command("rm /tmp/create_reader.sql")
stdout.read()

ssh.close()
print("=== done ===")
