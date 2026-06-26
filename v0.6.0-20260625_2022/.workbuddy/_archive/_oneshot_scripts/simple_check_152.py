#!/usr/bin/env python3
"""
简单检查152服务器数据状态
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
        
        # 获取所有表名
        print("📊 正在查询所有表的数据量...\n")
        cmd = """sudo -u postgres psql -d security_oa -t -c "
        SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
        " """
        
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        output = stdout.read().decode('utf-8')
        
        tables = [line.strip() for line in output.split('\n') if line.strip() and not line.strip().startswith('-')]
        
        print(f"共 {len(tables)} 张表\n")
        print("=" * 60)
        
        # 查询每张表的数据量
        total_records = 0
        for table in tables:
            cmd = f"""sudo -u postgres psql -d security_oa -t -c "SELECT COUNT(*) FROM {table};" """
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
            result = stdout.read().decode('utf-8').strip()
            
            try:
                count = int(result)
                total_records += count
                
                # 只显示有数据的表
                if count > 0:
                    print(f"  {table:30s}: {count:>6,} 条")
            except:
                pass
        
        print("=" * 60)
        print(f"\n总记录数: {total_records:,}")
        print(f"有数据的表: {len([t for t in tables if True])} 张")
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    main()
