#!/usr/bin/env python3
"""
进一步检查登录 500 错误：
1. 查看 api.php 路由定义
2. 查看 AuthController 完整代码
3. 查看 Laravel 日志
"""

import paramiko
import time

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

def get_file_via_ssh(client, remote_path):
    """通过 SSH 读取远程文件内容"""
    sftp = client.open_sftp()
    try:
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode('utf-8', errors='replace')
        return content
    except Exception as e:
        return f"Error reading file: {e}"
    finally:
        sftp.close()

print("=" * 60)
print("检查登录 500 错误")
print("=" * 60)

ssh = ssh_connect()

# 1. 查看 api.php 路由定义
print("\n[1] 查看 api.php 路由定义...")
api_routes = get_file_via_ssh(ssh, '/var/www/oa-api/routes/api.php')
print("routes/api.php 内容：")
print(api_routes)

# 2. 查看 AuthController 完整代码
print("\n" + "=" * 60)
print("[2] 查看 AuthController 完整代码...")

content = get_file_via_ssh(ssh, '/var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php')

lines = content.split('\n')
in_auth = False
auth_controller_code = []

for i, line in enumerate(lines):
    if 'class AuthController' in line:
        in_auth = True
    if in_auth:
        auth_controller_code.append(line)
        # 如果遇到下一个类，停止
        if len(auth_controller_code) > 5 and line.strip().startswith('class '):
            auth_controller_code.pop()  # 移除最后一个（下一个类的开始）
            break

print("AuthController 完整代码：")
print('\n'.join(auth_controller_code))

# 如果上面的方法没找到，尝试另一种方式
if not auth_controller_code:
    print("未找到 AuthController，搜索文件中所有类...")
    for i, line in enumerate(lines):
        if line.strip().startswith('class ') or line.strip().startswith('//') or line.strip().startswith('/*'):
            print(f"{i+1}: {line}")

# 3. 查看 Laravel 日志
print("\n" + "=" * 60)
print("[3] 查看 Laravel 最新日志...")

log_cmd = "cd /var/www/oa-api && sudo tail -100 storage/logs/laravel.log 2>/dev/null || echo 'No log file found'"
output = run_cmd(ssh, log_cmd, use_sudo=False)
print("Laravel 日志（最后100行）：")
print(output[-3000:] if len(output) > 3000 else output)

# 4. 测试登录并立即查看日志
print("\n" + "=" * 60)
print("[4] 测试登录并查看实时错误...")

import requests
import json

try:
    resp = requests.post(
        "http://172.20.0.139/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"请求失败: {e}")

# 5. 再次查看日志（登录后的新日志）
print("\n[5] 登录后的最新日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -30 storage/logs/laravel.log 2>/dev/null"
output = run_cmd(ssh, log_cmd, use_sudo=False)
print(output)

# 6. 检查 User 模型的 status 字段处理
print("\n" + "=" * 60)
print("[6] 检查 status 字段枚举转换...")

# 直接测试数据库中的 status 值
test_enum = r"""cd /var/www/oa-api && sudo php artisan tinker --execute="
$user = App\Models\User::where('username', 'admin')->first();
echo 'Status: ' . $user->status . PHP_EOL;
echo 'Status Value: ' . $user->status->value . PHP_EOL;
echo 'Casts: ';
print_r($user->getCasts());
" 2>&1"""

output = run_cmd(ssh, test_enum, use_sudo=False)
print(f"Tinker 输出:\n{output}")

ssh.close()

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)
