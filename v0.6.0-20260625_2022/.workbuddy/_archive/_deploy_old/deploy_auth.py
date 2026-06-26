"""Deploy AuthController.php to server and test change-password endpoint"""
import paramiko, os, sys
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123')
sftp = ssh.open_sftp()

LOCAL  = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\AuthController.php'
REMOTE = '/var/www/oa-api/app/Http/Controllers/Api/AuthController.php'
# 把 owner 临时调回 nbcy 才能 sftp 写
si,so,se = ssh.exec_command('sudo chown nbcy:nbcy /var/www/oa-api/app/Http/Controllers/Api/AuthController.php 2>&1')
print('pre-chown:', so.read().decode().strip() or se.read().decode().strip())
sftp.put(LOCAL, REMOTE)
print('sftp put:', REMOTE, os.path.getsize(LOCAL), 'bytes')

# 同时上传 routes/api.php
ROUTES_LOCAL  = r'D:\work\website\OA\pc-api\routes\api.php'
ROUTES_REMOTE = '/var/www/oa-api/routes/api.php'
si,so,se = ssh.exec_command('sudo chown nbcy:nbcy /var/www/oa-api/routes/api.php 2>&1')
print('pre-chown routes:', so.read().decode().strip() or se.read().decode().strip())
sftp.put(ROUTES_LOCAL, ROUTES_REMOTE)
print('sftp put:', ROUTES_REMOTE, os.path.getsize(ROUTES_LOCAL), 'bytes')

# chown for PHP-FPM
si,so,se = ssh.exec_command('sudo chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/AuthController.php /var/www/oa-api/routes/api.php && echo OK_CHOWN')
print('chown:', so.read().decode().strip() or se.read().decode().strip())

# route:list
si,so,se = ssh.exec_command("cd /var/www/oa-api && php artisan route:list --path=auth 2>&1 | head -20")
print('--- route:list ---')
print(so.read().decode())
print(se.read().decode() or '')

# clear cache
si,so,se = ssh.exec_command("cd /var/www/oa-api && php artisan optimize:clear 2>&1 | tail -10")
print('--- optimize:clear ---')
print(so.read().decode())
print(se.read().decode() or '')

# restart fpm
si,so,se = ssh.exec_command("sudo systemctl restart php8.3-fpm && echo OK_FPM")
print('fpm:', so.read().decode().strip() or se.read().decode().strip())

sftp.close()
ssh.close()
