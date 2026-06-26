#!/usr/bin/env python3
"""
上传并运行调试脚本到152服务器
"""

import paramiko
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
TMP_PATH = '/tmp/debug_table_structure.php'
FINAL_PATH = '/var/www/oa-api/debug_table_structure.php'
LOCAL_PATH = 'D:/work/website/OA/.workbuddy/debug_table_structure.php'

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
        
        # 1. 上传PHP脚本到/tmp目录
        print(f"📤 正在上传脚本到 {TMP_PATH}...")
        sftp.put(LOCAL_PATH, TMP_PATH)
        print("✅ 脚本上传到临时目录成功")
        
        # 关闭SFTP
        sftp.close()
        
        # 2. 使用sudo cp复制到目标目录
        print(f"📋 正在复制脚本到 {FINAL_PATH}...")
        cmd1 = f"sudo cp {TMP_PATH} {FINAL_PATH}"
        stdin, stdout, stderr = ssh.exec_command(cmd1, get_pty=True, timeout=30)
        time.sleep(2)  # 等待复制完成
        
        # 3. 修改文件所有者
        print("🔧 正在修改文件权限...")
        cmd2 = f"sudo chown www-data:www-data {FINAL_PATH}"
        ssh.exec_command(cmd2, timeout=10)
        time.sleep(1)
        
        # 4. 清理临时文件
        ssh.exec_command(f"rm -f {TMP_PATH}")
        print(f"🗑️  已清理临时文件 {TMP_PATH}")
        
        # 5. 运行PHP脚本
        print("🚀 正在运行调试脚本...")
        print("-" * 60)
        
        # 执行PHP脚本
        cmd3 = f"cd /var/www/oa-api && sudo -u www-data php {FINAL_PATH}"
        stdin, stdout, stderr = ssh.exec_command(cmd3, get_pty=True, timeout=120)
        
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
        print("✅ 调试脚本运行完成")
        
        # 6. 清理脚本文件
        ssh.exec_command(f"sudo rm -f {FINAL_PATH}")
        print(f"🗑️  已清理脚本文件 {FINAL_PATH}")
        
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
        print("\n🎉 调试完成！现在知道了表结构")
    else:
        print("\n❌ 操作失败，请检查错误信息")
