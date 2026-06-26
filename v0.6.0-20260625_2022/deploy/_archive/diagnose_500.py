#!/usr/bin/env python3
"""
全面诊断 500 错误：
1. 检查 PHP 语法错误
2. 查看完整 Laravel 日志
3. 测试路由是否可访问
4. 检查 User 模型枚举转换问题
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
print("全面诊断 500 错误")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查 PHP 语法错误
print("\n[1] 检查 AuthController PHP 语法...")
syntax_cmd = "cd /var/www/oa-api && sudo php -l app/Http/Controllers/Api/AuthController.php 2>&1"
output = run_cmd(ssh, syntax_cmd, use_sudo=False)
print(f"语法检查: {output}")

# 2. 查看完整的 Laravel 日志（最后 50 行）
print("\n[2] 查看完整 Laravel 日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -50 storage/logs/laravel.log 2>/dev/null"
output = run_cmd(ssh, log_cmd, use_sudo=False)
print("日志最后50行：")
print(output if output.strip() else "（日志文件为空或不存在）")

# 3. 如果日志为空，检查日志文件权限
print("\n[3] 检查日志文件权限...")
log_perm = "cd /var/www/oa-api && sudo ls -la storage/logs/ 2>/dev/null"
output = run_cmd(ssh, log_perm, use_sudo=False)
print(f"日志文件权限:\n{output}")

# 4. 查看 AuthController 完整代码
print("\n[4] 查看 AuthController 完整代码...")
auth_code = get_file_via_ssh(ssh, '/var/www/oa-api/app/Http/Controllers/Api/AuthController.php')
print("AuthController.php 完整内容：")
print(auth_code)

# 5. 检查 User 模型的 status 字段处理
print("\n" + "=" * 60)
print("[5] 检查 User 模型枚举转换...")

# 使用 tinker 测试
tinker_cmd = r"""cd /var/www/oa-api && sudo php artisan tinker --execute="
$user = App\Models\User::where('username', 'admin')->first();
var_dump($user->status);
var_dump($user->status === 'active');
var_dump($user->status->value ?? null);
" 2>&1"""

output = run_cmd(ssh, tinker_cmd, use_sudo=False)
print(f"Tinker 测试:\n{output}")

# 6. 临时修复：移除 User 模型的 status 枚举转换
print("\n[6] 临时修复：移除 status 枚举转换...")
user_model = get_file_via_ssh(ssh, '/var/www/oa-api/app/Models/User.php')

if 'status' in user_model and 'UserStatus' in user_model:
    print("找到 status 枚举转换，尝试移除...")
    
    # 下载、修改、上传
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy app/Models/User.php", use_sudo=False)
    
    sftp = ssh.open_sftp()
    try:
        # 修改：将 status 枚举转换注释掉或改为字符串
        modified_model = user_model.replace(
            "'status' => \\App\\Enums\\UserStatus::class,",
            "'status' => 'string',  // 临时：禁用枚举转换"
        )
        
        with sftp.open('/var/www/oa-api/app/Models/User.php', 'w') as f:
            f.write(modified_model.encode('utf-8'))
        
        print("User.php 已修改（status 枚举转换已禁用）")
        
        # 恢复权限
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data app/Models/User.php", use_sudo=False)
        
    finally:
        sftp.close()
else:
    print("未找到 status 枚举转换")

# 7. 清除所有缓存
print("\n[7] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear && sudo php artisan view:clear 2>&1")
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
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"请求失败: {e}")

# 9. 再次查看日志
print("\n[9] 再次查看日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -30 storage/logs/laravel.log 2>/dev/null"
output = run_cmd(ssh, log_cmd, use_sudo=False)
if output.strip():
    # 显示包含 error 或 Error 的行
    for line in output.split('\n'):
        if 'error' in line.lower() or 'exception' in line.lower() or '[' in line:
            print(line)
else:
    print("（无新日志）")
    # 也许日志没写入，检查 PHP error log
    php_error = "sudo tail -20 /var/log/php8.3-fpm.log 2>/dev/null || sudo tail -20 /var/log/php/error.log 2>/dev/null || echo 'No PHP error log'"
    output = run_cmd(ssh, php_error, use_sudo=False)
    print(f"PHP 错误日志:\n{output}")

ssh.close()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
