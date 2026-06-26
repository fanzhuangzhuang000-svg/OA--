#!/usr/bin/env python3
"""在152服务器上创建PHP脚本检查数据库状态"""
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
        
        # 创建PHP脚本检查数据库
        print("=" * 60)
        print("创建PHP脚本检查数据库状态...")
        
        php_script = """<?php
// 读取.env文件
$env = file_get_contents('/var/www/oa-api/.env');
$lines = explode("\n", $env);
$config = [];
foreach($lines as $line) {
    if (strpos($line, '=') !== false) {
        list($key, $value) = explode('=', $line, 2);
        $config[trim($key)] = trim($value);
    }
}

// 连接数据库
$db_host = $config['DB_HOST'] ?? '127.0.0.1';
$db_port = $config['DB_PORT'] ?? '5432';
$db_name = $config['DB_DATABASE'] ?? 'security_oa';
$db_user = $config['DB_USERNAME'] ?? 'oa_user';
$db_pass = $config['DB_PASSWORD'] ?? '';

$conn = pg_connect("host={$db_host} port={$db_port} dbname={$db_name} user={$db_user} password={$db_pass}");
if (!$conn) {
    die("数据库连接失败\n");
}

echo "✅ 数据库连接成功\n\n";

// 检查主要表的数据量
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

echo "主要表数据量:\n";
foreach($tables as $table => $name) {
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM {$table}");
    if ($result) {
        $row = pg_fetch_assoc($result);
        echo "  {$name}: {$row['cnt']}\n";
    } else {
        echo "  {$name}: 表不存在\n";
    }
}

// 检查数据时间跨度
echo "\n数据时间跨度:\n";

// 项目
$result = pg_query($conn, "SELECT MIN(created_at) as earliest, MAX(created_at) as latest, COUNT(*) as total FROM projects");
if ($result && $row = pg_fetch_assoc($result)) {
    echo "  项目: {$row['total']} 条, 最早: {$row['earliest']}, 最新: {$row['latest']}\n";
}

// 考勤
$result = pg_query($conn, "SELECT MIN(date) as earliest, MAX(date) as latest, COUNT(*) as total FROM attendances");
if ($result && $row = pg_fetch_assoc($result)) {
    echo "  考勤: {$row['total']} 条, 最早: {$row['earliest']}, 最新: {$row['latest']}\n";
}

// 报销
$result = pg_query($conn, "SELECT MIN(created_at) as earliest, MAX(created_at) as latest, COUNT(*) as total FROM expenses");
if ($result && $row = pg_fetch_assoc($result)) {
    echo "  报销: {$row['total']} 条, 最早: {$row['earliest']}, 最新: {$row['latest']}\n";
}

pg_close($conn);
?>
"""
        
        # 将PHP脚本写入服务器
        sftp = ssh.open_sftp()
        with open('/tmp/check_db.php', 'w') as f:
            f.write(php_script)
        
        # 实际上应该通过sftp上传，但是paramiko的sftp可能有权限问题
        # 让我直接用命令创建文件
        ssh.exec_command('cat > /tmp/check_db.php << "EOFPHP"\n' + php_script + 'EOFPHP')
        time.sleep(2)
        
        # 运行PHP脚本
        print("\n" + "=" * 60)
        print("运行PHP脚本检查数据库...")
        stdin, stdout, stderr = ssh.exec_command('php /tmp/check_db.php')
        
        for i in range(10):
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
        ssh.exec_command('rm /tmp/check_db.php')
        
        ssh.close()
        print("\n✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
