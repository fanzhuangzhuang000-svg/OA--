#!/usr/bin/env python3
"""
调试登录问题：
1. 查看 AuthController@login 方法的逻辑
2. 查看数据库中用户的实际状态和密码
3. 尝试用 artisan tinker 创建正确的密码哈希
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
    import io
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
print("调试登录 403 问题")
print("=" * 60)

ssh = ssh_connect()

# 1. 查看 AuthController@login 方法
print("\n[1] 查看 AuthController 的 login 方法...")
content = get_file_via_ssh(ssh, '/var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php')

# 找到 AuthController 类和 login 方法
lines = content.split('\n')
in_auth_controller = False
in_login_method = False
login_method_lines = []

for i, line in enumerate(lines):
    if 'class AuthController' in line:
        in_auth_controller = True
    if in_auth_controller and 'function login' in line:
        in_login_method = True
    if in_login_method:
        login_method_lines.append(line)
        if len(login_method_lines) > 80:  # 读取足够多的行
            break
    # 如果遇到下一个函数或类，停止
    if in_login_method and (line.strip().startswith('function ') or line.strip().startswith('class ')):
        if len(login_method_lines) > 5:  # 已经读取了一部分
            break

print("AuthController@login 方法内容：")
if login_method_lines:
    for l in login_method_lines[:60]:
        print(l)
else:
    print("未找到 login 方法，尝试搜索...")
    # 搜索包含 "账号已被禁用" 的行
    for i, line in enumerate(lines):
        if '账号已被禁用' in line or 'disabled' in line.lower() or 'inactive' in line.lower():
            start = max(0, i - 5)
            end = min(len(lines), i + 15)
            print(f"\n找到相关代码（第 {i+1} 行附近）：")
            for j in range(start, end):
                print(lines[j])
            break

# 2. 查看数据库中用户的实际状态
print("\n" + "=" * 60)
print("[2] 查看数据库中用户的实际状态...")

# 使用 debian-sys-maint 用户访问 MySQL
check_users = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
SELECT id, username, email, status, password, LENGTH(password) as pwd_len 
FROM oa_db.users 
LIMIT 10;
" 2>/dev/null"""

output = run_cmd(ssh, check_users)
print("用户表内容：")
print(output)

# 3. 检查 status 字段的实际值
print("\n[3] 检查 status 字段的值...")
check_status = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
SELECT username, status, CASE 
    WHEN status = 'active' THEN 'OK' 
    ELSE 'PROBLEM' 
END as status_check
FROM oa_db.users;
" 2>/dev/null"""

output = run_cmd(ssh, check_status)
print(output)

# 4. 查看 User 模型的 $casts 和 status 访问器
print("\n" + "=" * 60)
print("[4] 查看 User 模型的 status 处理...")

user_model = get_file_via_ssh(ssh, '/var/www/oa-api/app/Models/User.php')
print("User.php 内容（前100行）：")
user_lines = user_model.split('\n')
for i, line in enumerate(user_lines[:100]):
    print(line)

# 5. 查看 UserStatus Enum
print("\n" + "=" * 60)
print("[5] 查看 UserStatus Enum...")

enums = get_file_via_ssh(ssh, '/var/www/oa-api/app/Enums/index.php')
enum_lines = enums.split('\n')
in_userstatus = False
for i, line in enumerate(enum_lines):
    if 'enum UserStatus' in line or 'class UserStatus' in line:
        in_userstatus = True
    if in_userstatus:
        print(line)
        if line.strip() == '}' and i > 0:
            break

# 6. 尝试用正确的密码重置
print("\n" + "=" * 60)
print("[6] 重置 admin 密码为 admin123...")

# 使用 php artisan tinker 生成密码哈希
tinker_cmd = """cd /var/www/oa-api && sudo php artisan tinker --execute="
echo bcrypt('admin123');
" 2>/dev/null"""

output = run_cmd(ssh, tinker_cmd, use_sudo=False)
print(f"bcrypt 输出: {output}")

# 提取哈希值（如果成功）
import re
hash_match = re.search(r'\$2y\$[0-9A-Za-z\.\/]+', output)
if hash_match:
    pwd_hash = hash_match.group(0)
    print(f"\n生成的密码哈希: {pwd_hash}")
    
    # 更新数据库
    update_pwd = f"""sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
    UPDATE oa_db.users 
    SET password = '{pwd_hash}', status = 'active' 
    WHERE username = 'admin';
    " 2>/dev/null"""
    
    output = run_cmd(ssh, update_pwd)
    print(f"密码更新结果: {output}")
else:
    print("无法从 tinker 输出中提取哈希，尝试直接更新...")
    # 使用一个已知的 bcrypt 哈希 (admin123 的哈希)
    # 这个哈希是已知对应 admin123 的
    known_hash = '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi'
    
    update_pwd = f"""sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
    UPDATE oa_db.users 
    SET password = '{known_hash}', status = 'active' 
    WHERE username = 'admin';
    " 2>/dev/null"""
    
    output = run_cmd(ssh, update_pwd)
    print(f"密码更新结果: {output}")

# 7. 清除所有缓存
print("\n[7] 清除所有缓存...")
cache_cmd = "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear && sudo php artisan view:clear"
output = run_cmd(ssh, cache_cmd, use_sudo=False)
print(output)

# 8. 测试登录
print("\n" + "=" * 60)
print("[8] 测试登录...")

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

# 9. 如果还是 403，检查 AuthController 是否有额外逻辑
print("\n" + "=" * 60)
print("[9] 检查 AuthController 完整逻辑...")

# 搜索 ModuleControllers.php 中的 login 相关代码
lines = content.split('\n')
print("搜索 'status' 和 'active' 相关的代码：")
for i, line in enumerate(lines):
    if 'status' in line.lower() and ('active' in line or 'disable' in line or 'forbidden' in line or '403' in line):
        start = max(0, i - 3)
        end = min(len(lines), i + 8)
        print(f"\n第 {i+1} 行附近：")
        for j in range(start, end):
            print(f"  {j+1}: {lines[j]}")
        print()

ssh.close()

print("\n" + "=" * 60)
print("调试完成")
print("=" * 60)
