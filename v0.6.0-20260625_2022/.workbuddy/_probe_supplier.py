import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.3.117', username='nbcy', password='admin123', timeout=10)
def run(c, t=15):
    si, so, se = ssh.exec_command(c, timeout=t)
    return so.read().decode('utf-8', 'replace').strip()
sql = "SELECT id, name, phone FROM suppliers WHERE phone IS NOT NULL AND phone != '' LIMIT 3"
print(run(f"""PGPASSWORD=postgres123 psql -h 127.0.0.1 -U postgres -d oa -c "{sql}" """))
ssh.close()
