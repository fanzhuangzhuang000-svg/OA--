#!/usr/bin/env python3
"""
直接修复：检查并添加 auth 中间件别名到 bootstrap/app.php
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

def run_cmd(client, cmd, use_sudo=False, timeout=30):
    full_cmd = f"echo {SUDO_PASS} | sudo -S {cmd}" if use_sudo else cmd
    stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace') + stderr.read().decode('utf-8', errors='replace')

print("=" * 60)
print("直接修复 auth 中间件")
print("=" * 60)

ssh = ssh_connect()

# 1. 查看当前 bootstrap/app.php
print("\n[1] 查看当前 bootstrap/app.php...")
content = run_cmd(ssh, "cd /var/www/oa-api && sudo cat bootstrap/app.php 2>/dev/null")
print("当前内容：")
print(content)

# 2. 检查是否有 withMiddleware
if 'withMiddleware' in content:
    print("\n✅ withMiddleware 已存在")
    print("需要添加 auth 别名...")
    
    # 在 withMiddleware 中添加 alias
    # 找到 withMiddleware 调用并修改
    import re
    
    # 匹配 ->withMiddleware(...) 并添加 alias
    # 这是一个复杂的正则，让我用更简单的方法
    print("\n[2] 手动添加 auth 中间件别名...")
    
    # 下载文件并修改
    sftp = ssh.open_sftp()
    try:
        with sftp.open('/var/www/oa-api/bootstrap/app.php', 'r') as f:
            lines = f.read().decode('utf-8').split('\n')
        
        # 找到 withMiddleware 行并在后面添加 alias
        new_lines = []
        in_middleware = False
        added_alias = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            if 'withMiddleware' in line and '->' in line:
                in_middleware = True
                # 检查下一行是否有参数开始
                continue
            
            if in_middleware and not added_alias:
                # 在 withMiddleware( 后面添加 alias: [...]
                # 找到闭合的 ) 之前添加
                indent = ' ' * 16  # 估计的缩进
                new_lines.append(f"{indent}alias: [")
                new_lines.append(f"{indent}    'auth' => \\App\\Http\\Middleware\\Authenticate::class,")
                new_lines.append(f"{indent}],")
                added_alias = True
                in_middleware = False
        
        new_content = '\n'.join(new_lines)
        
        # 上传
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy bootstrap/app.php", use_sudo=False)
        with sftp.open('/var/www/oa-api/bootstrap/app.php', 'w') as f:
            f.write(new_content.encode('utf-8'))
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data bootstrap/app.php", use_sudo=False)
        
        print("✅ 已添加 auth 别名")
        print("\n新的 bootstrap/app.php：")
        print(new_content[:2000])
        
    finally:
        sftp.close()
        
else:
    print("\n❌ withMiddleware 不存在")
    print("需要在 bootstrap/app.php 中添加...")

# 3. 清除缓存并测试
print("\n[3] 清除缓存...")
run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear 2>&1")

# 4. 测试
print("\n[4] 测试获取用户信息...")
try:
    # 登录
    resp = requests.post("http://172.20.0.139/api/auth/login", 
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    if resp.status_code == 200:
        token = resp.json()['data']['token']
        print("✅ 登录成功")
        
        # 获取用户信息
        resp2 = requests.get("http://172.20.0.139/api/auth/userinfo",
                            headers={"Authorization": f"Bearer {token}"}, timeout=10)
        print(f"用户信息状态: {resp2.status_code}")
        print(f"响应: {resp2.text[:500]}")
    else:
        print(f"❌ 登录失败: {resp.text}")
except Exception as e:
    print(f"错误: {e}")

ssh.close()
print("\n完成")
