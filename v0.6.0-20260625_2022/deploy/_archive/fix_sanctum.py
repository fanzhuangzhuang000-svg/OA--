#!/usr/bin/env python3
"""
修复 createToken 失败问题：
1. 检查 personal_access_tokens 表是否存在
2. 运行 Sanctum 迁移
3. 检查完整错误信息
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
print("修复 createToken 失败问题")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查 personal_access_tokens 表是否存在
print("\n[1] 检查 personal_access_tokens 表...")
check_table = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
SHOW TABLES FROM oa_db LIKE 'personal_access_tokens';
" 2>/dev/null"""

output = run_cmd(ssh, check_table)
print(f"查询结果: {output}")

if 'personal_access_tokens' not in output:
    print("\n❌ personal_access_tokens 表不存在！")
    print("[2] 运行 Sanctum 迁移...")
    
    migrate_cmd = "cd /var/www/oa-api && sudo php artisan vendor:publish --provider='Laravel\\Sanctum\\SanctumServiceProvider' --force 2>&1"
    output = run_cmd(ssh, migrate_cmd, use_sudo=False)
    print(f"发布 Sanctum 配置: {output[:500]}")
    
    # 运行迁移
    migrate_cmd2 = "cd /var/www/oa-api && sudo php artisan migrate 2>&1"
    output = run_cmd(ssh, migrate_cmd2, use_sudo=False)
    print(f"迁移结果:\n{output}")
    
    # 再次检查表
    output = run_cmd(ssh, check_table)
    print(f"\n再次检查: {output}")
else:
    print("✅ personal_access_tokens 表已存在")

# 3. 检查表结构
print("\n[3] 检查 personal_access_tokens 表结构...")
desc_table = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
DESC oa_db.personal_access_tokens;
" 2>/dev/null"""

output = run_cmd(ssh, desc_table)
print(f"表结构:\n{output}")

# 4. 检查 Sanctum 配置
print("\n[4] 检查 Sanctum 配置...")
config_check = "cd /var/www/oa-api && sudo ls -la config/sanctum.php 2>/dev/null && echo 'Config exists' || echo 'Config missing'"
output = run_cmd(ssh, config_check, use_sudo=False)
print(f"Sanctum 配置: {output}")

# 5. 检查 User 模型是否使用 HasApiTokens
print("\n[5] 检查 User 模型 HasApiTokens trait...")
user_model_check = "cd /var/www/oa-api && sudo grep -n 'HasApiTokens' app/Models/User.php"
output = run_cmd(ssh, user_model_check, use_sudo=False)
print(f"HasApiTokens: {output}")

# 6. 清除日志并重新测试
print("\n[6] 清除日志并重新测试登录...")
clear_log = "cd /var/www/oa-api && sudo bash -c 'echo > storage/logs/laravel.log'"
run_cmd(ssh, clear_log, use_sudo=False)

# 测试登录
try:
    resp = requests.post(
        "http://172.20.0.139/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    print(f"\n登录状态码: {resp.status_code}")
    print(f"登录响应: {resp.text}")
except Exception as e:
    print(f"请求失败: {e}")

# 7. 立即查看完整日志
print("\n[7] 查看完整错误日志...")
log_cmd = "cd /var/www/oa-api && sudo cat storage/logs/laravel.log 2>/dev/null"
output = run_cmd(ssh, log_cmd, use_sudo=False)

# 提取关键信息
if output.strip():
    lines = output.split('\n')
    print("完整日志：")
    for line in lines[:50]:  # 只显示前50行
        print(line)
else:
    print("（日志为空）")
    
    # 检查 PHP-FPM 错误日志
    print("\n检查 PHP-FPM 错误日志...")
    php_log = "sudo grep -r 'error' /var/log/php* 2>/dev/null | tail -20 || echo 'No PHP log'"
    output = run_cmd(ssh, php_log, use_sudo=False)
    print(output[:1000])

# 8. 如果还是 500，尝试简化 AuthController（暂时注释掉 token 创建）
print("\n" + "=" * 60)
print("[8] 如果问题在 createToken，临时测试 Without Token...")
print("=" * 60)

# 创建一个测试脚本内容
test_php = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

use App\\Models\\User;
use Illuminate\\Support\\Facades\\Hash;

// 查找用户
$user = User::where('username', 'admin')->first();
if (! $user) {
    echo "User not found\\n";
    exit(1);
}

echo "User found: " . $user->name . "\\n";
echo "Status: " . ($user->status ?? 'null') . "\\n";

// 检查密码
if (Hash::check('admin123', $user->password)) {
    echo "Password correct\\n";
} else {
    echo "Password incorrect\\n";
}

// 尝试创建 token
try {
    $token = $user->createToken('test');
    echo "Token created: " . $token->plainTextToken . "\\n";
} catch (\\Exception $e) {
    echo "Token creation failed: " . $e->getMessage() . "\\n";
    echo "File: " . $e->getFile() . ":" . $e->getLine() . "\\n";
}
"""

# 上传测试脚本
print("上传测试脚本...")
sftp = ssh.open_sftp()
with sftp.open('/tmp/test_login.php', 'w') as f:
    f.write(test_php)
sftp.close()

# 执行测试脚本
print("执行测试脚本...")
output = run_cmd(ssh, "sudo php /tmp/test_login.php 2>&1", use_sudo=False)
print(f"测试脚本输出:\n{output}")

ssh.close()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
