import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')
stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/oa-api/app/Http/Controllers/Api/ | head -3 && echo "---stat api dir---" && stat /var/www/oa-api/app/Http/Controllers/Api/')
print(stdout.read().decode())
ssh.close()
