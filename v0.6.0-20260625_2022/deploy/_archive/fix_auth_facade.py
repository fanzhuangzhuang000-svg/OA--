#!/usr/bin/env python3
"""
修复 auth Facade 未注册问题：
1. 检查 auth facade 是否可解析
2. 检查服务提供者配置
3. 手动注册 auth facade
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
    full_cmd = (f"echo {SUDO_PASS} | sudo -S {cmd}") if use_sudo else cmd
    stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace') + stderr.read().decode('utf-8', errors='replace')

print("=" * 60)
print("修复 auth Facade 问题")
print("=" * 60)

ssh = ssh_connect()

# 1. 检查 auth facade 是否可解析
print("\n[1] 测试 auth facade...")

test_auth = r"""cd /var/www/oa-api && sudo php -r "
require 'vendor/autoload.php';
$app = require 'bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Http\Kernel::class);

// 测试 auth 是否可解析
try {
    $auth = $app->make('auth');
    echo 'auth resolved: ' . get_class($auth) . PHP_EOL;
} catch (Exception $e) {
    echo 'auth NOT resolvable: ' . $e->getMessage() . PHP_EOL;
}

// 测试 auth manager
try {
    $authManager = $app->make(Illuminate\Auth\AuthManager::class);
    echo 'AuthManager resolved: ' . get_class($authManager) . PHP_EOL;
} catch (Exception $e) {
    echo 'AuthManager NOT resolvable: ' . $e->getMessage() . PHP_EOL;
}
" 2>&1"""

output = run_cmd(ssh, test_auth, use_sudo=False)
print(f"测试结果:\n{output}")

# 2. 检查 config/app.php 中的 aliases 和 providers
print("\n[2] 检查 config/app.php...")
app_config = run_cmd(ssh, "cd /var/www/oa-api && sudo cat config/app.php 2>/dev/null")

# 搜索 aliases 和 providers
if 'aliases' in app_config:
    print("✅ aliases 部分存在")
    # 搜索 auth alias
    for i, line in enumerate(app_config.split('\n')):
        if 'aliases' in line.lower() or 'Auth' in line:
            print(f"  {i+1}: {line}")
else:
    print("❌ aliases 部分不存在")

# 3. 检查 bootstrap/app.php 中的 shouldRenderJsonWhen
print("\n[3] 检查 bootstrap/app.php...")
bootstrap = run_cmd(ssh, "cd /var/www/oa-api && sudo cat bootstrap/app.php 2>/dev/null")
print(bootstrap[:1500])

# 4. 检查 config/app.php 中是否缺少 aliases
print("\n[4] 检查是否需要在 config/app.php 中添加 aliases...")
if "'aliases'" not in app_config:
    print("需要在 config/app.php 中添加 aliases")
    
    # 下载并修改 config/app.php
    sftp = ssh.open_sftp()
    try:
        with sftp.open('/var/www/oa-api/config/app.php', 'r') as f:
            content = f.read().decode('utf-8')
        
        # 在最后的 ]; 之前添加 aliases
        if content.rstrip().endswith('];'):
            content = content.rstrip()[:-2] + """
    'aliases' => [
        'Auth' => Illuminate\\Support\\Facades\\Auth::class,
    ],
];
"""
        
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown nbcy:nbcy config/app.php", use_sudo=False)
        with sftp.open('/var/www/oa-api/config/app.php', 'w') as f:
            f.write(content.encode('utf-8'))
        run_cmd(ssh, "cd /var/www/oa-api && sudo chown www-data:www-data config/app.php", use_sudo=False)
        
        print("✅ 已添加 Auth alias 到 config/app.php")
        
    finally:
        sftp.close()

# 5. 清除缓存
print("\n[5] 清除所有缓存...")
output = run_cmd(ssh, "cd /var/www/oa-api && sudo php artisan config:clear && sudo php artisan cache:clear && sudo php artisan route:clear 2>&1")
print(output)

# 6. 测试
print("\n" + "=" * 60)
print("[6] 测试获取用户信息...")

try:
    resp = requests.post("http://172.20.0.139/api/auth/login",
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    if resp.status_code == 200:
        token = resp.json()['data']['token']
        print("✅ 登录成功")
        
        resp2 = requests.get("http://172.20.0.139/api/auth/userinfo",
                            headers={"Authorization": f"Bearer {token}",
                                    "Accept": "application/json"}, timeout=10)
        
        print(f"用户信息状态: {resp2.status_code}")
        if resp2.status_code == 200:
            print(f"✅ 用户信息获取成功!")
            print(f"响应: {resp2.text[:500]}")
        else:
            print(f"响应: {resp2.text[:500]}")
    else:
        print(f"❌ 登录失败: {resp.text}")
except Exception as e:
    print(f"错误: {e}")

ssh.close()
print("\n完成")
