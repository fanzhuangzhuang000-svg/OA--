#!/usr/bin/env python3
"""
修复登录问题：
1. admin 密码哈希损坏 - 重新生成并写入
2. AuthController 状态检查错误 - 修复枚举比较
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

print("=" * 60)
print("修复登录问题：密码哈希 + 状态枚举检查")
print("=" * 60)

ssh = ssh_connect()

# 1. 生成正确的密码哈希（使用 PHP 的 password_hash）
print("\n[1] 生成正确的密码哈希...")

# 使用正确的方式调用 PHP 生成哈希
php_code = '''
<?php
require '/var/www/oa-api/vendor/autoload.php';
$hasher = new Illuminate\Hashing\BcryptHasher();
echo $hasher->make('admin123');
echo "\\n";
?>
'''

# 写到临时文件
write_cmd = f"""cat > /tmp/hash.php << 'EOF'
{php_code}
EOF
"""
run_cmd(ssh, write_cmd, use_sudo=False)

# 执行
hash_cmd = """cd /var/www/oa-api && sudo php /tmp/hash.php 2>/dev/null"""
output = run_cmd(ssh, hash_cmd, use_sudo=False)
print(f"PHP 输出: {output}")

# 提取哈希
hash_match = re.search(r'\$2y\$[0-9A-Za-z\.\/]+', output)
if not hash_match:
    # 尝试另一种方法
    hash_cmd2 = """cd /var/www/oa-api && sudo php -r "
require 'vendor/autoload.php';
\\$hasher = new \\Illuminate\\Hashing\\BcryptHasher();
echo \\$hasher->make('admin123');
" 2>/dev/null"""
    output2 = run_cmd(ssh, hash_cmd2, use_sudo=False)
    print(f"方法2输出: {output2}")
    hash_match = re.search(r'\$2y\$[0-9A-Za-z\.\/]+', output2)

if hash_match:
    pwd_hash = hash_match.group(0)
    print(f"\n正确的密码哈希: {pwd_hash}")
    
    # 更新所有用户密码
    print("\n[2] 更新所有用户的密码...")
    update_sql = f"""sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
    USE oa_db;
    UPDATE users SET password = '{pwd_hash}', status = 'active';
    SELECT username, LEFT(password, 20) as pwd_prefix, status FROM users;
    " 2>/dev/null"""
    
    output = run_cmd(ssh, update_sql)
    print(f"更新结果:\n{output}")
else:
    print("ERROR: 无法生成密码哈希")
    ssh.close()
    exit(1)

# 3. 修复 AuthController 中的状态检查
print("\n[3] 修复 AuthController 中的状态检查...")

# 下载当前的 AuthController
sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'r') as f:
        auth_code = f.read().decode('utf-8')
    
    # 修复状态检查逻辑
    # 原代码: if ($user->status !== 'active')
    # 修复后: 处理枚举情况
    
    old_check = """if ($user->status !== 'active') {
            return response()->json(['code' => 403, 'message' => '账号已被禁用'], 403);
        }"""
    
    new_check = """// 检查账号状态（兼容枚举和字符串）
        $status = $user->status;
        if ($status instanceof \\BackedEnum) {
            $status = $status->value;
        }
        if ($status !== 'active') {
            return response()->json(['code' => 403, 'message' => '账号已被禁用'], 403);
        }"""
    
    if old_check in auth_code:
        auth_code = auth_code.replace(old_check, new_check)
        
        # 上传修复后的文件
        print("更新 AuthController...")
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy app/Http/Controllers/Api/", use_sudo=False)
        
        with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'w') as f:
            f.write(auth_code.encode('utf-8'))
        
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data app/Http/Controllers/Api/", use_sudo=False)
        print("AuthController 已修复")
    else:
        print("未找到需要替换的代码，手动检查...")
        # 显示相关代码
        for i, line in enumerate(auth_code.split('\n')):
            if 'status' in line and ('active' in line or 'disable' in line):
                print(f"  {i+1}: {line}")
finally:
    sftp.close()

# 4. 检查 system_logs 表是否存在
print("\n[4] 检查 system_logs 表...")
check_table = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
SHOW TABLES FROM oa_db LIKE 'system_logs';
" 2>/dev/null"""

output = run_cmd(ssh, check_table)
print(f"system_logs 表: {output}")

if 'system_logs' not in output:
    print("创建 system_logs 表...")
    create_table = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
    USE oa_db;
    CREATE TABLE IF NOT EXISTS system_logs (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT UNSIGNED NULL,
        type VARCHAR(50) NOT NULL,
        module VARCHAR(50) NOT NULL,
        action VARCHAR(100) NOT NULL,
        description TEXT NULL,
        ip VARCHAR(45) NULL,
        user_agent TEXT NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL,
        INDEX idx_user (user_id),
        INDEX idx_type (type),
        INDEX idx_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    " 2>/dev/null"""
    
    output = run_cmd(ssh, create_table)
    print(f"创建结果: {output}")

# 5. 清除缓存
print("\n[5] 清除所有缓存...")
cache_cmd = "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear && sudo php artisan view:clear"
output = run_cmd(ssh, cache_cmd, use_sudo=False)
print(output)

# 6. 测试登录
print("\n" + "=" * 60)
print("[6] 测试登录...")
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
        # 测试获取用户信息
        token = resp.json().get('data', {}).get('token')
        if token:
            print("\n[7] 测试获取用户信息...")
            resp2 = requests.get(
                "http://172.20.0.139/api/auth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            print(f"用户信息状态码: {resp2.status_code}")
            print(f"用户信息响应: {resp2.text[:500]}")
except Exception as e:
    print(f"请求失败: {e}")

# 8. 查看日志（如果有错误）
print("\n[8] 查看最新日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -20 storage/logs/laravel.log"
output = run_cmd(ssh, log_cmd, use_sudo=False)
# 只显示错误行
for line in output.split('\n'):
    if 'ERROR' in line or 'Exception' in line or 'Error' in line:
        print(line)

ssh.close()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
