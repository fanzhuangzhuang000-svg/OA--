import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 检查前端文件
print("=" * 60)
print("1. 检查前端部署状态")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/oa-web/ | head -20")
print(stdout.read().decode())

# 2. 检查 index.html 时间戳
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/oa-web/index.html")
print(stdout.read().decode())

# 3. 测试 API 端点
print("=" * 60)
print("2. 测试 API 端点")
print("=" * 60)
endpoints = [
    "/api/auth/login",
    "/api/dashboard/stats",
    "/api/dashboard/project-progress",
    "/api/dashboard/revenue-trend",
    "/api/dashboard/service-stats",
    "/api/dashboard/todo",
]
for ep in endpoints:
    stdin, stdout, stderr = ssh.exec_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost{ep}")
    code = stdout.read().decode().strip()
    print(f"  {code}  {ep}")

# 4. 检查 PHP-FPM 状态
print("=" * 60)
print("3. 检查 PHP-FPM 状态")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("systemctl status php8.3-fpm --no-pager | head -10")
print(stdout.read().decode())

# 5. 检查 nginx
print("=" * 60)
print("4. 检查 nginx 状态")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("systemctl status nginx --no-pager | head -10")
print(stdout.read().decode())

ssh.close()
print("done")
