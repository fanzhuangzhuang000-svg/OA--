import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 删 id=1 的重复超管
sql = """DELETE FROM role_has_permissions WHERE role_id=1;
DELETE FROM model_has_roles WHERE role_id=1;
DELETE FROM roles WHERE id=1;
ALTER TABLE roles AUTO_INCREMENT=1;
"""
sftp = ssh.open_sftp()
with sftp.open('/tmp/cleanup.sql', 'w') as f:
    f.write(sql)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db < /tmp/cleanup.sql 2>&1 | grep -v Warning')
print('CLEANUP:', stdout.read().decode())

# verify
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "SELECT id,name FROM roles ORDER BY id;" 2>&1 | grep -v Warning')
print(stdout.read().decode())
ssh.close()
