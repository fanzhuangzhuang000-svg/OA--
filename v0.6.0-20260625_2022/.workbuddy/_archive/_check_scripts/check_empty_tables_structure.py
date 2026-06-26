#!/usr/bin/env python3
"""
检查空白表的结构
"""
import paramiko

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
        
        # 检查几个关键空白表的结构
        tables_to_check = [
            'employee_skills',
            'project_pool',
            'purchase_plans',
            'quotation_items',
            'certificates'
        ]
        
        for table in tables_to_check:
            print("=" * 60)
            print(f"检查表结构: {table}")
            print("=" * 60)
            
            cmd_desc = f"""sudo -u postgres psql -d security_oa -c "\\d {table}" 2>&1"""
            stdin, stdout, stderr = ssh.exec_command(cmd_desc, get_pty=True, timeout=30)
            
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
                    import time
                    time.sleep(0.1)
            
            if "Did not find any relation" in output:
                print(f"\n❌ 表 {table} 不存在！\n")
            else:
                print(f"\n✅ 表 {table} 存在\n")
        
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
    main()
