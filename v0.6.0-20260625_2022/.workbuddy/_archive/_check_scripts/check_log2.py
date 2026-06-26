import paramiko, re
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
# 找最近的所有错误
stdin, stdout, stderr = ssh.exec_command('grep -E "production.ERROR|production\\[" /var/www/oa-api/storage/logs/laravel.log | tail -30')
print("=== errors (last 30) ===")
print(stdout.read().decode('utf-8', errors='ignore'))
# 找 :id 相关
stdin, stdout, stderr = ssh.exec_command('grep -B1 -A2 "ImplicitRouteBinding\\|:id\\|Invalid text representation" /var/www/oa-api/storage/logs/laravel.log | head -40')
print("\n=== :id related ===")
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
