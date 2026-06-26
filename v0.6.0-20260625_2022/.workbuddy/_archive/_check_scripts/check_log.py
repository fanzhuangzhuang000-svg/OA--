import paramiko

# 连接服务器
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

# 检查 Laravel 日志
print("Checking Laravel log for errors...")
stdin, stdout, stderr = ssh.exec_command('sudo tail -100 /var/www/oa-api/storage/logs/laravel.log | grep -A 20 "project-progress" || sudo tail -50 /var/www/oa-api/storage/logs/laravel.log')
output = stdout.read().decode()
err = stderr.read().decode()

if output:
    print("Log output:")
    print(output)
else:
    print("No specific project-progress error found, showing last 50 lines:")
    stdin, stdout, stderr = ssh.exec_command('sudo tail -50 /var/www/oa-api/storage/logs/laravel.log')
    output = stdout.read().decode()
    print(output)

if err:
    print(f"Error: {err}")

ssh.close()
