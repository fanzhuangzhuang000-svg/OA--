#!/usr/bin/env python3
"""
开启 Laravel 调试模式并查看详细错误：
1. 设置 APP_DEBUG=true
2. 清除配置缓存
3. 测试登录并查看详细错误
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
print("开启调试模式并查看详细错误")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查当前 APP_DEBUG 设置
print("\n[1] 检查当前 APP_DEBUG 设置...")
debug_check = "cd /var/www/oa-api && sudo grep 'APP_DEBUG' .env"
output = run_cmd(ssh, debug_check, use_sudo=False)
print(f"当前设置: {output.strip()}")

# 2. 设置为 true
print("\n[2] 设置 APP_DEBUG=true...")
# 下载 .env 文件
sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/.env', 'r') as f:
        env_content = f.read().decode('utf-8')
    
    # 替换 APP_DEBUG
    if 'APP_DEBUG=false' in env_content:
        env_content = env_content.replace('APP_DEBUG=false', 'APP_DEBUG=true')
    elif 'APP_DEBUG=TRUE' in env_content:
        env_content = env_content.replace('APP_DEBUG=TRUE', 'APP_DEBUG=true')
    else:
        env_content += '\nAPP_DEBUG=true\n'
    
    # 上传
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy .env", use_sudo=False)
    
    with sftp.open('/var/www/oa-api/.env', 'w') as f:
        f.write(env_content.encode('utf-8'))
    
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data .env", use_sudo=False)
    
    print("APP_DEBUG 已设置为 true")
    
finally:
    sftp.close()

# 3. 清除配置缓存
print("\n[3] 清除配置缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan config:clear && sudo php artisan cache:clear 2>&1")
print(output)

# 4. 清除日志
print("\n[4] 清除日志...")
run_cmd(ssh, "cd /var/www/oa-api && sudo bash -c 'echo > storage/logs/laravel.log'", use_sudo=False)

# 5. 测试登录
print("\n" + "=" * 60)
print("[5] 测试登录（带详细错误）...")
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

# 6. 立即查看日志
print("\n[6] 查看详细错误日志...")
log_cmd = "cd /var/www/oa-api && sudo cat storage/logs/laravel.log 2>/dev/null"
output = run_cmd(ssh, log_cmd, use_sudo=False)

if output.strip():
    print("完整错误日志：")
    # 显示完整日志
    lines = output.split('\n')
    for i, line in enumerate(lines[:80]):  # 显示前80行
        print(line)
else:
    print("（日志为空）")
    
    # 检查 PHP-FPM 错误
    print("\n检查 PHP-FPM 错误...")
    php_log = "sudo tail -30 /var/log/php8.3-fpm.log 2>/dev/null || echo 'No log'"
    output = run_cmd(ssh, php_log, use_sudo=False)
    if output.strip() and 'No log' not in output:
        print(f"PHP-FPM 日志:\n{output}")

# 7. 如果还是没错误，尝试直接访问路由并捕获异常
print("\n[7] 使用 artisan route:list 检查路由...")
route_cmd = "cd /var/www/oa-api && sudo php artisan route:list --path=auth/login 2>&1 | head -20"
output = run_cmd(ssh, route_cmd, use_sudo=False)
print(f"路由列表:\n{output}")

# 8. 检查 AuthController 语法和是否能加载
print("\n[8] 测试 AuthController 是否能加载...")
test_cmd = """cd /var/www/oa-api && sudo php -r "
require 'vendor/autoload.php';
\\$app = require 'bootstrap/app.php';
\\$app->make(Illuminate\\Contracts\\Http\\Kernel::class)->bootstrap();
echo 'OK';
" 2>&1"""
output = run_cmd(ssh, test_cmd, use_sudo=False)
print(f"应用加载测试: {output}")

ssh.close()

print("\n" + "=" * 60)
print("调试完成")
print("=" * 60)
