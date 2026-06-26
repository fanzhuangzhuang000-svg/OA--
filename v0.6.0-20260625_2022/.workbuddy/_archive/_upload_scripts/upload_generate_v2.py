#!/usr/bin/env python3
"""
上传并运行修正版的数据生成脚本
"""
import paramiko
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 上传PHP脚本
        print("=" * 60)
        print("上传数据生成脚本（修正版）")
        print("=" * 60)
        
        sftp = ssh.open_sftp()
        local_path = 'D:/work/website/OA/.workbuddy/generate_missing_data_v2.php'
        remote_path = '/tmp/generate_missing_data.php'
        
        print(f"📤 正在上传...")
        sftp.put(local_path, remote_path)
        print("✅ 上传成功")
        sftp.close()
        
        # 运行PHP脚本
        print("\n" + "=" * 60)
        print("运行数据生成脚本（这可能需要2-3分钟）")
        print("=" * 60)
        
        cmd_run = f"php {remote_path}"
        stdin, stdout, stderr = ssh.exec_command(cmd_run, get_pty=True, timeout=600)
        
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
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
        
        print("\n" + "=" * 60)
        print("✅ 数据生成完成")
        print("=" * 60)
        
        # 清理临时文件
        ssh.exec_command(f"rm -f {remote_path}")
        print(f"\n🗑️  已清理临时文件")
        
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
        print("\n❌ 数据生成失败，请检查错误信息")
