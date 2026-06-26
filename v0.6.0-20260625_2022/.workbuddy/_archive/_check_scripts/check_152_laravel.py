#!/usr/bin/env python3
"""通过Laravel artisan检查152服务器数据库状态"""
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
        
        # 通过Laravel tinker检查数据库状态
        print("=" * 60)
        print("检查数据库表数据量...")
        
        # 使用Laravel的DB facade查询
        tinker_code = """
$tables = [
    'employees' => '员工',
    'customers' => '客户', 
    'projects' => '项目',
    'attendances' => '考勤',
    'expenses' => '报销',
    'vehicles' => '车辆',
    'inventory_items' => '库存物品',
    'finance_accounts' => '财务账户',
    'finance_receivables' => '应收',
    'finance_payables' => '应付',
    'disk_folders' => '网盘文件夹',
    'knowledge_articles' => '知识库文章',
    'messages' => '消息'
];

foreach($tables as $table => $name) {
    try {
        $count = DB::table($table)->count();
        echo "{$name}: {$count}\n";
    } catch (Exception $e) {
        echo "{$name}: 表不存在或错误\n";
    }
}
"""
        
        # 将tinker代码写入临时文件
        ssh.exec_command('cat > /tmp/check_tables.php << "EOFPHP"\n' + tinker_code + 'EOFPHP')
        time.sleep(1)
        
        # 运行tinker
        stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan tinker < /tmp/check_tables.php')
        
        # 等待命令完成
        for i in range(10):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
            print(f"等待中... ({i*2}s)")
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print("\n查询结果:")
        print(result)
        if error:
            print(f"\n错误输出: {error}")
        
        # 检查项目数据的时间跨度
        print("\n" + "=" * 60)
        print("检查数据时间跨度...")
        
        time_tinker_code = """
// 检查项目
$projectStats = DB::table('projects')
    ->selectRaw('MIN(created_at) as earliest, MAX(created_at) as latest, COUNT(*) as total')
    ->first();
echo "项目数据:\n";
echo "  最早: " . ($projectStats->earliest ?? '无') . "\n";
echo "  最新: " . ($projectStats->latest ?? '无') . "\n";
echo "  总数: " . ($projectStats->total ?? 0) . "\n\n";

// 检查考勤
$attendanceStats = DB::table('attendances')
    ->selectRaw('MIN(date) as earliest, MAX(date) as latest, COUNT(*) as total')
    ->first();
echo "考勤数据:\n";
echo "  最早: " . ($attendanceStats->earliest ?? '无') . "\n";
echo "  最新: " . ($attendanceStats->latest ?? '无') . "\n";
echo "  总数: " . ($attendanceStats->total ?? 0) . "\n\n";

// 检查报销
$expenseStats = DB::table('expenses')
    ->selectRaw('MIN(created_at) as earliest, MAX(created_at) as latest, COUNT(*) as total')
    ->first();
echo "报销数据:\n";
echo "  最早: " . ($expenseStats->earliest ?? '无') . "\n";
echo "  最新: " . ($expenseStats->latest ?? '无') . "\n";
echo "  总数: " . ($expenseStats->total ?? 0) . "\n";
"""
        
        ssh.exec_command('cat > /tmp/check_time.php << "EOFPHP"\n' + time_tinker_code + 'EOFPHP')
        time.sleep(1)
        
        stdin, stdout, stderr = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan tinker < /tmp/check_time.php')
        
        for i in range(10):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print(result)
        if error:
            print(f"错误: {error}")
        
        # 清理临时文件
        ssh.exec_command('rm /tmp/check_tables.php /tmp/check_time.php')
        
        ssh.close()
        print("\n✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
