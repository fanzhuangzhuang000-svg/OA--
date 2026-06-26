import paramiko, requests

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 检查实际生效的 nginx config（看是哪个 server block 在用）
print("=" * 60)
print("1. 列出所有 sites-enabled")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/sites-enabled/")
print(stdout.read().decode())

# 2. 看主配置
print("\n" + "=" * 60)
print("2. nginx.conf 包含什么")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/nginx.conf | grep -E 'include|sites-enabled'")
print(stdout.read().decode())

# 3. 实际从外网拉 /dashboard 路由
print("\n" + "=" * 60)
print("3. 外网测试 SPA 路由")
print("=" * 60)
for path in ['/', '/dashboard', '/login', '/api/dashboard/stats']:
    try:
        r = requests.get(f'http://172.20.0.139{path}', timeout=5, allow_redirects=False)
        print(f"  {r.status_code}  {path}  len={len(r.text)}")
    except Exception as e:
        print(f"  ERR  {path}: {e}")

# 4. 看 nginx active config
print("\n" + "=" * 60)
print("4. nginx -T 看实际生效的 config（只看 server_name 172.20.0.139 的）")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("nginx -T 2>/dev/null | grep -A 50 'server_name 172.20.0.139' | head -120")
print(stdout.read().decode())

ssh.close()
print("done")
