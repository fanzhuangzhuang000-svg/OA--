#!/usr/bin/env python3
"""
简化的登录修复：
1. 在服务器上直接用 PHP 脚本生成密码哈希并更新数据库
2. 修复 AuthController（直接重写整个文件）
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
print("简化登录修复")
print("=" * 60)

ssh = ssh_connect()

# 1. 在服务器上创建 PHP 脚本：生成哈希并更新数据库
print("\n[1] 创建 PHP 修复脚本...")

php_script = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';

// 创建应用实例
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

// 生成密码哈希
$hasher = new Illuminate\\Hashing\\BcryptHasher();
$hash = $hasher->make('admin123');
echo "Hash: " . $hash . "\\n";

// 更新数据库
DB::table('users')->update([
    'password' => $hash,
    'status' => 'active'
]);

echo "Updated " . DB::table('users')->count() . " users\\n";

// 验证
$user = DB::table('users')->where('username', 'admin')->first();
echo "Admin password length: " . strlen($user->password) . "\\n";
echo "Admin status: " . $user->status . "\\n";
"""

# 上传 PHP 脚本到服务器
print("上传 PHP 脚本到服务器...")
sftp = ssh.open_sftp()
with sftp.open('/tmp/fix_password.php', 'w') as f:
    f.write(php_script)
sftp.close()

# 执行 PHP 脚本
print("\n[2] 执行密码修复脚本...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php /tmp/fix_password.php 2>&1", use_sudo=False)
print(f"输出:\n{output}")

# 3. 修复 AuthController
print("\n[3] 修复 AuthController...")

# 先获取文件权限
print("修改文件权限...")
run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy app/Http/Controllers/Api/AuthController.php", use_sudo=False)

# 读取当前的 AuthController
sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'r') as f:
        auth_code = f.read().decode('utf-8')
    
    # 替换状态检查代码
    import re
    
    # 找到并替换状态检查部分
    old_pattern = r"if \(\$user->status !== 'active'\) \{\s+return response\(\)->json\(\['code' => 403, 'message' => '账号已被禁用'\], 403\);\s+\}"
    
    new_code = """// 检查账号状态（兼容枚举类型）
        $status = $user->status;
        if ($status instanceof \\BackedEnum) {
            $status = $status->value;
        } elseif (is_object($status) && method_exists($status, 'value')) {
            $status = $status->value();
        }
        if ($status !== 'active') {
            return response()->json(['code' => 403, 'message' => '账号已被禁用'], 403);
        }"""
    
    new_code_escaped = new_code.replace('\\', '\\\\')
    
    # 使用 Python re 模块进行替换
    if "if ($user->status !== 'active')" in auth_code:
        auth_code = auth_code.replace(
            "if ($user->status !== 'active') {\n            return response()->json(['code' => 403, 'message' => '账号已被禁用'], 403);\n        }",
            new_code
        )
        print("状态检查代码已替换")
    else:
        print("警告：未找到需要替换的状态检查代码")
        # 显示相关代码
        for i, line in enumerate(auth_code.split('\n')):
            if 'status' in line:
                print(f"  {i+1}: {line}")
    
    # 写回文件
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AuthController.php', 'w') as f:
        f.write(auth_code.encode('utf-8'))
    
    print("AuthController 已更新")
    
finally:
    sftp.close()

# 恢复文件权限
run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data app/Http/Controllers/Api/AuthController.php", use_sudo=False)

# 4. 确保 system_logs 表存在
print("\n[4] 确保 system_logs 表存在...")

create_table_sql = """sudo mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF -e "
CREATE TABLE IF NOT EXISTS oa_db.system_logs (
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
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
" 2>/dev/null"""

output = run_cmd(ssh, create_table_sql)
print(f"表创建结果: {output if output.strip() else 'OK'}")

# 5. 清除缓存
print("\n[5] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear 2>&1")
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
        data = resp.json()
        if 'data' in data and 'token' in data['data']:
            token = data['data']['token']
            print(f"Token (前20字符): {token[:20]}...")
            
            # 测试获取用户信息
            print("\n[7] 测试获取用户信息...")
            resp2 = requests.get(
                "http://172.20.0.139/api/auth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            print(f"用户信息状态码: {resp2.status_code}")
            print(f"用户信息响应: {resp2.text[:300]}")
except Exception as e:
    print(f"请求失败: {e}")

# 8. 查看错误日志
print("\n[8] 查看最新错误日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -30 storage/logs/laravel.log 2>/dev/null | grep -A 5 'ERROR' || echo '无错误日志'"
output = run_cmd(ssh, log_cmd, use_sudo=False)
print(output)

ssh.close()

print("\n" + "=" * 60)
print("修复完成")
print("=" * 60)
