import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 把所有 SQL 直接写到 .sql 文件（避免 shell quote 转义）
sql_content = r"""
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='roles' AND COLUMN_NAME='color') = 0,
    CONCAT('ALTER TABLE roles ADD COLUMN color VARCHAR(16) NULL DEFAULT ', 0x23304334343743, ' AFTER guard_name'),
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='permissions' AND COLUMN_NAME='module') = 0,
    'ALTER TABLE permissions ADD COLUMN module VARCHAR(64) NULL AFTER guard_name',
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='permissions' AND COLUMN_NAME='description') = 0,
    'ALTER TABLE permissions ADD COLUMN description VARCHAR(255) NULL AFTER module',
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='permissions' AND INDEX_NAME='idx_module') = 0,
    'ALTER TABLE permissions ADD INDEX idx_module (module)',
    'SELECT 1'
));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
"""

sftp = ssh.open_sftp()
with sftp.open('/tmp/alter3.sql', 'w') as f:
    f.write(sql_content)
sftp.chmod('/tmp/alter3.sql', 0o644)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db < /tmp/alter3.sql 2>&1 | grep -v Warning')
print('ALTER:', stdout.read().decode())

# 验证
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "DESCRIBE roles; SELECT CHAR(45,45,45) AS s; DESCRIBE permissions;" 2>&1 | grep -v Warning')
print(stdout.read().decode())
ssh.close()
