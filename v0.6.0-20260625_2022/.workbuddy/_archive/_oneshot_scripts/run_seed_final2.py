import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

cmds = [
    'cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=PermissionRoleSeeder --force --no-interaction 2>&1 | tail -20',
    'mysql -uoa_user -poa_password oa_db -e "SELECT id,name,color,description FROM roles; SELECT CHAR(45,45,45) AS s; SELECT module,description FROM permissions LIMIT 12; SELECT CHAR(45,45,45) AS s; SELECT COUNT(*) AS perms FROM permissions; SELECT CHAR(45,45,45) AS s; SELECT COUNT(*) AS roles_cnt FROM roles; SELECT CHAR(45,45,45) AS s; SELECT r.name AS role, COUNT(rp.permission_id) AS perm_cnt FROM roles r LEFT JOIN role_has_permissions rp ON rp.role_id=r.id GROUP BY r.id, r.name;" 2>&1 | grep -v Warning',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c, timeout=120)
    print(f'> {c[:80]}')
    print(stdout.read().decode())
    err = stderr.read().decode().strip()
    if err: print(f'  ERR: {err}')
    print('---')

ssh.close()
