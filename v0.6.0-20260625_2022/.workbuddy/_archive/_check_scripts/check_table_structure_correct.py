#!/usr/bin/env python3
# D:\work\website\OA\.workbuddy\check_table_structure_correct.py
# 检查152服务器上的实际表结构和字段名

import paramiko
import time

# 服务器配置
host = '152.136.115.121'
username = 'ubuntu'
password = 'Aa782997781.'

def check_structure():
    try:
        print("🔌 正在连接152服务器...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)
        print("✅ SSH连接成功!")
        
        # 获取数据库配置
        print("🔍 获取数据库配置...")
        stdin, stdout, stderr = ssh.exec_command("cd /var/www/oa-api && grep DB_ .env | grep -v '#'")
        db_config = stdout.read().decode('utf-8').strip()
        print(f"📄 数据库配置:\n{db_config}\n")
        
        # 提取数据库名和密码
        db_name = 'security_oa'  # 从之前输出得知
        db_pass = 'oa_pg_pwd_782997781'  # 从之前输出得知
        
        # 检查重要的表结构
        tables_to_check = [
            'employee_profiles',
            'service_tickets', 
            'attendance_records',
            'expense_claims',
            'purchase_orders',
            'sales_opportunities',
            'vehicles',
            'inventory_items',
            'disk_folders',
            'knowledge_articles'
        ]
        
        for table in tables_to_check:
            print(f"📋 检查表: {table}")
            stdin, stdout, stderr = ssh.exec_command(f"sudo -u postgres psql -d {db_name} -c '\\d {table}' 2>&1")
            structure = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            
            if structure:
                print(f"{structure}\n")
            elif error:
                print(f"❌ 错误: {error}\n")
            else:
                print(f"ℹ️ 表 {table} 可能不存在或无法访问\n")
        
        ssh.close()
        print("✅ 检查完成!")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print(" 检查152服务器上的实际表结构")
    print("=" * 60 + "\n")
    
    check_structure()