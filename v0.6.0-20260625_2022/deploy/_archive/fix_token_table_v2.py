#!/usr/bin/env python3
"""
正确使用 Sanctum 迁移创建 personal_access_tokens 表：
1. 找到 Sanctum 迁移文件
2. 单独运行该迁移
3. 或者手动执行正确的 SQL
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
print("创建 personal_access_tokens 表（正确方法）")
print("=" * 60)

ssh = ssh_connect()

# 1. 查找 Sanctum 迁移文件
print("\n[1] 查找 Sanctum 迁移文件...")
find_cmd = "cd /var/www/oa-api && sudo find database/migrations -name '*sanctum*' -o -name '*personal_access_tokens*' 2>/dev/null"
output = run_cmd(ssh, find_cmd, use_sudo=False)
print(f"Sanctum 迁移文件:\n{output}")

# 2. 如果找到，单独运行该迁移
if output.strip() and 'personal_access_tokens' in output:
    print("\n[2] 单独运行 Sanctum 迁移...")
    # 提取文件名
    migration_file = output.strip().split('\n')[0]
    migrate_cmd = f"cd /var/www/oa-api && sudo php artisan migrate --path={migration_file} --force 2>&1"
    output = run_cmd(ssh, migrate_cmd, use_sudo=False)
    print(f"迁移输出:\n{output[:1000]}")
else:
    print("\n[2] 未找到迁移文件，手动创建表...")
    
    # 使用正确的 SQL 创建表
    create_sql = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
    USE oa_db;
    
    DROP TABLE IF EXISTS personal_access_tokens;
    CREATE TABLE personal_access_tokens (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        tokenable_type VARCHAR(255) NOT NULL,
        tokenable_id BIGINT UNSIGNED NOT NULL,
        name VARCHAR(255) NULL,
        token CHAR(64) NOT NULL,
        abilities TEXT NULL,
        expires_at TIMESTAMP NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL,
        UNIQUE KEY personal_access_tokens_token_unique (token),
        INDEX personal_access_tokens_tokenable_type_tokenable_id_index (tokenable_type, tokenable_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    
    SHOW TABLES LIKE 'personal_access_tokens';
    " 2>&1"""
    
    output = run_cmd(ssh, create_sql)
    print(f"创建表结果:\n{output}")

# 3. 验证表创建成功
print("\n[3] 验证 personal_access_tokens 表...")
verify_cmd = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
USE oa_db;
SHOW TABLES LIKE 'personal_access_tokens';
DESCRIBE personal_access_tokens;
" 2>/dev/null"""

output = run_cmd(ssh, verify_cmd)
print(f"验证结果:\n{output}")

# 4. 清除缓存
print("\n[4] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear 2>&1")
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
    print(f"响应: {resp.text[:1000]}")
    
    if resp.status_code == 200:
        print("\n✅ 登录成功！")
        data = resp.json()
        
        if 'data' in data and 'token' in data['data']:
            token = data['data']['token']
            print(f"Token: {token[:40]}...")
            
            # 测试获取用户信息
            print("\n[6] 测试获取用户信息...")
            resp2 = requests.get(
                "http://172.20.0.139/api/auth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            print(f"用户信息状态码: {resp2.status_code}")
            print(f"用户信息响应: {resp2.text[:500]}")
    else:
        print(f"\n❌ 登录失败")
        
except Exception as e:
    print(f"请求失败: {e}")

# 6. 查看错误日志
print("\n[7] 查看错误日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -30 storage/logs/laravel.log 2>/dev/null"
output = run_cmd(ssh, log_cmd, use_sudo=False)
if output.strip():
    # 只显示错误部分
    for line in output.split('\n'):
        if 'ERROR' in line or 'error' in line.lower() or '[' in line[:5]:
            print(line)
else:
    print("（无新错误日志）")

ssh.close()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
