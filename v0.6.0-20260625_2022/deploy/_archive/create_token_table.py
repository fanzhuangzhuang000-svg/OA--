#!/usr/bin/env python3
"""
修复 personal_access_tokens 表缺失问题：
1. 强制运行 Sanctum 迁移
2. 验证表创建成功
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
print("修复 personal_access_tokens 表")
print("=" * 60)

ssh = ssh_connect()

# 1. 强制运行迁移
print("\n[1] 强制运行迁移（--force 参数）...")
migrate_cmd = "cd /var/www/oa-api && sudo php artisan migrate --force 2>&1"
output = run_cmd(ssh, migrate_cmd, use_sudo=False)
print(f"迁移输出:\n{output[:2000]}")

# 2. 检查 personal_access_tokens 表是否创建成功
print("\n[2] 检查 personal_access_tokens 表...")
check_table = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
SHOW TABLES FROM oa_db LIKE 'personal_access_tokens';
DESCRIBE oa_db.personal_access_tokens;
" 2>/dev/null"""

output = run_cmd(ssh, check_table)
print(f"表检查结果:\n{output}")

if 'personal_access_tokens' not in output:
    print("\n❌ 迁移可能没创建表，手动创建...")
    
    create_table = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
    USE oa_db;
    CREATE TABLE IF NOT EXISTS personal_access_tokens (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        tokenable_type VARCHAR(255) NOT NULL,
        tokenable_id BIGINT UNSIGNED NOT NULL,
        name VARCHAR(255) NULL,
        token CHAR(64) NOT NULL UNIQUE,
        abilities TEXT NULL,
        expires_at TIMESTAMP NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL,
        INDEX tokenable (tokenable_type, tokenable_id),
        INDEX token (token(10))
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    " 2>/dev/null"""
    
    output = run_cmd(ssh, create_table)
    print(f"手动创建结果: {output if output.strip() else 'OK'}")
    
    # 再次检查
    output = run_cmd(ssh, check_table)
    print(f"\n再次检查:\n{output}")

# 3. 清除缓存
print("\n[3] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear 2>&1")
print(output)

# 4. 测试登录
print("\n" + "=" * 60)
print("[4] 测试登录...")
try:
    resp = requests.post(
        "http://172.20.0.139/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
    
    if resp.status_code == 200:
        print("\n✅ 登录成功！")
        data = resp.json()
        
        # 提取 token
        if 'data' in data and 'token' in data['data']:
            token = data['data']['token']
            print(f"Token (前30字符): {token[:30]}...")
            
            # 测试获取用户信息
            print("\n[5] 测试获取用户信息...")
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
                print(f"\n❌ 用户信息获取失败: {resp2.text[:200]}")
        else:
            print("响应中没有 token")
    else:
        print(f"\n❌ 登录失败")
        
except Exception as e:
    print(f"请求失败: {e}")

# 5. 查看错误日志（如果有）
print("\n[6] 查看最新错误日志...")
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
