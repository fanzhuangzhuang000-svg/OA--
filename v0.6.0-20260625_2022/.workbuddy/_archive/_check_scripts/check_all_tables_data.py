#!/usr/bin/env python3
"""
检查152服务器上所有表的数据量，找出空白模块
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
        print("=" * 60)
        print("获取所有表名")
        print("=" * 60)
        
        cmd_get_tables = """sudo -u postgres psql -d security_oa -t -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
" 2>&1"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd_get_tables, get_pty=True, timeout=30)
        tables_output = stdout.read().decode('utf-8', errors='ignore')
        
        tables = [t.strip() for t in tables_output.split('\n') if t.strip() and not t.strip().startswith('-')]
        print(f"找到 {len(tables)} 张表\n")
        
        # 检查每张表的数据量
        print("=" * 60)
        print("检查每张表的数据量")
        print("=" * 60)
        
        empty_tables = []
        low_data_tables = []
        table_stats = []
        
        for table in tables:
            cmd_count = f"""sudo -u postgres psql -d security_oa -t -c "SELECT COUNT(*) FROM {table};" 2>&1"""
            stdin, stdout, stderr = ssh.exec_command(cmd_count, get_pty=True, timeout=10)
            count_output = stdout.read().decode('utf-8', errors='ignore').strip()
            
            try:
                count = int(count_output)
                table_stats.append((table, count))
                
                if count == 0:
                    empty_tables.append(table)
                elif count < 10:
                    low_data_tables.append((table, count))
            except:
                pass
        
        # 按数据量排序
        table_stats.sort(key=lambda x: x[1])
        
        # 输出统计结果
        print(f"\n📊 数据量统计：")
        print(f"   总表数: {len(tables)}")
        print(f"   空白表 (0条): {len(empty_tables)}")
        print(f"   低数据表 (<10条): {len(low_data_tables)}")
        print(f"   有数据表 (≥10条): {len(tables) - len(empty_tables) - len(low_data_tables)}")
        
        # 输出空白表
        if empty_tables:
            print(f"\n❌ 空白表 (0条数据，需要生成):")
            for i, table in enumerate(empty_tables, 1):
                print(f"   {i}. {table}")
        
        # 输出低数据表
        if low_data_tables:
            print(f"\n⚠️ 低数据表 (<10条，建议增加):")
            for i, (table, count) in enumerate(low_data_tables, 1):
                print(f"   {i}. {table}: {count}条")
        
        # 输出有数据的表（前20个）
        print(f"\n✅ 有数据的表 (≥10条):")
        has_data = [(t, c) for t, c in table_stats if c >= 10]
        for i, (table, count) in enumerate(has_data[:30], 1):
            print(f"   {i}. {table}: {count}条")
        if len(has_data) > 30:
            print(f"   ... 还有 {len(has_data) - 30} 张表")
        
        print("\n" + "=" * 60)
        print("✅ 检查完成")
        print("=" * 60)
        
        # 关闭SSH连接
        ssh.close()
        
        return empty_tables, low_data_tables
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return [], []

if __name__ == "__main__":
    empty, low = main()
    if empty or low:
        print("\n💡 建议：")
        print("   1. 为空白表生成测试数据")
        print("   2. 为低数据表增加更多测试数据")
    else:
        print("\n🎉 所有表都有数据！")
