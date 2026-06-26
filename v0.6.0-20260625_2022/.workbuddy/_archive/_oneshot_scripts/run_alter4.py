import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# permissions 部分单独跑
sql_content = r"""
ALTER TABLE permissions ADD COLUMN module VARCHAR(64) NULL AFTER guard_name;
ALTER TABLE permissions ADD COLUMN description VARCHAR(255) NULL AFTER module;
ALTER TABLE permissions ADD INDEX idx_module (module);
"""

sftp = ssh.open_sftp()
with sftp.open('/tmp/alter5.sql', 'w') as f:
    f.write(sql_content)
sftp.chmod('/tmp/alter5.sql', 0o644)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db < /tmp/alter5.sql 2>&1')
print('ALTER:', stdout.read().decode())

# 验证
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "DESCRIBE permissions;" 2>&1')
print('PERMS:', stdout.read().decode())
ssh.close()
