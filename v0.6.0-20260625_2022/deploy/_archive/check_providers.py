#!/usr/bin/env python3
"""
检查 config/app.php 的 providers 部分，确保 AuthServiceProvider 已注册
"""
import paramiko
import requests

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
SUDO_PASS = "admin123"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS)
    return client

def run_cmd(client, cmd, use_sudo=False, timeout=60):
    full_cmd = (f"echo {SUDO_PASS} | sudo -S {cmd}") if use_sudo else cmd
    stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace') + stderr.read().decode('utf-8', errors='replace')

ssh = ssh_connect()

# 1. 查看 config/app.php 的 providers 部分
print("[1] 查看 config/app.php providers...")
providers = run_cmd(ssh, "cd /var/www/oa-api && sudo grep -n 'providers\\|Auth\\|auth' config/app.php")
print(providers)

# 2. 查看完整 providers 数组
print("\n[2] 查看 providers 数组内容...")
full_config = run_cmd(ssh, "cd /var/www/oa-api && sudo cat config/app.php")

# 找到 providers 部分
lines = full_config.split('\n')
in_providers = False
provider_lines = []
for i, line in enumerate(lines):
    if "'providers'" in line or '"providers"' in line:
        in_providers = True
    if in_providers:
        provider_lines.append(f"{i+1}: {line}")
        if line.strip() == '],' or line.strip() == ');':
            break

for line in provider_lines[:40]:
    print(line)

# 3. 检查是否有 AuthServiceProvider
print("\n[3] 检查 AuthServiceProvider...")
if 'AuthServiceProvider' in full_config:
    print("✅ AuthServiceProvider 已在配置中")
else:
    print("❌ AuthServiceProvider 不在配置中！这是根本原因！")
    print("添加 AuthServiceProvider...")
    
    sftp = ssh.open_sftp()
    try:
        with sftp.open('/var/www/oa-api/config/app.php', 'r') as f:
            content = f.read().decode('utf-8')
        
        # 在 providers 数组中添加 AuthServiceProvider
        # 在 PasswordResetServiceProvider 附近添加
        if 'PasswordResetServiceProvider' in content:
            old_line = "        Illuminate\\Auth\\Passwords\\PasswordResetServiceProvider::class,"
            new_lines = """        Illuminate\\Auth\\Passwords\\PasswordResetServiceProvider::class,
        Illuminate\\Auth\\AuthServiceProvider::class,"""
            content = content.replace(old_line, new_lines)
            print("✅ 已添加 AuthServiceProvider")
        else:
            print("尝试其他方式添加...")
            # 在第一个 provider 之前添加
            content = content.replace(
                "'providers' => [",
                "'providers' => [\n        Illuminate\\Auth\\AuthServiceProvider::class,"
            )
            print("✅ 已添加 AuthServiceProvider")
        
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy config/app.php", use_sudo=False)
        with sftp.open('/var/www/oa-api/config/app.php', 'w') as f:
            f.write(content.encode('utf-8'))
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data config/app.php", use_sudo=False)
    finally:
        sftp.close()

# 4. 清除缓存
print("\n[4] 清除缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan config:clear && sudo php artisan cache:clear && sudo php artisan route:clear 2>&1")
print(output)

# 5. 测试
print("\n[5] 测试...")
try:
    resp = requests.post("http://172.20.0.139/api/auth/login",
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    if resp.status_code == 200:
        token = resp.json()['data']['token']
        resp2 = requests.get("http://172.20.0.139/api/auth/userinfo",
                            headers={"Authorization": f"Bearer {token}",
                                    "Accept": "application/json"}, timeout=10)
        print(f"用户信息状态: {resp2.status_code}")
        if resp2.status_code == 200:
            print(f"✅ 成功! 响应: {resp2.text[:300]}")
        else:
            print(f"响应: {resp2.text[:300]}")
except Exception as e:
    print(f"错误: {e}")

ssh.close()
