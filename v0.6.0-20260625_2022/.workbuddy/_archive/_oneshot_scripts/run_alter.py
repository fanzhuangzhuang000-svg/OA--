import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 1) 分步 ALTER（先查列再决定加不加）
sql = """
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='roles' AND COLUMN_NAME='color') = 0,
    'ALTER TABLE roles ADD COLUMN color VARCHAR(16) NULL DEFAULT "#0C447C" AFTER guard_name',
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='permissions' AND COLUMN_NAME='module') = 0,
    'ALTER TABLE permissions ADD COLUMN module VARCHAR(64) NULL AFTER guard_name',
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='permissions' AND COLUMN_NAME='description') = 0,
    'ALTER TABLE permissions ADD COLUMN description VARCHAR(255) NULL AFTER module',
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='permissions' AND INDEX_NAME='idx_module') = 0,
    'ALTER TABLE permissions ADD INDEX idx_module (module)',
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
"""
script = f"""#!/bin/bash
mysql -uoa_user -poa_password oa_db -e "{sql}" 2>&1 | grep -v Warning
"""
sftp = ssh.open_sftp()
with sftp.open('/tmp/alter2.sh', 'w') as f:
    f.write(script)
sftp.chmod('/tmp/alter2.sh', 0o755)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('bash /tmp/alter2.sh')
print('ALTER:', stdout.read().decode())

# 验证
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "DESCRIBE roles; SELECT \"---\" AS x; DESCRIBE permissions;" 2>&1 | grep -v Warning')
print(stdout.read().decode())

ssh.close()
