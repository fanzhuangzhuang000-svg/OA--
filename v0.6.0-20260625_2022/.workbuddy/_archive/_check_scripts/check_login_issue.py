#!/usr/bin/env python3
"""
检查152服务器登录路由和重置admin密码
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
        
        # 1. 检查路由列表
        print("=" * 60)
        print("1. 检查登录相关路由")
        print("=" * 60)
        
        cmd_routes = """cd /var/www/oa-api && sudo -u www-data php artisan route:list 2>&1 | grep -i "login\|auth\|user" | head -20"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_routes, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 2. 直接修改数据库中的admin密码
        print("\n" + "=" * 60)
        print("2. 直接修改数据库中的admin密码")
        print("=" * 60)
        
        # 先获取数据库密码
        cmd_get_db_pwd = """cd /var/www/oa-api && sudo -u www-data grep DB_PASSWORD .env | cut -d '=' -f2"""
        stdin, stdout, stderr = ssh.exec_command(cmd_get_db_pwd, get_pty=True, timeout=10)
        db_password = stdout.read().decode('utf-8', errors='ignore').strip()
        print(f"数据库密码: {db_password}")
        
        # 使用psql直接修改密码
        cmd_reset_pwd = f"""sudo -u postgres psql -d security_oa -c "
UPDATE users 
SET password = crypt('Admin@2026', gen_salt('bf')) 
WHERE username = 'admin';
" 2>&1"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_reset_pwd, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 3. 检查用户表
        print("\n" + "=" * 60)
        print("3. 检查用户表")
        print("=" * 60)
        
        cmd_check_users = """sudo -u postgres psql -d security_oa -c "
SELECT id, username, name, email, status, created_at 
FROM users 
LIMIT 10;
" 2>&1"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_check_users, get_pty=True, timeout=30)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 4. 测试登录API（使用正确的端点）
        print("\n" + "=" * 60)
        print("4. 测试登录API（尝试不同端点）")
        print("=" * 60)
        
        # 尝试多个可能的登录端点
        endpoints = [
            "http://localhost/api/login",
            "http://localhost/api/auth/login",
            "http://localhost/api/user/login"
        ]
        
        for endpoint in endpoints:
            print(f"\n尝试端点: {endpoint}")
            cmd_test = f"""curl -s -X POST {endpoint} \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{{"username":"admin","password":"Admin@2026"}}' """
            
            stdin, stdout, stderr = ssh.exec_command(cmd_test, get_pty=True, timeout=10)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            print(output[:200])
            if "token" in output.lower() or "code" in output.lower():
                print(f"  ✅ 可能正确的端点: {endpoint}")
                break
        
        # 5. 检查API文档或控制器
        print("\n" + "=" * 60)
        print("5. 检查登录控制器")
        print("=" * 60)
        
        cmd_find_controller = """find /var/www/oa-api/app/Http/Controllers -name "*Login*.php" -o -name "*Auth*.php" 2>/dev/null | head -5"""
        stdin, stdout, stderr = ssh.exec_command(cmd_find_controller, get_pty=True, timeout=10)
        output = stdout.read().decode('utf-8', errors='ignore')
        print(output)
        
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
