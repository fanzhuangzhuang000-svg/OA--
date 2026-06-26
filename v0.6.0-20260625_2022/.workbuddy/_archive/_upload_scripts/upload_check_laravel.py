#!/usr/bin/env python3
"""
上传并运行使用Laravel的检查脚本
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
        local_path = 'D:/work/website/OA/.workbuddy/check_all_tables_laravel.php'
        remote_path = '/tmp/check_all_tables.php'
        
        print(f"📤 正在上传...")
        sftp.put(local_path, remote_path)
        print("✅ 上传成功")
        sftp.close()
        
        # 运行PHP脚本
        print("\n" + "=" * 60)
        print("运行检查脚本（这可能需要1-2分钟）")
        print("=" * 60)
        
        cmd_run = f"php {remote_path}"
        stdin, stdout, stderr = ssh.exec_command(cmd_run, get_pty=True, timeout=300)
        
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
            if "❌ 空白表" in line:
                capture = True
                continue
            if capture and line.strip():
                if line.startswith("   ") and ". " in line:
                    table = line.strip().split('. ', 1)[1].strip()
                    empty_tables.append(table)
            if "⚠️ 低数据表" in line:
                capture = False
        
        print("\n" + "=" * 60)
        print("✅ 检查完成")
        print("=" * 60)
        
        if empty_tables:
            print(f"\n❌ 发现 {len(empty_tables)} 张空白表")
            print("   需要为这些表生成测试数据\n")
            
            # 分类空白表
            modules = {}
            for table in empty_tables:
                # 提取模块前缀
                parts = table.split('_')
                if len(parts) > 1:
                    prefix = parts[0]
                else:
                    prefix = table
                
                if prefix not in modules:
                    modules[prefix] = []
                modules[prefix].append(table)
            
            print("📋 空白表按模块分类：")
            for prefix, tables in modules.items():
                print(f"   {prefix}: {len(tables)} 张表")
                for t in tables[:3]:
                    print(f"      - {t}")
                if len(tables) > 3:
                    print(f"      ... 还有 {len(tables) - 3} 张表")
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
        
        print("\n💡 下一步：")
        print("   是否要为这些空白表生成测试数据？")
