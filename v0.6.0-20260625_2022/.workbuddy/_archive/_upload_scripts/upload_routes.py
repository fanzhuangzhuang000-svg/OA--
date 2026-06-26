"""Upload routes/api.php to 152 server"""
import paramiko
import os

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'

# 读取本地文件
with open(r'D:\work\website\OA\pc-api\routes\api.php', 'r') as f:
    content = f.read()

# 写入临时文件
temp_path = r'D:\work\website\OA\temp_api.php'
with open(temp_path, 'w') as f:
    f.write(content)

# SSH连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)

# 上传到tmp
sftp = ssh.open_sftp()
sftp.put(temp_path, '/tmp/api.php')
sftp.close()

# 用sudo移动到目标位置
ssh.exec_command('sudo mv /tmp/api.php /var/www/oa-api/routes/api.php')
ssh.exec_command('sudo chown www-data:www-data /var/www/oa-api/routes/api.php')
ssh.exec_command('sudo chmod 644 /var/www/oa-api/routes/api.php')

# 清理缓存并验证
ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan route:clear')
stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan route:list | grep accounts')
print('accounts路由:', stdout.read().decode().strip())

ssh.close()
os.remove(temp_path)
print('✅ 路由已更新')