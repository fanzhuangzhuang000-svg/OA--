import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 重新部署 AppServiceProvider
sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\pc-api\app\Providers\AppServiceProvider.php', '/tmp/c2_provider.php')
sftp.close()
cmd = 'sudo -u www-data cp /tmp/c2_provider.php /var/www/oa-api/app/Providers/AppServiceProvider.php && echo OK'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('COPY:', stdout.read().decode(), stderr.read().decode().strip())

# 验证 routes
cmd = 'cd /var/www/oa-api && sudo -u www-data php artisan optimize:clear 2>&1 | tail -3 && sudo -u www-data php artisan route:list 2>&1 | grep audit'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
print('ROUTES:', stdout.read().decode())

ssh.close()
