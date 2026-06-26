#!/usr/bin/env python3
"""检查152服务器数据库状态 - 修复版"""
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
        
        # 2. 使用正确的方法查询数据库
        print("=" * 60)
        print("2. 检查主要表的数据量...")
        
        # 方法1: 使用PGPASSWORD环境变量
        psql_cmd = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -h 127.0.0.1 -U oa_user -d security_oa << 'EOF'
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
        time.sleep(5)
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        if result and 'count' in result.lower():
            print(result)
        else:
            print(f"方法1失败: {error}")
            print("\n尝试方法2: 通过Laravel artisan命令...")
            
            # 方法2: 使用Laravel的DB facade
            artisan_cmd = """cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="
            $tables = ['employees', 'customers', 'projects', 'attendances', 'expenses', 'vehicles', 'inventory_items', 'finance_accounts', 'finance_receivables', 'finance_payables', 'disk_folders', 'knowledge_articles', 'messages'];
            foreach($tables as $table) {
                try {
                    $count = DB::table($table)->count();
                    echo $table . ': ' . $count . PHP_EOL;
                } catch (Exception $e) {
                    echo $table . ': 表不存在' . PHP_EOL;
                }
            }
            "}"
            stdin, stdout, stderr = ssh.exec_command(artisan_cmd)
            time.sleep(10)
            result = stdout.read().decode()
            error = stderr.read().decode()
            print(result)
            if error:
                print(f"错误: {error}")
        
        ssh.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
