#!/usr/bin/env python3
"""
修复密码哈希问题：
1. 查看现有 AuthController 代码
2. 检查数据库中的密码哈希
3. 生成并写入正确的 bcrypt 哈希
"""

import paramiko
import re
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

def get_file_via_ssh(client, remote_path):
    sftp = client.open_sftp()
    try:
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode('utf-8', errors='replace')
        return content
    except Exception as e:
        return f"Error: {e}"
    finally:
        sftp.close()

print("=" * 60)
print("修复密码哈希问题")
print("=" * 60)

ssh = ssh_connect()

# 1. 查看现有 AuthController 代码
print("\n[1] 查看现有 AuthController 代码...")
auth_code = get_file_via_ssh(ssh, '/var/www/oa-api/app/Http/Controllers/Api/AuthController.php')
print("AuthController.php 内容：")
print(auth_code[:2000])  # 打印前2000字符

# 2. 检查数据库中的密码哈希
print("\n" + "=" * 60)
print("[2] 检查数据库中的密码哈希...")

check_hash = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
SELECT username, LEFT(password, 10) as pwd_start, LENGTH(password) as pwd_len
FROM oa_db.users;
" 2>/dev/null"""

output = run_cmd(ssh, check_hash)
print(f"密码哈希前缀和长度:\n{output}")

# 3. 使用 PHP 生成正确的密码哈希
print("\n[3] 使用 PHP 生成正确的密码哈希...")

# 写一个临时 PHP 脚本来生成哈希
php_script = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(\\Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();
echo password_hash('admin123', PASSWORD_BCRYPT);
echo PHP_EOL;
?>"""

# 将 PHP 脚本写到服务器
write_php = f"""cat > /tmp/gen_hash.php << 'PHPEOF'
{php_script}
PHPEOF
"""
run_cmd(ssh, write_php, use_sudo=False)

# 执行 PHP 脚本生成哈希
gen_hash = """cd /var/www/oa-api && sudo php /tmp/gen_hash.php 2>/dev/null"""
output = run_cmd(ssh, gen_hash, use_sudo=False)
print(f"生成的哈希: {output}")

# 提取哈希
hash_match = re.search(r'\$2y\$[0-9A-Za-z\.\/]+', output)
if hash_match:
    pwd_hash = hash_match.group(0)
    print(f"\n提取的密码哈希: {pwd_hash}")
    
    # 更新所有用户的密码
    update_pwd = f"""sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
    USE oa_db;
    UPDATE users SET password = '{pwd_hash}', status = 'active';
    " 2>/dev/null"""
    
    output = run_cmd(ssh, update_pwd)
    print(f"密码更新结果: {output}")
else:
    print("无法提取哈希，尝试另一种方法...")
    # 使用 artisan tinker
    tinker_cmd = """cd /var/www/oa-api && sudo php artisan tinker --execute="
echo password_hash('admin123', PASSWORD_BCRYPT);
" 2>&1 | grep '\\$2y\\$'"""
    
    output = run_cmd(ssh, tinker_cmd, use_sudo=False)
    print(f"Tinker 输出: {output}")

# 4. 清除缓存
print("\n[4] 清除缓存...")
cache_cmd = "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear"
output = run_cmd(ssh, cache_cmd, use_sudo=False)
print(output)

# 5. 测试登录
print("\n" + "=" * 60)
print("[5] 测试登录...")
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

# 6. 查看日志
print("\n[6] 查看最新日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -15 storage/logs/laravel.log"
output = run_cmd(ssh, log_cmd, use_sudo=False)
print(output)

ssh.close()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
