import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 用 nbcy 身份 chown（nbcy 是 owner）→ 改 Api/ 为 www-data:www-data
cmds = [
    'sudo chown -R www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/',
    'ls -la /var/www/oa-api/app/Http/Controllers/Api/ | head -3',
    'sudo -u www-data cp /tmp/c1_RoleController.php /var/www/oa-api/app/Http/Controllers/Api/RoleController.php',
    'ls -la /var/www/oa-api/app/Http/Controllers/Api/RoleController.php',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f'> {c}\n  {out} {err}')

ssh.close()
