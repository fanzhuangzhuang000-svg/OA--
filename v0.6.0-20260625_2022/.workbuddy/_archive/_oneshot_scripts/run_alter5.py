import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

sql = "ALTER TABLE roles ADD COLUMN description TEXT NULL AFTER guard_name;\n"
sftp = ssh.open_sftp()
with sftp.open('/tmp/alter6.sql', 'w') as f:
    f.write(sql)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db < /tmp/alter6.sql 2>&1 | grep -v Warning')
print('ALTER:', stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "DESCRIBE roles;" 2>&1 | grep -v Warning')
print(stdout.read().decode())

ssh.close()
