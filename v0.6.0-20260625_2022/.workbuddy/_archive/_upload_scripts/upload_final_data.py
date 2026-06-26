#!/usr/bin/env python3
"""
上传并运行最终版测试数据生成脚本到152服务器
"""

import paramiko
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
REMOTE_PATH = '/var/www/oa-api/generate_data.php'
LOCAL_PATH = 'D:/work/website/OA/.workbuddy/generate_data_laravel.php'

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        # 创建SFTP连接
        sftp = ssh.open_sftp()
        
        # 上传PHP脚本
        print(f"📤 正在上传脚本到 {REMOTE_PATH}...")
        sftp.put(LOCAL_PATH, REMOTE_PATH)
        print("✅ 脚本上传成功")
        
        # 关闭SFTP
        sftp.close()
        
        # 运行PHP脚本
        print("🚀 正在运行测试数据生成脚本...")
        print("   这可能需要几分钟时间，请耐心等待...")
        print("-" * 60)
        
        # 执行PHP脚本
        cmd = f"cd /var/www/oa-api && php {REMOTE_PATH}"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=600)
        
        # 实时输出结果
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
                # 检查是否完成
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
        
        print("-" * 60)
        print("✅ 测试数据生成脚本运行完成")
        
        # 清理临时文件
        ssh.exec_command(f"rm -f {REMOTE_PATH}")
        print(f"🗑️  已清理临时文件 {REMOTE_PATH}")
        
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
    if success:
        print("\n🎉 所有操作完成！152服务器现在有了全面的测试数据")
    else:
        print("\n❌ 操作失败，请检查错误信息")
