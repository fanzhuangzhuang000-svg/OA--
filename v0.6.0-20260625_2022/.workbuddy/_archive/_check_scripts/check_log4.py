import paramiko, re
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')
# 看 :id 错误附近的 SQL 看是哪个表
stdin, stdout, stderr = ssh.exec_command('grep -B0 -A1 "invalid input syntax for type bigint: \":id\"" /var/www/oa-api/storage/logs/laravel.log | grep -oE "select \* from \"[^\"]+\"|select \"[^\"]+\"" | sort -u')
print("=== :id 表 ===")
print(stdout.read().decode('utf-8', errors='ignore'))
# NaN 的表
stdin, stdout, stderr = ssh.exec_command('grep -B0 -A1 "invalid input syntax for type bigint: \"NaN\"" /var/www/oa-api/storage/logs/laravel.log | grep -oE "select \* from \"[^\"]+\"|select \"[^\"]+\"" | sort -u')
print("\n=== NaN 表 ===")
print(stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
