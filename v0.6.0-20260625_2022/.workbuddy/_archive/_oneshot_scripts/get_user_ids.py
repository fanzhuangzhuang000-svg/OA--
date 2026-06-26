import paramiko, json, urllib.request

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 查实际 user id
sql = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c "SELECT id, username FROM users ORDER BY id;" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(sql)
print(stdout.read().decode())

ssh.close()
