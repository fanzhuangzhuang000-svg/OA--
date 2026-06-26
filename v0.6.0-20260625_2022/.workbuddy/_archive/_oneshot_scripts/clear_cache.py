import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 清全部缓存
cmds = [
    'cd /var/www/oa-api && sudo -u www-data php artisan optimize:clear 2>&1',
    'cd /var/www/oa-api && sudo -u www-data php artisan config:clear 2>&1',
    'cd /var/www/oa-api && sudo -u www-data php artisan route:clear 2>&1',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c, timeout=60)
    print(stdout.read().decode())

# 重启 php-fpm 让 opcache 彻底清
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1')
print('fpm restart:', stdout.read().decode(), stderr.read().decode().strip())

ssh.close()
