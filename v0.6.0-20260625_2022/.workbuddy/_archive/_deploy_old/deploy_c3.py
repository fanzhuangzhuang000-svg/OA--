import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')
sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\DashboardController.php', '/tmp/c3_dashboard.php')
sftp.put(r'D:\work\website\OA\pc-api\routes\api.php', '/tmp/c3_api.php')
sftp.close()

cmds = [
    'sudo -u www-data cp /tmp/c3_dashboard.php /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php',
    'sudo -u www-data cp /tmp/c3_api.php /var/www/oa-api/routes/api.php',
    'sudo chown -R www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php /var/www/oa-api/routes/api.php',
    'cd /var/www/oa-api && sudo -u www-data php artisan optimize:clear 2>&1 | tail -3',
    'cd /var/www/oa-api && sudo -u www-data php artisan route:list 2>&1 | grep screen',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c, timeout=60)
    print(f'> {c[:60]}')
    print(stdout.read().decode())
    err = stderr.read().decode().strip()
    if err: print(f'  ERR: {err}')
ssh.close()
