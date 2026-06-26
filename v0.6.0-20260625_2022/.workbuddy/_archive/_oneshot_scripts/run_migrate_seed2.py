import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

cmds = [
    'cd /var/www/oa-api && sudo -u www-data php artisan migrate --force --no-interaction 2>&1 | tail -15',
    'cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=PermissionRoleSeeder --force --no-interaction 2>&1 | tail -15',
    'mysql -uoa_user -poa_password oa_db -e "DESCRIBE roles; SELECT \"---\" AS s; SELECT id,name,color,description FROM roles; SELECT \"---\" AS s; SELECT COUNT(*) AS perm_count FROM permissions;" 2>&1 | grep -v Warning',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c, timeout=120)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f'> {c[:80]}\n{out}\nERR={err}\n---')

ssh.close()
