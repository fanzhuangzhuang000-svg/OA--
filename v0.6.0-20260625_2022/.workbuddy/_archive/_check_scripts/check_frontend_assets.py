import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 看前端构建出的 dashboard 路由对应 JS
print("=" * 60)
print("1. 前端 assets 中的 dashboard 相关 JS")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/oa-web/assets/ | grep -iE 'dashboard|index' | head -20")
print(stdout.read().decode())

# 2. 检查 index.html 完整内容
print("\n" + "=" * 60)
print("2. index.html 完整内容")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("cat /var/www/oa-web/index.html")
print(stdout.read().decode())

# 3. 检查 dashboard 路由对应 JS（用 grep 看哪个 JS 包含 dashboard 字符串）
print("\n" + "=" * 60)
print("3. 包含 dashboard 字符串的 JS")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("cd /var/www/oa-web/assets && grep -l 'dashboard' *.js 2>/dev/null | head -5")
print(stdout.read().decode())

# 4. 查看前端 js 实际请求
print("\n" + "=" * 60)
print("4. 直接 curl 拉首页 index.html 测试")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("curl -s -I http://localhost/")
print(stdout.read().decode())

# 5. 检查 nginx 配置
print("\n" + "=" * 60)
print("5. nginx 配置")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/* | head -80")
print(stdout.read().decode())

ssh.close()
print("done")
