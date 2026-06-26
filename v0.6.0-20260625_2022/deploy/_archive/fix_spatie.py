#!/usr/bin/env python3
"""
修复 Spatie 权限包表缺失问题：
1. 删除所有 Spatie 相关表
2. 重新运行 Spatie 迁移
3. 测试登录
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
print("修复 Spatie 权限包表")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查 Spatie 相关表
print("\n[1] 检查 Spatie 相关表...")
check_tables = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
USE oa_db;
SHOW TABLES LIKE '%permission%';
SHOW TABLES LIKE '%role%';
" 2>/dev/null"""

output = run_cmd(ssh, check_tables)
print(f"Spatie 相关表:\n{output}")

# 2. 删除所有 Spatie 表（按外键依赖顺序）
print("\n[2] 删除所有 Spatie 表...")

drop_tables = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
USE oa_db;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS model_has_permissions;
DROP TABLE IF EXISTS model_has_roles;
DROP TABLE IF EXISTS role_has_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS roles;
SET FOREIGN_KEY_CHECKS = 1;
SHOW TABLES LIKE '%permission%';
SHOW TABLES LIKE '%role%';
" 2>/dev/null"""

output = run_cmd(ssh, drop_tables)
print(f"删除结果:\n{output}")

# 3. 找到 Spatie 迁移文件
print("\n[3] 找到 Spatie 迁移文件...")
find_cmd = "cd /var/www/oa-api && sudo find database/migrations -name '*permission*' -o -name '*role*' 2>/dev/null | head -5"
output = run_cmd(ssh, find_cmd, use_sudo=False)
print(f"Spatie 迁移文件:\n{output}")

# 4. 删除可能导致问题的重复迁移文件
print("\n[4] 检查并删除重复的迁移文件...")

# 查找所有包含 create_permission 或 create_role 的迁移
check_migrations = "cd /var/www/oa-api && sudo grep -l 'create_permission\\|create_role' database/migrations/*.php 2>/dev/null | xargs -I {} basename {}"
output = run_cmd(ssh, check_migrations, use_sudo=False)
print(f"包含权限表创建的迁移:\n{output}")

# 5. 重新运行所有待处理的迁移
print("\n[5] 重新运行所有待处理的迁移...")
migrate_cmd = "cd /var/www/oa-api && sudo php artisan migrate --force 2>&1"
output = run_cmd(ssh, migrate_cmd, use_sudo=False)
print(f"迁移输出:\n{output[:2000]}")

# 6. 验证 Spatie 表创建成功
print("\n[6] 验证 Spatie 表...")
verify_cmd = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
USE oa_db;
SHOW TABLES LIKE '%permission%';
SHOW TABLES LIKE '%role%';
SELECT COUNT(*) as permissions_count FROM permissions;
SELECT COUNT(*) as roles_count FROM roles;
" 2>/dev/null"""

output = run_cmd(ssh, verify_cmd)
print(f"验证结果:\n{output}")

# 7. 清除缓存
print("\n[7] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear 2>&1")
print(output)

# 8. 测试登录
print("\n" + "=" * 60)
print("[8] 测试登录...")
try:
    resp = requests.post(
        "http://172.20.0.139/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text[:1000]}")
    
    if resp.status_code == 200:
        print("\n✅ 登录成功！")
        data = resp.json()
        
        if 'data' in data and 'token' in data['data']:
            token = data['data']['token']
            print(f"Token (前40字符): {token[:40]}...")
            
            # 测试获取用户信息
            print("\n[9] 测试获取用户信息...")
            resp2 = requests.get(
                "http://172.20.0.139/api/auth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            print(f"用户信息状态码: {resp2.status_code}")
            print(f"用户信息响应: {resp2.text[:500]}")
            
            if resp2.status_code == 200:
                print("\n✅ 用户信息获取成功！")
                print("\n" + "=" * 60)
                print("🎉 登录 API 完全正常工作！")
                print("=" * 60)
            else:
                print(f"\n❌ 用户信息获取失败")
    else:
        print(f"\n❌ 登录失败")
        
except Exception as e:
    print(f"请求失败: {e}")

# 9. 查看错误日志
print("\n[10] 查看错误日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -30 storage/logs/laravel.log 2>/dev/null"
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
