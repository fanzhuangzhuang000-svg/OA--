import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

cmds = [
    'sudo -u www-data mkdir -p /var/www/oa-api/app/Observers',
    'sudo -u www-data cp /tmp/c2_AuditObserver.php /var/www/oa-api/app/Observers/AuditObserver.php',
    'sudo chown -R www-data:www-data /var/www/oa-api/app/Observers',
    'ls -la /var/www/oa-api/app/Observers/',
    # 验证
    'cd /var/www/oa-api && sudo -u www-data php artisan optimize:clear 2>&1 | tail -3',
    'cd /var/www/oa-api && sudo -u www-data php artisan route:list 2>&1 | grep audit',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c, timeout=60)
    print(f'> {c[:60]}')
    print(stdout.read().decode())
    err = stderr.read().decode().strip()
    if err: print(f'  ERR: {err}')
    print('---')
ssh.close()
