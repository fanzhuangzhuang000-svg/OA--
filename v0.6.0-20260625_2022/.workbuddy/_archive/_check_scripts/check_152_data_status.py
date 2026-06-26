#!/usr/bin/env python3
"""
检查152服务器当前数据状态
"""

import paramiko

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        print("================ 检查当前数据状态 =================\n")
        
        # 使用psql查询所有表的数据量
        cmd = """sudo -u postgres psql -d security_oa -c "
        SELECT 
            schemaname || '.' || tablename as table_name,
            (xpath('/row/cnt/text()', xml_out)[1]::text)::int as row_count
        FROM (
            SELECT 
                schemaname,
                tablename,
                query_to_xml('SELECT count(*) as cnt FROM ' || quote_ident(schemaname) || '.' || quote_ident(tablename), false, true, '') as xml_out
            FROM pg_tables
            WHERE schemaname = 'public'
        ) t
        ORDER BY row_count DESC
        LIMIT 50;
        " 2>&1"""
        
        print("📊 正在查询所有表的数据量...")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print(output)
        if error:
            print(f"错误: {error}")
        
        # 也查询数据库大小
        print("\n================ 数据库信息 =================\n")
        
        cmd = """sudo -u postgres psql -d security_oa -c "
        SELECT 
            pg_size_pretty(pg_database_size('security_oa')) as database_size,
            (SELECT count(*) FROM pg_tables WHERE schemaname = 'public') as table_count
        " 2>&1"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        
        output = stdout.read().decode('utf-8')
        if output:
            print(output)
        
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
        print("\n✅ 数据状态检查完成！")
    else:
        print("\n❌ 检查失败，请检查错误信息")
