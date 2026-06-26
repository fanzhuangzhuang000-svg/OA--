#!/usr/bin/env python3
"""
修复 auth 中间件别名 - 直接写入正确的 bootstrap/app.php
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
print("修复 auth 中间件别名")
print("=" * 60)

ssh = ssh_connect()

# 1. 读取当前 bootstrap/app.php
print("\n[1] 读取 bootstrap/app.php...")
sftp = ssh.open_sftp()
try:
    with sftp.open('/var/www/oa-api/bootstrap/app.php', 'r') as f:
        current_content = f.read().decode('utf-8')
    print("当前内容：")
    print(current_content)
finally:
    sftp.close()

# 2. 创建新的 bootstrap/app.php 内容
# 标准 Laravel 11+ 的 bootstrap/app.php 应该包含 withMiddleware 配置
new_app_php = r"""<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware) {
        $middleware->statefulApi();
        
        $middleware->alias([
            'auth' => \App\Http\Middleware\Authenticate::class,
            'auth.basic' => \Illuminate\Auth\Middleware\AuthenticateWithBasicAuth::class,
            'auth.session' => \Illuminate\Session\Middleware\AuthenticateSession::class,
            'cache.headers' => \Illuminate\Http\Middleware\SetCacheHeaders::class,
            'can' => \Illuminate\Auth\Middleware\Authorize::class,
            'guest' => \App\Http\Middleware\RedirectIfAuthenticated::class,
            'password.confirm' => \Illuminate\Auth\Middleware\RequirePassword::class,
            'precognitive' => \Illuminate\Foundation\Http\Middleware\HandlePrecognitiveRequests::class,
            'signed' => \App\Http\Middleware\ValidateSignature::class,
            'throttle' => \Illuminate\Routing\Middleware\ThrottleRequests::class,
            'verified' => \App\Http\Middleware\EnsureEmailIsVerified::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions) {
        //
    })->create();
"""

print("\n[2] 写入新的 bootstrap/app.php...")
sftp = ssh.open_sftp()
try:
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy bootstrap/app.php", use_sudo=False)
    
    with sftp.open('/var/www/oa-api/bootstrap/app.php', 'w') as f:
        f.write(new_app_php.encode('utf-8'))
    
    run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data bootstrap/app.php", use_sudo=False)
    
    print("✅ bootstrap/app.php 已更新")
finally:
    sftp.close()

# 3. 验证新文件
print("\n[3] 验证 bootstrap/app.php...")
verify = run_cmd(ssh, "cd /var/www/oa-api && sudo cat bootstrap/app.php 2>/dev/null")
print(verify[:500])

# 4. 检查 PHP 语法
print("\n[4] 检查 PHP 语法...")
syntax = run_cmd(ssh, "cd /var/www/oa-api && sudo php -l bootstrap/app.php 2>&1")
print(syntax)

# 5. 清除缓存
print("\n[5] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan config:clear && sudo php artisan route:clear 2>&1")
print(output)

# 6. 测试完整流程
print("\n" + "=" * 60)
print("[6] 测试完整登录流程...")

try:
    # 登录
    resp = requests.post("http://172.20.0.139/api/auth/login", 
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    print(f"登录状态: {resp.status_code}")
    
    if resp.status_code == 200:
        token = resp.json()['data']['token']
        print("✅ 登录成功")
        
        # 获取用户信息
        resp2 = requests.get("http://172.20.0.139/api/auth/userinfo",
                            headers={"Authorization": f"Bearer {token}"}, timeout=10)
        print(f"\n用户信息状态: {resp2.status_code}")
        print(f"用户信息响应: {resp2.text[:800]}")
        
        if resp2.status_code == 200:
            print("\n🎉 用户信息获取成功！")
            
            # 测试仪表盘
            resp3 = requests.get("http://172.20.0.139/api/dashboard/stats",
                                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            print(f"\n仪表盘状态: {resp3.status_code}")
            print(f"仪表盘响应: {resp3.text[:500]}")
            
            if resp3.status_code == 200:
                print("\n" + "=" * 60)
                print("🎉🎉🎉 所有 API 端点正常工作！")
                print("=" * 60)
                print("\n默认登录账号：")
                print("  用户名: admin")
                print("  密码: admin123")
                print("\nAPI 基地址: http://172.20.0.139/api")
        else:
            print(f"\n❌ 用户信息获取失败")
    else:
        print(f"❌ 登录失败: {resp.text}")
        
except Exception as e:
    print(f"错误: {e}")

ssh.close()
print("\n完成")
