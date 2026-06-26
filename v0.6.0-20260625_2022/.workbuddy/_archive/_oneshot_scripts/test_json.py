"""dump disk_settings 错"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

cmd = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c "INSERT INTO disk_settings (key, value, created_at, updated_at) VALUES ('test_xxx', '{\"quota\":1073741824,\"used\":100000}'::json, NOW(), NOW()) RETURNING *;" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print('STDERR:', err[:500])
ssh.close()
