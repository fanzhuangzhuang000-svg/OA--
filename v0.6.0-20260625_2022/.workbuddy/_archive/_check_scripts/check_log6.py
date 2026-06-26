import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
# 看 :id 错误前后 8 行
stdin, stdout, stderr = ssh.exec_command('grep -B2 -A10 "invalid input syntax for type bigint: .:id" /var/www/oa-api/storage/logs/laravel.log | tail -80')
print("=== :id 错误上下文 ===")
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
