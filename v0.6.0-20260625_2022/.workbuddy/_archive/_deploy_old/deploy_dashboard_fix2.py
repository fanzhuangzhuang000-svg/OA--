import paramiko
import os

# 连接服务器
print("Connecting to server...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

# 上传修改后的 DashboardController.php
print("Uploading DashboardController.php...")
sftp = ssh.open_sftp()
local_file = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\DashboardController.php'
remote_file = '/tmp/DashboardController.php'
sftp.put(local_file, remote_file)
sftp.close()
print("  Upload complete!")

# 复制到目标位置
print("Deploying to /var/www/oa-api...")
stdin, stdout, stderr = ssh.exec_command(
    f'sudo cp {remote_file} /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php && '
    f'sudo chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php && '
    f'sudo rm {remote_file}'
)
stdout.read()
err = stderr.read().decode()
if err:
    print(f"  Warning: {err}")

# 重启 PHP-FPM
print("Restarting PHP-FPM...")
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart php8.3-fpm')
stdout.read()
err = stderr.read().decode()
if err:
    print(f"  Restart warning: {err}")

print("\n✅ Backend deployed successfully!")
print("\nNext steps:")
print("1. Clear browser cache (Ctrl+F5)")
print("2. Login to the system")
print("3. Check if project progress data is now visible")
print("\nIf still not working, check browser console for API errors.")

ssh.close()
