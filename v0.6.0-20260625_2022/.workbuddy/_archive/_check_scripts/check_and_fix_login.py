#!/usr/bin/env python3
"""
检查152服务器上admin账号的状态
"""
import paramiko
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
        
        # 1. 检查admin账号状态
        print("=" * 60)
        print("1. 检查admin账号状态")
        print("=" * 60)
        
        cmd_check_admin = """
cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="
\$user = \\App\\Models\\User::where('username', 'admin')->first();
if (\$user) {
    echo 'ID: ' . \$user->id . PHP_EOL;
    echo '用户名: ' . \$user->username . PHP_EOL;
    echo '姓名: ' . \$user->name . PHP_EOL;
    echo '邮箱: ' . \$user->email . PHP_EOL;
    echo '状态: ' . (\$user->status ?? 'N/A') . PHP_EOL;
    echo '密码哈希: ' . substr(\$user->password, 0, 20) . '...' . PHP_EOL;
    echo '创建时间: ' . \$user->created_at . PHP_EOL;
} else {
    echo '用户不存在';
}
"
"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_check_admin, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 2. 重置admin密码为 Admin@2026
        print("\n" + "=" * 60)
        print("2. 重置admin密码为 Admin@2026")
        print("=" * 60)
        
        cmd_reset_pwd = """
cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="
\$user = \\App\\Models\\User::where('username', 'admin')->first();
if (\$user) {
    \$user->password = bcrypt('Admin@2026');
    \$user->save();
    echo '密码已重置为: Admin@2026' . PHP_EOL;
    echo '用户名: ' . \$user->username . PHP_EOL;
} else {
    // 创建admin用户
    \$user = new \\App\\Models\\User();
    \$user->username = 'admin';
    \$user->name = '系统管理员';
    \$user->email = 'admin@oa.com';
    \$user->password = bcrypt('Admin@2026');
    \$user->status = 1;
    \$user->save();
    echo '已创建admin用户' . PHP_EOL;
    echo '密码: Admin@2026' . PHP_EOL;
}
"
"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_reset_pwd, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 3. 验证密码
        print("\n" + "=" * 60)
        print("3. 验证密码是否正确")
        print("=" * 60)
        
        cmd_verify = """
cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="
\$user = \\App\\Models\\User::where('username', 'admin')->first();
if (\$user) {
    \$check = password_verify('Admin@2026', \$user->password);
    echo '密码验证结果: ' . (\$check ? '成功' : '失败') . PHP_EOL;
    echo '用户名: ' . \$user->username . PHP_EOL;
} else {
    echo '用户不存在';
}
"
"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_verify, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 4. 测试登录API
        print("\n" + "=" * 60)
        print("4. 测试登录API")
        print("=" * 60)
        
        cmd_test_login = """
curl -s -X POST http://localhost/api/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"admin","password":"Admin@2026"}' \
  | python3 -m json.tool 2>/dev/null || curl -s -X POST http://localhost/api/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"admin","password":"Admin@2026"}'
"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_test_login, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        print("\n" + "=" * 60)
        print("✅ 检查完成")
        print("=" * 60)
        print("\n如果登录成功，会显示token。")
        print("如果失败，会显示错误信息。")
        
        # 关闭SSH连接
        ssh.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 操作失败，请检查错误信息")
