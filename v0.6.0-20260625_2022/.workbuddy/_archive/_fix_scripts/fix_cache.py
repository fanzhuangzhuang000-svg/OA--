import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

sql = """
ALTER TABLE cache ADD COLUMN `key` VARCHAR(255) NOT NULL;
ALTER TABLE cache ADD COLUMN `value` TEXT NOT NULL;
ALTER TABLE cache ADD COLUMN `expiration` INT NULL;
ALTER TABLE cache ADD UNIQUE KEY cache_key_unique (`key`);
"""
sftp = ssh.open_sftp()
with sftp.open('/tmp/cache.sql', 'w') as f:
    f.write(sql)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db < /tmp/cache.sql 2>&1 | grep -v Warning')
print('ALTER:', stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "DESCRIBE cache;" 2>&1 | grep -v Warning')
print(stdout.read().decode())
ssh.close()
