#!/usr/bin/env python3
"""
上传并运行检查所有表数据量的PHP脚本
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
        print("上传检查脚本")
        print("=" * 60)
        
        sftp = ssh.open_sftp()
        local_path = 'D:/work/website/OA/.workbuddy/check_all_tables.php'
        remote_path = '/tmp/check_all_tables.php'
        
        print(f"📤 正在上传 {local_path} -> {remote_path}...")
        sftp.put(local_path, remote_path)
        print("✅ 上传成功")
        sftp.close()
        
        # 运行PHP脚本
        print("\n" + "=" * 60)
        print("运行检查脚本")
        print("=" * 60)
        
        cmd_run = f"php {remote_path}"
        stdin, stdout, stderr = ssh.exec_command(cmd_run, get_pty=True, timeout=120)
        
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
        
        # 解析输出，获取空白表
        empty_tables = []
        lines = output.split('\n')
        capture = False
        for line in lines:
            if "空白表" in line:
                capture = True
                continue
            if capture and line.strip():
                if line.startswith("   ") and "." in line:
                    table = line.strip().split('. ', 1)[1].strip()
                    empty_tables.append(table)
            if "⚠️ 低数据表" in line:
                capture = False
        
        print("\n" + "=" * 60)
        print("✅ 检查完成")
        print("=" * 60)
        
        if empty_tables:
            print(f"\n❌ 发现 {len(empty_tables)} 张空白表")
            print("   需要为这些表生成测试数据")
            print("\n💡 下一步：")
            print("   1. 为空白表生成测试数据")
            print("   2. 为低数据表增加更多数据")
        else:
            print("\n🎉 所有表都有数据！")
        
        # 清理临时文件
        ssh.exec_command(f"rm -f {remote_path}")
        print(f"\n🗑️  已清理临时文件")
        
        ssh.close()
        return empty_tables
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return []

if __name__ == "__main__":
    empty_tables = main()
    if empty_tables:
        print("\n" + "=" * 60)
        print("空白表列表：")
        print("=" * 60)
        for i, table in enumerate(empty_tables, 1):
            print(f"   {i}. {table}")
