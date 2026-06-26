#!/usr/bin/env python3
"""检查152服务器数据库状态"""
import paramiko
import time

HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"正在连接 {HOST}...")
        ssh.connect(HOST, username=USER, password=PASS, timeout=15)
        print("SSH连接成功")
        
        # 读取数据库连接信息
        print("\n1. 读取数据库连接信息...")
        stdin, stdout, stderr = ssh.exec_command('cat /var/www/oa-api/.env | grep -E "DB_|PG"')
        env_output = stdout.read().decode()
        print(env_output)
        
        # 检查数据库表记录数
        print("\n2. 检查主要表的数据量...")
        sql = """
SELECT 
    'employees' as table_name, COUNT(*) as count FROM employees
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'attendances', COUNT(*) FROM attendances
UNION ALL SELECT 'expenses', COUNT(*) FROM expenses
UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL SELECT 'inventory_items', COUNT(*) FROM inventory_items
UNION ALL SELECT 'finance_accounts', COUNT(*) FROM finance_accounts
UNION ALL SELECT 'finance_receivables', COUNT(*) FROM finance_receivables
UNION ALL SELECT 'finance_payables', COUNT(*) FROM finance_payables
UNION ALL SELECT 'disk_folders', COUNT(*) FROM disk_folders
UNION ALL SELECT 'knowledge_articles', COUNT(*) FROM knowledge_articles
UNION ALL SELECT 'messages', COUNT(*) FROM messages
ORDER BY table_name;
"""
        
        # 需要先获取数据库密码
        stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="echo config(\'database.connections.pgsql.password\')"')
        db_pass_output = stdout.read().decode().strip()
        print(f"数据库密码: {db_pass_output[:10]}...")
        
        # 直接通过psql查询
        psql_cmd = f'''sudo -u www-data psql -h localhost -U oa_user -d oa_db -c "{sql}"'''
        stdin, stdout, stderr = ssh.exec_command(psql_cmd)
        time.sleep(2)
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        if result:
            print("表数据量:")
            print(result)
        else:
            print(f"查询失败: {error}")
            # 尝试另一种方法
            print("\n尝试通过.env文件获取密码...")
            stdin, stdout, stderr = ssh.exec_command("cat /var/www/oa-api/.env | grep DB_PASSWORD")
            db_password = stdout.read().decode().strip().split('=')[1] if '=' in stdout.read().decode() else ''
            print(f"DB_PASSWORD: {db_password}")
        
        ssh.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
