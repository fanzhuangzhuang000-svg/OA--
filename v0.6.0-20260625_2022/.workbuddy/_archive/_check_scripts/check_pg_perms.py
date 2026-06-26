import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 检查 nbcy 能不能 sudo 到 postgres
stdin, stdout, stderr = ssh.exec_command("sudo -l -U postgres 2>&1 | head -5")
print("nbcy sudo perms for postgres:", stdout.read().decode().strip())

# 试试 sudo -u postgres psql
stdin, stdout, stderr = ssh.exec_command("sudo -u postgres psql -c 'SELECT version();' 2>&1 | head -3")
out = stdout.read().decode()
err = stderr.read().decode()
print("\npostgres access test:")
print(out)
if err.strip():
    print("STDERR:", err[:300])

ssh.close()
