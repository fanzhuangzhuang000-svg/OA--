import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

cmd = 'mysql -uoa_user -poa_password oa_db -e "SHOW TABLES; DESCRIBE cache;" 2>&1 | grep -v Warning'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
ssh.close()
