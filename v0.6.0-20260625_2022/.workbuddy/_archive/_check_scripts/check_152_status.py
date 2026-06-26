#!/usr/bin/env python3
"""检查152服务器状态和数据库数据量"""
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
        print("✅ SSH连接成功\n")
        
        # 1. 读取.env获取数据库信息
        print("=" * 60)
        print("1. 读取数据库连接配置...")
        stdin, stdout, stderr = ssh.exec_command('cat /var/www/oa-api/.env | grep DB_')
        env_output = stdout.read().decode()
        print(env_output)
        
        # 2. 检查主要表的数据量
        print("=" * 60)
        print("2. 检查主要表的数据量...")
        
        # 通过psql直接查询
        psql_cmd = """sudo -u www-data psql -h localhost -U oa_user -d oa_db << 'EOF'
SELECT '员工' as name, COUNT(*) as cnt FROM employees
UNION ALL SELECT '客户', COUNT(*) FROM customers
UNION ALL SELECT '项目', COUNT(*) FROM projects
UNION ALL SELECT '考勤', COUNT(*) FROM attendances
UNION ALL SELECT '报销', COUNT(*) FROM expenses
UNION ALL SELECT '车辆', COUNT(*) FROM vehicles
UNION ALL SELECT '库存物品', COUNT(*) FROM inventory_items
UNION ALL SELECT '财务账户', COUNT(*) FROM finance_accounts
UNION ALL SELECT '应收', COUNT(*) FROM finance_receivables
UNION ALL SELECT '应付', COUNT(*) FROM finance_payables
UNION ALL SELECT '网盘文件夹', COUNT(*) FROM disk_folders
UNION ALL SELECT '知识库文章', COUNT(*) FROM knowledge_articles
UNION ALL SELECT '消息', COUNT(*) FROM messages
ORDER BY name;
EOF
"""
        stdin, stdout, stderr = ssh.exec_command(psql_cmd)
        time.sleep(3)
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        if result:
            print(result)
        else:
            print(f"❌ 查询失败: {error}")
            
        # 3. 检查项目数据的时间跨度
        print("=" * 60)
        print("3. 检查数据时间跨度...")
        time_cmd = """sudo -u www-data psql -h localhost -U oa_user -d oa_db << 'EOF'
SELECT 
    '项目' as name,
    MIN(created_at) as earliest,
    MAX(created_at) as latest,
    COUNT(*) as total
FROM projects
UNION ALL
SELECT 
    '考勤',
    MIN(date),
    MAX(date),
    COUNT(*)
FROM attendances
UNION ALL
SELECT 
    '报销',
    MIN(created_at),
    MAX(created_at),
    COUNT(*)
FROM expenses;
EOF
"""
        stdin, stdout, stderr = ssh.exec_command(time_cmd)
        time.sleep(3)
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        if result:
            print(result)
        else:
            print(f"❌ 查询失败: {error}")
        
        ssh.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
