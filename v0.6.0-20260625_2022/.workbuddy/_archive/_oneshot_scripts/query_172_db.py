import paramiko

print("📊 查询 172 服务器数据库状态...")
print("=" * 60)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 用 PHP 脚本查询数据库（避免 tinker 问题）
    print("\n创建数据库查询脚本...")
    php_script = '''
<?php
// 读取 .env 文件获取数据库配置
$env = file_get_contents('/var/www/oa-api/.env');
$lines = explode("\\n", $env);
$config = [];
foreach ($lines as $line) {
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

$conn = pg_connect("host=$db_host port=$db_port dbname=$db_name user=$db_user password=$db_pass");
if (!$conn) {
    echo "数据库连接失败\\n";
    exit(1);
}

// 查询主要表的数据量
$tables = [
    'projects', 'customers', 'leads', 'opportunities', 
    'attendance_records', 'vehicles', 'inventory_items',
    'users', 'work_orders', 'reimbursements'
];

foreach ($tables as $table) {
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM $table");
    if ($result) {
        $row = pg_fetch_assoc($result);
        echo "$table: " . $row['cnt'] . " 条\\n";
    } else {
        echo "$table: 查询失败\\n";
    }
}

pg_close($conn);
?>
'''
    
    # 上传 PHP 脚本到服务器
    sftp = ssh.open_sftp()
    remote_script = '/tmp/check_db.php'
    with open('/tmp/check_db.php', 'w') as f:
        f.write(php_script)
    sftp.put('/tmp/check_db.php', remote_script)
    sftp.close()
    
    # 运行 PHP 脚本
    print("运行数据库查询...")
    stdin, stdout, stderr = ssh.exec_command(f'php {remote_script}')
    output = stdout.read().decode()
    err = stderr.read().decode()
    
    if output:
        print("\n数据库状态:")
        print(output)
    else:
        print(f"\n查询失败: {err[:300]}")
    
    # 清理临时文件
    ssh.exec_command(f'rm {remote_script}')
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 数据库状态查询完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
