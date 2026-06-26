#!/usr/bin/env python3
"""获取152服务器上所有的表名"""
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
        
        # 创建PHP脚本获取所有表名
        php_script = """<?php
$env = file_get_contents('/var/www/oa-api/.env');
$lines = explode("\n", $env);
$config = [];
foreach($lines as $line) {
    if (strpos($line, '=') !== false) {
        list($key, $value) = explode('=', $line, 2);
        $config[trim($key)] = trim($value);
    }
}

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
echo "所有表名:\n";

// 查询所有表
$result = pg_query($conn, "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename");
while ($row = pg_fetch_assoc($result)) {
    echo $row['tablename'] . "\n";
}

pg_close($conn);
?>
"""
        
        # 将PHP脚本上传到服务器
        sftp = ssh.open_sftp()
        
        # 先本地创建脚本
        with open('/tmp/get_tables.php', 'w') as f:
            f.write(php_script)
        
        # 上传到服务器
        sftp.put('/tmp/get_tables.php', '/tmp/get_tables.php')
        sftp.close()
        
        # 运行PHP脚本
        print("=" * 60)
        print("获取所有表名...")
        stdin, stdout, stderr = ssh.exec_command('php /tmp/get_tables.php')
        
        for i in range(10):
            if stdout.channel.exit_status_ready():
                break
            time.sleep(2)
            print(f"等待中... ({i*2}s)")
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print("\n结果:")
        print(result)
        if error:
            print(f"\n错误: {error}")
        
        # 清理临时文件
        ssh.exec_command('rm /tmp/get_tables.php')
        
        ssh.close()
        print("\n✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
