import paramiko, sys
table = sys.argv[1] if len(sys.argv) > 1 else 'projects'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.3.117', port=22, username='nbcy', password='admin123', timeout=20)
sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='{table}' ORDER BY ordinal_position"
cmd = f'sudo -n -u postgres psql -d security_oa -c "{sql}"'
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())
ssh.close()
