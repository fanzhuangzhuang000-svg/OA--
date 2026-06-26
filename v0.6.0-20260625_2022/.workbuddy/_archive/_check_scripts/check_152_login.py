#!/usr/bin/env python3
"""
检查152服务器上的登录页面内容
"""
import paramiko

HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 检查index.html内容
        print("\n📋 检查前端文件...")
        cmd = "grep -o 'v1.0.[0-9]' /var/www/oa-web/index.html | head -1"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        version = stdout.read().decode('utf-8').strip()
        print(f"   版本号: {version if version else '未找到'}")
        
        # 检查JS文件中是否有演示账号
        print("\n🔍 检查演示账号提示...")
        cmd2 = "grep -r '演示账号' /var/www/oa-web/ 2>/dev/null | wc -l"
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        count = stdout.read().decode('utf-8').strip()
        print(f"   包含'演示账号'的文件数: {count}")
        
        # 检查Nginx缓存配置
        print("\n⚙️ 检查Nginx配置...")
        cmd3 = "grep -r 'Cache-Control' /etc/nginx/sites-enabled/ 2>/dev/null | head -3"
        stdin, stdout, stderr = ssh.exec_command(cmd3)
        cache_config = stdout.read().decode('utf-8').strip()
        print(f"   缓存配置: {cache_config if cache_config else '未配置'}")
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    main()
