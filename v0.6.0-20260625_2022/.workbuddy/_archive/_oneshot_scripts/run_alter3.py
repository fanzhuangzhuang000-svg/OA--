import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 简单粗暴：直接 ALTER，错误就忽略
sql_content = r"""
ALTER TABLE roles ADD COLUMN color VARCHAR(16) NULL DEFAULT '#0C447C' AFTER guard_name;
ALTER TABLE permissions ADD COLUMN module VARCHAR(64) NULL AFTER guard_name;
ALTER TABLE permissions ADD COLUMN description VARCHAR(255) NULL AFTER module;
ALTER TABLE permissions ADD INDEX idx_module (module);
"""

sftp = ssh.open_sftp()
with sftp.open('/tmp/alter4.sql', 'w') as f:
    f.write(sql_content)
sftp.chmod('/tmp/alter4.sql', 0o644)
sftp.close()

# 用 --force 强制 + verbose 看错误
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password -f oa_db < /tmp/alter4.sql 2>&1 | grep -v Warning')
print('ALTER:', stdout.read().decode())

# 验证
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "DESCRIBE roles; SELECT \"---\" AS s; DESCRIBE permissions;" 2>&1 | grep -v Warning')
print(stdout.read().decode())
ssh.close()
