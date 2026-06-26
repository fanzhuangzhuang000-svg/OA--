#!/usr/bin/env python3
"""
检查152服务器上所有表的数据量（优化版）
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
        
        # 一次性获取所有表的数据量
        print("=" * 60)
        print("获取所有表的数据量")
        print("=" * 60)
        
        cmd_all_counts = """
sudo -u postgres psql -d security_oa -t -c "
SELECT 
    tablename,
    (xpath('/row/cnt/text()', 
        query_to_xml('SELECT COUNT(*) as cnt FROM ' || quote_ident(tablename), false, true, '')))[1]::text::int as row_count
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY row_count ASC, tablename;
" 2>&1 | head -100
"""
        
        # 更简单的方法：使用存储过程
        cmd_simple = """
sudo -u postgres psql -d security_oa -t -c "
DO $$$$
DECLARE
    r RECORD;
    cnt INTEGER;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
        EXECUTE 'SELECT COUNT(*) FROM ' || quote_ident(r.tablename) INTO cnt;
        RAISE NOTICE '%: %', r.tablename, cnt;
    END LOOP;
END $$$$;
" 2>&1 | grep -E "^NOTICE:|^[a-z_]+: [0-9]+" | head -100
"""
        
        # 实际更简单的方法：生成所有COUNT语句
        cmd_generate = """
sudo -u postgres psql -d security_oa -t -c "
SELECT 'SELECT ''' || tablename || ''' as table_name, COUNT(*) as row_count FROM ' || quote_ident(tablename) || ' UNION ALL'
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
" 2>&1 | head -100
"""
        
        # 最简单的方法：直接运行一个Python脚本来检查
        print("使用Python脚本检查所有表的数据量...")
        
        python_script = """
import psycopg2
import sys

try:
    conn = psycopg2.connect("dbname=security_oa user=postgres")
    cur = conn.cursor()
    
    # 获取所有表
    cur.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    tables = [r[0] for r in cur.fetchall()]
    
    empty_tables = []
    low_data_tables = []
    table_stats = []
    
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            table_stats.append((table, count))
            
            if count == 0:
                empty_tables.append(table)
            elif count < 10:
                low_data_tables.append((table, count))
        except:
            pass
    
    print(f"总表数: {len(tables)}")
    print(f"空白表 (0条): {len(empty_tables)}")
    print(f"低数据表 (<10条): {len(low_data_tables)}")
    print(f"有数据表 (≥10条): {len(tables) - len(empty_tables) - len(low_data_tables)}")
    print()
    
    if empty_tables:
        print("❌ 空白表 (0条数据):")
        for i, table in enumerate(empty_tables, 1):
            print(f"   {i}. {table}")
        print()
    
    if low_data_tables:
        print("⚠️ 低数据表 (<10条):")
        for i, (table, count) in enumerate(low_data_tables, 1):
            print(f"   {i}. {table}: {count}条")
        print()
    
    print("✅ 有数据的表 (≥10条):")
    has_data = [(t, c) for t, c in table_stats if c >= 10]
    has_data.sort(key=lambda x: x[1], reverse=True)
    for i, (table, count) in enumerate(has_data[:30], 1):
        print(f"   {i}. {table}: {count}条")
    if len(has_data) > 30:
        print(f"   ... 还有 {len(has_data) - 30} 张表")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""
        
        # 先检查是否安装了psycopg2
        cmd_check_psycopg2 = """python3 -c "import psycopg2; print('psycopg2 available')" 2>&1"""
        stdin, stdout, stderr = ssh.exec_command(cmd_check_psycopg2, timeout=10)
        result = stdout.read().decode('utf-8', errors='ignore').strip()
        
        if "psycopg2 available" not in result:
            print("⚠️ psycopg2未安装，使用psql手动检查...")
            
            # 使用psql检查关键表
            key_tables = [
                "users", "customers", "projects", "employees", "attendance_records",
                "expense_claims", "receivables", "payables", "vehicles", 
                "inventory_items", "finance_accounts", "disk_folders", 
                "knowledge_articles", "service_orders", "purchase_orders",
                "sales_opportunities", "leads", "quotations", "notifications"
            ]
            
            print(f"\n检查 {len(key_tables)} 张关键表的数据量:")
            empty_key_tables = []
            
            for table in key_tables:
                cmd_count = f"""sudo -u postgres psql -d security_oa -t -c "SELECT COUNT(*) FROM {table};" 2>&1"""
                stdin, stdout, stderr = ssh.exec_command(cmd_count, timeout=10)
                count_output = stdout.read().decode('utf-8', errors='ignore').strip()
                
                try:
                    count = int(count_output)
                    status = "✅" if count > 0 else "❌"
                    print(f"   {status} {table}: {count}条")
                    
                    if count == 0:
                        empty_key_tables.append(table)
                except:
                    print(f"   ⚠️ {table}: 表不存在或查询失败")
            
            if empty_key_tables:
                print(f"\n❌ 以下关键表没有数据，需要生成:")
                for t in empty_key_tables:
                    print(f"   - {t}")
        else:
            # 使用psycopg2
            print("✅ psycopg2已安装，使用Python脚本检查...")
            
            # 将Python脚本写入临时文件
            cmd_write_script = f"""cat > /tmp/check_tables.py << 'EOPYTHON'
{python_script}
EOPYTHON
"""
            ssh.exec_command(cmd_write_script, get_pty=True, timeout=10)
            
            # 运行脚本
            cmd_run_script = """python3 /tmp/check_tables.py"""
            stdin, stdout, stderr = ssh.exec_command(cmd_run_script, get_pty=True, timeout=120)
            
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
        
        print("\n" + "=" * 60)
        print("✅ 检查完成")
        print("=" * 60)
        
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
