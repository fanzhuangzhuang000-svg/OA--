"""Deploy C2 backend (3 files)"""
import paramiko, os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')
sftp = ssh.open_sftp()

files = [
    (r'D:\work\website\OA\pc-api\app\Observers\AuditObserver.php', 'app/Observers/AuditObserver.php'),
    (r'D:\work\website\OA\pc-api\app\Providers\AppServiceProvider.php', 'app/Providers/AppServiceProvider.php'),
    (r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\AuditController.php', 'app/Http/Controllers/Api/AuditController.php'),
    (r'D:\work\website\OA\pc-api\routes\api.php', 'routes/api.php'),
]
for src, dst in files:
    sftp.put(src, f'/tmp/c2_{os.path.basename(dst)}')
    cmd = f'sudo -u www-data cp /tmp/c2_{os.path.basename(dst)} /var/www/oa-api/{dst} && sudo chown www-data:www-data /var/www/oa-api/{dst} && echo OK'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(f'{dst}: {stdout.read().decode().strip()} {stderr.read().decode().strip()}')

# 验证 routes 注册
cmd = 'cd /var/www/oa-api && sudo -u www-data php artisan optimize:clear 2>&1 | tail -3 && sudo -u www-data php artisan route:list 2>&1 | grep audit'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
print('ROUTES:', stdout.read().decode())
sftp.close()
ssh.close()
