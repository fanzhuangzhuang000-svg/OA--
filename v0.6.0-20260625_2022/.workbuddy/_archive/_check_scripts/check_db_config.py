#!/usr/bin/env python3
"""
获取152服务器上的数据库凭据
"""

import paramiko

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
        print("✅ SSH连接成功")
        
        # 读取.env文件获取数据库配置
        print("\n📄 读取数据库配置...")
        cmd = "cd /var/www/oa-api && grep -E '^(DB_|PGSQL_)' .env | head -20"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print("数据库配置:")
            print(output)
        else:
            print("❌ 无法读取数据库配置")
            if error:
                print(f"错误: {error}")
        
        # 也检查config/database.php
        print("\n📄 读取数据库配置文件...")
        cmd = "cd /var/www/oa-api && cat config/database.php | grep -A 20 'pgsql'"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        output = stdout.read().decode('utf-8')
        if output:
            print("数据库配置(pgsql):")
            print(output)
        
        # 测试数据库连接
        print("\n🧪 测试数据库连接...")
        cmd = """cd /var/www/oa-api && php -r "
require 'vendor/autoload.php';
\\$app = require 'bootstrap/app.php';
\\$app->make(\\Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();
try {
    \\$pdo = DB::connection()->getPdo();
    echo '✅ 数据库连接成功: ' . DB::connection()->getDatabaseName();
} catch (\\Exception \\$e) {
    echo '❌ 数据库连接失败: ' . \\$e->getMessage();
}
"\"
"""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print(output)
        if error:
            print(f"错误: {error}")
        
        # 关闭SSH连接
        ssh.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    main()
