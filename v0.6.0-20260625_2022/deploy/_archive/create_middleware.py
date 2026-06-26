#!/usr/bin/env python3
"""
创建缺失的中间件文件并修复路由问题
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
    return stdout.read().decode('utf-8', errors='replace') + stderr.read().decode('utf-8', errors='replace')

print("=" * 60)
print("创建缺失的中间件文件")
print("=" * 60)

ssh = ssh_connect()

# 1. 创建 Middleware 目录
print("\n[1] 创建 Middleware 目录...")
run_cmd(ssh, "cd /var/www/oa-api && sudo mkdir -p app/Http/Middleware && sudo chown nbcy:nbcy app/Http/Middleware", use_sudo=False)
print("✅ 目录已创建")

# 2. 创建 Authenticate 中间件
print("\n[2] 创建 Authenticate.php...")

auth_mw_content = """<?php

namespace App\\Http\\Middleware;

use Illuminate\\Auth\\Middleware\\Authenticate as Middleware;
use Illuminate\\Http\\Request;

class Authenticate extends Middleware
{
    /**
     * Get the path the user should be redirected to when they are not authenticated.
     */
    protected function redirectTo(Request $request): ?string
    {
        return $request->expectsJson() ? null : route('login');
    }
}
"""

sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/app/Http/Middleware/Authenticate.php', 'w') as f:
        f.write(auth_mw_content)
    print("✅ Authenticate.php 已创建")
except Exception as e:
    print(f"创建失败: {e}")
finally:
    sftp.close()

# 3. 创建 RedirectIfAuthenticated 中间件
print("\n[3] 创建 RedirectIfAuthenticated.php...")

guest_mw_content = """<?php

namespace App\\Http\\Middleware;

use Closure;
use Illuminate\\Http\\Request;
use Illuminate\\Support\\Facades\\Auth;
use Symfony\\Component\\HttpFoundation\\Response;

class RedirectIfAuthenticated
{
    public function handle(Request $request, Closure $next, string ...$guards): Response
    {
        $guards = empty($guards) ? [null] : $guards;

        foreach ($guards as $guard) {
            if (Auth::guard($guard)->check()) {
                return redirect('/');
            }
        }

        return $next($request);
    }
}
"""

sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/app/Http/Middleware/RedirectIfAuthenticated.php', 'w') as f:
        f.write(guest_mw_content)
    print("✅ RedirectIfAuthenticated.php 已创建")
except Exception as e:
    print(f"创建失败: {e}")
finally:
    sftp.close()

# 4. 恢复文件权限
run_cmd(ssh, "cd /var/www/oa-api && sudo chown -R www-data:www-data app/Http/Middleware", use_sudo=False)

# 5. 验证文件
print("\n[4] 验证中间件文件...")
verify = run_cmd(ssh, "cd /var/www/oa-api && sudo ls -la app/Http/Middleware/")
print(verify)

# 6. 检查 PHP 语法
print("\n[5] 检查 PHP 语法...")
syntax = run_cmd(ssh, "cd /var/www/oa-api && sudo php -l app/Http/Middleware/Authenticate.php 2>&1")
print(syntax)
syntax2 = run_cmd(ssh, "cd /var/www/oa-api && sudo php -l app/Http/Middleware/RedirectIfAuthenticated.php 2>&1")
print(syntax2)

# 7. 清除缓存
print("\n[6] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear 2>&1")
print(output)

# 8. 测试
print("\n" + "=" * 60)
print("[7] 测试完整流程...")

try:
    # 登录
    resp = requests.post("http://172.20.0.139/api/auth/login",
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    
    print(f"登录状态: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ 登录成功")
        data = resp.json()
        token = data['data']['token']
        print(f"用户: {data['data']['user']['name']}")
        
        # 获取用户信息
        print("\n[8] 测试获取用户信息...")
        resp2 = requests.get("http://172.20.0.139/api/auth/userinfo",
                            headers={"Authorization": f"Bearer {token}",
                                    "Accept": "application/json"}, timeout=10)
        
        print(f"用户信息状态: {resp2.status_code}")
        content_type = resp2.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        
        if 'application/json' in content_type:
            print(f"用户信息响应: {resp2.text[:800]}")
        else:
            print(f"⚠ 返回了 HTML（前200字符）: {resp2.text[:200]}")
        
        if resp2.status_code == 200:
            print("\n" + "=" * 60)
            print("🎉🎉🎉 后端 API 完全正常工作！")
            print("=" * 60)
            print("\n默认登录账号：")
            print("  用户名: admin")
            print("  密码: admin123")
            print("\nAPI 基地址: http://172.20.0.139/api")
            
            # 测试仪表盘
            print("\n[9] 测试仪表盘 API...")
            resp3 = requests.get("http://172.20.0.139/api/dashboard/stats",
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=10)
            print(f"仪表盘状态: {resp3.status_code}")
            if resp3.status_code == 200:
                print(f"仪表盘数据: {resp3.text[:500]}")
        else:
            print(f"\n❌ 用户信息获取失败")
    else:
        print(f"❌ 登录失败: {resp.text}")
        
except Exception as e:
    print(f"请求错误: {e}")

# 10. 查看错误日志
print("\n[10] 查看错误日志...")
log = run_cmd(ssh, "cd /var/www/oa-api && sudo tail -10 storage/logs/laravel.log 2>/dev/null")
if log.strip():
    for line in log.split('\n'):
        if 'ERROR' in line or 'error' in line.lower() or '[' in line[:2]:
            print(line)
else:
    print("（无新错误）")

ssh.close()
print("\n完成")
