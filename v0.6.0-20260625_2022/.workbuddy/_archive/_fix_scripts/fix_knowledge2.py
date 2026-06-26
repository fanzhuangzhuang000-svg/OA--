import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
sftp = ssh.open_sftp()
sftp.put('D:/work/website/OA/.workbuddy/OtherModels.php', '/tmp/OtherModels.php')
sftp.close()
# sudo 移动到正确位置 + 改 owner
cmd = 'sudo mv /tmp/OtherModels.php /var/www/oa-api/app/Models/OtherModels.php && sudo chown www-data:www-data /var/www/oa-api/app/Models/OtherModels.php'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('mv:', stdout.read().decode('utf-8', errors='ignore'), stderr.read().decode('utf-8', errors='ignore'))
# 验证
stdin, stdout, stderr = ssh.exec_command('sudo grep -A1 "function articles" /var/www/oa-api/app/Models/OtherModels.php')
print('verify:', stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
