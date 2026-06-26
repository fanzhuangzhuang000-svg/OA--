import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')
stdin, stdout, stderr = ssh.exec_command('id www-data && id nbcy && groups www-data && groups nbcy')
print(stdout.read().decode())
ssh.close()
