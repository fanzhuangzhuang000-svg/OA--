#!/usr/bin/env python3
"""
上传并运行检查脚本到152服务器
"""

import paramiko
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'
TMP_PATH = '/tmp/check_leads_opportunities.php'
FINAL_PATH = '/var/www/oa-api/check_leads_opportunities.php'
LOCAL_PATH = 'D:/work/website/OA/.workbuddy/check_leads_opportunities.php'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功")
        
        sftp = ssh.open_sftp()
        print(f"📤 正在上传脚本到 {TMP_PATH}...")
        sftp.put(LOCAL_PATH, TMP_PATH)
        print("✅ 脚本上传到临时目录成功")
        sftp.close()
        
        print(f"📋 正在复制脚本到 {FINAL_PATH}...")
        cmd1 = f"sudo cp {TMP_PATH} {FINAL_PATH}"
        ssh.exec_command(cmd1, timeout=30)
        time.sleep(1)
        
        print("🔧 正在修改文件权限...")
        cmd2 = f"sudo chown www-data:www-data {FINAL_PATH}"
        ssh.exec_command(cmd2, timeout=10)
        time.sleep(1)
        
        ssh.exec_command(f"rm -f {TMP_PATH}")
        print(f"🗑️  已清理临时文件 {TMP_PATH}")
        
        print("🚀 正在运行检查脚本...")
        print("-" * 60)
        
        cmd3 = f"cd /var/www/oa-api && sudo -u www-data php {FINAL_PATH}"
        stdin, stdout, stderr = ssh.exec_command(cmd3, get_pty=True, timeout=120)
        
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
        
        print("-" * 60)
        print("✅ 检查脚本运行完成")
        
        ssh.exec_command(f"sudo rm -f {FINAL_PATH}")
        print(f"🗑️  已清理脚本文件 {FINAL_PATH}")
        
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
        print("\n🎉 检查完成！现在知道了数据状态")
    else:
        print("\n❌ 操作失败，请检查错误信息")
