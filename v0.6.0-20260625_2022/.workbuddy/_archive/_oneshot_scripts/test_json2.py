import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 直接用 stdin 传 -c 命令避免引号问题
PG = "export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa"

# 用 heredoc
sql = """DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..4 LOOP
        INSERT INTO disk_settings (key, value, created_at, updated_at)
        VALUES ('user_quota_' || i::text, json_build_object('quota', 1073741824, 'used', 100000), NOW(), NOW());
    END LOOP;
END $$;"""

# 写到 /tmp 然后 psql -f
with open(r'D:\work\website\OA\.workbuddy\disk_fix.sql', 'w') as f:
    f.write(sql)

sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\.workbuddy\disk_fix.sql', '/tmp/disk_fix.sql')
sftp.close()

stdin, stdout, stderr = ssh.exec_command(f'{PG} -f /tmp/disk_fix.sql 2>&1')
print(stdout.read().decode())
err = stderr.read().decode()
if err: print('STDERR:', err[:500])

# 验证
stdin, stdout, stderr = ssh.exec_command(f"{PG} -t -A -c \"SELECT count(*) FROM disk_settings;\"")
print('count:', stdout.read().decode().strip())

ssh.close()
