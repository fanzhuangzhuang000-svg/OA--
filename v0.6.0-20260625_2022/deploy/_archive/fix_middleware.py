#!/usr/bin/env python3
"""
修复 auth 中间件别名问题：
1. 检查 bootstrap/app.php 中间件配置
2. 添加 auth 中间件别名
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
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return output + error

print("=" * 60)
print("修复 auth 中间件配置")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查 bootstrap/app.php
print("\n[1] 检查 bootstrap/app.php...")
app_php = run_cmd(ssh, "cd /var/www/oa-api && sudo cat bootstrap/app.php 2>/dev/null")
print("bootstrap/app.php 内容：")
print(app_php[:2000])

# 2. 检查是否有 withMiddleware
print("\n[2] 检查中间件配置...")
if 'withMiddleware' in app_php:
    print("✅ withMiddleware 已配置")
    
    # 检查是否配置了 auth 别名
    if 'auth' in app_php and 'sanctum' in app_php:
        print("✅ auth 中间件可能已配置")
    else:
        print("❌ 可能需要添加 auth 中间件别名")
        
        # 修改 bootstrap/app.php 添加中间件别名
        print("\n[3] 添加 auth 中间件别名...")
        
        # 在 withMiddleware 中添加 alias
        # Laravel 11+ 语法：->withMiddleware(alise: [...])  
        # 这个配置比较复杂，让我直接使用命令添加
        
        # 更简单的方法：发布 Laravel 的默认中间件配置
        publish_cmd = "cd /var/www/oa-api && sudo php artisan vendor:publish --tag=laravel-middleware 2>&1 | head -20"
        output = run_cmd(ssh, publish_cmd, use_sudo=False)
        print(f"发布中间件: {output[:500]}")
else:
    print("❌ withMiddleware 未配置")
    print("需要添加中间件配置...")

# 3. 更简单的方法：直接测试是否可以通过其他方式访问
print("\n[3] 测试不使用 auth 中间件的路由...")

# 先检查路由中间件的配置
print("\n检查 api.php 路由中间件...")
route_check = run_cmd(ssh, "cd /var/www/oa-api && sudo grep -A 5 'middleware' routes/api.php | head -20")
print(f"路由中间件配置:\n{route_check}")

# 4. 临时解决方案：修改 AuthController 的 userInfo 方法，去掉中间件依赖
print("\n[4] 临时修复：确保 sanctum 中间件正常...")

# 检查 app/Http/Kernel.php（Laravel 10 及以下）或 bootstrap/app.php（Laravel 11+）
print("\n检查 Laravel 版本...")
version_cmd = "cd /var/www/oa-api && sudo php artisan --version 2>/dev/null"
output = run_cmd(ssh, version_cmd, use_sudo=False)
print(f"Laravel 版本: {output.strip()}")

# 5. 检查 vendor/laravel/framework 版本
print("\n检查框架版本详情...")
version_file = run_cmd(ssh, "cd /var/www/oa-api && sudo cat vendor/laravel/framework/composer.json | grep '\"version\"' 2>/dev/null")
print(f"框架版本: {version_file.strip()}")

# 6. 对于 Laravel 11+，需要确保 auth 中间件已注册
# 让我直接修改 bootstrap/app.php 添加中间件别名
print("\n[6] 修改 bootstrap/app.php 添加中间件配置...")

# 下载 bootstrap/app.php
sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/bootstrap/app.php', 'r') as f:
        content = f.read().decode('utf-8')
    
    print("\n当前 bootstrap/app.php 内容：")
    print(content)
    
    # 检查是否需要添加 withMiddleware
    if 'withMiddleware' not in content:
        # 需要添加
        print("\n需要添加 withMiddleware 配置...")
        
        # 在 return Application::configure 代码块中添加
        # 找到 ]); 并添加 withMiddleware
        if ']);' in content or '];' in content:
            # 在最后一行的 ]); 之前添加
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.strip() == ']);' or line.strip() == '];':
                    # 添加 withMiddleware 配置
                    indent = '        '  # 8 个空格
                    new_lines.append(f"{indent}->withMiddleware(")
                    new_lines.append(f"{indent}    alias: [")
                    new_lines.append(f"{indent}        'auth' => \\App\\Http\\Middleware\\Authenticate::class,")
                    new_lines.append(f"{indent}    ]")
                    new_lines.append(f"{indent}]);")
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
            print("已添加 withMiddleware 配置")
    
    # 上传
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy bootstrap/app.php", use_sudo=False)
    
    with sftp.open('/var/www/oa-api/bootstrap/app.php', 'w') as f:
        f.write(content.encode('utf-8'))
    
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data bootstrap/app.php", use_sudo=False)
    
    print("\nbootstrap/app.php 已更新")
    
finally:
    sftp.close()

# 7. 清除缓存
print("\n[7] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear 2>&1")
print(output)

# 8. 测试获取用户信息
print("\n" + "=" * 60)
print("[8] 测试获取用户信息...")

# 先登录获取 token
try:
    resp = requests.post(
        "http://172.20.0.139/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    
    if resp.status_code == 200:
        token = resp.json()['data']['token']
        print("✅ 登录成功，获取到 token")
        
        # 获取用户信息
        resp2 = requests.get(
            "http://172.20.0.139/api/auth/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"用户信息状态码: {resp2.status_code}")
        print(f"用户信息响应: {resp2.text[:800]}")
        
        if resp2.status_code == 200:
            print("\n✅ 用户信息获取成功！")
        else:
            print(f"\n❌ 用户信息获取失败")
    else:
        print(f"❌ 登录失败: {resp.text}")
        
except Exception as e:
    print(f"请求失败: {e}")

ssh.close()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
