"""验证 idle keys"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=10)
cmd = "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c \"SELECT key, value::text FROM system_settings WHERE key LIKE 'idle%' ORDER BY key;\""
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())
ssh.close()
