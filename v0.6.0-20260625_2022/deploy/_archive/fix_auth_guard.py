#!/usr/bin/env python3
"""
修复 auth guard 配置问题：
1. 检查 config/auth.php
2. 添加 sanctum guard 配置
3. 测试用户信息获取
"""

import paramiko
import requests
import json

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
print("修复 auth guard 配置")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查 config/auth.php
print("\n[1] 检查 config/auth.php...")
auth_config = run_cmd(ssh, "cd /var/www/oa-api && sudo cat config/auth.php 2>/dev/null")
print(f"auth.php 内容（前80行）:")
lines = auth_config.split('\n')
for i, line in enumerate(lines[:80]):
    print(f"{i+1}: {line}")

# 2. 检查是否有 sanctum guard
print("\n[2] 检查 sanctum guard 配置...")
if 'sanctum' in auth_config.lower():
    print("✅ sanctum guard 已配置")
else:
    print("❌ sanctum guard 未配置，需要添加...")
    
    # 下载、修改、上传 config/auth.php
    print("\n[3] 修复 config/auth.php...")
    
    sftp = ssh.open_sftp()
    try:
        # 读取完整内容
        with sftp.open('/var/www/oa-api/config/auth.php', 'r') as f:
            content = f.read().decode('utf-8')
        
        # 添加 sanctum guard
        # 在 'guards' 数组中添加
        if "'guards'" in content and "'web'" in content:
            # 在 web guard 后面添加 sanctum guard
            old_web_guard = "'web' => [\n            'driver' => 'session',\n            'provider' => 'users',\n        ],"
            new_guards = "'web' => [\n            'driver' => 'session',\n            'provider' => 'users',\n        ],\n        'sanctum' => [\n            'driver' => 'sanctum',\n            'provider' => 'users',\n        ],"
            
            if old_web_guard in content:
                content = content.replace(old_web_guard, new_guards)
                print("已添加 sanctum guard")
            else:
                print("未找到 web guard 模式，手动检查...")
                # 显示 guards 部分
                in_guards = False
                for i, line in enumerate(content.split('\n')):
                    if "'guards'" in line:
                        in_guards = True
                    if in_guards:
                        print(f"  {i+1}: {line}")
                        if line.strip() == ');':
                            break
        
        # 上传修改后的文件
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy config/auth.php", use_sudo=False)
        
        with sftp.open('/var/www/oa-api/config/auth.php', 'w') as f:
            f.write(content.encode('utf-8'))
        
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data config/auth.php", use_sudo=False)
        
        print("config/auth.php 已更新")
        
    finally:
        sftp.close()

# 4. 检查 config/sanctum.php
print("\n[4] 检查 config/sanctum.php...")
sanctum_config = run_cmd(ssh, "cd /var/www/oa-api && sudo cat config/sanctum.php 2>/dev/null | head -40")
print(f"Sanctum 配置:\n{sanctum_config[:1000]}")

# 5. 清除配置缓存
print("\n[5] 清除配置缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan config:clear && sudo php artisan cache:clear 2>&1")
print(output)

# 6. 测试登录并获取用户信息
print("\n" + "=" * 60)
print("[6] 测试完整登录流程...")

# 登录
try:
    resp = requests.post(
        "http://172.20.0.139/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    
    if resp.status_code == 200:
        print("✅ 登录成功")
        data = resp.json()
        token = data['data']['token']
        print(f"Token 获取成功")
        
        # 获取用户信息
        print("\n[7] 测试获取用户信息...")
        resp2 = requests.get(
            "http://172.20.0.139/api/auth/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"用户信息状态码: {resp2.status_code}")
        print(f"用户信息响应: {resp2.text[:800]}")
        
        if resp2.status_code == 200:
            print("\n✅ 用户信息获取成功！")
            
            # 测试访问一个需要认证的 API
            print("\n[8] 测试访问受保护的 API（仪表盘）...")
            resp3 = requests.get(
                "http://172.20.0.139/api/dashboard/stats",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            print(f"仪表盘状态码: {resp3.status_code}")
            print(f"仪表盘响应: {resp3.text[:500]}")
            
            if resp3.status_code == 200:
                print("\n🎉 所有 API 测试通过！")
                print("\n" + "=" * 60)
                print("✅ 后端 API 部署成功并且可以正常工作！")
                print("=" * 60)
                print("\n默认登录账号：")
                print("  用户名: admin")
                print("  密码: admin123")
                print("\nAPI 地址: http://172.20.0.139/api")
            else:
                print(f"\n❌ 仪表盘访问失败: {resp3.text[:300]}")
        else:
            print(f"\n❌ 用户信息获取失败")
            
except Exception as e:
    print(f"请求失败: {e}")

# 9. 查看错误日志
print("\n[9] 查看错误日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -20 storage/logs/laravel.log 2>/dev/null"
output = run_cmd(ssh, log_cmd, use_sudo=False)
if output.strip():
    for line in output.split('\n'):
        if 'ERROR' in line or 'error' in line.lower():
            print(line)
else:
    print("（无新错误）")

ssh.close()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
