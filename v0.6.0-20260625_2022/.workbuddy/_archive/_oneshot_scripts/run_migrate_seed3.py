import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 1) 直接 SQL ALTER 加 color 和 module/description 字段
sql = """
ALTER TABLE roles ADD COLUMN IF NOT EXISTS color VARCHAR(16) NULL DEFAULT '#0C447C' AFTER description;
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS module VARCHAR(64) NULL AFTER guard_name;
ALTER TABLE permissions ADD COLUMN IF NOT EXISTS description VARCHAR(255) NULL AFTER module;
ALTER TABLE permissions ADD INDEX IF NOT EXISTS idx_module (module);
"""
script = f"""#!/bin/bash
mysql -uoa_user -poa_password oa_db -e "{sql}" 2>&1 | grep -v Warning
"""
sftp = ssh.open_sftp()
with sftp.open('/tmp/alter.sh', 'w') as f:
    f.write(script)
sftp.chmod('/tmp/alter.sh', 0o755)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('bash /tmp/alter.sh')
print('ALTER:', stdout.read().decode())

# 2) 验证
stdin, stdout, stderr = ssh.exec_command('mysql -uoa_user -poa_password oa_db -e "DESCRIBE roles; SELECT \"---\" AS x; DESCRIBE permissions;" 2>&1 | grep -v Warning')
print(stdout.read().decode())

# 3) 跑 seeder
cmds = [
    'cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=PermissionRoleSeeder --force --no-interaction 2>&1 | tail -20',
    'mysql -uoa_user -poa_password oa_db -e "SELECT id,name,color,description FROM roles; SELECT \"---\" AS x; SELECT module,name,description FROM permissions LIMIT 10; SELECT \"---\" AS x; SELECT COUNT(*) AS perm_count FROM permissions; SELECT \"---\" AS x; SELECT COUNT(*) AS role_count FROM roles;" 2>&1 | grep -v Warning',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c, timeout=120)
    print(f'> {c[:80]}\n{stdout.read().decode()}')
    print(f'  ERR={stderr.read().decode().strip()}\n---')

ssh.close()
