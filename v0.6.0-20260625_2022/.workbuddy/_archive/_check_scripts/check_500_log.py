import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 查最近 100 行日志
stdin, stdout, stderr = ssh.exec_command('sudo tail -100 /var/www/oa-api/storage/logs/laravel.log')
log = stdout.read().decode()
err = stderr.read().decode()

# 输出全文（最近的错误）
print("=" * 60)
print("LARAVEL LOG (last 4000 chars):")
print(log[-4000:] if log else "EMPTY")
if err.strip():
    print("STDERR:", err[:500])

# 同时查 nginx 错误日志
print("\n" + "=" * 60)
print("NGINX ERROR LOG (last 30 lines):")
stdin2, stdout2, stderr2 = ssh.exec_command('sudo tail -30 /var/log/nginx/error.log 2>/dev/null || echo "no nginx log"')
print(stdout2.read().decode()[-2000:])

ssh.close()
