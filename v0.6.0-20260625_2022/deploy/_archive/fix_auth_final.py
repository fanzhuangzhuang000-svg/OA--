#!/usr/bin/env python3
"""
全面修复 auth 中间件问题：
1. 检查所有注册路由
2. 检查 Authenticate 中间件是否存在
3. 确保 API 请求返回 JSON
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
print("全面修复 auth 中间件")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查注册路由
print("\n[1] 检查注册路由...")
route_list = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan route:list 2>&1 | head -60")
print(route_list[:3000])

# 2. 检查 Authenticate 中间件
print("\n[2] 检查 Authenticate 中间件...")
check_auth_mw = "cd /var/www/oa-api && sudo ls -la app/Http/Middleware/ 2>/dev/null"
output = run_cmd(ssh, check_auth_mw, use_sudo=False)
print(f"中间件文件:\n{output}")

# 检查 Authenticate.php 是否存在
check_authenticate = "cd /var/www/oa-api && sudo test -f app/Http/Middleware/Authenticate.php && echo 'EXISTS' || echo 'MISSING'"
output = run_cmd(ssh, check_authenticate, use_sudo=False)
print(f"Authenticate.php: {output.strip()}")

if 'MISSING' in output:
    print("\n⚠ Authenticate.php 不存在！需要创建...")
    
    # 创建 Authenticate 中间件
    auth_mw = """<?php

namespace App\\Http\\Middleware;

use Illuminate\\Auth\\Middleware\\Authenticate as Middleware;
use Illuminate\\Http\\Request;

class Authenticate extends Middleware
{
    protected function redirectTo(Request $request): ?string
    {
        if ($request->expectsJson()) {
            return null;
        }
        
        return route('login');
    }
}
"""
    
    sftp = ssh.open_sftp()
    try:
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy app/Http/Middleware/ 2>/dev/null", use_sudo=False)
        with sftp.open('/var/www/oa-api/app/Http/Middleware/Authenticate.php', 'w') as f:
            f.write(auth_mw)
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data app/Http/Middleware/ 2>/dev/null", use_sudo=False)
        print("✅ Authenticate.php 已创建")
    finally:
        sftp.close()

# 3. 检查 RedirectIfAuthenticated.php
print("\n[3] 检查 RedirectIfAuthenticated 中间件...")
check_guest_mw = "cd /var/www/oa-api && sudo test -f app/Http/Middleware/RedirectIfAuthenticated.php && echo 'EXISTS' || echo 'MISSING'"
output = run_cmd(ssh, check_guest_mw, use_sudo=False)
print(f"RedirectIfAuthenticated.php: {output.strip()}")

if 'MISSING' in output:
    print("创建 RedirectIfAuthenticated.php...")
    
    guest_mw = """<?php

namespace App\\Http\\Middleware;

use App\\Providers\\RouteServiceProvider;
use Closure;
use Illuminate\\Http\\Request;
use Illuminate\\Support\\Facades\\Auth;

class RedirectIfAuthenticated
{
    public function handle(Request $request, Closure $next, string ...$guards)
    {
        $guards = empty($guards) ? [null] : $guards;

        foreach ($guards as $guard) {
            if (Auth::guard($guard)->check()) {
                return redirect(RouteServiceProvider::HOME);
            }
        }

        return $next($request);
    }
}
"""
    
    sftp = ssh.open_sftp()
    try:
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy app/Http/Middleware/ 2>/dev/null", use_sudo=False)
        with sftp.open('/var/www/oa-api/app/Http/Middleware/RedirectIfAuthenticated.php', 'w') as f:
            f.write(guest_mw)
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data app/Http/Middleware/ 2>/dev/null", use_sudo=False)
        print("✅ RedirectIfAuthenticated.php 已创建")
    finally:
        sftp.close()

# 4. 恢复原始的 bootstrap/app.php 但添加中间件别名
print("\n[4] 更新 bootstrap/app.php（保留原始功能+添加中间件别名）...")

sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/bootstrap/app.php', 'r') as f:
        content = f.read().decode('utf-8')
    
    # 检查当前内容是否需要更新
    if 'alias' not in content or 'Authenticate' not in content:
        # 替换 withMiddleware 内容
        old_mw = """->withMiddleware(function (Middleware $middleware) {
        $middleware->statefulApi();"""
        
        new_mw = """->withMiddleware(function (Middleware $middleware) {
        $middleware->statefulApi();
        
        $middleware->alias([
            'auth' => \\App\\Http\\Middleware\\Authenticate::class,
        ]);"""
        
        if old_mw in content:
            content = content.replace(old_mw, new_mw)
            print("✅ 已添加 auth 中间件别名")
        else:
            print("⚠ 未找到匹配模式，检查当前内容...")
    else:
        print("✅ 中间件别名已配置")
    
    # 保存
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy bootstrap/app.php", use_sudo=False)
    with sftp.open('/var/www/oa-api/bootstrap/app.php', 'w') as f:
        f.write(content.encode('utf-8'))
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data bootstrap/app.php", use_sudo=False)
    
finally:
    sftp.close()

# 5. 清除缓存
print("\n[5] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear 2>&1")
print(output)

# 6. 测试
print("\n" + "=" * 60)
print("[6] 测试完整流程...")

try:
    # 登录
    resp = requests.post("http://172.20.0.139/api/auth/login",
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    
    print(f"登录状态: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ 登录成功")
        token = resp.json()['data']['token']
        
        # 获取用户信息
        resp2 = requests.get("http://172.20.0.139/api/auth/userinfo",
                            headers={"Authorization": f"Bearer {token}",
                                    "Accept": "application/json"}, timeout=10)
        
        print(f"\n用户信息状态: {resp2.status_code}")
        
        # 检查是否返回 HTML
        content_type = resp2.headers.get('content-type', '')
        if 'text/html' in content_type:
            print(f"⚠ 返回 HTML 而不是 JSON！")
            print(f"响应前200字符: {resp2.text[:200]}")
        else:
            print(f"用户信息响应: {resp2.text[:800]}")
        
        if resp2.status_code == 200:
            print("\n🎉 所有功能正常！")
        elif resp2.status_code == 401:
            print("\n⚠ 401 未授权 - Token 可能无效")
            print(f"响应: {resp2.text}")
        else:
            print(f"\n❌ 状态码: {resp2.status_code}")
            
except Exception as e:
    print(f"请求错误: {e}")

ssh.close()
print("\n完成")
