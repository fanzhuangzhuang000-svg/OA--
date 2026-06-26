import paramiko
ssh = paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=10)
cmd = 'curl -sk -X POST https://localhost/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\' -w "\\n%{http_code}"'
si,so,se = ssh.exec_command(cmd, timeout=15)
print(so.read().decode()[:500])
