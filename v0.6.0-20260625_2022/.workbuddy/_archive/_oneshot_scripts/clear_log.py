import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 清空日志，让用户重新登录后再查最新错误
stdin, stdout, stderr = ssh.exec_command('sudo truncate -s 0 /var/www/oa-api/storage/logs/laravel.log && echo "log cleared"')
print("CLEAR:", stdout.read().decode())

ssh.close()
