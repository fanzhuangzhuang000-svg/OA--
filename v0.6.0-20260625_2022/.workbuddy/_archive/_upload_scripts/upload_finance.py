"""Upload FinanceController fix to 152 server"""
import paramiko
import os

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'

# 读取本地文件
with open(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\FinanceController.php', 'r') as f:
    content = f.read()

# 写入临时文件
temp_path = r'D:\work\website\OA\temp_finance_controller.php'
with open(temp_path, 'w') as f:
    f.write(content)

# SSH连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)

# 上传到tmp
sftp = ssh.open_sftp()
sftp.put(temp_path, '/tmp/FinanceController.php')
sftp.close()

# 用sudo移动到目标位置
ssh.exec_command('sudo mv /tmp/FinanceController.php /var/www/oa-api/app/Http/Controllers/Api/FinanceController.php')
ssh.exec_command('sudo chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/FinanceController.php')
ssh.exec_command('sudo chmod 644 /var/www/oa-api/app/Http/Controllers/Api/FinanceController.php')

# 验证
stdin, stdout, stderr = ssh.exec_command('grep -c "transfer_date" /var/www/oa-api/app/Http/Controllers/Api/FinanceController.php')
print('transfer_date出现次数:', stdout.read().decode().strip())

ssh.close()
os.remove(temp_path)
print('✅ 文件已更新')