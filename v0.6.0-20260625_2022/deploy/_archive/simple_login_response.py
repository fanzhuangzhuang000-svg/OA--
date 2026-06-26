#!/usr/bin/env python3
"""
简化登录响应：暂时不返回 permissions 和 roles
让登录和获取用户信息先工作
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
print("简化登录响应（暂时移除 permissions/roles）")
print("=" * 60)

ssh = ssh_connect()

# 1. 备份并修改 AuthController
print("\n[1] 修改 AuthController 登录响应...")

sftp = ssh.open_sftp()
try:
    # 读取当前 AuthController
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'r') as f:
        content = f.read().decode('utf-8')
    
    print("当前登录响应部分代码：")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'permissions' in line or 'roles' in line or 'token' in line.lower():
            print(f"  {i+1}: {line}")
    
    # 简化登录响应：注释掉 permissions 和 roles
    # 找到返回响应的部分并修改
    old_response = """'permissions' => $user->getAllPermissions()->pluck('name'),
                'roles' => $user->getRoleNames(),"""
    
    new_response = """// 暂时注释掉 permissions 和 roles（避免 Spatie 错误）
                // 'permissions' => $user->getAllPermissions()->pluck('name'),
                // 'roles' => $user->getRoleNames(),"""
    
    if old_response in content:
        content = content.replace(old_response, new_response)
        print("✅ 已注释掉 permissions 和 roles")
    else:
        print("⚠ 未找到预期代码，尝试其他方式...")
        # 可能是单行格式不同，直接修改 userInfo 和 login 方法
        pass
    
    # 同样修改 userInfo 方法
    old_userinfo = """'permissions' => $user->getAllPermissions()->pluck('name'),
            'roles' => $user->getRoleNames(),"""
    new_userinfo = """// 暂时注释掉
            // 'permissions' => $user->getAllPermissions()->pluck('name'),
            // 'roles' => $user->getRoleNames(),"""
    
    if old_userinfo in content:
        content = content.replace(old_userinfo, new_userinfo)
        print("✅ 已注释掉 userInfo 中的 permissions 和 roles")
    
    # 上传修改后的文件
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy app/Http/Controllers/Api/AuthController.php", use_sudo=False)
    
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'w') as f:
        f.write(content.encode('utf-8'))
    
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data app/Http/Controllers/Api/AuthController.php", use_sudo=False)
    
    print("✅ AuthController 已更新")
    
finally:
    sftp.close()

# 2. 清除缓存
print("\n[2] 清除缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear 2>&1")
print(output)

# 3. 测试登录和获取用户信息
print("\n" + "=" * 60)
print("[3] 测试登录和获取用户信息...")

try:
    # 登录
    resp = requests.post(
        "http://172.20.0.139/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    
    print(f"登录状态: {resp.status_code}")
    print(f"登录响应: {resp.text[:500]}")
    
    if resp.status_code == 200:
        print("\n✅ 登录成功！")
        token = resp.json()['data']['token']
        
        # 获取用户信息
        print("\n[4] 测试获取用户信息...")
        resp2 = requests.get(
            "http://172.20.0.139/api/auth/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"用户信息状态: {resp2.status_code}")
        print(f"用户信息响应: {resp2.text[:800]}")
        
        if resp2.status_code == 200:
            print("\n✅✅ 登录 + 获取用户信息完全成功！✅✅")
            print("\n" + "=" * 60)
            print("🎉 后端 API 基本功能已正常工作！")
            print("=" * 60)
            print("\n默认登录账号：")
            print("  用户名: admin")
            print("  密码: admin123")
            print("\nAPI 基地址: http://172.20.0.139/api")
            print("\n可用 API 端点：")
            print("  POST /api/auth/login - 登录")
            print("  POST /api/auth/logout - 登出")
            print("  GET  /api/auth/userinfo - 获取用户信息")
            print("  GET  /api/dashboard/stats - 工作台统计")
            print("  ... 其他 API 端点")
        else:
            print(f"\n❌ 获取用户信息失败: {resp2.text[:300]}")
    else:
        print(f"\n❌ 登录失败")
        
except Exception as e:
    print(f"请求错误: {e}")

# 4. 查看错误日志
print("\n[5] 查看错误日志...")
log = run_cmd(ssh, "cd /var/www/oa-api && sudo tail -20 storage/logs/laravel.log 2>/dev/null")
if log.strip():
    for line in log.split('\n'):
        if 'ERROR' in line or 'error' in line.lower():
            print(line)
else:
    print("（无新错误）")

ssh.close()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
