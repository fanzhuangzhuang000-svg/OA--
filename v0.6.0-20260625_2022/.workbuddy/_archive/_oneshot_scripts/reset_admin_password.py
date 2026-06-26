#!/usr/bin/env python3
"""
重置152服务器admin密码并测试登录
"""
import paramiko
import json
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 1. 查看现有密码哈希格式
        print("=" * 60)
        print("1. 查看现有密码哈希格式")
        print("=" * 60)
        
        cmd_check_hash = """sudo -u postgres psql -d security_oa -c "
SELECT id, username, substring(password from 1 for 30) as hash_prefix 
FROM users 
WHERE username = 'admin';
" 2>&1"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_check_hash, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        
        # 2. 使用PHP生成正确的bcrypt哈希，然后更新数据库
        print("\n" + "=" * 60)
        print("2. 使用Laravel方式重置admin密码")
        print("=" * 60)
        
        cmd_reset_pwd = """
cd /var/www/oa-api && sudo -u www-data php -r '
require_once "vendor/autoload.php";
$app = require_once "bootstrap/app.php";
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

use Illuminate\\Support\\Facades\\Hash;

$user = App\\Models\\User::where("username", "admin")->first();
if ($user) {
    $user->password = Hash::make("Admin@2026");
    $user->save();
    echo "密码已重置为: Admin@2026" . PHP_EOL;
    echo "用户名: " . $user->username . PHP_EOL;
    echo "哈希: " . substr($user->password, 0, 30) . "..." . PHP_EOL;
} else {
    echo "用户不存在，将创建新用户" . PHP_EOL;
}
'
"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_reset_pwd, get_pty=True, timeout=60)
        
        # 实时输出
        output = ""
        while True:
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                print(chunk, end='')
                output += chunk
            elif stderr.channel.recv_ready():
                chunk = stderr.channel.recv(4096).decode('utf-8', errors='ignore')
                print(chunk, end='')
                output += chunk
            else:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
        
        # 3. 测试登录API（使用正确的端点）
        print("\n" + "=" * 60)
        print("3. 测试登录API")
        print("=" * 60)
        
        cmd_test_login = """curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"admin","password":"Admin@2026"}' """
        
        stdin, stdout, stderr = ssh.exec_command(cmd_test_login, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 检查是否登录成功
        if '"code":0' in output or '"token"' in output:
            print("\n✅ 登录成功！admin账号可以正常登录了")
            print("   用户名: admin")
            print("   密码: Admin@2026")
        elif '"code":4' in output or '密码错误' in output:
            print("\n❌ 密码错误，需要重新检查")
            print("   请检查Laravel的密码加密方式")
        else:
            print("\n⚠️ 登录失败，请检查错误信息")
        
        # 4. 更新前端演示账号提示（如果需要）
        print("\n" + "=" * 60)
        print("4. 检查前端演示账号提示")
        print("=" * 60)
        
        cmd_check_demo = """grep -A2 "demo-tip" /var/www/oa-web/index.html 2>/dev/null | head -10"""
        stdin, stdout, stderr = ssh.exec_command(cmd_check_demo, get_pty=True, timeout=10)
        output = stdout.read().decode('utf-8', errors='ignore')
        
        if "admin" in output and "Admin@2026" in output:
            print("✅ 前端演示账号提示已正确显示")
            print("   用户名: admin")
            print("   密码: Admin@2026")
        else:
            print("⚠️ 前端演示账号提示可能未部署或内容不正确")
        
        print("\n" + "=" * 60)
        print("✅ 检查完成")
        print("=" * 60)
        
        # 关闭SSH连接
        ssh.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 操作失败，请检查错误信息")
