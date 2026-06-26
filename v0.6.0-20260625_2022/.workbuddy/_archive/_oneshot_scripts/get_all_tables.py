#!/usr/bin/env python3
# D:\work\website\OA\.workbuddy\get_all_tables.py
# 获取152服务器上所有的表名

import paramiko

host = '152.136.115.121'
username = 'ubuntu'
password = 'Aa782997781.'

def get_tables():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)
        
        # 获取所有表名
        stdin, stdout, stderr = ssh.exec_command("sudo -u postgres psql -d security_oa -c \"SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;\"")
        tables_output = stdout.read().decode('utf-8').strip()
        
        print("📊 152服务器上的所有表:")
        print(tables_output)
        
        # 获取表数量
        stdin, stdout, stderr = ssh.exec_command("sudo -u postgres psql -d security_oa -c \"SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';\"")
        count_output = stdout.read().decode('utf-8').strip()
        print(f"\n📈 总表数: {count_output}")
        
        ssh.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    get_tables()