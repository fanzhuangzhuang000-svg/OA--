# D:\work\website\OA\.workbuddy\upload_and_run_v3.py
# 上传并运行V3版测试数据生成脚本

import paramiko
import time

host = '152.136.115.121'
username = 'ubuntu'
password = 'Aa782997781.'
remote_path = '/tmp/generate_v3.php'
local_path = r'D:\work\website\OA\.workbuddy\generate_correct_data_v3.php'

def upload_and_run():
    try:
        print("🔌 正在连接152服务器...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)
        print("✅ SSH连接成功!")
        
        # 1. 上传PHP脚本
        print(f"📁 上传脚本到 {remote_path}...")
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        print("✅ 上传完成!")
        
        # 2. 运行PHP脚本
        print("🚀 运行测试数据生成脚本...")
        stdin, stdout, stderr = ssh.exec_command(f"cd /tmp && php {remote_path}", get_pty=True)
        
        # 实时输出
        output = ""
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                output += chunk
                print(chunk, end='')
            time.sleep(0.1)
        
        # 获取剩余输出
        remaining = stdout.read().decode('utf-8', errors='ignore')
        output += remaining
        print(remaining, end='')
        
        error_output = stderr.read().decode('utf-8', errors='ignore')
        
        if error_output:
            print("\n❌ 错误输出:")
            print(error_output)
        
        # 3. 清理临时文件
        print("\n🧹 清理临时文件...")
        ssh.exec_command(f"rm -f {remote_path}")
        
        ssh.close()
        print("✅ 任务完成!")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print(" 为152服务器生成正确的测试数据 (V3版)")
    print("=" * 60 + "\n")
    
    success = upload_and_run()
    
    if success:
        print("\n" + "=" * 60)
        print(" ✅ 所有模块的测试数据已生成！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(" ❌ 生成测试数据失败")
        print("=" * 60)