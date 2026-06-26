import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 查 bootstrap/providers.php
stdin, stdout, stderr = ssh.exec_command('cat /var/www/oa-api/bootstrap/providers.php 2>/dev/null || echo NOT_FOUND')
print("--- bootstrap/providers.php ---")
print(stdout.read().decode())

# 查 config/app.php 的 providers
print("\n--- config/app.php providers section ---")
stdin, stdout, stderr = ssh.exec_command("grep -A 30 'providers' /var/www/oa-api/config/app.php | head -60")
print(stdout.read().decode())

# 实际路由错误信息
print("\n--- actual error message in log ---")
stdin, stdout, stderr = ssh.exec_command("sudo grep -E 'production\\]\\.ERROR|exception' /var/www/oa-api/storage/logs/laravel.log | head -10")
print(stdout.read().decode()[-2500:])

# 是否能列出 route
print("\n--- route:list first 5 lines ---")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan route:list 2>&1 | head -10')
print(stdout.read().decode()[:1500])

ssh.close()
