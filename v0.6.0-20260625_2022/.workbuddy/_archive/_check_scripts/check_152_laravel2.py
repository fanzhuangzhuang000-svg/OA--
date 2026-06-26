#!/usr/bin/env python3
"""在152服务器上创建使用Laravel的测试数据生成脚本"""
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
        
        # 创建使用Laravel的PHP脚本
        print("=" * 60)
        print("创建使用Laravel的PHP脚本...")
        
        php_script = """<?php
// 加载Laravel环境
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Http\Kernel::class);
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

echo "✅ Laravel环境加载成功\n\n";

// 获取所有表名
$tables = DB::select("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename");
echo "所有表名:\n";
foreach($tables as $table) {
    echo $table->tablename . "\n";
}

echo "\n检查主要表的数据量:\n";

// 检查主要表
$checkTables = [
    'users' => '用户',
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

foreach($checkTables as $table => $name) {
    try {
        $count = DB::table($table)->count();
        echo "  {$name} ({$table}): {$count} 条\n";
    } catch (Exception $e) {
        echo "  {$name} ({$table}): 表不存在\n";
    }
}

echo "\n检查数据时间跨度:\n";

// 项目
try {
    $projectStats = DB::table('projects')
        ->selectRaw('MIN(created_at) as earliest, MAX(created_at) as latest, COUNT(*) as total')
        ->first();
    echo "  项目: {$projectStats->total} 条\n";
    echo "    最早: {$projectStats->earliest}\n";
    echo "    最新: {$projectStats->latest}\n";
} catch (Exception $e) {
    echo "  项目: 无数据\n";
}

// 考勤
try {
    $attendanceStats = DB::table('attendances')
        ->selectRaw('MIN(date) as earliest, MAX(date) as latest, COUNT(*) as total')
        ->first();
    echo "  考勤: {$attendanceStats->total} 条\n";
    echo "    最早: {$attendanceStats->earliest}\n";
    echo "    最新: {$attendanceStats->latest}\n";
} catch (Exception $e) {
    echo "  考勤: 无数据\n";
}

// 报销
try {
    $expenseStats = DB::table('expenses')
        ->selectRaw('MIN(created_at) as earliest, MAX(created_at) as latest, COUNT(*) as total')
        ->first();
    echo "  报销: {$expenseStats->total} 条\n";
    echo "    最早: {$expenseStats->earliest}\n";
    echo "    最新: {$expenseStats->latest}\n";
} catch (Exception $e) {
    echo "  报销: 无数据\n";
}
?>
"""
        
        # 将PHP脚本写入服务器
        sftp = ssh.open_sftp()
        
        # 先本地创建脚本
        with open('/tmp/check_db_laravel.php', 'w') as f:
            f.write(php_script)
        
        # 上传到服务器
        sftp.put('/tmp/check_db_laravel.php', '/tmp/check_db_laravel.php')
        sftp.close()
        
        # 运行PHP脚本
        print("\n" + "=" * 60)
        print("运行PHP脚本检查数据库...")
        stdin, stdout, stderr = ssh.exec_command('php /tmp/check_db_laravel.php')
        
        for i in range(15):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
            print(f"等待中... ({i*2}s)")
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print("\n检查结果:")
        print(result)
        if error:
            print(f"\n错误: {error}")
        
        # 清理临时文件
        ssh.exec_command('rm /tmp/check_db_laravel.php')
        
        ssh.close()
        print("\n✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
