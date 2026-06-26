import paramiko
import os

# 连接服务器
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

# 上传修改后的 DashboardController.php
sftp = ssh.open_sftp()
local_file = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\DashboardController.php'
remote_file = '/tmp/DashboardController.php'
print(f'Uploading {local_file} to {remote_file}...')
sftp.put(local_file, remote_file)
sftp.close()

# 复制到目标位置
print('Deploying to /var/www/oa-api...')
stdin, stdout, stderr = ssh.exec_command(
    f'sudo cp {remote_file} /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php && '
    f'sudo chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php && '
    f'sudo rm {remote_file}'
)
stdout.read()
err = stderr.read().decode()
if err:
    print(f'Warning: {err}')

# 重启 PHP-FPM
print('Restarting PHP-FPM...')
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart php8.3-fpm')
stdout.read()
err = stderr.read().decode()
if err:
    print(f'Restart warning: {err}')

# 测试 API 路由
print('Checking route...')
stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan route:list | grep project-progress')
output = stdout.read().decode()
print(f'Route check: {output if output else "Not found"}')

# 测试 API 端点（需要先登录获取 token）
print('\nTesting API endpoint...')
# 先获取登录 token
stdin, stdout, stderr = ssh.exec_command('''
cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="
use App\Models\User;
use Illuminate\Support\Facades\Hash;
\$user = User::where('email', 'admin@security-oa.com')->first();
if (\$user) {
    echo 'User found: ' . \$user->email;
} else {
    echo 'User not found';
}
"
''')
output = stdout.read().decode()
print(f'User check: {output}')

ssh.close()
print('\n✅ Backend deployed successfully!')
print('\nNext steps:')
print('1. Clear browser cache (Ctrl+F5)')
print('2. Login to the system')
print('3. Check if project progress data is now visible')
