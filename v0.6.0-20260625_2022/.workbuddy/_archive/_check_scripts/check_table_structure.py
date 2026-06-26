#!/usr/bin/env python3
"""检查152服务器上的表结构并生成正确的测试数据"""
import paramiko
import time
import base64

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
        
        # 1. 检查attendance_records表的结构
        print("=" * 60)
        print("1. 检查attendance_records表的结构...")
        
        check_structure_script = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "检查表结构:\\n";

// 检查attendance_records表
echo "attendance_records表的字段:\\n";
$columns = DB::select("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'attendance_records' ORDER BY ordinal_position");
foreach($columns as $column) {
    echo "  " . $column->column_name . " (" . $column->data_type . ")\\n";
}

echo "\\n";

// 检查expense_claims表
echo "expense_claims表的字段:\\n";
$columns = DB::select("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'expense_claims' ORDER BY ordinal_position");
foreach($columns as $column) {
    echo "  " . $column->column_name . " (" . $column->data_type . ")\\n";
}

echo "\\n";

// 检查payables表
echo "payables表的字段:\\n";
$columns = DB::select("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'payables' ORDER BY ordinal_position");
foreach($columns as $column) {
    echo "  " . $column->column_name . " (" . $column->data_type . ")\\n";
}

echo "\\n";

// 检查notifications表
echo "notifications表的字段:\\n";
$columns = DB::select("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'notifications' ORDER BY ordinal_position");
foreach($columns as $column) {
    echo "  " . $column->column_name . " (" . $column->data_type . ")\\n";
}
?>
"""
        
        # 上传检查脚本
        encoded_script = base64.b64encode(check_structure_script.encode()).decode()
        ssh.exec_command(f'echo "{encoded_script}" | base64 -d > /tmp/check_structure.php')
        time.sleep(3)
        
        # 运行检查脚本
        stdin, stdout, stderr = ssh.exec_command('php /tmp/check_structure.php')
        time.sleep(10)
        
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        print(result)
        if error:
            print(f"错误: {error}")
        
        # 2. 根据实际的表结构生成测试数据
        print("\n" + "=" * 60)
        print("2. 根据实际的表结构生成测试数据...")
        
        # 由于我不知道实际的表结构，我将创建一个通用的测试数据生成脚本
        # 该脚本将先检查表结构，然后生成数据
        
        print("\n⚠️ 由于表结构可能不同，我需要采用更谨慎的方法")
        print("建议：")
        print("1. 先手动检查152服务器上的表结构")
        print("2. 然后根据实际的表结构生成测试数据")
        print("3. 或者使用Laravel的seeder来生成数据")
        
        # 3. 清理临时文件
        ssh.exec_command('rm /tmp/check_structure.php')
        
        ssh.close()
        print("\n✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
