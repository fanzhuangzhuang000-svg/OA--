#!/usr/bin/env python3
"""
1. 查看完整的 Laravel 错误日志
2. 创建 AuthController
3. 上传到服务器
"""

import paramiko
import io

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
print("修复 AuthController 缺失问题")
print("=" * 60)

ssh = ssh_connect()

# 1. 查看完整的错误日志
print("\n[1] 查看完整的 Laravel 错误日志...")
log_cmd = "cd /var/www/oa-api && sudo cat storage/logs/laravel.log | tail -50"
output = run_cmd(ssh, log_cmd, use_sudo=False)
print("最新日志：")
# 只显示关键信息
lines = output.split('\n')
for line in lines:
    if 'ERROR' in line or 'Class' in line or 'not found' in line or 'AuthController' in line:
        print(line)

# 2. 确认 AuthController 不存在
print("\n[2] 确认 AuthController 不存在...")
check_cmd = "cd /var/www/oa-api && sudo find . -name 'AuthController.php' 2>/dev/null"
output = run_cmd(ssh, check_cmd, use_sudo=False)
print(f"搜索结果: {output}")

# 3. 在本地创建 AuthController
print("\n[3] 在本地创建 AuthController...")

auth_controller_code = """<?php

namespace App\\Http\\Controllers\\Api;

use App\\Models\\User;
use Illuminate\\Http\\Request;
use Illuminate\\Http\\JsonResponse;
use Illuminate\\Support\\Facades\\Hash;
use Illuminate\\Support\\Facades\\Auth;

class AuthController extends \\App\\Http\\Controllers\\Controller
{
    /**
     * 用户登录
     */
    public function login(Request $request): JsonResponse
    {
        $data = $request->validate([
            'username' => 'required|string',
            'password' => 'required|string',
        ]);

        // 查找用户（支持用户名或邮箱登录）
        $user = User::where('username', $data['username'])
            ->orWhere('email', $data['username'])
            ->first();

        // 检查用户是否存在
        if (! $user) {
            return response()->json([
                'code'    => 401,
                'message' => '用户名或密码错误',
            ]);
        }

        // 检查密码
        if (! Hash::check($data['password'], $user->password)) {
            return response()->json([
                'code'    => 401,
                'message' => '用户名或密码错误',
            ]);
        }

        // 检查账号状态（使用枚举值比较）
        if ($user->status !== null && method_exists($user->status, 'value')) {
            // 如果是枚举
            if ($user->status->value !== 'active') {
                return response()->json([
                    'code'    => 403,
                    'message' => '账号已被禁用',
                ]);
            }
        } else {
            // 如果是字符串
            if ($user->status !== 'active') {
                return response()->json([
                    'code'    => 403,
                    'message' => '账号已被禁用',
                ]);
            }
        }

        // 更新最后登录信息
        $user->update([
            'last_login_at' => now(),
            'last_login_ip'  => $request->ip(),
        ]);

        // 创建 token（使用 Sanctum）
        $token = $user->createToken('auth_token')->plainTextToken;

        return response()->json([
            'code'    => 0,
            'message' => '登录成功',
            'data'    => [
                'token' => $token,
                'user'  => [
                    'id'       => $user->id,
                    'name'     => $user->name,
                    'username' => $user->username,
                    'email'    => $user->email,
                    'avatar'   => $user->avatar,
                    'roles'    => $user->getRoleNames(),
                ],
            ],
        ]);
    }

    /**
     * 用户登出
     */
    public function logout(Request $request): JsonResponse
    {
        $request->user()->currentAccessToken()->delete();

        return response()->json([
            'code'    => 0,
            'message' => '登出成功',
        ]);
    }

    /**
     * 获取当前用户信息
     */
    public function userInfo(Request $request): JsonResponse
    {
        $user = $request->user();

        return response()->json([
            'code' => 0,
            'data' => [
                'id'          => $user->id,
                'name'        => $user->name,
                'username'    => $user->username,
                'email'       => $user->email,
                'phone'       => $user->phone,
                'avatar'      => $user->avatar,
                'department'  => $user->department?->name,
                'position'    => $user->position?->name,
                'roles'       => $user->getRoleNames(),
                'permissions' => $user->getAllPermissions()->pluck('name'),
            ],
        ]);
    }
}
"""

# 保存到本地
local_path = 'D:/work/website/OA/pc-api/app/Http/Controllers/Api/AuthController.php'
with open(local_path, 'w', encoding='utf-8') as f:
    f.write(auth_controller_code)

print(f"AuthController 已创建: {local_path}")

# 4. 上传到服务器
print("\n[4] 上传 AuthController 到服务器...")

# 先修改权限
run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy app/Http/Controllers/Api/", use_sudo=False)

# 上传文件
sftp = ssh.open_sftp()
remote_path = '/var/www/oa-api/app/Http/Controllers/Api/AuthController.php'
with sftp.open(remote_path, 'w') as f:
    f.write(auth_controller_code)
sftp.close()

print(f"已上传到: {remote_path}")

# 恢复权限
run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data app/Http/Controllers/Api/", use_sudo=False)

# 5. 清除缓存
print("\n[5] 清除路由和配置缓存...")
cache_cmd = "cd /var/www/oa-api && sudo php artisan cache:clear && sudo php artisan route:clear && sudo php artisan config:clear"
output = run_cmd(ssh, cache_cmd, use_sudo=False)
print(output)

# 6. 测试登录
print("\n" + "=" * 60)
print("[6] 测试登录...")
import requests

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

# 7. 如果还是失败，查看日志
print("\n[7] 查看最新错误日志...")
log_cmd = "cd /var/www/oa-api && sudo tail -20 storage/logs/laravel.log"
output = run_cmd(ssh, log_cmd, use_sudo=False)
print(output)

ssh.close()

print("\n" + "=" * 60)
print("AuthController 修复完成")
print("=" * 60)
